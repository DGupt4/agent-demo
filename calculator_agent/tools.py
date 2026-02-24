from langchain.tools import tool

@tool
def multiply(a: int, b: int) -> int:
    """ This function MULTIPLIES integers 'a' and 'b' and returns the output. """
    return a * b

@tool
def add(a: int, b: int) -> int:
    """ This function ADDS integers 'a' and 'b' and returns the output. """
    return a + b

@tool
def subtract(a: int, b: int) -> int:
    """ This function SUBTRACTS integers 'a' and 'b' and returns the output. """
    return a - b

@tool
def divide(a: int, b: int) -> float:
    """ This function DIVIDES integers 'a' and 'b' and returns the output. """
    return a / b

TOOLS = [multiply, add, subtract, divide]
TOOL_MAP = {tool.name: tool for tool in TOOLS}