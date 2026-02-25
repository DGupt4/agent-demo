from langchain_openai import ChatOpenAI
from langgraph.graph import START, END, StateGraph
from langgraph.graph.message import add_messages
from langchain_core.messages import AIMessage, ToolMessage, SystemMessage, HumanMessage
from pydantic import BaseModel

from typing import Annotated, Literal
from typing_extensions import TypedDict

class DebateState(TypedDict):
  messages: Annotated[list, add_messages]
  topic: str
  round: int
  scores: dict
  verdict: str

class JudgeResult(BaseModel):
  verdict: str
  reason: str
  should_continue: bool

llm = ChatOpenAI(base_url="http://127.0.0.1:1234/v1", model="google/gemma-3-12b", api_key="sk-lm-2PGULx4r:xvKyZEs7oqhtIJSlDFwv")

def plato_agent(state: DebateState) -> DebateState:
  print("Plato is thinking...")

  SYSTEM_PROMPT = f"You are Plato, a philosopher in a debate. Arguing FOR this position {state['topic']}. Keep responses to a maximum of 3 sentences."

  history = '\n'.join([f"{m.type}: {m.content}" for m in state["messages"][-4:]])
  r = llm.invoke([SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=f"Conversation History: {history}")])
  return {"messages": [AIMessage(content=f"Plato's Argument: {r.content}")], "round": state["round"] + 1}

def aristotle_agent(state: DebateState) -> DebateState:
  print("Aristotle is thinking...")

  SYSTEM_PROMPT = f"You are Aristotle, a philosopher in a debate. Arguing AGAINST this position {state['topic']}. Keep responses to a maximum of 3 sentences."

  history = '\n'.join([f"{m.type}: {m.content}" for m in state["messages"][-4:]])
  r = llm.invoke([SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=f"Conversation History: {history}")])
  return {"messages": [AIMessage(content=f"Aristotle's Argument: {r.content}")], "round": state["round"] + 1}

def judge_agent(state: DebateState) -> DebateState:
  print("Judge is thinking...")
  plato_history = '\n'.join([f"{m.type}: {m.content}" for m in state["messages"] if "Plato's Argument" in m.content])
  aristotle_history = '\n'.join([f"{m.type}: {m.content}" for m in state["messages"] if "Aristotle's Argument" in m.content])

  SYSTEM_PROMPT = """ You are a neutral academic debate judge. " 
                   Judge argument quality only, not the topic. Always return a verdict and reason. 
                   Set should_continue=True unless one side has made a clearly decisive argument.
                     The debate should usually last 3-5 rounds. """

  HUMAN_PROMPT = f""" Topic: {state['topic']}\n\n
                  Plato (FOR):\n{plato_history}\n\n
                  Aristotle (AGAINST):\n{aristotle_history}\n\n
                  Who made the stronger argument? Provide a verdict and the reasoning."""

  r = llm.with_structured_output(JudgeResult).invoke([
    SystemMessage(content=SYSTEM_PROMPT),
    HumanMessage(content=HUMAN_PROMPT)
  ])

  verdict = f"Winner: {r.winner}\nReason: {r.reason}" if not r.should_continue else ""
  return {"verdict": verdict, "messages": [AIMessage(content=f"[JUDGE] {r.reason}")]}

def post_judge(state: DebateState) -> str:
  return END if state["verdict"] or state["round"] > 8 else "plato"

builder = StateGraph(DebateState)
builder.add_node("plato", plato_agent)
builder.add_node("aristotle", aristotle_agent)
builder.add_node("judge", judge_agent)
builder.add_edge(START, "plato")
builder.add_edge("plato", "aristotle")
builder.add_edge("aristotle", "judge")
builder.add_conditional_edges("judge", post_judge, {END: END, "plato": "plato"})

graph = builder.compile()