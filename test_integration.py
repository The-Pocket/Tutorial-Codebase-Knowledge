"""
This is a simple test script to verify PocketFlow MCP server integration with Cline.
Run this in Cline to check if the integration is working properly.
"""
import os

def print_test_instructions():
    print("PocketFlow Tutorial MCP Server Test")
    print("===================================")
    print("To test if the PocketFlow MCP server is working with Cline, execute this command in a new Cline session:")
    print()
    print("```python")
    print("# Import Cline MCP module (if it exists)")
    print("try:")
    print("    import cline_mcp")
    print("    print('Cline MCP module is available')")
    print("except ImportError:")
    print("    print('Cline MCP module not found')")
    print()
    print("# List all available MCP servers")
    print("try:")
    print("    servers = cline_mcp.list_servers()")
    print("    print(f'Available MCP servers: {servers}')")
    print("    if 'pocketflow-tutorial' in servers:")
    print("        print('✅ PocketFlow Tutorial MCP server is available')")
    print("    else:")
    print("        print('❌ PocketFlow Tutorial MCP server is not available')")
    print("except Exception as e:")
    print("    print(f'Error listing MCP servers: {e}')")
    print("```")
    print()
    print("If the PocketFlow Tutorial MCP server is available, you can then use it with the following commands:")
    print()
    print("```python")
    print("# List available tools in the PocketFlow Tutorial MCP server")
    print("tools = cline_mcp.list_tools('pocketflow-tutorial')")
    print("print(f'Available tools: {tools}')")
    print("```")

if __name__ == "__main__":
    print_test_instructions()
