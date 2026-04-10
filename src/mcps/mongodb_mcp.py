#! /usr/bin/env python3
"""
mongodb.py

Implements a FastMCP server with tools for MongoDB database interaction.
This module is designed for extensibility and integration with AI-powered workflows.
"""

import os
import json
from typing import Any, Dict
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from mcp.server.fastmcp import FastMCP


mcp = FastMCP(name="mongodb_tool")


@mcp.tool()
def my_mcp_mongodb(
    collection: str,
    operation: str = "find",
    query: Dict[str, Any] = {},
    projection: Dict[str, Any] = {},
    limit: int = 100,
) -> Dict[str, Any]:
    """
    Execute a read-only operation against a MongoDB database.

    Args:
        collection: Name of the MongoDB collection to query.
        operation:  Operation to perform. Supported: "find", "find_one",
                    "count_documents", "aggregate".
        query:      Filter document (for find/find_one/count_documents)
                    or pipeline list (for aggregate).
        projection: Fields to include/exclude (only for find/find_one).
        limit:      Maximum number of documents to return (only for find).
    """
    try:
        client = MongoClient(
            os.getenv("MONGODB_URL"),
            serverSelectionTimeoutMS=5000,
        )
        db_name = os.getenv("MONGODB_DATABASE")
        db = client[db_name]
        col = db[collection]

        match operation:
            case "find":
                cursor = col.find(query, projection).limit(limit)
                result = [_serialize(doc) for doc in cursor]

            case "find_one":
                doc = col.find_one(query, projection)
                result = _serialize(doc) if doc else None

            case "count_documents":
                result = col.count_documents(query)

            case "aggregate":
                # query is used as the pipeline list in this case
                pipeline = query if isinstance(query, list) else [query]
                cursor = col.aggregate(pipeline)
                result = [_serialize(doc) for doc in cursor]

            case _:
                return {
                    "error": f"Unsupported operation '{operation}'. "
                    "Use: find, find_one, count_documents, aggregate."
                }

        client.close()
        return {"result": result}

    except ConnectionFailure as e:
        return {"error": f"Connection failed: {e}"}
    except OperationFailure as e:
        return {"error": f"Operation failed (check permissions): {e}"}


def _serialize(doc: Any) -> Any:
    """Recursively converts MongoDB-specific types (e.g. ObjectId) to strings."""
    if isinstance(doc, dict):
        return {k: _serialize(v) for k, v in doc.items()}
    if isinstance(doc, list):
        return [_serialize(i) for i in doc]
    # ObjectId, Decimal128, datetime, etc.
    try:
        json.dumps(doc)
        return doc
    except (TypeError, ValueError):
        return str(doc)

def  main():
    mcp.run()

if __name__ == "__main__":
    main()
