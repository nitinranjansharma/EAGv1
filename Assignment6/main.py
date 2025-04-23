import asyncio
import os
import json
from dotenv import load_dotenv
from perception import PerceptionLayer
from memory import MemoryLayer
from decision_making import DecisionMakingLayer
from action import ActionLayer

# Load environment variables from .env file
load_dotenv()

# Default system prompt
DEFAULT_SYSTEM_PROMPT = """You are a methodical and logical computer agent designed to solve problems through a sequence of reasoned steps. You have access to a set of tools to interact with the system or gather information.

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
"""

# Default output format
DEFAULT_OUTPUT_FORMAT = """
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
"""

class CognitiveSystem:
    """Main class that orchestrates all cognitive layers"""
    
    def __init__(self, system_prompt: str = DEFAULT_SYSTEM_PROMPT, output_format: str = DEFAULT_OUTPUT_FORMAT):
        # Initialize memory layer
        self.memory_layer = MemoryLayer()
        
        # Initialize perception layer
        self.perception_layer = PerceptionLayer(system_prompt)
        
        # Initialize decision-making layer
        self.decision_making_layer = DecisionMakingLayer(self.memory_layer)
        
        # Initialize action layer
        self.action_layer = ActionLayer(self.memory_layer)
        
        # Store output format
        self.output_format = output_format
        
        # Store iteration state
        self.iteration = 0
        self.max_iterations = 7
        self.last_response = None
        self.iteration_responses = []
    
    async def initialize(self) -> None:
        """Initialize the cognitive system"""
        # Initialize the action layer
        await self.action_layer.initialize()
        
        # Get tool descriptions
        tools_description = self.action_layer.get_tool_description()
        
        # Update the system prompt with tool descriptions
        self.perception_layer.system_prompt = self.perception_layer.system_prompt.format(
            tools_description=tools_description,
            output_format=self.output_format
        )
        
        # Store initialization in memory
        self.memory_layer.add_memory(
            content={"initialization": "Cognitive system initialized"},
            importance=10,
            category="system"
        )
    
    async def process_query(self, query: str) -> str:
        """Process a user query through all cognitive layers"""
        print(f"Processing query: {query}")
        
        # Reset iteration state for new query
        self.iteration = 0
        self.last_response = None
        self.iteration_responses = []
        
        while self.iteration < self.max_iterations:
            print(f"\n--- Iteration {self.iteration + 1} ---")
            
            # Build the current query with context from previous iterations
            current_query = query
            if self.iteration_responses:
                current_query = query + "\n\n" + " ".join(self.iteration_responses)
                current_query = current_query + "  What should I do next?"
            
            # Get tool descriptions for the perception layer
            tools_description = self.action_layer.get_tool_description()
            
            # Perception: Process the query with the LLM
            llm_response = await self.perception_layer.process_query(current_query, tools_description)
            
            # Decision-Making: Analyze the LLM response and make a decision
            decision = self.decision_making_layer.analyze_llm_response(llm_response)
            
            # Consider alternatives based on memory
            decision = self.decision_making_layer.consider_alternatives(decision)
            
            # Action: Execute the decision
            action_result = await self.action_layer.execute_decision(decision)
            
            # Evaluate the decision outcome
            self.decision_making_layer.evaluate_decision(decision, action_result.result)
            
            # Store the iteration response
            if decision.action == "function_call":
                function_name = decision.parameters.get("function")
                args = decision.parameters.get("args", {})
                self.iteration_responses.append(
                    f"In iteration {self.iteration + 1} called {function_name} with {args} parameters, "
                    f"and got result: {action_result.result}."
                )
            elif decision.action == "final_answer":
                self.iteration_responses.append(
                    f"Final answer in iteration {self.iteration + 1}: {action_result.result}"
                )
                return action_result.result
            
            # Update the last response and increment iteration
            self.last_response = action_result.result
            self.iteration += 1
        
        return "Maximum number of iterations reached. Please try a different approach."
    
    def reset(self) -> None:
        """Reset the cognitive system state"""
        self.iteration = 0
        self.last_response = None
        self.iteration_responses = []
        
        # Store reset in memory
        self.memory_layer.add_memory(
            content={"reset": "Cognitive system reset"},
            importance=5,
            category="system"
        )

async def main():
    """Main function to run the cognitive system"""
    cognitive_system = None
    try:
        # Create the cognitive system
        cognitive_system = CognitiveSystem()
        
        # Initialize the system
        await cognitive_system.initialize()
        
        # Example query
        query = """ Create a new Microsoft presentation and figure out what is the capital of India and write it in morse code? Format the answer as Question and Answer in the same rectangle box"""
        
        # Process the query
        result = await cognitive_system.process_query(query)
        print("Final result:", result)
        
    except Exception as e:
        print(f"Error in main execution: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if cognitive_system and cognitive_system.action_layer:
            await cognitive_system.action_layer.cleanup()

if __name__ == "__main__":
    asyncio.run(main()) 