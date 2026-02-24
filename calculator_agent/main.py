import os
from langchain_core.messages import HumanMessage
from graph import graph

os.environ["LANGCHAIN_TRACING_V2"] = "false"

def run(question: str) -> str:
  state = graph.invoke({"messages": [HumanMessage(content=question)], "iteration": 0})
  answer = state["messages"][-1].content
  return answer

if __name__ == "__main__":
  while True:
    print('-' * 50)
    q = input("Q: ")
    print(f"A: {run(q)}")
    print('-' * 50 + "\n\n")