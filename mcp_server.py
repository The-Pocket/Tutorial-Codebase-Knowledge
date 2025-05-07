import json
import os
import datetime

# Crude startup log
with open("D:/MCP/pocketflowtutorial/mcp_startup_log.txt", "a") as f:
    f.write(f"MCP server script started at {datetime.datetime.now()}\\n")
import sys
from typing import Dict, Any, List, Optional

# Import PocketFlow functionality
from flow import create_tutorial_flow

class MCPServer:
    def __init__(self):
        self.tools = {
            "generate_tutorial": {
                "description": "Generate a tutorial for a GitHub repository or local directory",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repo": {
                            "type": "string",
                            "description": "URL of the public GitHub repository"
                        },
                        "dir": {
                            "type": "string",
                            "description": "Path to local directory"
                        },
                        "name": {
                            "type": "string", 
                            "description": "Project name (optional, derived from repo/directory if omitted)"
                        },
                        "token": {
                            "type": "string",
                            "description": "GitHub personal access token"
                        },
                        "output": {
                            "type": "string",
                            "description": "Base directory for output (default: ./output)"
                        },
                        "include": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Include file patterns (e.g. ['*.py', '*.js'])"
                        },
                        "exclude": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Exclude file patterns (e.g. ['tests/*', 'docs/*'])"
                        },
                        "max_size": {
                            "type": "integer",
                            "description": "Maximum file size in bytes (default: 100000, about 100KB)"
                        },
                        "language": {
                            "type": "string",
                            "description": "Language for the generated tutorial (default: english)"
                        },
                        "no_cache": {
                            "type": "boolean",
                            "description": "Disable LLM response caching (default: False)"
                        },
                        "max_abstractions": {
                            "type": "integer",
                            "description": "Maximum number of abstractions to identify (default: 10)"
                        }
                    },
                    "required": []
                }
            }
        }
        self.resources = {}

    def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        message_type = message.get("type")
        
        if message_type == "ping":
            return self.handle_ping(message)
        elif message_type == "list_tools":
            return self.handle_list_tools(message)
        elif message_type == "list_resources":
            return self.handle_list_resources(message)
        elif message_type == "tool_call":
            return self.handle_tool_call(message)
        elif message_type == "resource_get":
            return self.handle_resource_get(message)
        else:
            return {
                "type": "error",
                "error": f"Unknown message type: {message_type}",
                "id": message.get("id")
            }

    def handle_ping(self, message: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "type": "pong",
            "id": message.get("id")
        }

    def handle_list_tools(self, message: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "type": "tools",
            "tools": self.tools,
            "id": message.get("id")
        }

    def handle_list_resources(self, message: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "type": "resources",
            "resources": self.resources,
            "id": message.get("id")
        }

    def handle_tool_call(self, message: Dict[str, Any]) -> Dict[str, Any]:
        tool_name = message.get("name")
        tool_parameters = message.get("parameters", {})
        message_id = message.get("id")
        
        if tool_name not in self.tools:
            return {
                "type": "error",
                "error": f"Unknown tool: {tool_name}",
                "id": message_id
            }
        
        try:
            if tool_name == "generate_tutorial":
                result = self.execute_generate_tutorial(tool_parameters)
                return {
                    "type": "tool_result",
                    "id": message_id,
                    "result": result
                }
            else:
                return {
                    "type": "error",
                    "error": f"Tool {tool_name} is not implemented",
                    "id": message_id
                }
        except Exception as e:
            return {
                "type": "error",
                "error": f"Error executing tool {tool_name}: {str(e)}",
                "id": message_id
            }

    def handle_resource_get(self, message: Dict[str, Any]) -> Dict[str, Any]:
        resource_uri = message.get("uri")
        message_id = message.get("id")
        
        if resource_uri not in self.resources:
            return {
                "type": "error",
                "error": f"Unknown resource: {resource_uri}",
                "id": message_id
            }
        
        try:
            return {
                "type": "resource",
                "id": message_id,
                "resource": self.resources[resource_uri]
            }
        except Exception as e:
            return {
                "type": "error",
                "error": f"Error retrieving resource {resource_uri}: {str(e)}",
                "id": message_id
            }

    def execute_generate_tutorial(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        # Default file patterns
        DEFAULT_INCLUDE_PATTERNS = {
            "*.py", "*.js", "*.jsx", "*.ts", "*.tsx", "*.go", "*.java", "*.pyi", "*.pyx",
            "*.c", "*.cc", "*.cpp", "*.h", "*.md", "*.rst", "Dockerfile",
            "Makefile", "*.yaml", "*.yml",
        }

        DEFAULT_EXCLUDE_PATTERNS = {
            "assets/*", "data/*", "examples/*", "images/*", "public/*", "static/*", "temp/*",
            "docs/*", 
            "venv/*", ".venv/*", "*test*", "tests/*", "docs/*", "examples/*", "v1/*",
            "dist/*", "build/*", "experimental/*", "deprecated/*", "misc/*", 
            "legacy/*", ".git/*", ".github/*", ".next/*", ".vscode/*", "obj/*", "bin/*", "node_modules/*", "*.log"
        }

        # Extract parameters
        repo_url = parameters.get("repo")
        local_dir = parameters.get("dir")
        project_name = parameters.get("name")
        github_token = parameters.get("token", os.environ.get('GITHUB_TOKEN'))
        output_dir = parameters.get("output", "output")
        include_patterns = set(parameters.get("include", [])) or DEFAULT_INCLUDE_PATTERNS
        exclude_patterns = set(parameters.get("exclude", [])) or DEFAULT_EXCLUDE_PATTERNS
        max_file_size = parameters.get("max_size", 100000)
        language = parameters.get("language", "english")
        use_cache = not parameters.get("no_cache", False)
        max_abstraction_num = parameters.get("max_abstractions", 10)

        # Check that one of repo_url or local_dir is provided
        if not repo_url and not local_dir:
            return {
                "error": "Either repo or dir parameter must be provided"
            }

        # Initialize the shared dictionary with inputs
        shared = {
            "repo_url": repo_url,
            "local_dir": local_dir,
            "project_name": project_name,
            "github_token": github_token,
            "output_dir": output_dir,
            "include_patterns": include_patterns,
            "exclude_patterns": exclude_patterns,
            "max_file_size": max_file_size,
            "language": language,
            "use_cache": use_cache,
            "max_abstraction_num": max_abstraction_num,
            "files": [],
            "abstractions": [],
            "relationships": {},
            "chapter_order": [],
            "chapters": [],
            "final_output_dir": None
        }

        # Create the flow instance
        tutorial_flow = create_tutorial_flow()

        # Run the flow
        tutorial_flow.run(shared)

        # Return the results
        return {
            "success": True,
            "project_name": shared.get("project_name"),
            "output_dir": shared.get("final_output_dir"),
            "abstractions": shared.get("abstractions"),
            "chapters": len(shared.get("chapters", [])),
            "files_processed": len(shared.get("files", [])),
            "message": f"Tutorial generated successfully at {shared.get('final_output_dir')}"
        }

    def start(self):
        """Start the MCP server - read from stdin and write to stdout."""
        for line in sys.stdin:
            try:
                message = json.loads(line)
                response = self.handle_message(message)
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
            except json.JSONDecodeError:
                error_response = {
                    "type": "error",
                    "error": "Invalid JSON message"
                }
                sys.stdout.write(json.dumps(error_response) + "\n")
                sys.stdout.flush()
            except Exception as e:
                error_response = {
                    "type": "error",
                    "error": f"Unexpected error: {str(e)}"
                }
                sys.stdout.write(json.dumps(error_response) + "\n")
                sys.stdout.flush()

if __name__ == "__main__":
    server = MCPServer()
    server.start()
