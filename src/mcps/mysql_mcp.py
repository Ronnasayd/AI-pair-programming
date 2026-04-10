#!/home/ronnas/develop/personal/AI-pair-programming/src/venv/bin/python3
"""
mysql.py

Implements a FastMCP server with tools for Mysql database interaction.
This module is designed for extensibility and integration with AI-powered workflows.
"""

import os
from typing import Any, Dict
from urllib.parse import urlparse
import mysql.connector
from mysql.connector import Error

from mcp.server.fastmcp import FastMCP


mcp = FastMCP(name="mysql_tool")


def _parse_mysql_url(url: str) -> Dict[str, Any]:
    """
    Parse a Mysql connection URL into mysql.connector config dict.
    Expected format: mysql://user:password@host:port/database
    """
    parsed = urlparse(url)
    return {
        "host": parsed.hostname,
        "port": parsed.port or 3306,
        "user": parsed.username,
        "password": parsed.password,
        "database": parsed.path.lstrip("/"),
    }


@mcp.tool()
def my_mcp_mysql(query: str) -> Dict[str, Any]:
    """
    Execute a single read-only SQL query against a Mysql database.
    """
    conn = None
    try:
        config = _parse_mysql_url(os.getenv("MYSQL_URL"))
        conn = mysql.connector.connect(**config)

        cur = conn.cursor()
        cur.execute("SET SESSION TRANSACTION READ ONLY")
        cur.execute("START TRANSACTION")

        cur.execute(query)
        result = cur.fetchall()

        conn.rollback()
        cur.close()

        return {"result": result}

    except Error as e:
        if "read-only" in str(e).lower() or e.errno in (1290, 1792):
            return {"error": f"Operação bloqueada: sessão é somente leitura. {e}"}
        return {"error": str(e)}

    finally:
        if conn and conn.is_connected():
            conn.close()

def  main():
     mcp.run()
if __name__ == "__main__":
    main()
