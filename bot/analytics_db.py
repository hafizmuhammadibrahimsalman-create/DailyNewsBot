#!/usr/bin/env python3
"""
DailyNewsBot - Analytics Database
==================================
Persistent analytics storage using SQLite.
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import logging
import json

from bot.config import CACHE_DIR
logger = logging.getLogger(__name__)


class AnalyticsDatabase:
    """Persistent analytics storage using SQLite."""
    
    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            db_path = CACHE_DIR / "analytics.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Create tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Runs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    duration_seconds FLOAT,
                    success BOOLEAN,
                    articles_count INTEGER,
                    messages_sent INTEGER DEFAULT 0,
                    error_message TEXT,
                    mode TEXT
                )
            ''')
            
            # Articles table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id INTEGER,
                    topic TEXT,
                    title TEXT,
                    source TEXT,
                    url TEXT,
                    was_included BOOLEAN,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (run_id) REFERENCES runs(id)
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_runs_timestamp ON runs(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_run ON articles(run_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_topic ON articles(topic)')
            
            conn.commit()
    
    def log_run(
        self, 
        duration: float, 
        success: bool, 
        articles_count: int,
        messages_sent: int = 0,
        error_message: str = None,
        mode: str = "live"
    ) -> int:
        """
        Log a bot run.
        
        Returns:
            Run ID for linking articles
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO runs (duration_seconds, success, articles_count, 
                                  messages_sent, error_message, mode)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (duration, success, articles_count, messages_sent, error_message, mode))
            conn.commit()
            
            logger.debug(f"Logged run {cursor.lastrowid}: {articles_count} articles, {duration:.1f}s")
            return cursor.lastrowid
    
    def log_articles(
        self, 
        run_id: int, 
        topic: str, 
        articles: List[Dict],
        included_indices: List[int] = None
    ):
        """Log articles from a run."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for idx, article in enumerate(articles):
                was_included = included_indices is None or idx in included_indices
                cursor.execute('''
                    INSERT INTO articles (run_id, topic, title, source, url, was_included)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    run_id,
                    topic,
                    article.get('title', '')[:500],
                    article.get('source', '')[:100],
                    article.get('url', '')[:500],
                    was_included
                ))
            conn.commit()
    
    def get_statistics(self) -> Dict:
        """Get overall statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_runs,
                    SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful_runs,
                    AVG(CASE WHEN success THEN duration_seconds END) as avg_duration,
                    SUM(articles_count) as total_articles,
                    SUM(messages_sent) as total_messages
                FROM runs
            ''')
            
            row = cursor.fetchone()
            
            success_rate = 0
            if row[0] and row[0] > 0:
                success_rate = (row[1] or 0) / row[0] * 100
            
            return {
                'total_runs': row[0] or 0,
                'successful_runs': row[1] or 0,
                'success_rate': round(success_rate, 1),
                'avg_duration': round(row[2] or 0, 2),
                'total_articles': row[3] or 0,
                'total_messages': row[4] or 0,
            }
    
    def get_recent_runs(self, limit: int = 10) -> List[Dict]:
        """Get recent run history."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, timestamp, duration_seconds, success, 
                       articles_count, messages_sent, mode
                FROM runs
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            
            return [
                {
                    'id': row[0],
                    'timestamp': row[1],
                    'duration': row[2],
                    'success': bool(row[3]),
                    'articles': row[4],
                    'messages': row[5],
                    'mode': row[6]
                }
                for row in cursor.fetchall()
            ]
    
    def get_top_topics(self, limit: int = 5) -> List[Dict]:
        """Get most frequently appearing topics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT topic, COUNT(*) as count, 
                       SUM(CASE WHEN was_included THEN 1 ELSE 0 END) as included_count
                FROM articles
                GROUP BY topic
                ORDER BY count DESC
                LIMIT ?
            ''', (limit,))
            
            return [
                {'topic': row[0], 'count': row[1], 'included': row[2]}
                for row in cursor.fetchall()
            ]


if __name__ == "__main__":
    # Test database
    db = AnalyticsDatabase()
    
    # Log a test run
    run_id = db.log_run(
        duration=15.5,
        success=True,
        articles_count=25,
        messages_sent=1,
        mode="test"
    )
    
    # Log test articles
    db.log_articles(run_id, "ai", [
        {"title": "Test AI Article", "source": "Test", "url": "http://test.com"}
    ])
    
    # Print stats
    print("Statistics:", json.dumps(db.get_statistics(), indent=2))
    print("\nRecent runs:", json.dumps(db.get_recent_runs(5), indent=2))
    print("\nTop topics:", json.dumps(db.get_top_topics(), indent=2))
