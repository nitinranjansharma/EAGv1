## basic import 
import os
import ast
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
import asyncio
from google import genai
import time
from concurrent.futures import TimeoutError
from functools import partial
import json

# Load environment variables from .env file
load_dotenv()

# Access your API key and initialize Gemini client correctly
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

max_iterations = 7
last_response = None
iteration = 0
iteration_response = []

# Language preference
preferred_language = "English"  # Default language

output_format = """
1. For function calls Return in below JSON format ONLY:
   {
      "reasoning": "reasoning",
      "self_correction": "self_correction",
      "function": "function_name",
      "parameters": {
         "param1": "value1",
         "param2": "value2",
         "param3": "value3"
      }
   }
   The parameters must match the required input types for the function.
   if No input is required, use:
    {
        "reasoning": "reasoning",
         "self_correction": "self_correction",
        "function": "function_name",
        "parameters": ''
    }

     Example: For add(a: integer, b: integer), use:
   {
      "reasoning": "reasoning",
       "self_correction": "self_correction",
      "function": "add",
      "parameters": {
         "a": 5,
         "b": 3
      }
   }

2. For final answers, 
if there is a final output, return in below format:
    {
        "reasoning": "...",
        "self_correction": "...",
        "answer": "answer"
    }
    or 
    {
        "reasoning": "...",
        "self_correction": "...",
        "answer": "DONE"
    }



While using any application, make sure to open the application first before using application specific tools.
Complete the unrelated tasks first and then move on to the application specific tasks.
DO NOT PROVIDE INPUTS TO ANY TOOL UNLESS SPECIFIED IN THE QUERY IT SELF. KEEP THE INPUT BLANK
DO NOT include multiple responses. Give ONE response at a time.
Make sure to provide parameters in the correct order as specified in the function signature. 
DO NOT USE ANY OTHER TEXT"""

