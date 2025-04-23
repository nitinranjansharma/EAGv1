from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import json
import os
from datetime import datetime

class MemoryItem(BaseModel):
    """Represents a single memory item"""
    timestamp: datetime = Field(default_factory=datetime.now)
    content: Dict[str, Any] = Field(..., description="The content of the memory")
    importance: int = Field(default=1, description="Importance level of the memory (1-10)")
    category: str = Field(default="general", description="Category of the memory")

class MemoryLayer:
    """Handles storing and retrieving information"""
    
    def __init__(self, memory_file: str = "memory.json"):
        self.memory_file = memory_file
        self.memories: List[MemoryItem] = []
        self.load_memories()
    
    def load_memories(self) -> None:
        """Load memories from file"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    data = json.load(f)
                    self.memories = [MemoryItem(**item) for item in data]
            except Exception as e:
                print(f"Error loading memories: {e}")
                self.memories = []
        else:
            self.memories = []
    
    def save_memories(self) -> None:
        """Save memories to file"""
        try:
            with open(self.memory_file, 'w') as f:
                json.dump([memory.dict() for memory in self.memories], f, default=str)
        except Exception as e:
            print(f"Error saving memories: {e}")
    
    def add_memory(self, content: Dict[str, Any], importance: int = 1, category: str = "general") -> None:
        """Add a new memory"""
        memory = MemoryItem(content=content, importance=importance, category=category)
        self.memories.append(memory)
        self.save_memories()
    
    def get_memories(self, category: Optional[str] = None, min_importance: int = 0) -> List[MemoryItem]:
        """Get memories filtered by category and importance"""
        filtered_memories = self.memories
        
        if category:
            filtered_memories = [m for m in filtered_memories if m.category == category]
        
        if min_importance > 0:
            filtered_memories = [m for m in filtered_memories if m.importance >= min_importance]
        
        # Sort by timestamp (newest first)
        return sorted(filtered_memories, key=lambda x: x.timestamp, reverse=True)
    
    def get_recent_memories(self, limit: int = 5) -> List[MemoryItem]:
        """Get the most recent memories"""
        return sorted(self.memories, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    def clear_memories(self, category: Optional[str] = None) -> None:
        """Clear all memories or memories of a specific category"""
        if category:
            self.memories = [m for m in self.memories if m.category != category]
        else:
            self.memories = []
        self.save_memories()
    
    def update_memory(self, index: int, content: Dict[str, Any]) -> bool:
        """Update a memory at the specified index"""
        if 0 <= index < len(self.memories):
            self.memories[index].content.update(content)
            self.save_memories()
            return True
        return False 