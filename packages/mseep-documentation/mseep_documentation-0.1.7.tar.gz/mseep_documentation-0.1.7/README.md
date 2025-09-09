[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/addhe-mcp-websearch-badge.png)](https://mseep.ai/app/addhe-mcp-websearch)

# Web Search MCP Server

A Model Context Protocol (MCP) server implementation for searching content from various Indonesian news portals and Wikipedia. This application can be deployed as a Google Cloud Function.

## What is MCP?

MCP (Model Context Protocol) is an open protocol that standardizes how applications provide context to LLMs. Think of MCP like a USB-C port for AI applications - it provides a standardized way to connect AI models to different data sources and tools.

![MCP Diagram](img/mcp-diagram-bg.png)

### Key Benefits

- A growing list of pre-built integrations that your LLM can directly plug into
- Flexibility to switch between LLM providers and vendors
- Best practices for securing your data within your infrastructure

## Architecture Overview

MCP follows a client-server architecture where a host application can connect to multiple servers:

- **MCP Hosts**: Programs like Claude Desktop, IDEs, or AI tools that want to access data through MCP
- **MCP Clients**: Protocol clients that maintain 1:1 connections with servers
- **MCP Servers**: Lightweight programs that expose specific capabilities through the standardized Model Context Protocol
- **Data Sources**: Both local (files, databases) and remote services (APIs) that MCP servers can access

## Core MCP Concepts

MCP servers can provide three main types of capabilities:

- **Resources**: File-like data that can be read by clients (like API responses or file contents)
- **Tools**: Functions that can be called by the LLM (with user approval)
- **Prompts**: Pre-written templates that help users accomplish specific tasks

## System Requirements

- Python 3.11 or higher
- Google Cloud SDK
- Google Cloud account with billing enabled
- Serper API key for web search functionality

## Local Development Setup

1. Clone the repository:
```bash
git clone git@github.com:addhe/mcp-websearch.git
cd mcp-websearch
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your Serper API key:
```
SERPER_API_KEY=your_api_key_here
```

5. Run locally:
```bash
python main.py
```

## VS Code Integration

1. Create `.vscode/mcp.json` with the following configuration:
```json
{
    "servers": {
        "my-mcp-server-websearch": {
            "type": "http",
            "url": "https://your-cloud-function-url.cloudfunctions.net/websearch"
        }
    }
}
```

2. Install any MCP-compatible extension in VS Code to use the search functionality.

## Deploying to Google Cloud Functions

### Prerequisites

1. Install the [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
2. Initialize the SDK and set your project:
```bash
gcloud init
```

### Deployment Steps

1. Make sure your SERPER_API_KEY is set in your environment:
```bash
export SERPER_API_KEY=your_api_key_here
```

2. Run the deployment script:
```bash
./deploy.sh
```

The script will:
- Enable required Google Cloud APIs
- Deploy the function with Python 3.11 runtime
- Configure the function with your SERPER_API_KEY

### Function Usage

When using the MCP protocol, send HTTP POST requests with this JSON body format:

```json
{
    "name": "get_docs",
    "parameters": {
        "query": "your search query",
        "library": "detik|liputan6|cnn|wikipedia"
    }
}
```

Example response:
```json
{
    "result": "Text content from the searched portal",
    "type": "success"
}
```

Available portals:
- detik (news.detik.com/berita)
- liputan6 (liputan6.com/news)
- cnn (cnnindonesia.com/nasional)
- wikipedia (www.wikipedia.org)

## Technical Details

- Runtime: Python 3.11
- HTTP Trigger with MCP protocol support
- Async implementation using httpx and aiohttp
- BeautifulSoup4 for HTML parsing
- Memory: 256MB (default)
- Timeout: 60 seconds (default)

## Environment Variables

- `SERPER_API_KEY`: Your Google Serper API key for web search functionality (required)

## Error Handling

The function returns appropriate HTTP status codes:
- 200: Successful request with MCP format response
- 400: Missing or invalid parameters
- 404: Function name not found
- 500: Server error or timeout

Error responses follow MCP format:
```json
{
    "error": "Error message",
    "type": "error"
}
```

## Limitations

- Maximum timeout: 60 seconds
- Maximum memory: 256MB (can be increased if needed)
- Rate limits apply based on your Serper API plan
- Currently supports only Indonesian news portals and Wikipedia

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
