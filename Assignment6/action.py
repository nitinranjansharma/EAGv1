from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Union, Callable, Awaitable
from decision_making import Decision
from memory import MemoryLayer
import asyncio
import json
import subprocess
import os
from mcp import ClientSession, types
from mcp.client.stdio import stdio_client
from mcp import StdioServerParameters

class ActionResult(BaseModel):
    """Represents the result of an action"""
    success: bool = Field(..., description="Whether the action was successful")
    result: Any = Field(..., description="The result of the action")
    error: Optional[str] = Field(None, description="Error message if the action failed")
    execution_time: float = Field(..., description="Time taken to execute the action in seconds")

class ActionLayer:
    """Handles executing actions based on decisions"""
    
    def __init__(self, memory_layer: MemoryLayer):
        self.memory_layer = memory_layer
        self.session = None
        self.tools = []
    
    async def initialize(self, server_command: str = "python", server_args: List[str] = ["new_server.py"]) -> None:
        """Initialize the action layer with a connection to the MCP server"""
        try:
            # Create a connection to the MCP server
            server_params = StdioServerParameters(
                command=server_command,
                args=server_args
            )
            
            # Create and store the client and session
            client = stdio_client(server_params)
            self.client = client
            self.read, self.write = await client.__aenter__()
            self.session = ClientSession(self.read, self.write)
            await self.session.__aenter__()
            await self.session.initialize()
            
            # Get available tools
            tools_result = await self.session.list_tools()
            self.tools = tools_result.tools
            
            # Store the tools in memory
            self.memory_layer.add_memory(
                content={"tools": [{"name": t.name, "description": t.description} for t in self.tools]},
                importance=8,
                category="tools"
            )
            
            print("Action layer initialized successfully with tools:", [t.name for t in self.tools])
            
        except Exception as e:
            print(f"Error initializing action layer: {e}")
            if hasattr(self, 'session') and self.session:
                await self.session.__aexit__(None, None, None)
            if hasattr(self, 'client') and self.client:
                await self.client.__aexit__(None, None, None)
            self.session = None
            self.tools = []
            raise
    
    async def execute_decision(self, decision: Decision) -> ActionResult:
        """Execute a decision and return the result"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            if decision.action == "function_call":
                # Execute a function call
                function_name = decision.parameters.get("function")
                args = decision.parameters.get("args", {})
                
                # Find the matching tool
                tool = next((t for t in self.tools if t.name == function_name), None)
                if not tool:
                    raise ValueError(f"Unknown tool: {function_name}")
                
                # Prepare arguments according to the tool's input schema
                arguments = {}
                for param_name, param_info in tool.inputSchema['properties'].items():
                    if param_name in args:
                        # Convert the value to the correct type based on the schema
                        if param_info['type'] == 'integer':
                            arguments[param_name] = int(args[param_name])
                        elif param_info['type'] == 'number':
                            arguments[param_name] = float(args[param_name])
                        elif param_info['type'] == 'array':
                            arguments[param_name] = args[param_name]
                        else:
                            arguments[param_name] = args[param_name]
                
                # Call the tool
                result = await self.session.call_tool(function_name, arguments=arguments)
                
                # Process the result
                if hasattr(result, 'content'):
                    if isinstance(result.content, list):
                        processed_result = []
                        for i in result.content:
                            if isinstance(i, str):
                                processed_result.append(i)
                            else:
                                processed_result.append(i.text)
                    else:
                        processed_result = result.content
                else:
                    processed_result = str(result)
                
                # Store the result in memory
                self.memory_layer.add_memory(
                    content={
                        "function": function_name,
                        "arguments": arguments,
                        "result": processed_result
                    },
                    importance=6,
                    category="function_call"
                )
                
                execution_time = asyncio.get_event_loop().time() - start_time
                return ActionResult(
                    success=True,
                    result=processed_result,
                    execution_time=execution_time
                )
                
            elif decision.action == "final_answer":
                # Return the final answer
                answer = decision.parameters.get("answer")
                
                # Store the answer in memory
                self.memory_layer.add_memory(
                    content={"answer": answer},
                    importance=9,
                    category="final_answer"
                )
                
                execution_time = asyncio.get_event_loop().time() - start_time
                return ActionResult(
                    success=True,
                    result=answer,
                    execution_time=execution_time
                )
                
            else:
                # Error or invalid action
                error_msg = decision.parameters.get("error", "Invalid action")
                
                execution_time = asyncio.get_event_loop().time() - start_time
                return ActionResult(
                    success=False,
                    result=None,
                    error=error_msg,
                    execution_time=execution_time
                )
                
        except Exception as e:
            # Handle any exceptions
            error_msg = str(e)
            
            # Store the error in memory
            self.memory_layer.add_memory(
                content={"error": error_msg, "decision": decision.dict()},
                importance=5,
                category="error"
            )
            
            execution_time = asyncio.get_event_loop().time() - start_time
            return ActionResult(
                success=False,
                result=None,
                error=error_msg,
                execution_time=execution_time
            )
    
    def get_tool_description(self) -> str:
        """Get a description of all available tools"""
        if not self.tools:
            return "No tools available"
        
        tools_description = []
        for i, tool in enumerate(self.tools):
            try:
                # Get tool properties
                params = tool.inputSchema
                desc = getattr(tool, 'description', 'No description available')
                name = getattr(tool, 'name', f'tool_{i}')
                
                # Format the input schema in a more readable way
                if 'properties' in params:
                    param_details = []
                    for param_name, param_info in params['properties'].items():
                        param_type = param_info.get('type', 'unknown')
                        param_details.append(f"{param_name}: {param_type}")
                    params_str = ', '.join(param_details)
                else:
                    params_str = 'no parameters'
                
                tool_desc = f"{i+1}. {name}({params_str}) - {desc}"
                tools_description.append(tool_desc)
            except Exception as e:
                print(f"Error processing tool {i}: {e}")
                tools_description.append(f"{i+1}. Error processing tool")
        
        return "\n".join(tools_description)
    
    async def cleanup(self) -> None:
        """Cleanup resources and close connections"""
        try:
            if self.session:
                await self.session.__aexit__(None, None, None)
            if hasattr(self, 'client') and self.client:
                await self.client.__aexit__(None, None, None)
        except Exception as e:
            print(f"Error during cleanup: {e}")
        finally:
            self.session = None
            self.tools = [] 