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


mcp = FastMCP(name="postgresql_tool")


@mcp.tool()
def my_mcp_postgresql(query: str) -> Dict[str, Any]:
    """
    Execute a single read-only SQL query against a PostgreSQL database.
    """
    try:
        conn = psycopg2.connect(os.getenv("POSTGRES_URL"))
        conn.set_session(readonly=True, autocommit=True)  # força readonly na sessão
        cur = conn.cursor()
        cur.execute(query)
        result = cur.fetchall()  # fetchall em vez de fetchone
        cur.close()
        conn.close()
        return {"result": result}
    except OperationalError as e:
        return {"error": str(e)}
    except psycopg2.errors.ReadOnlySqlTransaction as e:  # captura tentativas de escrita
        return {"error": f"Operação bloqueada: sessão é somente leitura. {e}"}

def main():
    mcp.run()
if __name__ == "__main__":
    main()
