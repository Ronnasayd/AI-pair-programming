import asyncio
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession

command={
    "command":"my_run_command",
    "arguments":{"command": "ls -la", "cwd": None}
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
