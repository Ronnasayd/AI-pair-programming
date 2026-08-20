import asyncio

from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

command = {
    "command": "my_run_command",
    "arguments": {
        "command": "cd notebook_crawler/spiders && ls",
        "cwd": "/home/ronnas/develop/poc/notebook-search-crawler",
    },
}


async def main():
    server_params = StdioServerParameters(command="my_mcp_server", args=[])
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()  # handshake obrigatório!
            result = await session.call_tool(
                command["command"], arguments=command["arguments"]
            )
            print("Response from server:", result)


if __name__ == "__main__":
    asyncio.run(main())
