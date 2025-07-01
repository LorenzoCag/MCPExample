import streamlit as st
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

st.title("MCP Agent Interface")

# Helper to run async code in Streamlit
def run_async(coro):
    return asyncio.run(coro)

# List available tools
def get_tools():
    async def list_tools():
        server_params = StdioServerParameters(command="python3.11", args=["server.py"])
        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                tools_result = await session.list_tools()
                return tools_result.tools
    return run_async(list_tools())

tools = get_tools()
tool_names = [tool.name for tool in tools]
tool_map = {tool.name: tool for tool in tools}

selected_tool = st.selectbox("Select a tool", tool_names)
tool_desc = tool_map[selected_tool].description
st.write(f"**Description:** {tool_desc}")

# Get tool argument schema from inputSchema
input_schema = tool_map[selected_tool].inputSchema
properties = input_schema.get("properties", {})

args = {}
for param_name, param_info in properties.items():
    param_type = param_info.get("type", "string")
    args[param_name] = st.text_input(f"{param_name} ({param_type})")

if st.button("Call Tool"):
    async def call_tool():
        server_params = StdioServerParameters(command="python3.11", args=["server.py"])
        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                result = await session.call_tool(selected_tool, arguments=args)
                return result.content[0].text
    output = run_async(call_tool())
    st.success(f"Result: {output}")

# Debug: Show all attributes of the selected tool
st.write("Tool attributes:", vars(tool_map[selected_tool])) 