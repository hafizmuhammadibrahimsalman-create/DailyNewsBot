
import sys
import importlib
import os

# Set encoding to utf-8 for stdout if possible, or just use ascii
sys.stdout.reconfigure(encoding='utf-8')

def check_import(module_name):
    try:
        importlib.import_module(module_name)
        print(f"[OK] {module_name} installed")
        return True
    except ImportError:
        print(f"[MISSING] {module_name} MISSING")
        return False

print("--- Checking Dependencies ---")
required_modules = [
    'dotenv', 'requests', 'bs4', 'feedparser', 
    'google.generativeai', 'edge_tts', 'moviepy', 'PIL', 'keyring', 'pywhatkit'
]

all_installed = True
for mod in required_modules:
    if not check_import(mod):
        all_installed = False

if not all_installed:
    print("\nCRITICAL: Missing dependencies. Run: pip install -r requirements.txt")
    sys.exit(1)

print("\n--- Checking News Fetcher ---")
try:
    from news_fetcher import NewsFetcher
    fetcher = NewsFetcher()
    print("[OK] NewsFetcher initialized")
    
    # Simple fetch test
    print("   Attempting simple fetch (Google RSS)...")
    articles = fetcher._fetch_from_google_news_rss(["test"])
    if articles:
        print(f"[OK] Fetch successful (Found {len(articles)} articles)")
    else:
        print("[WARN] Fetch returned no articles (might be network or query issue)")
except Exception as e:
    print(f"[ERROR] NewsFetcher Error: {e}")

print("\n--- Checking WhatsApp Sender ---")
try:
    from whatsapp_sender import WhatsAppSender
    sender = WhatsAppSender()
    print(f"[OK] WhatsAppSender initialized (Target: {sender.phone_number})")
except Exception as e:
    print(f"[ERROR] WhatsAppSender Error: {e}")

print("\n--- Verification Complete ---")
