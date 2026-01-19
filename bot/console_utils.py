# Console Utilities for Windows Encoding Safety
# This module provides safe print functions that handle encoding errors gracefully.

import sys
import os

def setup_console():
    """Configure console for maximum encoding compatibility."""
    if sys.platform == 'win32':
        # Set console to UTF-8 mode
        os.system('chcp 65001 > nul 2>&1')
        
        # Reconfigure stdout/stderr with error handling
        try:
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
        except AttributeError:
            # Python < 3.7
            import io
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def safe_print(*args, **kwargs):
    """Print that replaces problematic characters instead of crashing."""
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        # Convert to string and replace unencodable characters
        text = ' '.join(str(a) for a in args)
        safe_text = text.encode('ascii', errors='replace').decode('ascii')
        print(safe_text, **kwargs)

def sanitize_text(text: str) -> str:
    """Remove/replace all non-ASCII characters from text."""
    if not text:
        return text
    # Replace common emojis with text equivalents
    replacements = {
        '✅': '[OK]', '❌': '[ERR]', '⚠️': '[WARN]', '⚠': '[WARN]',
        '🚀': '[>>]', '📰': '[NEWS]', '🤖': '[AI]', '📊': '[DATA]',
        '💥': '[!]', '⛔': '[BLOCK]', '🧹': '[CLEAN]', '🔍': '[>>]',
        '📱': '[MSG]', '🔸': '[*]', '⏹️': '[STOP]', '🔥': '[!]',
        '⚡': '[*]', 'ℹ️': '[INFO]', '🎬': '[>>]', '📅': '[DATE]',
        '📚': '', '💻': '', '🇵🇰': '', '🏛️': '', '💼': '', '⚽': '',
        '🔬': '', '🧠': '[AI]', '🎯': '[KEY]', '🔒': '[OK]',
    }
    for emoji, replacement in replacements.items():
        text = text.replace(emoji, replacement)
    
    # Remove any remaining non-ASCII characters
    return text.encode('ascii', errors='ignore').decode('ascii')

# Auto-configure on import
setup_console()
