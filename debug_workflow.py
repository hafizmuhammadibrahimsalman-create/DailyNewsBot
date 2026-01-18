import json
import urllib.request
import urllib.error
import sys

# Force UTF-8 for Windows Console
sys.stdout.reconfigure(encoding='utf-8')

N8N_URL = "http://localhost:5678/api/v1/workflows"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3MGJkNjQ5ZC0yMjk1LTQzYjgtOWFjZC1kMjliZTg4NTBiMzUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzY2NDMzMzg5fQ._Lc7URhX2rBxiIxdN8yS5WtiqjzpsFjVXUZiYbDdZR0"

# Target Workflow Name
TARGET_NAME = "DailyNewsBot Sovereign Orchestrator"

def check_workflow():
    print("🔍 Inspecting n8n Workflows...")
    
    headers = {
        "X-N8N-API-KEY": API_KEY,
        "Content-Type": "application/json"
    }
    
    req = urllib.request.Request(N8N_URL, headers=headers, method='GET')
    
    try:
        with urllib.request.urlopen(req) as response:
            workflows = json.loads(response.read().decode('utf-8')).get('data', [])
            
            target_wf = next((w for w in workflows if w['name'] == TARGET_NAME), None)
            
            if not target_wf:
                print(f"❌ Workflow '{TARGET_NAME}' NOT FOUND on server.")
                return

            print(f"✅ Found Workflow: {target_wf['name']} (ID: {target_wf['id']})")
            print(f"   Active: {target_wf['active']}")
            
            print("\n🔗 Connections State:")
            connections = target_wf.get('connections', {})
            if not connections:
                print("   ❌ NO CONNECTIONS DEFINED in JSON!")
            else:
                for source, targets in connections.items():
                    print(f"   - {source} connects to:")
                    for output_name, links in targets.items():
                        for link in links:
                            for item in link:
                                print(f"     -> {item.get('node')}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_workflow()
