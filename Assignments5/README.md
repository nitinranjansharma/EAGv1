# PowerPoint MCP Project

This project implements an agent-based system that uses the Gemini LLM to interact with PowerPoint through MCP (Model Control Protocol). The agent can perform tasks like opening PowerPoint, creating presentations, drawing shapes, and adding text.

## System Architecture

The system consists of:
1. A client that communicates with the Gemini LLM
2. An MCP server that provides tools for PowerPoint manipulation
3. A prompt engineering system that guides the LLM to use the tools correctly

## System Prompt

The system prompt is designed to guide the LLM in using the available tools correctly. Here's the current system prompt:

```
You are a methodical and logical computer agent designed to solve problems through a sequence of reasoned steps. You have access to a set of tools to interact with the system or gather information.

*Your Goal:* Accurately fulfill the user's request by breaking it down into logical steps. At each step, you will first reason about the plan, then potentially use a tool, or provide the final answer.

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


While using any application, make sure to open the application first before using application specific tools.
Complete the unrelated tasks first and then move on to the application specific tasks.
DO NOT PROVIDE INPUTS TO ANY TOOL UNLESS SPECIFIED IN THE QUERY IT SELF. KEEP THE INPUT BLANK
DO NOT include multiple responses. Give ONE response at a time.
Make sure to provide parameters in the correct order as specified in the function signature. 
DO NOT USE ANY OTHER TEXT
```

## Output Format

The output format is defined as follows:

```
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
```

## Thought Process

The thought process for this project involved several key considerations:

1. **Prompt Engineering**: 
   - The system prompt needed to be carefully crafted to guide the LLM in using the tools correctly.
   - We needed to ensure the LLM understood the format for function calls and final answers.
   - The prompt needed to include examples of function calls to help the LLM understand how to format them.

2. **JSON Parsing**:
   - The LLM generates responses in JSON format, which needed to be parsed correctly.
   - We needed to handle different types of responses (function calls and final answers).
   - We needed to extract the function name and arguments from the JSON.

3. **Error Handling**:
   - We needed to handle errors in JSON parsing, function calls, and LLM responses.
   - We needed to provide meaningful error messages to help with debugging.

4. **Iterative Execution**:
   - The system executes tasks iteratively, with each iteration building on the results of the previous one.
   - We needed to track the state of the execution and provide context to the LLM for each iteration.

## Example Query and Response

Here's an example query and the expected response:

**Query**:
```
Create a new Microsoft presentation and figure out what is the capital of India and write it in morse code? Format the answer as Question and Answer in the same rentangle box
```

**Expected Response Flow**:
1. Open PowerPoint
2. Create a new presentation
3. Draw a rectangle
4. Write the text "Question: What is the capital of India? Answer: New Delhi (in morse code: -. . .-- / -.. . .-.. .... ..)" in the rectangle

## Implementation Details

The implementation consists of:

1. **Client-Server Communication**:
   - The client communicates with the Gemini LLM to get responses.
   - The client communicates with the MCP server to execute tools.

2. **Tool Execution**:
   - The client parses the LLM response to extract the function name and arguments.
   - The client calls the appropriate tool with the extracted arguments.
   - The client processes the tool response and provides it to the LLM for the next iteration.

3. **Iteration Management**:
   - The client tracks the iteration count and provides context to the LLM for each iteration.
   - The client continues iterating until the LLM provides a final answer or the maximum number of iterations is reached.

## Future Improvements

1. **Enhanced Error Handling**:
   - Improve error handling for JSON parsing and function calls.
   - Provide more detailed error messages to help with debugging.

2. **Improved Prompt Engineering**:
   - Refine the system prompt to better guide the LLM in using the tools correctly.
   - Add more examples of function calls to help the LLM understand how to format them.

3. **Extended Tool Set**:
   - Add more tools for PowerPoint manipulation.
   - Add tools for other applications like Word, Excel, etc.

4. **User Interface**:
   - Develop a user interface for interacting with the system.
   - Provide visual feedback on the execution of tasks. 
