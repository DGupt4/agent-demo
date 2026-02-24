from langchain_openai import ChatOpenAI
from langgraph.graph import START, END, StateGraph
from langgraph.graph.message import add_messages
from langchain_core.messages import ToolMessage, SystemMessage

from tools import TOOLS, TOOL_MAP
from typing import Annotated, Literal
from typing_extensions import TypedDict

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    count: int

llm = ChatOpenAI(base_url="http://127.0.0.1:1234/v1", model="openai/gpt-oss-20b", api_key="sk-lm-2PGULx4r:xvKyZEs7oqhtIJSlDFwv")
llm = llm.bind_tools(TOOLS)

SYSTEM_PROMPT = "Just use the tools!"

def llm_node(state: AgentState) -> AgentState:
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = llm.invoke(messages)

    if response.tool_calls:
        print(f"[LLM NODE] Tool Call: {response.tool_calls[0]["name"]} | Args: {response.tool_calls[0]["args"]}")
    else:
        print(f"[LLM NODE] Content: {response.content}")

    return {"messages": [response], "count": state.get("count", 0) + 1}

def tool_node(state: AgentState) -> AgentState:

    last_message = state["messages"][-1]
    results = []

    for tc in last_message.tool_calls:
        tool_fnc = TOOL_MAP[tc["name"]]
        result_text = str(tool_fnc.invoke(tc["args"]))
        results.append(ToolMessage(content=result_text, tool_call_id=tc["id"], name=tc["name"]))

    print(f"[TOOL NODE] Content: {result_text}")

    return {"messages": results, "iteration": state.get("iteration", 0)}

def should_continue(state: AgentState) -> Literal["tool_node", END]:

    messages = state["messages"]
    last_message = messages[-1]


    if last_message.tool_calls:
        print(f"[ROUTER] Going to tool node")
        return "tool"
    print(f"[ROUTER] Ending agent")
    return END

def build_graph():
    builder = StateGraph(AgentState)
    builder.add_node("llm", llm_node)
    builder.add_node("tool",tool_node)

    builder.add_edge(START, "llm")
    builder.add_conditional_edges(
        "llm",
        should_continue,
        ["tool", END]
    )
    builder.add_edge("tool", "llm")

    return builder.compile()

graph = build_graph()