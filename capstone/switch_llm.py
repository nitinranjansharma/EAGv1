#!/usr/bin/env python3
"""
LLM Provider Switch Utility

This script helps you easily switch between Ollama and Gemini Flash LLM providers
for the Research Paper Discovery system.
"""

import os
import sys
import re
from pathlib import Path

def read_config():
    """Read the current config.py file."""
    config_path = Path("config.py")
    if not config_path.exists():
        print("❌ config.py not found!")
        return None
    
    with open(config_path, 'r') as f:
        return f.read()

def write_config(content):
    """Write content to config.py file."""
    config_path = Path("config.py")
    
    # Create backup
    backup_path = Path("config.py.backup")
    if config_path.exists():
        with open(config_path, 'r') as f:
            backup_content = f.read()
        with open(backup_path, 'w') as f:
            f.write(backup_content)
        print(f"💾 Backup created: {backup_path}")
    
    # Write new config
    with open(config_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Updated: {config_path}")

def switch_to_ollama():
    """Switch configuration to use Ollama."""
    print("🔄 Switching to Ollama...")
    
    content = read_config()
    if content is None:
        return False
    
    # Update USE_GEMINI flag
    content = re.sub(
        r'USE_GEMINI = True',
        'USE_GEMINI = False',
        content
    )
    
    # Update Gemini API key comment
    content = re.sub(
        r'GEMINI_API_KEY = "[^"]*"',
        'GEMINI_API_KEY = "your_gemini_api_key_here"',
        content
    )
    
    write_config(content)
    print("✅ Successfully switched to Ollama!")
    print("📝 Make sure Ollama is running with: ollama serve")
    return True

def switch_to_gemini():
    """Switch configuration to use Gemini Flash."""
    print("🔄 Switching to Gemini Flash...")
    
    content = read_config()
    if content is None:
        return False
    
    # Update USE_GEMINI flag
    content = re.sub(
        r'USE_GEMINI = False',
        'USE_GEMINI = True',
        content
    )
    
    write_config(content)
    print("✅ Successfully switched to Gemini Flash!")
    print("🔑 Please update GEMINI_API_KEY in config.py with your actual API key")
    return True

def show_current_config():
    """Show the current LLM configuration."""
    content = read_config()
    if content is None:
        return False
    
    # Extract current settings
    use_gemini_match = re.search(r'USE_GEMINI = (True|False)', content)
    gemini_key_match = re.search(r'GEMINI_API_KEY = "([^"]*)"', content)
    
    if use_gemini_match:
        use_gemini = use_gemini_match.group(1) == 'True'
        current_provider = "Gemini Flash" if use_gemini else "Ollama"
        
        print("🔧 Current LLM Configuration:")
        print(f"   🤖 Provider: {current_provider}")
        print(f"   ⚙️  USE_GEMINI: {use_gemini}")
        
        if use_gemini and gemini_key_match:
            api_key = gemini_key_match.group(1)
            if api_key == "your_gemini_api_key_here":
                print("   🔑 API Key: Not configured (using placeholder)")
            else:
                print("   🔑 API Key: Configured")
        
        return True
    
    print("❌ Could not determine current configuration")
    return False

def main():
    """Main function."""
    print("🤖 LLM Provider Switch Utility")
    print("=" * 50)
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python switch_llm.py show     - Show current configuration")
        print("  python switch_llm.py ollama   - Switch to Ollama")
        print("  python switch_llm.py gemini   - Switch to Gemini Flash")
        print()
        show_current_config()
        return
    
    command = sys.argv[1].lower()
    
    if command == "show":
        show_current_config()
    elif command == "ollama":
        switch_to_ollama()
    elif command == "gemini":
        switch_to_gemini()
    else:
        print(f"❌ Unknown command: {command}")
        print("Available commands: show, ollama, gemini")

if __name__ == "__main__":
    main()
