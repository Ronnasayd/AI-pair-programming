#!/usr/bin/env python3
"""
sqlite_mcp.py

Implements a FastMCP server with tools for SQLite database interaction.
This module is designed for extensibility and integration with AI-powered workflows.
"""

import os
import sqlite3
from typing import Any, Dict

from mcp.server.fastmcp import FastMCP


mcp = FastMCP(name="sqlite_tool")

# Caminho do banco de dados via variável de ambiente ou fallback para ./database.db
SQLITEDB_PATH = os.getenv("SQLITE_DB_PATH", "database.db")

# Palavras-chave que indicam operações de escrita — bloqueadas em modo somente leitura
_WRITE_KEYWORDS = {
    "insert",
    "update",
    "delete",
    "drop",
    "alter",
    "create",
    "replace",
    "truncate",
}


def _is_write_query(query: str) -> bool:
    """Verifica se a query contém operações de escrita."""
    first_token = query.strip().split()[0].lower() if query.strip() else ""
    return first_token in _WRITE_KEYWORDS


@mcp.tool()
def my_mcp_sqlite(query: str) -> Dict[str, Any]:
    """
    Execute a single read-only SQL query against a SQLite database.

    The database path is read from the SQLITE_DB_PATH environment variable,
    falling back to 'database.db' in the current directory.
    """
    if _is_write_query(query):
        return {
            "error": "Operação bloqueada: sessão é somente leitura. "
            "Apenas queries SELECT são permitidas."
        }

    try:
        # uri=True + ?mode=ro garante abertura somente leitura no nível do arquivo
        uri = f"file:{SQLITEDB_PATH}?mode=ro"
        conn = sqlite3.connect(uri, uri=True)
        conn.row_factory = sqlite3.Row  # retorna rows como dicionários

        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()

        # Converte sqlite3.Row para dicts serializáveis
        result = [dict(row) for row in rows]

        cur.close()
        conn.close()
        return {"result": result}

    except sqlite3.OperationalError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Erro inesperado: {e}"}


if __name__ == "__main__":
    mcp.run()
