import os
import json
import asyncio
from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List, Union

# Load environment variables from .env file
load_dotenv()

# Access your API key and initialize Gemini client correctly
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

class LLMResponse(BaseModel):
    """Standardized response from LLM"""
    reasoning: str = Field(..., description="The reasoning behind the decision")
    self_correction: str = Field(..., description="Self-correction or verification of the reasoning")
    function: Optional[str] = Field(None, description="The function to call, if any")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Parameters for the function call")
    answer: Optional[str] = Field(None, description="Final answer if no function call is needed")

class PerceptionLayer:
    """Handles LLM interactions and perception of the environment"""
    
    def __init__(self, system_prompt: str):
        self.system_prompt = system_prompt
        self.client = client
    
    async def generate_with_timeout(self, prompt: str, timeout: int = 10) -> genai.types.GenerateContentResponse:
        """Generate content with a timeout"""
        print("Starting LLM generation...")
        try:
            # Convert the synchronous generate_content call to run in a thread
            loop = asyncio.get_event_loop()
            response = await asyncio.wait_for(
                loop.run_in_executor(
                    None, 
                    lambda: self.client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=prompt
                    )
                ),
                timeout=timeout
            )
            print("LLM generation completed")
            return response
        except asyncio.TimeoutError:
            print("LLM generation timed out!")
            raise
        except Exception as e:
            print(f"Error in LLM generation: {e}")
            raise
    
    async def process_query(self, query: str, tools_description: str) -> LLMResponse:
        """Process a query and return a structured response"""
        full_prompt = f"{self.system_prompt}\n\nQuery: {query}"
        
        try:
            response = await self.generate_with_timeout(full_prompt)
            response_text = response.text.strip()
            
            # Extract JSON from response
            start_index = response_text.find('{')
            end_index = response_text.rfind('}') 
            
            if start_index != -1 and end_index != -1:
                clean_json_string = response_text[start_index : end_index + 1]
                response_dict = json.loads(clean_json_string)
                
                # Handle the case where parameters is an empty string
                if "parameters" in response_dict and isinstance(response_dict["parameters"], str):
                    if response_dict["parameters"] == '':
                        response_dict["parameters"] = {}
                
                return LLMResponse(**response_dict)
            else:
                raise ValueError("Failed to extract JSON from LLM response")
                
        except Exception as e:
            print(f"Error processing query: {e}")
            # Return a default response in case of error
            return LLMResponse(
                reasoning="Error occurred during processing",
                self_correction="Failed to process the query",
                answer=f"Error: {str(e)}"
            ) 