async def get_language_preference():
    """Ask the user for their language preference"""
    global preferred_language
    
    print("\n=== Language Preference ===")
    print("Please select your preferred language for responses:")
    print("1. English")
    print("2. German")
    print("3. French")
    
    while True:
        try:
            choice = input("Enter your choice (1-3): ")
            if choice == "1":
                preferred_language = "English"
                break
            elif choice == "2":
                preferred_language = "German"
                break
            elif choice == "3":
                preferred_language = "French"
                break
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")
        except Exception as e:
            print(f"Error: {e}")
            print("Please try again.")
    
    print(f"Language preference set to: {preferred_language}")
    return preferred_language

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
        # Get language preference before starting
        await get_language_preference()
        
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
                
                # Add language instruction to the system prompt
                language_instruction = f"""
**Language Preference:**
You MUST respond in {preferred_language} language. All your reasoning, self-correction, and final answers MUST be in {preferred_language}.
"""
                
                system_prompt = f"""You are a methodical and logical computer agent designed to solve problems through a sequence of reasoned steps. You have access to a set of tools to interact with the system or gather information.

*Your Goal:* Accurately fulfill the user's request by breaking it down into logical steps. At each step, you will first reason about the plan, then potentially use a tool, or provide the final answer.

{language_instruction}

Available tools:
{tools_description}

**Operational Cycle (Follow these steps in each turn):**

1.  **Reasoning Step:**
    *   Analyze the current situation and the user's request.
    *   Explain your thought process for the *next* action (e.g., "I need to add two numbers," "I need to check if the file exists," "The task is complete").
    *   If planning a tool call, state its specific purpose (e.g., "Using 'add' tool to calculate the sum").

2.  **Self-Correction/Verification Step:**
    *   Review your reasoning and the details of your planned action (especially tool parameters). Does it logically follow? Are the parameters correct?
    *   If you identify an issue, go back to the Reasoning Step to correct it.

3.  **Action Step (Choose ONE):**
    Based on your verified reasoning, select *one* of the following output format 
    {output_format}

   Example: For add(a: integer, b: integer), use:
   FUNCTION_CALL: {{"name": "add", "args": {{"a": 5, "b": 3}}}}
   if No input is required, use the format:
   FUNCTION_CALL: {{"name": "function_name", "args": {{"param_name": "value"}}}}
   The parameters must match the required input types for the function.
   FUNCTION_CALL: {{"name": "open_powerpoint"}}
   FUNCTION_CALL: {{"name": "create_new_presentation"}}
   FUNCTION_CALL: {{"name": "draw_rectangle"}}
   FUNCTION_CALL: {{"name": "write_text", "args": {{"text": "text"}}}}

    b. For final answers:
   FINAL_ANSWER: ['DONE']


**Mandatory Guidelines:**

*   **Structured Responses:** Strictly adhere to the OUTPUT FORMAT, OUTPUT MUST BE A JSON.
*   **Step-by-Step Execution:** Process the request iteratively. Wait for the outcome of a function call before proceeding with the next reasoning step.
*   **Tool Prerequisites:** Ensure any necessary applications are open before using application-specific tools (e.g., call `open_paint` before using paint tools). Address general tasks first.
*   **Error Handling:** If a tool call fails, returns an error, or provides unexpected results, report this in your next `REASONING:` step and explain your plan to handle it (e.g., retry, use a different tool, ask for clarification).
*   **Uncertainty:** If you are unsure how to proceed or lack necessary information, state this clearly in the `REASONING:` step and explain what is needed.
*   **Parameter Order:** Ensure parameters in `FUNCTION_CALL` are in the exact order specified by the tool description.
*   **Language:** Always respond in {preferred_language} language.


While using any application, make sure to open the application first before using application specific tools.
Complete the unrelated tasks first and then move on to the application specific tasks.
DO NOT PROVIDE INPUTS TO ANY TOOL UNLESS SPECIFIED IN THE QUERY IT SELF. KEEP THE INPUT BLANK
DO NOT include multiple responses. Give ONE response at a time.
Make sure to provide parameters in the correct order as specified in the function signature. 
DO NOT USE ANY OTHER TEXT


"""

                query = """ Create a new Microsoft presentation and figure out how do you greet people and write it in morse code? Format the answer as Question and Answer in the same rentangle box"""
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
                        start_index = response_text.find('{')
                        end_index = response_text.rfind('}') 
                        if start_index != -1 and end_index != -1:
                            clean_json_string = response_text[start_index : end_index + 1]
                            response_json = ast.literal_eval(clean_json_string)
                            print(response_json)
                        else:
                            print("Failed to get LLM response: {e}")
                            break
                    except Exception as e:
                        print(f"Error in LLM generation: {e}")
                        break

                    if response_json.get("function"):
                        func_name = response_json.get("function")
                        params = response_json.get("parameters")
                        print(f"Calling function {func_name} with params {params}")
                        try:
                            # Find the matching tool to get its input schema
                            tool = next((t for t in tools if t.name == func_name), None)
                            if not tool:
                                raise ValueError(f"Unknown tool: {func_name}")

                            # Prepare arguments according to the tool's input schema
                            arguments = {}
                            for (param_name, param_info), value in zip(tool.inputSchema['properties'].items(), params):
                                # Convert the value to the correct type based on the schema
                                if param_info['type'] == 'integer':
                                    arguments[param_name] = int(params[param_name])
                                elif param_info['type'] == 'number':
                                    arguments[param_name] = float(params[param_name])
                                elif param_info['type'] == 'array':
                                    # Handle array types if needed
                                    arguments[param_name] = params[param_name]
                                else:
                                    arguments[param_name] = params[param_name]
                            print(f"Executing MCP tool call with arguments: {arguments}")
                            result = await session.call_tool(func_name, arguments=arguments)
                            
                            # Get the full result content
                            if hasattr(result, 'content'):
                                if isinstance(result.content, list):
                                    iteration_result = []
                                    for i in result.content:
                                        if isinstance(i, str):
                                            iteration_result.append(i)
                                        else:
                                            iteration_result.append(i.text)
                                else:
                                    iteration_result = result.content
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

                    elif response_text.startswith("FINAL_ANSWER:") or response_json.get("answer") == "DONE":
                        print("\n=== Agent Execution Complete ===")
                        break

                    iteration += 1

    except Exception as e:
        print(f"Error in main execution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())