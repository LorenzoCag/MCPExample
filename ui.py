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

# Smart routing function
def route_to_tool(user_input: str):
    """Route natural language input to the appropriate tool"""
    user_input = user_input.lower()
    
    # Define routing rules
    routing_rules = {
        'web_search': ['search', 'find', 'look up', 'google', 'web search', 'search for'],
        'reddit_scrape': ['reddit', 'subreddit', 'reddit posts', 'reddit scrape'],
        'say_hello': ['hello', 'hi', 'greet', 'say hello']
    }
    
    # Find the best matching tool
    for tool_name, keywords in routing_rules.items():
        if tool_name in tool_names:  # Make sure tool exists
            for keyword in keywords:
                if keyword in user_input:
                    return tool_name, user_input
    
    return None, user_input

# Smart input section
st.header("🤖 Smart Agent")
user_command = st.text_input("Tell me what you want to do:", placeholder="e.g., 'Search for Python tutorials' or 'Show me Reddit posts from r/programming'")

if user_command:
    selected_tool, remaining_input = route_to_tool(user_command)
    
    if selected_tool:
        st.success(f"🎯 I'll use the '{selected_tool}' tool for you!")
        
        # Get tool argument schema
        input_schema = tool_map[selected_tool].inputSchema
        properties = input_schema.get("properties", {})
        
        # Auto-fill arguments based on remaining input
        args = {}
        for param_name, param_info in properties.items():
            if param_name == 'query' and 'search' in user_command.lower():
                # Extract search query from user input
                search_terms = user_command.lower().replace('search', '').replace('for', '').replace('find', '').strip()
                args[param_name] = st.text_input(f"{param_name} ({param_info.get('type', 'string')})", value=search_terms)
            elif param_name == 'subreddit' and 'reddit' in user_command.lower():
                # Extract subreddit name
                if 'r/' in user_command:
                    subreddit = user_command.split('r/')[-1].split()[0]
                else:
                    subreddit = remaining_input.split()[-1] if remaining_input else ''
                args[param_name] = st.text_input(f"{param_name} ({param_info.get('type', 'string')})", value=subreddit)
            elif param_name == 'name' and 'hello' in user_command.lower():
                # Extract name for greeting
                name = remaining_input.split()[-1] if remaining_input else 'there'
                args[param_name] = st.text_input(f"{param_name} ({param_info.get('type', 'string')})", value=name)
            else:
                args[param_name] = st.text_input(f"{param_name} ({param_info.get('type', 'string')})")
        
        if st.button("🚀 Execute"):
            async def call_tool():
                server_params = StdioServerParameters(command="python3.11", args=["server.py"])
                async with stdio_client(server_params) as (read_stream, write_stream):
                    async with ClientSession(read_stream, write_stream) as session:
                        await session.initialize()
                        result = await session.call_tool(selected_tool, arguments=args)
                        return result.content[0].text
            output = run_async(call_tool())
            st.success(f"Result: {output}")
    else:
        st.warning("🤔 I'm not sure which tool to use for that request. Try being more specific!")

# Manual tool selection (existing functionality)
st.header("🔧 Manual Tool Selection")
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