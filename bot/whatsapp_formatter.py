#!/usr/bin/env python3
"""
DailyNewsBot - WhatsApp Message Formatter (Enhanced v2)
=======================================================
Format reports for optimal WhatsApp display with improved sanitization,
validation, and customization options.

Features:
- HTML entity and encoding fix
- Character limit enforcement
- Customizable formatting
- Error handling and validation
- Statistics formatting
- Health report formatting
- Emoji support

Author: DailyNewsBot Team
Version: 2.0.0
"""

import logging
import re
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class FormatterConfig:
    """Configuration for message formatter."""
    max_message_length: int = 4096
    max_title_length: int = 100
    max_articles_per_topic: int = 5
    include_emojis: bool = True
    include_timestamp: bool = True
    include_footer: bool = True


class WhatsAppFormatter:
    """
    Enhanced formatter for WhatsApp messages with comprehensive sanitization
    and formatting options.
    
    Handles:
    - HTML entity decoding
    - Character encoding fixes
    - Message truncation
    - Customizable formatting
    - Emoji support
    """
    
    TOPIC_HEADERS = {
        'ai': '🤖 AI & Machine Learning',
        'technology': '💻 Technology',
        'pakistan': '🇵🇰 Pakistan News',
        'politics': '🏛️ Politics',
        'business': '💼 Business',
        'sports': '⚽ Sports',
        'science': '🔬 Science',
        'ijt': '📚 Islami Jamiat Talaba',
        'health': '🏥 Health',
        'entertainment': '🎬 Entertainment',
        'world': '🌍 World News',
    }
    
    # Common HTML entities
    HTML_ENTITIES = {
        '&amp;': '&',
        '&lt;': '<',
        '&gt;': '>',
        '&quot;': '"',
        '&apos;': "'",
        '&nbsp;': ' ',
        '&#039;': "'",
    }
    
    # UTF-8 encoding fixes
    ENCODING_FIXES = {
        'â€™': "'", 'â€˜': "'", 'â€œ': '"', 'â€': '"',
        'â€"': '-', 'â€"': '-', 'â€¦': '...', 'Â': '',
        'Ã©': 'é', 'Ã¡': 'á', 'Ã³': 'ó', 'Ã±': 'ñ',
        'Ã¨': 'è', 'Ã†': 'Æ', 'Â°': '°',
        '\u2018': "'", '\u2019': "'", '\u201c': '"', '\u201d': '"',
        '\u2013': '-', '\u2014': '-', '\u2026': '...',
    }
    
    @classmethod
    def sanitize(cls, text: str, remove_emojis: bool = False) -> str:
        """
        Remove problematic characters and fix encoding issues.
        
        Args:
            text: Text to sanitize
            remove_emojis: Strip emoji characters if True
        
        Returns:
            Sanitized text
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Decode HTML entities
        for entity, char in cls.HTML_ENTITIES.items():
            text = text.replace(entity, char)
        
        # Fix UTF-8 encoding issues
        for bad, good in cls.ENCODING_FIXES.items():
            text = text.replace(bad, good)
        
        # Remove control characters
        text = ''.join(char for char in text if not (ord(char) < 32 and char not in '\n\t\r'))
        
        # Remove emojis if requested
        if remove_emojis:
            # Keep ASCII + common symbols, remove extended unicode
            text = text.encode('ascii', errors='ignore').decode('ascii')
        
        # Clean up excess whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    @classmethod
    def truncate_text(cls, text: str, max_length: int = 100, suffix: str = "...") -> str:
        """
        Truncate text to maximum length.
        
        Args:
            text: Text to truncate
            max_length: Maximum length
            suffix: Suffix to add if truncated
        
        Returns:
            Truncated text
        """
        if len(text) <= max_length:
            return text
        
        available = max_length - len(suffix)
        if available < 0:
            return text[:max_length]
        
        # Try to break at word boundary
        truncated = text[:available].rsplit(' ', 1)[0]
        if len(truncated) > 0:
            return truncated + suffix
        
        return text[:max_length]
    
    @classmethod
    def format_report(
        cls,
        all_news: Dict[str, List[Dict]],
        config: Optional[FormatterConfig] = None
    ) -> str:
        """
        Format intelligence report for WhatsApp.
        
        Args:
            all_news: Dictionary of topic -> list of articles
            config: Optional formatter configuration
        
        Returns:
            Formatted message string
        
        Raises:
            ValueError: If all_news is invalid
        """
        if not isinstance(all_news, dict):
            raise ValueError("all_news must be a dictionary")
        
        config = config or FormatterConfig()
        lines = []
        
        # Header
        lines.append("=" * 40)
        if config.include_emojis:
            lines.append("  📰 DAILY NEWS INTELLIGENCE REPORT")
        else:
            lines.append("  DAILY NEWS INTELLIGENCE REPORT")
        
        if config.include_timestamp:
            lines.append(f"  📅 {datetime.now().strftime('%B %d, %Y')}")
        
        lines.append("=" * 40)
        lines.append("")
        
        # Process each topic
        article_count = 0
        for topic_id, articles in all_news.items():
            if not articles or not isinstance(articles, list):
                continue
            
            topic_name = cls.TOPIC_HEADERS.get(topic_id, topic_id.replace('_', ' ').title())
            lines.append(f"*{topic_name}*")
            
            # Add articles (respect max_articles_per_topic)
            for i, article in enumerate(articles[:config.max_articles_per_topic], 1):
                if not isinstance(article, dict):
                    continue
                
                title = cls.sanitize(article.get('title', 'No title'))
                title = cls.truncate_text(title, config.max_title_length)
                source = cls.sanitize(article.get('source', 'Unknown'))
                
                lines.append(f"  {i}. {title}")
                lines.append(f"     via {source}")
                article_count += 1
            
            lines.append("")
        
        # Footer
        if article_count > 0:
            lines.append("-" * 40)
            lines.append("*Summary*")
            lines.append(f"• Total articles: {article_count}")
            lines.append("• Curated by AI for relevance")
            
            if config.include_footer:
                lines.append("• Updated daily at 9:00 PM")
                lines.append("")
                lines.append("_Powered by DailyNewsBot_")
        else:
            lines.append("_No articles available_")
        
        result = "\n".join(lines)
        
        # Ensure message doesn't exceed limit
        if len(result) > config.max_message_length:
            logger.warning(
                f"Report exceeds {config.max_message_length} chars "
                f"({len(result)} chars). Truncating."
            )
            result = result[:config.max_message_length-3] + "..."
        
        return result
    
    @staticmethod
    def format_summary(stats: Dict) -> str:
        """
        Format statistics summary for WhatsApp.
        
        Args:
            stats: Dictionary with statistics
        
        Returns:
            Formatted statistics message
        """
        if not isinstance(stats, dict):
            return "Invalid statistics data"
        
        total_runs = stats.get('total_runs', 0)
        success_rate = stats.get('success_rate', 0)
        total_articles = stats.get('total_articles', 0)
        total_messages = stats.get('total_messages', 0)
        avg_duration = stats.get('avg_duration', 0)
        
        return f"""📊 *Daily Bot Statistics*

