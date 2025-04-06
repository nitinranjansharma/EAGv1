## basic import 
import os
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
import asyncio
from google import genai
import time
from concurrent.futures import TimeoutError
from functools import partial

# Load environment variables from .env file
load_dotenv()

# Access your API key and initialize Gemini client correctly
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

max_iterations = 5
last_response = None
iteration = 0
iteration_response = []

async def generate_with_timeout(client, prompt, timeout=10):
    """Generate content with a timeout"""
    print("Starting LLM generation...")
    try:
        # Convert the synchronous generate_content call to run in a thread
        loop = asyncio.get_event_loop()
        response = await asyncio.wait_for(
            loop.run_in_executor(
                None, 
                lambda: client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt
                )
            ),
            timeout=timeout
        )
        print("LLM generation completed")
        return response
    except TimeoutError:
        print("LLM generation timed out!")
        raise
    except Exception as e:
        print(f"Error in LLM generation: {e}")
        raise

async def main():
    print("Starting main execution...")
    try:
        # Create a single MCP server connection
        print("Establishing connection to MCP server...")
        server_params = StdioServerParameters(
            command="python",
            args=["server.py"]
        )

        async with stdio_client(server_params) as (read, write):
            print("Connection established, creating session...")
            async with ClientSession(read, write) as session:
                print("Session created, initializing...")
                await session.initialize()
                # Get available tools
                print("Requesting tool list...")
                tools_result = await session.list_tools()
                tools = tools_result.tools
                print(f"Successfully retrieved {len(tools)} tools")

                # Create system prompt with available tools
                print("Creating system prompt...")
                print(f"Number of tools: {len(tools)}")
                
                try:
                    # First, let's inspect what a tool object looks like
                    if tools:
                        print(f"First tool properties: {dir(tools[0])}")
                        print(f"First tool example: {tools[0]}")
                    
                    tools_description = []
                    for i, tool in enumerate(tools):
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
                            print(f"Added description for tool: {tool_desc}")
                        except Exception as e:
                            print(f"Error processing tool {i}: {e}")
                            tools_description.append(f"{i+1}. Error processing tool")
                    
                    tools_description = "\n".join(tools_description)
                    print("Successfully created tools description")
                except Exception as e:
                    print(f"Error creating tools description: {e}")
                    tools_description = "Error loading tools"
                
                print("Created system prompt...")
                
                system_prompt = f"""You are a computer wizard agent solving problems in iterations. You have access to various tools.

Available tools:
{tools_description}

Respond with EXACTLY ONE of these formats:
1. For function calls:
   FUNCTION_CALL: function_name|param1|param2|...
   The parameters must match the required input types for the function.
   
   Example: For add(a: integer, b: integer), use:
   FUNCTION_CALL: add|5|3
   if No input is required, use:
   FUNCTION_CALL: open_powerpoint|
   FUNCTION_CALL: create_new_presentation|
   FUNCTION_CALL: draw_rectangle|
   FUNCTION_CALL: write_text|text

2. For final answers:
   FINAL_ANSWER: ['DONE']

While using any application, make sure to open the application first before using application specific tools.
Complete the unrelated tasks first and then move on to the application specific tasks.
DO NOT PROVIDE INPUTS TO ANY TOOL UNLESS SPECIFIED IN THE QUERY ITSELF. KEEP THE INPUT BLANK
DO NOT include multiple responses. Give ONE response at a time.
Make sure to provide parameters in the correct order as specified in the function signature."""

                query = """Open PowerPoint, create a new blank presentation, draw rectangle using the function call draw_rectangleand call the write text function add the text which is the capital of India in the rectangle using the functions write_text. 
                Format it like Question: What is the capital of India? Answer: New Delhi"""
                print("Starting iteration loop...")
                
                # Use global iteration variables
                global iteration, last_response
                
                while iteration < max_iterations:
                    time.sleep(2)
                    print(f"\n--- Iteration {iteration + 1} ---")
                    if last_response is None:
                        current_query = query
                    else:
                        current_query = current_query + "\n\n" + " ".join(iteration_response)
                        current_query = current_query + "  What should I do next?"

                    # Get model's response with timeout
                    print("Preparing to generate LLM response...")
                    prompt = f"{system_prompt}\n\nQuery: {current_query}"
                    try:
                        response = await generate_with_timeout(client, prompt)
                        response_text = response.text.strip()
                        print(f"LLM Response: {response_text}")
                    except Exception as e:
                        print(f"Failed to get LLM response: {e}")
                        break
                    
                    if response_text.strip().startswith("FUNCTION_CALL:"):
                        _, function_info = response_text.split(":", 1)
                        parts = [p.strip() for p in function_info.split("|")]
                        func_name, params = parts[0], parts[1:]
                        
                        print(f"Calling function {func_name} with params {params}")
                        try:
                            # Find the matching tool to get its input schema
                            tool = next((t for t in tools if t.name == func_name), None)
                            if not tool:
                                raise ValueError(f"Unknown tool: {func_name}")

                            # Prepare arguments according to the tool's input schema
                            arguments = {}
                            if 'properties' in tool.inputSchema and params:
                                for i, (param_name, param_info) in enumerate(tool.inputSchema['properties'].items()):
                                    if i < len(params):
                                        # Convert the value to the correct type based on the schema
                                        if param_info['type'] == 'integer':
                                            arguments[param_name] = int(params[i])
                                        elif param_info['type'] == 'number':
                                            arguments[param_name] = float(params[i])
                                        elif param_info['type'] == 'array':
                                            # Handle array types if needed
                                            arguments[param_name] = eval(params[i])
                                        else:
                                            arguments[param_name] = params[i]

                            print(f"Executing MCP tool call with arguments: {arguments}")
                            result = await session.call_tool(func_name, arguments=arguments)
                            
                            # Get the full result content
                            if hasattr(result, 'content'):
                                if isinstance(result.content[0], str):
                                    iteration_result = result.content[0]
                                else:
                                    iteration_result = result.content[0].text
                            else:
                                iteration_result = str(result)
                                
                            print(f"Full result received: {iteration_result}")
                            
                            iteration_response.append(
                                f"In the {iteration + 1} iteration you called {func_name} with {arguments} parameters, "
                                f"and the function returned {iteration_result}."
                            )
                            last_response = iteration_result

                        except Exception as e:
                            print(f"Error calling tool: {e}")
                            iteration_response.append(f"Error in iteration {iteration + 1}: {str(e)}")
                            break

                    elif response_text.startswith("FINAL_ANSWER:"):
                        print("\n=== Agent Execution Complete ===")
                        break

                    iteration += 1

    except Exception as e:
        print(f"Error in main execution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())