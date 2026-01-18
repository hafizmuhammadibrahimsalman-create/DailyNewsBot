import os
import json
import sys
from pathlib import Path

def setup_mcp():
    print("="*60)
    print("🔌 Google Antigravity MCP Bridge Setup")
    print("="*60)
    print("This script connects your Antigravity IDE to your n8n instance.")
    print("\nPre-requisites:")
    print("1. n8n must be running (use START_BOT.bat)")
    print("2. You need an API Key from n8n (Settings -> Public API)")
    print("-" * 60)
    
    api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3MGJkNjQ5ZC0yMjk1LTQzYjgtOWFjZC1kMjliZTg4NTBiMzUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzY2NDMzMzg5fQ._Lc7URhX2rBxiIxdN8yS5WtiqjzpsFjVXUZiYbDdZR0"
    print(f"\n🔑 Using provided API Key: {api_key[:10]}...")

    # Define path based on report
    user_home = Path.home()
    config_path = user_home / ".gemini" / "antigravity" / "mcp_config.json"
    
    # Ensure directory exists
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configuration from the Sovereign Automation Report
    config_data = {
        "mcpServers": {
            "n8n-mcp": {
                "command": "cmd.exe", 
                "args": [
                    "/c",
                    "npx",
                    "-y",
                    "n8n-mcp"
                ],
                "env": {
                    "MCP_MODE": "stdio",
                    "LOG_LEVEL": "error",
                    "DISABLE_CONSOLE_OUTPUT": "true",
                    "N8N_API_URL": "http://localhost:5678",
                    "N8N_API_KEY": api_key
                }
            }
        }
    }
    
    # Write file
    try:
        with open(config_path, "w") as f:
            json.dump(config_data, f, indent=2)
        print(f"\n✅ Configuration written to: {config_path}")
        print("\n🎉 Setup Complete!")
        print("Please restart your Antigravity IDE/Session to pick up the changes.")
    except Exception as e:
        print(f"\n❌ Error writing config: {e}")

if __name__ == "__main__":
    setup_mcp()