▸ Total Runs: {total_runs}
▸ Success Rate: {success_rate:.1f}%
▸ Articles Processed: {total_articles}
▸ Messages Sent: {total_messages}
▸ Avg Duration: {avg_duration:.1f}s

_Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}_"""
    
    @staticmethod
    def format_error(error: str) -> str:
        """
        Format error notification for WhatsApp.
        
        Args:
            error: Error message
        
        Returns:
            Formatted error message
        """
        if not error:
            error = "Unknown error"
        
        error_text = str(error)[:200]
        
        return f"""⚠️ *Daily News Report Failed*

Error: {error_text}

Please check logs for details.
_Error time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_"""
    
    @staticmethod
    def format_health_report(health: Dict) -> str:
        """
        Format health check results for WhatsApp.
        
        Args:
            health: Health check results dictionary
        
        Returns:
            Formatted health report
        """
        if not isinstance(health, dict):
            return "Invalid health data"
        
        lines = ["🏥 *System Health Report*", ""]
        
        # Add individual checks
        for check_name, result in health.items():
            if check_name == 'summary' or not isinstance(result, dict):
                continue
            
            is_ok = result.get('is_ok', False)
            status = "✅" if is_ok else "⚠️"
            check_display = check_name.replace('_', ' ').title()
            lines.append(f"{status} {check_display}")
            
            # Add details if available
            if 'message' in result:
                lines.append(f"   {result['message']}")
        
        # Add summary
        summary = health.get('summary', {})
        lines.append("")
        if summary.get('all_ok'):
            lines.append("_All systems operational ✅_")
        else:
            lines.append("_Some issues detected - check logs ⚠️_")
        
        return "\n".join(lines)
    
    @staticmethod
    def format_batch_report(batch_results: List[Dict]) -> str:
        """
        Format batch send results.
        
        Args:
            batch_results: List of message send results
        
        Returns:
            Formatted batch report
        """
        if not batch_results:
            return "_No batch results_"
        
        total = len(batch_results)
        sent = sum(1 for r in batch_results if r.get('status') == 'sent')
        failed = sum(1 for r in batch_results if r.get('status') == 'failed')
        
        return f"""📧 *Batch Send Report*

