from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Union
from perception import LLMResponse
from memory import MemoryLayer, MemoryItem

class Decision(BaseModel):
    """Represents a decision made by the system"""
    action: str = Field(..., description="The action to take (function call or final answer)")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Parameters for the action")
    confidence: float = Field(..., description="Confidence level in the decision (0-1)")
    reasoning: str = Field(..., description="Reasoning behind the decision")
    alternatives: List[Dict[str, Any]] = Field(default_factory=list, description="Alternative decisions considered")

class DecisionMakingLayer:
    """Handles analyzing information and making decisions"""
    
    def __init__(self, memory_layer: MemoryLayer):
        self.memory_layer = memory_layer
    
    def analyze_llm_response(self, llm_response: LLMResponse) -> Decision:
        """Analyze LLM response and make a decision"""
        # Extract information from LLM response
        reasoning = llm_response.reasoning
        self_correction = llm_response.self_correction
        function = llm_response.function
        parameters = llm_response.parameters if llm_response.parameters else {}
        answer = llm_response.answer
        
        # Determine the action based on the LLM response
        if function:
            # Function call decision
            action = "function_call"
            confidence = 0.8  # Default confidence for function calls
            alternatives = []
            
            # Store the decision in memory
            self.memory_layer.add_memory(
                content={
                    "action": action,
                    "function": function,
                    "parameters": parameters,
                    "reasoning": reasoning,
                    "self_correction": self_correction
                },
                importance=5,
                category="decision"
            )
            
            # Format parameters for function call
            formatted_parameters = {
                "function": function,
                "args": parameters if parameters else {}
            }
            
            print(f"Making function call decision: {function} with parameters: {formatted_parameters}")
            
            return Decision(
                action=action,
                parameters=formatted_parameters,
                confidence=confidence,
                reasoning=reasoning,
                alternatives=alternatives
            )
        elif answer:
            # Final answer decision
            action = "final_answer"
            confidence = 0.9  # Default confidence for final answers
            alternatives = []
            
            # Store the decision in memory
            self.memory_layer.add_memory(
                content={
                    "action": action,
                    "answer": answer,
                    "reasoning": reasoning,
                    "self_correction": self_correction
                },
                importance=7,
                category="decision"
            )
            
            return Decision(
                action=action,
                parameters={"answer": answer},
                confidence=confidence,
                reasoning=reasoning,
                alternatives=alternatives
            )
        else:
            # Error or invalid response
            action = "error"
            confidence = 0.0
            
            # Store the error in memory
            self.memory_layer.add_memory(
                content={
                    "action": action,
                    "error": "Invalid LLM response",
                    "reasoning": reasoning,
                    "self_correction": self_correction
                },
                importance=3,
                category="error"
            )
            
            return Decision(
                action=action,
                parameters={"error": "Invalid LLM response"},
                confidence=confidence,
                reasoning="Invalid LLM response",
                alternatives=[]
            )
    
    def consider_alternatives(self, decision: Decision) -> Decision:
        """Consider alternative decisions based on memory"""
        # Get recent memories related to similar decisions
        recent_memories = self.memory_layer.get_memories(category="decision", min_importance=5)
        
        # If we have similar memories, consider them as alternatives
        if recent_memories:
            for memory in recent_memories[:3]:  # Consider top 3 recent memories
                if memory.content.get("action") == decision.action:
                    # Add as an alternative
                    decision.alternatives.append({
                        "action": memory.content.get("action"),
                        "parameters": memory.content.get("parameters"),
                        "reasoning": memory.content.get("reasoning")
                    })
        
        return decision
    
    def evaluate_decision(self, decision: Decision, result: Any) -> None:
        """Evaluate the outcome of a decision and update memory"""
        # Store the evaluation in memory
        self.memory_layer.add_memory(
            content={
                "decision": decision.dict(),
                "result": str(result),
                "success": True if result else False
            },
            importance=4,
            category="evaluation"
        ) 