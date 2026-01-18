import os
import sys
try:
    import keyring
except ImportError:
    keyring = None

from dotenv import load_dotenv

class SecureConfig:
    SERVICE_NAME = "DailyNewsBot"
    
    @staticmethod
    def initialize():
        """Load environment variables once"""
        load_dotenv()

    @staticmethod
    def store_credential(key: str, value: str):
        """Store in Windows Credential Manager"""
        if keyring:
            try:
                keyring.set_password(SecureConfig.SERVICE_NAME, key, value)
                print(f"[OK] Securely stored {key}")
            except Exception as e:
                print(f"[WARN] Keyring error: {e}. Fallback to .env recommended.")
        else:
            print("[WARN] 'keyring' module not installed. Cannot store securely.")

    @staticmethod
    def get_credential(key: str) -> str:
        """Retrieve securely with .env fallback"""
        # 1. Try Keyring (Best Security)
        if keyring:
            try:
                val = keyring.get_password(SecureConfig.SERVICE_NAME, key)
                if val: return val
            except:
                pass
        
        # 2. Fallback to .env (Compatibility)
        val = os.getenv(key)
        if val: return val
        
        return None

# Initialize on import
SecureConfig.initialize()
