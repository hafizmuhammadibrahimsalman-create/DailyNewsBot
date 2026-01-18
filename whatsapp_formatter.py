#!/usr/bin/env python3
"""
DailyNewsBot - WhatsApp Message Formatter
==========================================
Format reports for optimal WhatsApp display.
"""

from datetime import datetime
from typing import Dict, List


class WhatsAppFormatter:
    """Format reports for better WhatsApp display."""
    
    TOPIC_HEADERS = {
        'ai': 'AI & Machine Learning',
        'technology': 'Technology',
        'pakistan': 'Pakistan News',
        'politics': 'Politics',
        'business': 'Business',
        'sports': 'Sports',
        'science': 'Science',
        'ijt': 'Islami Jamiat Talaba',
    }
    
    @staticmethod
    def sanitize(text: str) -> str:
        """Remove problematic characters for console/WhatsApp."""
        if not text:
            return text
        
        # Fix common mojibake
        fixes = {
            'â€™': "'", 'â€˜': "'", 'â€œ': '"', 'â€': '"',
            'â€"': '-', 'â€"': '-', 'â€¦': '...', 'Â': '',
            '\u2018': "'", '\u2019': "'", '\u201c': '"', '\u201d': '"',
            '\u2013': '-', '\u2014': '-', '\u2026': '...',
        }
        for bad, good in fixes.items():
            text = text.replace(bad, good)
        
        return text.encode('ascii', errors='ignore').decode('ascii')
    
    @classmethod
    def format_report(cls, all_news: Dict[str, List[Dict]]) -> str:
        """
        Format intelligence report for WhatsApp.
        
        Args:
            all_news: Dictionary of topic -> list of articles
        
        Returns:
            Formatted message string
        """
        lines = []
        
        # Header
        lines.append("=" * 35)
        lines.append("  DAILY NEWS INTELLIGENCE REPORT")
        lines.append(f"  {datetime.now().strftime('%B %d, %Y')}")
        lines.append("=" * 35)
        lines.append("")
        
        # Topics
        for topic_id, articles in all_news.items():
            if not articles:
                continue
            
            topic_name = cls.TOPIC_HEADERS.get(topic_id, topic_id.replace('_', ' ').title())
            
            lines.append(f"*{topic_name}*")
            
            for i, article in enumerate(articles[:3], 1):
                title = cls.sanitize(article.get('title', 'No title'))
                # Truncate title
                if len(title) > 70:
                    title = title[:67] + "..."
                
                source = article.get('source', 'Unknown')
                lines.append(f"  {i}. {title}")
                lines.append(f"     _via {source}_")
            
            lines.append("")
        
        # Footer
        lines.append("-" * 35)
        lines.append("*Key Insights*")
        lines.append("* Curated by AI for relevance")
        lines.append("* Updated daily at 9:00 PM")
        lines.append("")
        lines.append("_Powered by DailyNewsBot_")
        
        return "\n".join(lines)
    
    @staticmethod
    def format_summary(stats: Dict) -> str:
        """Format statistics summary."""
        return f"""
*Daily Bot Statistics*

Total Runs: {stats.get('total_runs', 0)}
Success Rate: {stats.get('success_rate', 0)}%
Articles Processed: {stats.get('total_articles', 0)}
Messages Sent: {stats.get('total_messages', 0)}
Avg Duration: {stats.get('avg_duration', 0)}s

_Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}_
"""
    
    @staticmethod
    def format_error(error: str) -> str:
        """Format error notification."""
        return f"""
*[!] Daily News Report Failed*

Error: {error[:200]}

Please check logs for details.
_Error time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_
"""
    
    @staticmethod
    def format_health_report(health: Dict) -> str:
        """Format health check results."""
        lines = ["*System Health Report*", ""]
        
        for check_name, result in health.items():
            if check_name == 'summary':
                continue
            if isinstance(result, dict):
                status = "[OK]" if result.get('is_ok') else "[!]"
                lines.append(f"{status} {check_name.replace('_', ' ').title()}")
        
        summary = health.get('summary', {})
        if summary.get('all_ok'):
            lines.append("\n_All systems operational_")
        else:
            lines.append("\n_Some issues detected - check logs_")
        
        return "\n".join(lines)


if __name__ == "__main__":
    # Test formatting
    test_news = {
        "ai": [
            {"title": "OpenAI launches GPT-5 with groundbreaking capabilities", "source": "TechCrunch"},
            {"title": "Google Gemini 2.0 rivals human performance", "source": "The Verge"},
        ],
        "pakistan": [
            {"title": "Islamabad Metro project reaches milestone", "source": "Dawn"},
        ]
    }
    
    formatted = WhatsAppFormatter.format_report(test_news)
    print(formatted)
