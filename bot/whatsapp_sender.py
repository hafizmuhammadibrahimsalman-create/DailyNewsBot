#!/usr/bin/env python3
"""
DailyNewsBot - WhatsApp Sender (Enhanced v2)
=============================================
Sends messages via WhatsApp Web using PyWhatKit automation with comprehensive
error handling, retry logic, validation, and security features.

Features:
- Automatic retry with exponential backoff
- Input validation and sanitization
- Comprehensive error handling
- Type hints throughout
- Thread-safe operations
- Rate limiting
- Message batching
- Delivery status tracking

Author: DailyNewsBot Team
Version: 2.0.0
"""

import pywhatkit as kit
import webbrowser
import logging
import time
import re
import threading
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
from pathlib import Path

try:
    from bot.config import WHATSAPP_NUMBER
except ImportError:
    WHATSAPP_NUMBER = None

logger = logging.getLogger(__name__)


class SendStatus(Enum):
    """Message send status enumeration."""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    RETRY = "retry"
    TIMEOUT = "timeout"


@dataclass
class WhatsAppMessage:
    """Data class for WhatsApp message tracking."""
    phone_number: str
    message: str
    timestamp: datetime
    status: SendStatus = SendStatus.PENDING
    attempts: int = 0
    last_error: Optional[str] = None
    
    def __post_init__(self):
        """Validate message data."""
        if not self.phone_number or not isinstance(self.phone_number, str):
            raise ValueError("Invalid phone number")
        if not self.message or not isinstance(self.message, str):
            raise ValueError("Invalid message")
        if len(self.message) > 4096:
            raise ValueError("Message exceeds WhatsApp limit (4096 chars)")


