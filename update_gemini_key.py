import sys
import keyring

# Force UTF-8 for Windows Console
sys.stdout.reconfigure(encoding='utf-8')

print("=" * 60)
print("🔑 Google Gemini Pro API Key Updater")
print("=" * 60)
print()
print("Follow these steps to get your Pro API key:")
print()
print("1. Go to: https://aistudio.google.com/apikey")
print("2. Click 'Create API Key' or use existing one")
print("3. Make sure you're logged into your GOOGLE PRO account")
print("4. Copy the API key")
print()
print("-" * 60)

api_key = input("\n📋 Paste your Google Pro API Key here: ").strip()

if not api_key:
    print("❌ No API key provided. Exiting.")
    sys.exit(1)

# Store in Windows Credential Manager
try:
    keyring.set_password("DailyNewsBot", "GEMINI_API_KEY", api_key)
    print(f"\n✅ API Key saved securely to Windows Credential Manager!")
    print(f"🔒 Your key is encrypted and safe.")
    print(f"\n🚀 You can now run the bot with unlimited Pro quota!")
    print(f"\nTest it: python antigravity_query.py \"Bitcoin news today\"")
except Exception as e:
    print(f"\n⚠️ Couldn't save to keyring: {e}")
    print(f"\nFalling back to .env file...")
    
    # Fallback to .env
    try:
        with open(".env", "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        lines = []
    
    # Update or add GEMINI_API_KEY
    found = False
    for i, line in enumerate(lines):
        if line.startswith("GEMINI_API_KEY="):
            lines[i] = f"GEMINI_API_KEY={api_key}\n"
            found = True
            break
    
    if not found:
        lines.append(f"GEMINI_API_KEY={api_key}\n")
    
    with open(".env", "w") as f:
        f.writelines(lines)
    
    print("✅ API Key saved to .env file!")
    print("🚀 You can now run the bot!")
