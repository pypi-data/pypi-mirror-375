# MCP Server

A minimal Model Context Protocol (MCP) server that exposes documentation-search tools for any AI agent. Use this server to fetch and search docs for popular libraries (LangChain, LlamaIndex, OpenAI) and wire them seamlessly into your agents.

---

## Features

* **Doc Search Tool**: Provides a `get_docs` tool to search and fetch documentation based on a query and library.
* **Web Scraping**: Uses Serper API for search results and BeautifulSoup for fetching page text.
* **Easy Integration**: Decorate functions with `@mcp.tool()` and run the server over stdio transport.

---

## Prerequisites

* Python 3.8 or higher
* A Serper API key (set in `.env` as `SERPER_API_KEY`)

---

## Installation

1. Clone this repo:

   ```bash
   git clone https://github.com/<your-username>/MCP-Server-Latest_Doc-.git
   cd MCP-Server-Latest_Doc-
   ```

2. Create a virtual environment & install dependencies:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. Add your Serper API key in a `.env` file:

   ```bash
   echo "SERPER_API_KEY=your_api_key_here" > .env
   ```

---

## Usage

### Running the MCP Server

Execute the main script to start the MCP server on stdio:

```bash
python main.py
```

### Using the `get_docs` Tool

Within any AI agent that supports MCP, the `get_docs` tool will automatically register. It expects two arguments:

1. `query`: The search term (e.g., `"Chroma DB"`).
2. `library`: One of `langchain`, `llama-index`, or `openai`.

The tool returns the concatenated text of the top search results from the specified library docs.

---

## Integrating into an AI Agent

Any agent framework that implements the MCP transport can import and run this server. For example, in Python:

```python
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import os

load_dotenv()

mcp = FastMCP("docs")

# ... define @mcp.tool() functions here ...

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

After starting this script, your agent can call the `get_docs` tool over the stdio channel.

---

## Example: Using with Claude Code CLI

First, install the Claude Code CLI:

```bash
npm install -g @anthropic-ai/claude-code
```

Add the MCP server to Claude:

```bash
claude mcp add
```

Specify the `uv` binary path (find with `where uv`):

```bash
claude mcp configure --binary-path /full/path/to/uv
```

Set the working directory of the server:

```bash
claude mcp configure --workdir /path/to/MCP-Server-Latest_Doc-
```

Run the MCP server:

```bash
python main.py
```

Confirm registration:

```bash
claude mcp list
```

For debugging, you can use the Inspector:

```bash
npx @modelcontextprotocol/inspector uv run main.py
```

---

## License

MIT © <Your Name>
