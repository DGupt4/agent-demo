import sys, os
from graph import graph

os.environ["LANGCHAIN_TRACING_V2"] = "false"

if len(sys.argv) < 2:
    print("Usage: python main.py \"<debate topic>\"")
    sys.exit(1)

topic = " ".join(sys.argv[1:])
print(f"\n{'═'*60}\nTOPIC: {topic}\n{'═'*60}")

state = graph.invoke({
    "topic":   topic,
    "messages": [],
    "round":   1,
    "scores":  {"for": 0, "against": 0},
    "verdict": "",
})

print(f"\n{'='*60}\nVERDICT\n{'='*60}\n{state['verdict']}\n")

for msg in state["messages"]:
  print(msg.content + "\n")