▸ Total: {total}
▸ Sent: {sent} ✅
▸ Failed: {failed} ❌
▸ Success Rate: {(sent/total*100):.1f}%

_Completed at {datetime.now().strftime('%H:%M:%S')}_"""


if __name__ == "__main__":
    import logging
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s'
    )
    
    print("=" * 70)
    print(" WhatsApp Formatter v2.0 - Test Suite")
    print("=" * 70 + "\n")
    
    # Test 1: Basic report formatting
    print("TEST 1: Basic Report Formatting")
    print("-" * 70)
    test_news = {
        "ai": [
            {"title": "OpenAI launches GPT-5 with groundbreaking capabilities", "source": "TechCrunch"},
            {"title": "Google Gemini 2.0 rivals human performance", "source": "The Verge"},
        ],
        "pakistan": [
            {"title": "Islamabad Metro project reaches milestone", "source": "Dawn"},
        ],
        "technology": [
            {"title": "New quantum computer achieves breakthrough", "source": "Nature"},
        ]
    }
    
    formatted = WhatsAppFormatter.format_report(test_news)
    print(formatted)
    print(f"\n✅ Length: {len(formatted)} chars\n")
    
    # Test 2: Sanitization
    print("\nTEST 2: Text Sanitization")
    print("-" * 70)
    dirty_text = "â€œQuote with mojibakeâ€ and â€" dash â€"â€¦ entities"
    clean = WhatsAppFormatter.sanitize(dirty_text)
    print(f"Input:  {repr(dirty_text)}")
    print(f"Output: {repr(clean)}\n")
    
    # Test 3: Truncation
    print("\nTEST 3: Text Truncation")
    print("-" * 70)
    long_title = "This is a very long title that exceeds the maximum length and should be truncated properly"
    truncated = WhatsAppFormatter.truncate_text(long_title, max_length=50)
    print(f"Input ({len(long_title)} chars):  {long_title}")
    print(f"Output ({len(truncated)} chars): {truncated}\n")
    
    # Test 4: Statistics
    print("\nTEST 4: Statistics Formatting")
    print("-" * 70)
    stats = {
        'total_runs': 30,
        'success_rate': 96.7,
        'total_articles': 450,
        'total_messages': 27,
        'avg_duration': 45.3
    }
    print(WhatsAppFormatter.format_summary(stats))
    print()
    
    # Test 5: Error formatting
    print("\nTEST 5: Error Formatting")
    print("-" * 70)
    print(WhatsAppFormatter.format_error("API timeout after 30 seconds"))
    print()
    
    # Test 6: Health report
    print("\nTEST 6: Health Report Formatting")
    print("-" * 70)
    health = {
        'database': {'is_ok': True, 'message': 'Connected'},
        'api': {'is_ok': False, 'message': 'Rate limited'},
        'whatsapp': {'is_ok': True, 'message': 'Session active'},
        'summary': {'all_ok': False}
    }
    print(WhatsAppFormatter.format_health_report(health))
    print()
    
    # Test 7: Batch report
    print("\nTEST 7: Batch Report Formatting")
    print("-" * 70)
    batch_results = [
        {'status': 'sent'},
        {'status': 'sent'},
        {'status': 'failed'},
        {'status': 'sent'},
    ]
    print(WhatsAppFormatter.format_batch_report(batch_results))
    print("\n" + "=" * 70)
    print("✅ All tests completed successfully!")
    print("=" * 70)
