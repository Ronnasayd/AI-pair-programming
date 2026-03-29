#!/home/ronnas/develop/personal/AI-pair-programming/src/venv/bin/python3
"""
postgresql.py

Implements a FastMCP server with tools for PostgreSQL database interaction.
This module is designed for extensibility and integration with AI-powered workflows.
"""

import os
from typing import Any, Dict
import psycopg2
from psycopg2 import OperationalError

from mcp.server.fastmcp import FastMCP


# Properly initializes the MCP server
mcp = FastMCP(name="postgresql_tool")


@mcp.tool()
def my_mcp_postgresql(query: str) -> Dict[str, Any]:
    try:
        conn = psycopg2.connect(os.getenv("POSTGRES_URL"))
        cur = conn.cursor()
        cur.execute(query)
        result = cur.fetchone()
        cur.close()
        conn.close()
        return {"result": result}
    except OperationalError as e:
        return {"error": str(e)}


if __name__ == "__main__":
    mcp.run()  # Starts the server using stdio by default
