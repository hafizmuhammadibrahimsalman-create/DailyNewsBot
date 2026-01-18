
import pywhatkit as kit
import webbrowser
import logging
import time
from config import WHATSAPP_NUMBER

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WhatsAppSender:
    def __init__(self):
        self.phone_number = f"+{WHATSAPP_NUMBER}" if not WHATSAPP_NUMBER.startswith("+") else WHATSAPP_NUMBER
    
    def login_whatsapp(self):
        """First time login helper."""
        print("\n--- WhatsApp Web Login ---")
        print("1. Browser opening...")
        print("2. Scan QR code via Phone Linked Devices")
        print("3. Wait for chats to load, then close this script.")
        webbrowser.open("https://web.whatsapp.com")
    
    def send_message(self, message: str, phone_number: str = None) -> bool:
        """Send message using PyWhatKit with improved reliability."""
        target = phone_number or self.phone_number
        if not target.startswith("+"): target = f"+{target}"
        
        try:
            logger.info(f"[>>] Sending to {target}...")
            
            # Method 1: Use sendwhatmsg_instantly with longer wait
            # wait_time=30 gives WhatsApp Web more time to load
            # tab_close=False keeps tab open so we can verify
            kit.sendwhatmsg_instantly(
                target, 
                message, 
                wait_time=30,      # Wait 30 seconds for WhatsApp to load
                tab_close=False,   # Don't close - user can verify
                close_time=5
            )
            
            # Press Enter using pyautogui for extra reliability
            try:
                import pyautogui
                time.sleep(2)  # Wait for message to be typed
                pyautogui.press('enter')
                logger.info("[OK] Enter pressed to send message.")
            except ImportError:
                logger.info("[INFO] pyautogui not installed - message may need manual Enter press")
            except Exception as e:
                logger.warning(f"[WARN] Auto-send failed: {e}")
            
            time.sleep(3)  # Wait for send to complete
            logger.info("[OK] Send command issued. Check WhatsApp Web to verify.")
            return True
            
        except Exception as e:
            logger.error(f"[ERR] Send failed: {e}")
            return False
    
    def send_long_message(self, message: str, phone_number: str = None) -> bool:
        return self.send_message(message, phone_number)

if __name__ == "__main__":
    sender = WhatsAppSender()
    print(f"Target: {sender.phone_number}")
    opt = input("1: Login, 2: Test Send\n> ")
    if opt == "1": sender.login_whatsapp()
    elif opt == "2": sender.send_message("Test Message from DailyNewsBot")

