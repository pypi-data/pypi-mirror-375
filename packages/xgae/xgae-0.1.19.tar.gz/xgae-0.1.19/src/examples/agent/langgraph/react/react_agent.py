import logging
import os

from typing import Any, Dict, List, Annotated, Sequence, TypedDict, Optional, AsyncGenerator
from uuid import uuid4

from langfuse.callback import CallbackHandler
from langfuse import Langfuse

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.message import add_messages
from langgraph.config import get_stream_writer

from xgae.utils.misc import read_file
from xgae.utils import log_trace

from xgae.engine.engine_base import XGATaskResult, XGAResponseMessage
from xgae.engine.mcp_tool_box import XGAMcpToolBox
from xgae.engine.task_engine import XGATaskEngine


class AgentContext(TypedDict, total=False):
    task_id: str
    session_id: str
    user_id: str
    agent_id: str
    thread_id: str


class TaskState(TypedDict, total=False):
    """State definition for the agent orchestration graph"""
    messages: Annotated[Sequence[BaseMessage], add_messages]  # for message persistent
    user_input: str
    next_node: str
    system_prompt: str
    custom_tools: List[str]
    general_tools: List[str]
    task_result: XGATaskResult
    final_result: XGATaskResult
    iteration_count: int
    agent_context: AgentContext


