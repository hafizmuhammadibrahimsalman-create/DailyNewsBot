import logging
import requests
import shutil
import socket
import subprocess
import time
import sys
from pathlib import Path
from secure_config import SecureConfig

# Force UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Setup robust logging
HEALTH_LOG = "health.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - HEALTH - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(HEALTH_LOG),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("SystemHealth")

class SystemHealth:
    """Monitors system components and attempts repairs."""
    
    @staticmethod
    def check_network() -> bool:
        """Check internet connectivity via Google DNS."""
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except OSError:
            logger.error("❌ Network is unreachable")
            return False

    @staticmethod
    def check_disk_space(path=".", min_mb=500) -> bool:
        """Ensure disk has space."""
        total, used, free = shutil.disk_usage(path)
        free_mb = free / (1024 * 1024)
        if free_mb < min_mb:
            logger.warning(f"⚠️ Low Disk Space: {free_mb:.0f}MB free")
            return False
        return True

    @staticmethod
    def check_n8n() -> bool:
        """Check if n8n server is responding."""
        try:
            r = requests.get("http://localhost:5678/healthz", timeout=2)
            if r.status_code == 200:
                pass # Status OK
            return True
        except requests.RequestException:
            logger.error("❌ n8n Server is DOWN")
            return False

    @staticmethod
    def heal_n8n():
        """Attempt to restart n8n."""
        logger.info("🩹 Attempting to restart n8n...")
        try:
            # We use the robust START_BOT.bat
            subprocess.Popen("START_BOT.bat", shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
            logger.info("✅ Restart signal sent")
            time.sleep(10) # Wait for startup
        except Exception as e:
            logger.critical(f"🔥 Failed to restart n8n: {e}")

    @staticmethod
    def run_full_check() -> dict:
        """Run all checks and return status."""
        logger.info("🔍 Running System Health Scan...")
        
        status = {
            "network": SystemHealth.check_network(),
            "disk": SystemHealth.check_disk_space(),
            "n8n": SystemHealth.check_n8n(),
            "timestamp": time.time()
        }
        
        # Self-Healing Logic
        if not status["n8n"]:
            SystemHealth.heal_n8n()
            # Re-check
            status["n8n"] = SystemHealth.check_n8n()
            
        all_ok = all(status.values())
        if all_ok:
            logger.info("✅ System is HEALTHY")
        else:
            logger.warning("⚠️ System has ISSUES")
            
        return status

if __name__ == "__main__":
    SystemHealth.run_full_check()
