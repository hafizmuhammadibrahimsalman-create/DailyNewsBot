#!/usr/bin/env python3
"""
Test script to send a WhatsApp message
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from whatsapp_sender import WhatsAppSender

def test_whatsapp():
    print("=" * 60)
    print("📱 WhatsApp Test Message Sender")
    print("=" * 60)
    print()
    print("This will:")
    print("1. Open WhatsApp Web in your browser")
    print("2. Send a test message to your number")
    print()
    print("⚠️  IMPORTANT:")
    print("- If this is your FIRST time, you'll need to:")
    print("  • Open WhatsApp on your phone")
    print("  • Go to: Settings → Linked Devices")
    print("  • Click 'Link a Device'")
    print("  • Scan the QR code that appears in the browser")
    print()
    input("Press Enter when ready...")
    
    # Create test message
    test_message = """
🧪 **WhatsApp Test Message**

This is a test from your DailyNewsBot system!

If you received this, WhatsApp delivery is working correctly! ✅

Next step: Run the full bot to get daily news reports.
"""
    
    try:
        sender = WhatsAppSender()
        result = sender.send_message(test_message)
        
        if result:
            print("\n✅ TEST SUCCESSFUL!")
            print("   Check your WhatsApp - you should receive the message shortly.")
        else:
            print("\n❌ TEST FAILED")
            print("   Please check if you scanned the QR code correctly.")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure WhatsApp is installed on your phone")
        print("2. Make sure you have internet connection")
        print("3. Try scanning the QR code again")

if __name__ == "__main__":
    test_whatsapp()
