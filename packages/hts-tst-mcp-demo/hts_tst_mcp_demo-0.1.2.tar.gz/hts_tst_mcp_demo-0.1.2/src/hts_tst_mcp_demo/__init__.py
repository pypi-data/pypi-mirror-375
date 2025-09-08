from fastmcp import FastMCP

mcp = FastMCP("My_Server")


@mcp.tool
def greet(name: str) -> str:
    '''问候语'''
    return f"Hello, {name}!"


@mcp.tool()
def deal_num(a: float, n: float) -> float:
    """计算数字a 的n次方"""
    return a ** n


@mcp.tool()
def divide(a: float, b: float) -> float:
    """Divide a by b."""
    if b == 0:
        # Raise a standard exception
        raise ValueError("Division by zero is not allowed.")
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError("Both arguments must be numbers.")
    return a / b


def main() -> None:
    mcp.run(transport="stdio")
