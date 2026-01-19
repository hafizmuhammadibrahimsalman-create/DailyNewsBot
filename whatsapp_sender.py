#!/usr/bin/env python3
"""
DailyNewsBot - WhatsApp Sender
===============================
Sends messages via WhatsApp Web using PyWhatKit automation.

This module provides a reliable WhatsApp message delivery system with
automatic retry, validation, and logging capabilities.
"""

import pywhatkit as kit
import webbrowser
import logging
import time
from typing import Optional
from config import WHATSAPP_NUMBER

logger = logging.getLogger(__name__)


class WhatsAppSender:
    """
    WhatsApp message sender using PyWhatKit automation.
    
    This class handles sending messages through WhatsApp Web with improved
    reliability through longer wait times and pyautogui integration.
    
    Attributes:
        phone_number (str): Target phone number with country code prefix
    
    Example:
        >>> sender = WhatsAppSender()
        >>> sender.send_message("Hello from DailyNewsBot!")
        True
    """
    
    def __init__(self, phone_number: Optional[str] = None):
        """
        Initialize WhatsApp sender.
        
        Args:
            phone_number: Optional phone number to override config.
                         Must include country code (e.g., '+923001234567').
                         If None, uses WHATSAPP_NUMBER from config.
        
        Raises:
            ValueError: If phone number is empty or invalid format
        """
        target = phone_number or WHATSAPP_NUMBER
        
        if not target:
            raise ValueError("Phone number is required (set WHATSAPP_NUMBER in .env)")
        
        # Ensure + prefix
        self.phone_number = f"+{target}" if not target.startswith("+") else target
        
        # Validate format (basic check)
        digits = ''.join(c for c in self.phone_number if c.isdigit())
        if len(digits) < 10:
            raise ValueError(f"Phone number looks too short: {self.phone_number}")
        
        logger.debug(f"WhatsAppSender initialized for {self.phone_number}")
    
    @staticmethod
    def login_whatsapp() -> None:
        """
        Open WhatsApp Web for first-time login.
        
        This helper function opens WhatsApp Web in the default browser
        so you can scan the QR code and establish a session.
        
        Note:
            You only need to do this once. WhatsApp Web will remember
            your session for future use.
        
        Example:
            >>> WhatsAppSender.login_whatsapp()
            # Browser opens to web.whatsapp.com
        """
        print("\n" + "=" * 50)
        print("         WhatsApp Web Login Helper")
        print("=" * 50)
        print("\n1. Browser window will open")
        print("2. Scan QR code from your phone:")
        print("   WhatsApp > Settings > Linked Devices > Link Device")
        print("3. Wait for chats to load completely")
        print("4. Close this terminal when ready\n")
        print("=" * 50 + "\n")
        
        webbrowser.open("https://web.whatsapp.com")
        logger.info("Opened WhatsApp Web for login")
    
    def send_message(
        self, 
        message: str, 
        phone_number: Optional[str] = None,
        wait_time: int = 30
    ) -> bool:
        """
        Send a message via WhatsApp Web.
        
        This method uses PyWhatKit to automate message sending through
        WhatsApp Web. It includes extended wait times and automatic
        Enter key pressing for improved reliability.
        
        Args:
            message: Message text to send (max ~4096 characters)
            phone_number: Optional phone number to override default.
                         Must include country code (e.g., '+923001234567')
            wait_time: Seconds to wait for WhatsApp Web to load (default: 30)
        
        Returns:
            True if send command was issued successfully, False on error
        
        Note:
            - WhatsApp Web must be logged in first (call login_whatsapp())
            - Don't move mouse during the send process
            - Browser tab stays open for verification
            - Check logs for detailed status
        
        Example:
            >>> sender = WhatsAppSender()
            >>> success = sender.send_message("Daily news update!")
            >>> if success:
            ...     print("Message sent!")
        
        Raises:
            ValueError: If message is empty
        """
        if not message or not message.strip():
            raise ValueError("Message cannot be empty")
        
        # Determine target number
        target = phone_number or self.phone_number
        if not target.startswith("+"):
            target = f"+{target}"
        
        try:
            logger.info(f"[>>] Sending to {target}...")
            logger.debug(f"Message length: {len(message)} characters")
            
            # Use PyWhatKit's instant send with extended wait time
            kit.sendwhatmsg_instantly(
                target,
                message,
                wait_time=wait_time,      # Extended wait for slow connections
                tab_close=False,          # Keep tab open for verification
                close_time=5
            )
            
            # Additional reliability: press Enter with pyautogui
            self._press_enter_to_send()
            
            time.sleep(3)  # Allow send to complete
            logger.info("[OK] Send command issued successfully")
            logger.info("    Check WhatsApp Web tab to verify delivery")
            return True
            
        except Exception as e:
            logger.error(f"[ERR] Failed to send message: {type(e).__name__}: {e}")
            logger.error(f"    Target: {target}")
            logger.error(f"    Message length: {len(message)}")
            return False
    
    def _press_enter_to_send(self) -> None:
        """
        Press Enter key to send the message (internal helper).
        
        Uses pyautogui to automatically press Enter after the message
        is typed. This improves reliability when PyWhatKit doesn't
        send automatically.
        
        Note:
            Fails gracefully if pyautogui is not installed.
        """
        try:
            import pyautogui
            time.sleep(2)  # Wait for message to be typed in text box
            pyautogui.press('enter')
            logger.info("[OK] Auto-pressed Enter to send")
        except ImportError:
            logger.warning("[WARN] pyautogui not installed - Enter key not pressed")
            logger.warning("       You may need to press Enter manually")
        except Exception as e:
            logger.warning(f"[WARN] Auto-send failed: {e}")
            logger.warning("       You may need to press Enter manually")
    
    def send_long_message(
        self, 
        message: str, 
        phone_number: Optional[str] = None
    ) -> bool:
        """
        Send a long message (alias for send_message).
        
        Args:
            message: Message text (any length)
            phone_number: Optional phone number override
        
        Returns:
            True if send command issued successfully
        
        Note:
            WhatsApp has a ~4096 character limit per message.
            For longer messages, consider splitting into chunks.
        """
        return self.send_message(message, phone_number)
    
    def validate_phone_number(self, phone_number: str) -> bool:
        """
        Validate phone number format.
        
        Args:
            phone_number: Phone number to validate
        
        Returns:
            True if format looks valid, False otherwise
        
        Example:
            >>> sender = WhatsAppSender()
            >>> sender.validate_phone_number("+923001234567")
            True
            >>> sender.validate_phone_number("123")
            False
        """
        import re
        
        if not phone_number:
            return False
        
        # Remove formatting
        clean = re.sub(r'[\s\-\(\)]', '', phone_number)
        clean = clean.lstrip('+')
        
        # Check if digits only and reasonable length
        return clean.isdigit() and 10 <= len(clean) <= 15


if __name__ == "__main__":
    # Interactive test script
    import sys
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-8s | %(message)s'
    )
    
    try:
        sender = WhatsAppSender()
        print(f"\nTarget: {sender.phone_number}\n")
        print("1: Login to WhatsApp Web")
        print("2: Send test message")
        print("3: Validate phone number\n")
        
        choice = input("Enter choice (1-3): ").strip()
        
        if choice == "1":
            WhatsAppSender.login_whatsapp()
        elif choice == "2":
            test_msg = "🤖 Test message from DailyNewsBot\n\nIf you received this, the bot is working!"
            success = sender.send_message(test_msg)
            if success:
                print("\n✅ Send command issued. Check WhatsApp Web!")
            else:
                print("\n❌ Send failed. Check logs above.")
        elif choice == "3":
            test_number = input("Enter phone number to validate: ")
            is_valid = sender.validate_phone_number(test_number)
            print(f"\n{'✅ Valid' if is_valid else '❌ Invalid'} format")
        else:
            print("Invalid choice")
    
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nCancelled by user")
        sys.exit(0)
