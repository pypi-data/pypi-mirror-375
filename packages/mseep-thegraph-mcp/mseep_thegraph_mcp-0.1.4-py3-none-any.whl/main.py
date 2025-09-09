from mcp.server.fastmcp import FastMCP
import httpx
import json
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Create MCP server instance
mcp = FastMCP("TheGraph MCP Server")

# Base URL for The Graph decentralized network API
THEGRAPH_API_BASE_URL = "https://gateway.thegraph.com/api/"

# Retrieve API key from environment variables
API_KEY = os.getenv("THEGRAPH_API_KEY")

def json_to_graphql_schema(schema_json):
    """Convert JSON schema from introspection to GraphQL text format."""
    types = schema_json["types"]
    schema_text = ""
    
    for t in types:
        if t["kind"] == "OBJECT" and not t["name"].startswith("__"):
            schema_text += f"type {t['name']} {{\n"
            if t["fields"]:
                for f in t["fields"]:
                    field_type = f["type"]
                    type_name = field_type["name"]
                    if field_type["kind"] == "NON_NULL":
                        type_name = f"{field_type['ofType']['name']}!"
                    elif field_type["kind"] == "LIST":
                        type_name = f"[{field_type['ofType']['name']}]"
                    schema_text += f"  {f['name']}: {type_name}\n"
            schema_text += "}\n\n"
    
    return schema_text.strip()

@mcp.tool()
async def getSubgraphSchema(subgraphId: str, asText: bool = False) -> str:
    """Fetch the schema of a specified subgraph using GraphQL introspection.

    Args:
        subgraphId (str): The ID of the subgraph to query.
        asText (bool): If True, return schema as GraphQL text; otherwise, return JSON.

    Returns:
        str: Schema in JSON or GraphQL text format, or an error message.
    """
    if not API_KEY:
        return "API key is required. Set THEGRAPH_API_KEY in your .env file."
    
    async with httpx.AsyncClient() as client:
        url = f"{THEGRAPH_API_BASE_URL}{API_KEY}/subgraphs/id/{subgraphId}"
        introspection_query = """
        query IntrospectionQuery {
          __schema {
            types {
              name
              kind
              fields {
                name
                type {
                  name
                  kind
                  ofType {
                    name
                    kind
                  }
                }
              }
            }
          }
        }
        """
        try:
            response = await client.post(url, json={"query": introspection_query}, timeout=10)
            response.raise_for_status()
            schema_data = response.json()
            if "data" in schema_data and "__schema" in schema_data["data"]:
                schema = schema_data["data"]["__schema"]
                return json_to_graphql_schema(schema) if asText else json.dumps(schema)
            else:
                return f"Failed to fetch schema for {subgraphId}"
        except httpx.HTTPError as e:
            return f"Error fetching schema: {str(e)}"

@mcp.tool()
async def querySubgraph(subgraphId: str, query: str) -> str:
    """Execute a GraphQL query against a specified subgraph.

    Args:
        subgraphId (str): The ID of the subgraph to query.
        query (str): The GraphQL query string to execute.

    Returns:
        str: Query result in JSON format, or an error message.
    """
    if not API_KEY:
        return "API key is required. Set THEGRAPH_API_KEY in your .env file."
    
    async with httpx.AsyncClient() as client:
        url = f"{THEGRAPH_API_BASE_URL}{API_KEY}/subgraphs/id/{subgraphId}"
        try:
            response = await client.post(url, json={"query": query}, timeout=10)
            response.raise_for_status()
            return json.dumps(response.json())
        except httpx.HTTPError as e:
            return f"Error executing query: {str(e)}"

def main():
    # Start the MCP server
    mcp.run()
