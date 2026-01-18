import json
import urllib.request
import urllib.error
import sys
import time

# Force UTF-8 for Windows Console
sys.stdout.reconfigure(encoding='utf-8')

# Configuration
N8N_URL = "http://localhost:5678/api/v1/workflows"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3MGJkNjQ5ZC0yMjk1LTQzYjgtOWFjZC1kMjliZTg4NTBiMzUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzY2NDMzMzg5fQ._Lc7URhX2rBxiIxdN8yS5WtiqjzpsFjVXUZiYbDdZR0"
WORKFLOW_FILE = "n8n_workflow_unified.json"

def import_workflow():
    print("🚀 Starting Automatic Workflow Import...")
    
    # 1. Read the Workflow JSON
    try:
        with open(WORKFLOW_FILE, 'r', encoding='utf-8') as f:
            workflow_data = json.load(f)
        print(f"✅ Loaded workflow file: {WORKFLOW_FILE}")
    except Exception as e:
        print(f"❌ Failed to read file: {e}")
        return

    # 2. Prepare the Request
    headers = {
        "X-N8N-API-KEY": API_KEY,
        "Content-Type": "application/json"
    }
    
    # Ensure settings object exists
    if "settings" not in workflow_data:
        workflow_data["settings"] = {}
    
    # Remove active status for creation (read-only)
    if "active" in workflow_data:
        del workflow_data["active"]
        
    data = json.dumps(workflow_data).encode('utf-8')
    req = urllib.request.Request(N8N_URL, data=data, headers=headers, method='POST')

    # 3. Send to n8n
    try:
        print(f"📡 Sending to n8n at {N8N_URL}...")
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            workflow_id = result.get('id')
            print(f"✅ Success! Workflow ID: {workflow_id}")
            
            # 4. Activate the Workflow
            print("🚀 Activating workflow...")
            activate_url = f"{N8N_URL}/{workflow_id}/activate"
            req_activate = urllib.request.Request(activate_url, headers=headers, method='POST')
            try:
                with urllib.request.urlopen(req_activate) as act_resp:
                    print(f"✨ Workflow '{result.get('name')}' is now ACTIVE!")
            except Exception as e:
                 print(f"⚠️ Created but failed to auto-activate: {e}")
                 print("👉 Please activate it manually in the dashboard.")

            print("👉 You can go to http://localhost:5678 and refresh the page to see it.")
            
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP Error: {e.code} - {e.reason}")
        print(e.read().decode('utf-8'))
    except urllib.error.URLError as e:
        print(f"❌ Connection Error: {e.reason}")
        print("Is n8n running? Make sure to run START_BOT.bat first.")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

if __name__ == "__main__":
    import_workflow()
