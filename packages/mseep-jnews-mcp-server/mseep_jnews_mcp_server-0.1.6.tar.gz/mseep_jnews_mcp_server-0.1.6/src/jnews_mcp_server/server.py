# import asyncio
import httpx
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
# from pydantic import AnyUrl
import mcp.server.stdio
import os
from dotenv import load_dotenv
load_dotenv()  # 从.env文件加载环境变量


server = Server("jnews-mcp-server")

JUHE_NEWS_API_BASE = "https://v.juhe.cn/toutiao"
JUHE_NEWS_API_KEY = os.environ.get("JUHE_NEWS_API_KEY")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools.
    Each tool specifies its arguments using JSON Schema validation.
    """
    return [
        types.Tool(
            name="get_news_list",
            description="通过新闻类型获取今日热点新闻头条",
            inputSchema={
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string", "description": "新闻类型:top(推荐,默认),guonei(国内),guoji(国际),yule(娱乐),tiyu(体育),junshi(军事),keji(科技),caijing(财经),youxi(游戏),qiche(汽车),jiankang(健康)",
                    },
                    "page": {
                        "type": "number", "description": "当前页数, 默认1, 最大50"
                    },
                    "page_size": {
                        "type": "number", "description": "每页返回新闻条数, 默认20, 最大50"
                    },
                },
                # "required": ["type"],
            },
        ),
        types.Tool(
            name="get_news_content",
            description="根据新闻ID获取新闻的详细内容",
            inputSchema={
                "type": "object",
                "properties": {
                    "uniquekey": {"type": "string", "description": "新闻ID(gew_news_list中返回的uniquekey)"},  
                },
                "required": ["uniquekey"],
            },
        ),
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle tool execution requests.
    Tools can modify server state and notify clients of changes.
    """
    if name == "get_news_list":
        type_value = type_value = arguments.get("type", "top") if arguments else "top"
        return await get_news_list(type_value)
    elif name == "get_news_content":
        uniquekey = arguments.get("uniquekey") if arguments else None
        if not uniquekey:
            raise ValueError("Missing name or content")
        return await get_news_content(uniquekey)
    else:
        raise ValueError(f"Unknown tool: {name}")
        # return [
        #     types.TextContent(
        #         type="text",
        #         text=f"Added note '{note_name}' with content: {content}",
        #     )
        # ]

async def get_news_list(type: str = "top", page: int = 1, page_size: int = 20) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    根据新闻类型获取今日热点新闻头条.
    """
    url = f"{JUHE_NEWS_API_BASE}/index"
    params = {
        "type": type,
        "page": page,
        "page_size": page_size,
        "key": JUHE_NEWS_API_KEY
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        data = response.json()
        if data["error_code"] == 0:
            news_list = data["result"]["data"]
            return [
                types.TextContent(
                    type="text",
                    text=f"{news_list}"
                )
            ]
        else:
            return [
                types.TextContent(
                    type="text",
                    text=f"Error: {data['reason']}"
                )
            ]

async def get_news_content(uniquekey: str) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    根据新闻ID(uniquekey)获取新闻的详细内容.
    """
    url = f"{JUHE_NEWS_API_BASE}/content"
    params = {
        "uniquekey": uniquekey,
        "key": JUHE_NEWS_API_KEY
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        data = response.json()
        if data["error_code"] == 0:
            news_content = data["result"]
            return [
                # types.TextContent(
                #     type="text",
                #     text=f"""
                #     标题: {news_content['title']}
                #     作者: {news_content['author_name']}
                #     URL: {news_content['url']}
                #     新闻id: {news_content['uniquekey']}
                #     新闻内容: {news_content['content']}
                #     """
                # )
                types.TextContent(
                    type="text",
                    text=f"{news_content}"
                )
            ]
        else:
            return [
                types.TextContent(
                    type="text",
                    text=f"Error: {data['reason']}"
                )
            ]

async def main():
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="jnews-mcp-server",
                server_version="0.1.3",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )