import io
import aiofiles
import datetime
import pandas as pd
from PIL import Image as PILImage
from fastmcp import FastMCP, Image, Context

mcp = FastMCP("My_Server")


@mcp.tool
def greet(name: str) -> str:
    '''问候语'''
    return f"Hello, {name}!"


@mcp.tool
def save_dict_to_excel(dic: list[dict], file_name=f'{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.xlsx') -> str:
    # 将list object 存储到excel 中
    df = pd.DataFrame(dic)
    df.to_excel(r'G:\AIProject\xsdcscd.xlsx', index=False)
    return f"文件保存成功, {file_name}!"


@mcp.tool()
def generate_image(width: int, height: int, color: str) -> Image:
    """Generates a solid color image."""
    img = PILImage.new("RGB", (width, height), color=color)

    # Save to a bytes buffer
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    img_bytes = buffer.getvalue()

    # Return using FastMCP's Image helper
    return Image(data=img_bytes, format="png")


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


@mcp.tool()
async def process_data(data_uri: str, ctx: Context) -> dict:
    """Process data from a resource with progress reporting."""
    await ctx.info(f"Processing data from {data_uri}")

    resource = await ctx.read_resource(data_uri)
    data = resource[0].content if resource else ""

    # Report progress
    await ctx.report_progress(progress=50, total=100)

    # Example request to the client's LLM for help
    summary = await ctx.sample(f"Summarize this in 10 words: {data[:200]}")

    await ctx.report_progress(progress=100, total=100)
    return {
        "length": len(data), "summary": summary.text
    }


@mcp.resource("file:///app/data/important_log.txt", mime_type="text/plain")
async def read_important_log() -> str:
    """Reads content from a specific log file asynchronously."""
    try:
        async with aiofiles.open("/app/data/important_log.txt", mode="r") as f:
            content = await f.read()
        return content
    except FileNotFoundError:
        return "Log file not found."


def main() -> None:
    mcp.run(transport="stdio")