class XGAReactAgent:
    MAX_TASK_RETRY = 2

    def __init__(self):
        self.tool_box = XGAMcpToolBox(custom_mcp_server_file="mcpservers/custom_servers.json")
        self.graph = None
        self.graph_config = None
        self.graph_langfuse = Langfuse(enabled=False)

        self.task_engine: XGATaskEngine = None

    async def _create_graph(self) -> StateGraph:
        try:
            graph_builder = StateGraph(TaskState)

            # Add nodes
            graph_builder.add_node('supervisor', self._supervisor_node)
            graph_builder.add_node('select_tool', self._select_tool_node)
            graph_builder.add_node('exec_task', self._exec_task_node)
            graph_builder.add_node('final_result', self._final_result_node)

            # Add edges
            graph_builder.add_edge(START, 'supervisor')
            graph_builder.add_conditional_edges(
                'supervisor',
                self._next_condition,
                {
                    'select_tool': 'select_tool',
                    'exec_task': 'exec_task',
                    'end': END
                }
            )

            graph_builder.add_edge('select_tool', 'exec_task')
            graph_builder.add_edge('exec_task', 'final_result')

            graph_builder.add_conditional_edges(
                'final_result',
                self._next_condition,
                {
                    'supervisor': 'supervisor',
                    'exec_task': 'exec_task',
                    'end': END
                }
            )
            
            graph = graph_builder.compile(checkpointer=MemorySaver())
            graph.name = "XGARectAgentGraph"

            return graph
        except Exception as e:
            logging.error("Failed to create XGARectAgent Graph: %s", str(e))
            raise

    def _search_system_prompt(self, user_input: str) -> str:
        # You should search RAG use user_input, fetch COT or Prompt for your business
        system_prompt = None if "fault" not in user_input else read_file("templates/example/fault_user_prompt.txt")
        return system_prompt

    async def _supervisor_node(self, state: TaskState) -> Dict[str, Any]:
        user_input = state.get("user_input", "")
        system_prompt = self._search_system_prompt(user_input)

        general_tools = [] if system_prompt else ["*"]
        custom_tools = ["*"] if system_prompt  else []

        next_node = "select_tool" if system_prompt else "exec_task"

        return {
            'system_prompt' : system_prompt,
            'next_node'     : next_node,
            'general_tools' : general_tools,
            'custom_tools'  : custom_tools,
        }

    def _select_custom_tools(self, system_prompt: str) -> list[str]:
        custom_tools = ["*"] if system_prompt  else []
        return custom_tools

    async def _select_tool_node(self, state: TaskState) -> Dict[str, Any]:
        system_prompt = state.get('system_prompt',None)
        general_tools = []
        custom_tools = self._select_custom_tools(system_prompt)
        return {
            'general_tools' : general_tools,
            'custom_tools'  : custom_tools,
        }

    async def _exec_task_node(self, state: TaskState) -> Dict[str, Any]:
        user_input = state['user_input']
        system_prompt = state.get('system_prompt',None)
        general_tools = state.get('general_tools',[])
        custom_tools = state.get('custom_tools',[])
        is_system_prompt = True if system_prompt is not None else False

        trace_id = self.graph_langfuse.get_trace_id()
        try:
            logging.info(f"🔥 XGATaskEngine run_task: user_input={user_input}, general_tools={general_tools}, "
                         f"custom_tools={custom_tools}, is_system_prompt={is_system_prompt}")
            if self.task_engine is None:
                self.task_engine = XGATaskEngine(
                    task_id         = state['agent_context']['task_id'],
                    session_id=state['agent_context'].get('session_id', None),
                    user_id         = state['agent_context'].get('user_id', None),
                    agent_id        = state['agent_context'].get('agent_id', None),
                    tool_box        = self.tool_box,
                    general_tools   = general_tools,
                    custom_tools    = custom_tools,
                    system_prompt   = system_prompt
                )

            chunks = []
            stream_writer = get_stream_writer()
            async for chunk in self.task_engine.run_task(task_input={"role": "user", "content": user_input},
                                                         trace_id=trace_id):
                chunks.append(chunk)
                stream_writer({"engine_message": chunk})

            task_result = self.task_engine.parse_final_result(chunks)
        except Exception as e:
            logging.error(f"XReactAgent exec_task_node: Failed to execute task: {e}")
            task_result = XGATaskResult(type="error", content="Failed to execute task")

        iteration_count = state.get('iteration_count', 0) + 1
        return {
            'task_result' : task_result,
            'iteration_count': iteration_count,
        }

    async def _final_result_node(self, state: TaskState) -> Dict[str, Any]:
        user_input = state['user_input']
        iteration_count = state['iteration_count']
        task_result = state['task_result']

        next_node = "end"
        if task_result['type'] == "error" and iteration_count < self.MAX_TASK_RETRY:
            next_node = "supervisor"
            final_result = None
        elif task_result['type'] == "ask":
            final_result = task_result
            logging.info(f"XReactAgent final_result_node: ASK_USER_QUESTION: {task_result['content']}")
            user_input = interrupt({
                'final_result' : final_result
            })
            logging.info(f"XReactAgent final_result_node: ASK_USER_ANSWER: {user_input}")
            next_node = "exec_task"
        else:
            final_result = task_result

        return {
            'user_input' : user_input,
            'next_node' : next_node,
            'final_result' : final_result,
        }


    def _next_condition(self, state: TaskState) -> str:
        next_node = state['next_node']
        return next_node


    async def generate_with_result(self, user_input: str,
                                   agent_context: Optional[AgentContext] = None,
                                   is_resume: Optional[bool]=False) -> XGATaskResult:
        agent_context = agent_context or {}
        try:

            if is_resume:
                logging.info(f"=== Start React Agent for USER_ASK_ANSWER: {user_input}")
                graph_input = Command(resume=user_input)
            else:
                logging.info(f"=== Start React Agent for USER_INPUT: {user_input}")
                graph_input = await self._prepare_graph_start(user_input, agent_context)

            final_state = await self.graph.ainvoke(graph_input, config=self.graph_config)

            if "__interrupt__" in final_state:
                interrupt_event = final_state["__interrupt__"][0]
                interrupt_value = interrupt_event.value
                result = interrupt_value['final_result']
            else:
                result = final_state['final_result']

            return result
        except Exception as e:
            log_trace(e, f"XReactAgent generate: user_input={user_input}")
            result = XGATaskResult(type="error", content=f"React Agent error: {e}")
            return result


    async def generate(self, user_input: str,
                       agent_context: Optional[AgentContext]=None,
                       is_resume: Optional[bool]=False) -> AsyncGenerator[Dict[str, Any], None]:
        agent_context = agent_context or {}
        try:
            if is_resume:
                logging.info(f"=== Start React Stream Agent for USER_ASK_ANSWER: {user_input}")
                graph_input = Command(resume=user_input)
            else:
                logging.info(f"=== Start React Stream Agent USER_ASK_ANSWER: {user_input}")
                graph_input = await self._prepare_graph_start(user_input, agent_context)

            async for msg_type, message in self.graph.astream(input=graph_input,
                                                              config=self.graph_config,
                                                              stream_mode=["custom", "updates"]):
                if msg_type == "updates" and '__interrupt__' in message:
                    interrupt_event = message["__interrupt__"][0]
                    interrupt_value = interrupt_event.value
                    final_result = interrupt_value['final_result']
                    yield final_result
                elif msg_type == "updates" and 'final_result' in message:
                    message = message['final_result']
                    final_result = message.get('final_result', None)
                    if final_result:
                        yield final_result
                elif msg_type == "custom" and 'engine_message' in message:
                    message = {'type': "message", 'content': message['engine_message']}
                    yield message

        except Exception as e:
            log_trace(e, f"XReactAgent generate: user_input={user_input}")
            yield XGATaskResult(type="error", content=f"React Agent error: {e}")


    async def _prepare_graph_start(self, user_input, agent_context: AgentContext):
        if self.graph is None:
            self.graph = await self._create_graph()

        agent_context = agent_context or {}
        task_id = agent_context.get("task_id", f"xga_task_{uuid4()}")
        agent_context["task_id"] = task_id
        thread_id = agent_context.get('thread_id', task_id)
        agent_context['thread_id'] = thread_id
        session_id = agent_context.get('session_id', task_id)
        agent_context['session_id'] = session_id

        graph_input = {
            'messages'          : [HumanMessage(content=f"information for: {user_input}")],
            'user_input'        : user_input,
            'next_node'         : None,
            'agent_context'     : agent_context,
            'iteration_count'   : 0
        }

        langfuse_handler = self._get_langfuse_handler(agent_context)
        callbacks = None
        if langfuse_handler:
            callbacks = [langfuse_handler]
            self.graph_langfuse = langfuse_handler.langfuse


        self.graph_config = {
            'recursion_limit': 100,
            'configurable': {
                'thread_id': thread_id
            },
            'callbacks': callbacks
        }

        return graph_input


    def _get_langfuse_handler(self, agent_context: AgentContext)->CallbackHandler:
        langfuse_handler = None
        public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
        secret_key = os.getenv("LANGFUSE_SECRET_KEY")
        host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

        if public_key and secret_key:
            langfuse_handler =  CallbackHandler(
                public_key  = public_key,
                secret_key  = secret_key,
                host        = host,
                trace_name  = "xga_react_agent",
                session_id  = agent_context.get('session_id', None),
                user_id     = agent_context.get('user_id', None),
            )
        return langfuse_handler


