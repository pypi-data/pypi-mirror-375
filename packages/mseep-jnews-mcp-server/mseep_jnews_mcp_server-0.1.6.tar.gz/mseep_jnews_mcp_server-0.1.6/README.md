# Juhe News MCP Server

一个提供新闻头条信息功能的模型上下文协议（Model Context Protocol）服务器。该服务器使大型语言模型（LLMs）能够获取当前最新的热点新闻头条（包括：推荐、国内、科技、体育等类型）及详细内容信息。


## Components

### Tools

服务器实现了两个工具:

- get_news_list: 根据新闻类型获取今日热点新闻头条
  - 需要传入 "type"（新闻类型）作为选填的字符串参数。
```
async def get_news_list(type: str = "top", page: int = 1, page_size: int = 20) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
```

- get_news_content: 根据新闻类型获取今日热点新闻头条
  - 需要传入 "uniquekey"（新闻id）作为必须的字符串参数。
```
async def get_news_content(uniquekey: str) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
```



## Install
This server requires Python 3.10 or higher. Install dependencies using uv (recommended) or pip

### Using uv (recommended)
When using [uv](https://docs.astral.sh/uv/) no specific installation is needed. We will use [uvx](https://docs.astral.sh/uv/guides/tools/) to directly run jnews-mcp-server.

```bash
uvx jnews-mcp-server
```

### Using PIP
Alternatively you can install jnews-mcp-server via pip:
```
pip install jnews-mcp-server
```
After installation, you can run it as a script using:
```
python -m jnews_mcp_server
```

### Configuration

#### Environment Variables
`JUHE_NEWS_API_KEY`: 聚合数据的新闻头条API密钥。获取：[https://www.juhe.cn/docs/api/id/235](https://www.juhe.cn/docs/api/id/235)
```
JUHE_NEWS_API_KEY=your_api_key
```

#### Claude Desktop

- On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`
- On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

<details>
  <summary>Using uvx</summary>

  ```
  "mcpServers": {
    "jnews-mcp-server": {
      "command": "uvx",
      "args": [
        "jnews-mcp-server"
      ],
      "env": {
        "JUHE_NEWS_API_KEY": "your_api_key"
      }
    }
  }
  ```
</details>

<details>
  <summary>Using pip installation</summary>

  ```
  "mcpServers": {
    "jnews-mcp-server": {
      "command": "python",
      "args": [
        "-m",
        "jnews_mcp_server"
      ],
      "env": {
        "JUHE_NEWS_API_KEY": "your_api_key"
      }
    }
  }
  ```
</details>

## Debugging
You can use the MCP inspector to debug the server. For uvx installations:

```bash
npx @modelcontextprotocol/inspector uvx jnews-mcp-server 
```

Or if you've installed the package in a specific directory or are developing on it:

```bash
cd path/to/servers/src/jnews-mcp-server
npx @modelcontextprotocol/inspector uv run jnews-mcp-server
```

## Examples of Questions for Cline
1. "今日有哪些热点新闻?"
2. "当前体育热点头条?"
3. "第5条新闻的详细内容"