from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import httpx
import json
import os
from bs4 import BeautifulSoup
import functions_framework
from flask import Request
import re
load_dotenv()

mcp = FastMCP("websearch")

USER_AGENT = "websearch-app/1.0"

SERPER_URL="https://google.serper.dev/search"

portal_web_urls = {
    "detik": "news.detik.com/berita",
    "liputan6": "liputan6.com/news",
    "cnn": "cnnindonesia.com/nasional",
    "wikipedia": "www.wikipedia.org"
}

async def search_web(query: str) -> dict | None:
    payload = json.dumps({"q": query, "num": 2})

    headers = {
        "X-API-KEY": os.getenv("SERPER_API_KEY"),
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                SERPER_URL, headers=headers, data=payload, timeout=30.0
            )
            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException:
            return {"organic": []}
  
async def fetch_url(url: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=30.0)
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Remove unwanted elements
            for element in soup.find_all(['script', 'style', 'nav', 'footer', 'iframe']):
                element.decompose()
                
            # Get text and clean it
            text = soup.get_text(' ', strip=True)
            # Replace multiple spaces and newlines with single space
            text = re.sub(r'\s+', ' ', text)
            # Add proper paragraph separation
            text = re.sub(r'\.(?=[A-Z])', '.\n\n', text)
            return text.strip()
            
        except httpx.TimeoutException:
            return "Timeout error"

@mcp.tool()  
async def get_docs(query: str, library: str):
  """
  Search the latest content from news portals and Wikipedia.
  Supports detik, liputan6, cnn indonesia, and wikipedia.

  Args:
    query: The query to search for
    library: The portal to search in (e.g. "detik", "wikipedia")

  Returns:
    Text from the portal
  """
  if library not in portal_web_urls:
    raise ValueError(f"Portal {library} not supported by this tool")
  
  query = f"site:{portal_web_urls[library]} {query}"
  results = await search_web(query)
  if len(results["organic"]) == 0:
    return "No results found"
  
  text = ""
  for result in results["organic"]:
    text += await fetch_url(result["link"])
  return text

@functions_framework.http
def cloud_function_handler(request: Request):
    """
    Entry point for Google Cloud Functions
    Handles MCP format payload
    """
    try:
        request_json = request.get_json()
        if not request_json:
            return json.dumps({"error": "No JSON data received"}), 400
        
        # Extract function name and parameters from MCP format
        function_name = request_json.get("name")
        parameters = request_json.get("parameters", {})
        
        if function_name != "get_docs":
            return json.dumps({"error": f"Function {function_name} not found"}), 404
            
        query = parameters.get("query")
        library = parameters.get("library")
        
        if not query or not library:
            return json.dumps({"error": "Missing query or library parameter"}), 400

        # Use asyncio to run async function
        import asyncio
        result = asyncio.run(get_docs(query, library))
        return json.dumps({
            "result": result,
            "type": "success"
        })

    except Exception as e:
        return json.dumps({
            "error": str(e),
            "type": "error"
        }), 500

def main():
    # For local development
    PORT = int(os.getenv("PORT", "8080"))
    mcp.run(transport="http", host="0.0.0.0", port=PORT)