class RateLimiter:
    """Thread-safe rate limiter for WhatsApp API."""
    
    def __init__(self, max_messages: int = 10, window_seconds: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            max_messages: Maximum messages per window
            window_seconds: Time window in seconds
        """
        self.max_messages = max_messages
        self.window_seconds = window_seconds
        self.messages: List[datetime] = []
        self._lock = threading.Lock()
    
    def can_send(self) -> bool:
        """Check if message can be sent."""
        with self._lock:
            now = datetime.now()
            # Remove old messages outside window
            self.messages = [
                m for m in self.messages 
                if now - m < timedelta(seconds=self.window_seconds)
            ]
            
            if len(self.messages) < self.max_messages:
                self.messages.append(now)
                return True
            return False
    
    def wait_until_ready(self) -> float:
        """Wait and return seconds waited."""
        if self.can_send():
            return 0.0
        
        with self._lock:
            if not self.messages:
                return 0.0
            
            oldest = self.messages[0]
            wait_time = (oldest + timedelta(seconds=self.window_seconds) - datetime.now()).total_seconds()
            wait_time = max(0, wait_time)
        
        if wait_time > 0:
            logger.info(f"Rate limited. Waiting {wait_time:.1f}s before next message")
            time.sleep(wait_time)
        return wait_time


class WhatsAppSender:
    """
    Enhanced WhatsApp message sender using PyWhatKit automation.
    
    Features:
    - Automatic retry with exponential backoff
    - Rate limiting and message throttling
    - Input validation and sanitization
    - Thread-safe operations
    - Message batching support
    - Delivery tracking
    - Comprehensive error handling
    
    Attributes:
        phone_number (str): Target phone number with country code prefix
        retry_config (Dict): Configuration for retry attempts
        rate_limiter (RateLimiter): Rate limiting instance
        message_history (List): History of sent messages
    
    Example:
        >>> sender = WhatsAppSender(phone_number="+923001234567")
        >>> result = sender.send_message("Hello!", retry_attempts=3)
        >>> if result.status == SendStatus.SENT:
        ...     print("Message delivered!")
    """
    
    def __init__(
        self, 
        phone_number: Optional[str] = None,
        max_retries: int = 3,
        retry_delay: float = 2.0,
        wait_time: int = 30,
        enable_rate_limiting: bool = True,
        max_messages_per_minute: int = 10
    ):
        """
        Initialize WhatsApp sender with configuration.
        
        Args:
            phone_number: Optional phone number override (country code required)
            max_retries: Maximum retry attempts for failed sends
            retry_delay: Initial delay between retries in seconds
            wait_time: Seconds to wait for WhatsApp Web to load
            enable_rate_limiting: Enable message rate limiting
            max_messages_per_minute: Max messages per 60 seconds
        
        Raises:
            ValueError: If phone number is invalid
            ImportError: If required dependencies are missing
        """
        # Get phone number from parameter or config
        target = phone_number or WHATSAPP_NUMBER
        
        if not target:
            raise ValueError(
                "Phone number required. Pass as parameter or set WHATSAPP_NUMBER in .env"
            )
        
        # Validate and normalize phone number
        self.phone_number = self._normalize_phone_number(target)
        
        # Configuration
        self.max_retries = max(1, max_retries)  # At least 1 retry
        self.retry_delay = max(0.5, retry_delay)  # At least 0.5s
        self.wait_time = max(10, wait_time)  # At least 10s
        self._lock = threading.Lock()
        
        # Rate limiting
        self.rate_limiter = RateLimiter(
            max_messages=max_messages_per_minute,
            window_seconds=60
        ) if enable_rate_limiting else None
        
        # Message tracking
        self.message_history: List[WhatsAppMessage] = []
        self.max_history_size = 1000
        
        logger.info(f"WhatsAppSender initialized for {self.phone_number}")
        logger.debug(f"Config - Retries: {self.max_retries}, Delay: {self.retry_delay}s, Wait: {self.wait_time}s")
    
    @staticmethod
    def _normalize_phone_number(phone: str) -> str:
        """
        Normalize and validate phone number format.
        
        Args:
            phone: Phone number (with or without + prefix)
        
        Returns:
            Normalized phone number with + prefix
        
        Raises:
            ValueError: If phone number format is invalid
        """
        if not phone or not isinstance(phone, str):
            raise ValueError("Phone number must be a non-empty string")
        
        # Remove spaces, hyphens, parentheses
        clean = re.sub(r'[\s\-\(\)]', '', phone.strip())
        
        # Ensure + prefix
        if not clean.startswith('+'):
            clean = f"+{clean}"
        
        # Validate: + followed by 10-15 digits
        if not re.match(r'^\+\d{10,15}$', clean):
            raise ValueError(
                f"Invalid phone format: {phone}. "
                "Use format like +923001234567 (country code + digits)"
            )
        
        return clean
    
    def send_message(
        self,
        message: str,
        phone_number: Optional[str] = None,
        retry_attempts: Optional[int] = None,
        wait_time: Optional[int] = None
    ) -> WhatsAppMessage:
        """
        Send a message via WhatsApp Web with automatic retry.
        
        Args:
            message: Message text (max 4096 characters)
            phone_number: Optional phone number override
            retry_attempts: Override max retries for this message
            wait_time: Override wait time for this message
        
        Returns:
            WhatsAppMessage with status and metadata
        
        Raises:
            ValueError: If message or phone number is invalid
        
        Example:
            >>> result = sender.send_message("Hello world!")
            >>> if result.status == SendStatus.SENT:
            ...     print("Success!")
        """
        # Validate inputs
        if not message or not isinstance(message, str):
            raise ValueError("Message must be a non-empty string")
        
        message = message.strip()
        if len(message) > 4096:
            raise ValueError(f"Message too long ({len(message)} chars). Max 4096.")
        
        # Determine target phone number
        target = phone_number or self.phone_number
        try:
            target = self._normalize_phone_number(target)
        except ValueError as e:
            logger.error(f"Invalid phone number: {e}")
            raise
        
        # Create message object
        msg = WhatsAppMessage(
            phone_number=target,
            message=message,
            timestamp=datetime.now()
        )
        
        # Apply rate limiting if enabled
        if self.rate_limiter:
            wait_secs = self.rate_limiter.wait_until_ready()
            if wait_secs > 0:
                logger.info(f"Applied rate limit delay: {wait_secs:.1f}s")
        
        # Attempt to send with retries
        max_attempts = retry_attempts or self.max_retries
        delay = self.retry_delay
        
        for attempt in range(1, max_attempts + 1):
            try:
                msg.attempts = attempt
                logger.info(f"[SEND {attempt}/{max_attempts}] To: {target}")
                
                # Send the message
                self._send_with_automation(
                    target, 
                    message, 
                    wait_time or self.wait_time
                )
                
                msg.status = SendStatus.SENT
                logger.info(f"[OK] Message sent successfully")
                break
                
            except Exception as e:
                msg.last_error = str(e)
                msg.status = SendStatus.RETRY if attempt < max_attempts else SendStatus.FAILED
                
                logger.warning(
                    f"[WARN] Attempt {attempt} failed: {type(e).__name__}: {e}"
                )
                
                if attempt < max_attempts:
                    logger.info(f"[RETRY] Waiting {delay}s before retry...")
                    time.sleep(delay)
                    delay *= 1.5  # Exponential backoff
        
        # Track message
        with self._lock:
            self.message_history.append(msg)
            if len(self.message_history) > self.max_history_size:
                self.message_history = self.message_history[-self.max_history_size:]
        
        return msg
    
    def _send_with_automation(
        self, 
        phone_number: str, 
        message: str, 
        wait_time: int
    ) -> None:
        """
        Internal method to send message using PyWhatKit + pyautogui.
        
        Args:
            phone_number: Destination phone number
            message: Message text
            wait_time: Wait time in seconds
        
        Raises:
            RuntimeError: If send fails
        """
        try:
            logger.debug(f"Sending {len(message)} chars to {phone_number}")
            
            # Use PyWhatKit's instant send
            kit.sendwhatmsg_instantly(
                phone_number,
                message,
                wait_time=wait_time,
                tab_close=False,
                close_time=5
            )
            
            # Try to press Enter with pyautogui for reliability
            self._press_enter_to_send()
            
            # Allow send to complete
            time.sleep(3)
            
        except Exception as e:
            raise RuntimeError(f"PyWhatKit send failed: {e}") from e
    
    def send_batch(
        self,
        messages: List[Tuple[str, str]],
        delay_between: float = 5.0,
        stop_on_error: bool = False
    ) -> List[WhatsAppMessage]:
        """
        Send multiple messages with delay between each.
        
        Args:
            messages: List of (phone_number, message) tuples
            delay_between: Delay between messages in seconds
            stop_on_error: Stop sending if any message fails
        
        Returns:
            List of WhatsAppMessage objects with statuses
        
        Example:
            >>> msgs = [
            ...     ("+923001234567", "Hello"),
            ...     ("+923009876543", "World"),
            ... ]
            >>> results = sender.send_batch(msgs, delay_between=5)
            >>> sent_count = sum(1 for m in results if m.status == SendStatus.SENT)
        """
        results: List[WhatsAppMessage] = []
        
        logger.info(f"Starting batch send: {len(messages)} messages")
        
        for idx, (phone, msg_text) in enumerate(messages, 1):
            logger.info(f"[BATCH {idx}/{len(messages)}]")
            
            try:
                result = self.send_message(msg_text, phone_number=phone)
                results.append(result)
                
                if result.status == SendStatus.FAILED and stop_on_error:
                    logger.error("Batch sending stopped due to error")
                    break
                
                if idx < len(messages):
                    logger.debug(f"Waiting {delay_between}s before next message...")
                    time.sleep(delay_between)
                    
            except Exception as e:
                logger.error(f"Batch send error: {e}")
                if stop_on_error:
                    break
        
        success_count = sum(1 for r in results if r.status == SendStatus.SENT)
        logger.info(f"Batch complete: {success_count}/{len(results)} sent")
        
        return results
    
    def get_send_statistics(self) -> Dict:
        """
        Get statistics about sent messages.
        
        Returns:
            Dictionary with statistics
        """
        with self._lock:
            total = len(self.message_history)
            sent = sum(1 for m in self.message_history if m.status == SendStatus.SENT)
            failed = sum(1 for m in self.message_history if m.status == SendStatus.FAILED)
        
        return {
            "total_messages": total,
            "sent_count": sent,
            "failed_count": failed,
            "success_rate": (sent / total * 100) if total > 0 else 0,
            "last_message_time": (
                self.message_history[-1].timestamp.isoformat() 
                if self.message_history else None
            )
        }

    @staticmethod
    def login_whatsapp() -> None:
        """
        Open WhatsApp Web for first-time login.
        
        Interactive helper to establish WhatsApp Web session by scanning QR code.
        Session persists for future use.
        
        Note:
            Only needed once. WhatsApp Web remembers your session.
        """
        print("\n" + "=" * 60)
        print("       WhatsApp Web Login Helper (Enhanced v2)")
        print("=" * 60)
        print("\n📱 SETUP INSTRUCTIONS:")
        print("\n1. Browser window will open (web.whatsapp.com)")
        print("2. On your phone, open WhatsApp")
        print("3. Go to: Settings > Linked Devices")
        print("4. Tap 'Link a Device'")
        print("5. Scan the QR code shown in browser")
        print("\n6. Wait for all chats to load completely")
        print("7. Close this terminal when ready\n")
        print("=" * 60)
        print("\n⏳ Opening browser in 3 seconds...\n")
        
        time.sleep(3)
        webbrowser.open("https://web.whatsapp.com")
        logger.info("Opened WhatsApp Web for login")
        print("✅ Browser opened. Complete the QR scan on your phone.")
    
    def _press_enter_to_send(self) -> None:
        """
        Press Enter key to send message using pyautogui.
        
        Improves reliability by automating the send action.
        Fails gracefully if pyautogui unavailable.
        """
        try:
            import pyautogui
            
            # Wait for message to be typed in text box
            time.sleep(2)
            
            # Press Enter to send
            pyautogui.press('enter')
            logger.debug("Auto-pressed Enter key")
            
        except ImportError:
            logger.debug(
                "pyautogui not available. Message may require manual Enter press."
            )
        except Exception as e:
            logger.warning(f"Auto-send with pyautogui failed: {e}")
    
    def split_long_message(
        self, 
        message: str, 
        chunk_size: int = 4000
    ) -> List[str]:
        """
        Split long message into chunks for WhatsApp.
        
        Args:
            message: Long message text
            chunk_size: Characters per chunk (default 4000, max 4096)
        
        Returns:
            List of message chunks
        
        Example:
            >>> chunks = sender.split_long_message(very_long_text)
            >>> for chunk in chunks:
            ...     sender.send_message(chunk)
        """
        chunk_size = min(4096, max(100, chunk_size))
        
        if len(message) <= chunk_size:
            return [message]
        
        chunks = []
        words = message.split()
        current_chunk = []
        current_length = 0
        
        for word in words:
            word_length = len(word) + 1  # +1 for space
            
            if current_length + word_length > chunk_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_length = word_length
            else:
                current_chunk.append(word)
                current_length += word_length
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        logger.info(f"Split message into {len(chunks)} chunks")
        return chunks
    
    def validate_phone_number(self, phone_number: str) -> bool:
        """
        Validate phone number format.
        
        Args:
            phone_number: Phone number to validate
        
        Returns:
            True if valid format, False otherwise
        
        Example:
            >>> sender.validate_phone_number("+923001234567")
            True
            >>> sender.validate_phone_number("123")
            False
        """
        try:
            self._normalize_phone_number(phone_number)
            return True
        except (ValueError, TypeError):
            return False
    
    def clear_history(self) -> None:
        """Clear message history."""
        with self._lock:
            self.message_history.clear()
        logger.info("Message history cleared")


if __name__ == "__main__":
    import sys
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-8s | %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )
    
    try:
        print("\n" + "=" * 70)
        print(" WhatsApp Sender v2.0 - Interactive Test Tool")
        print("=" * 70)
        
        # Get phone number
        phone = input("\n📱 Enter phone number (with country code, e.g., +923001234567): ").strip()
        
        if not phone:
            raise ValueError("Phone number is required")
        
        # Initialize sender
        sender = WhatsAppSender(
            phone_number=phone,
            max_retries=3,
            enable_rate_limiting=True
        )
        
        print(f"\n✅ Sender initialized for: {sender.phone_number}\n")
        print("Options:")
        print("  1: Login to WhatsApp Web (first time setup)")
        print("  2: Send test message")
        print("  3: Validate phone number")
        print("  4: View statistics")
        print("  5: Exit\n")
        
        while True:
            choice = input("Enter choice (1-5): ").strip()
            
            if choice == "1":
                WhatsAppSender.login_whatsapp()
                input("\nPress Enter after scanning QR code...")
                
            elif choice == "2":
                msg = input("\n📝 Enter message to send: ").strip()
                if msg:
                    result = sender.send_message(msg)
                    print(f"\n{'✅ SENT' if result.status == SendStatus.SENT else '❌ FAILED'}")
                    if result.last_error:
                        print(f"Error: {result.last_error}")
                else:
                    print("❌ Message cannot be empty")
            
            elif choice == "3":
                test_num = input("\n📞 Enter phone to validate: ").strip()
                is_valid = sender.validate_phone_number(test_num)
                print(f"Result: {'✅ Valid' if is_valid else '❌ Invalid'}")
            
            elif choice == "4":
                stats = sender.get_send_statistics()
                print(f"\n📊 Statistics:")
                print(f"  Total: {stats['total_messages']}")
                print(f"  Sent: {stats['sent_count']}")
                print(f"  Failed: {stats['failed_count']}")
                print(f"  Success Rate: {stats['success_rate']:.1f}%")
            
            elif choice == "5":
                print("\nGoodbye!")
                break
            
            else:
                print("❌ Invalid choice. Please try again.")
    
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        logger.exception("Unexpected error in main")
        sys.exit(1)
