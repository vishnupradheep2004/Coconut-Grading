"""
utils/database.py
Database management for Coconut Grading AI
Stores analysis results, user data, and history using SQLite
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import json


class Database:
    """SQLite database manager for Coconut Grading AI"""
    
    def __init__(self, db_path: Path):
        """Initialize database connection"""
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT,
                role TEXT DEFAULT 'farmer',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Analysis results table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_results (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                filename TEXT NOT NULL,
                total_coconuts INTEGER,
                dry_count INTEGER,
                green_count INTEGER,
                tender_count INTEGER,
                grade TEXT,
                avg_confidence REAL,
                total_value REAL,
                market_rates TEXT,
                analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Batch processing history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS batch_history (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                batch_name TEXT,
                image_count INTEGER,
                total_coconuts INTEGER,
                batch_grade TEXT,
                total_batch_value REAL,
                processing_time REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_settings (
                id INTEGER PRIMARY KEY,
                user_id INTEGER UNIQUE,
                market_rate_dry REAL DEFAULT 50.0,
                market_rate_green REAL DEFAULT 35.0,
                market_rate_tender REAL DEFAULT 25.0,
                confidence_threshold REAL DEFAULT 0.25,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def create_user(self, username: str, password_hash: str, email: str, role: str = "farmer") -> int:
        """Create a new user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO users (username, password_hash, email, role)
                VALUES (?, ?, ?, ?)
            """, (username, password_hash, email, role))
            
            conn.commit()
            user_id = cursor.lastrowid
            
            # Create default settings
            cursor.execute("""
                INSERT INTO user_settings (user_id)
                VALUES (?)
            """, (user_id,))
            conn.commit()
            
            return user_id
        finally:
            conn.close()
    
    def get_user(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
    
    def save_analysis_result(self, user_id: int, filename: str, counts: Dict, 
                            grade: str, confidence: float, total_value: float, 
                            market_rates: Dict) -> int:
        """Save analysis result to database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO analysis_results 
                (user_id, filename, total_coconuts, dry_count, green_count, tender_count, 
                 grade, avg_confidence, total_value, market_rates)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                filename,
                sum(counts.values()),
                counts.get("dry", 0),
                counts.get("green", 0),
                counts.get("tender", 0),
                grade,
                confidence,
                total_value,
                json.dumps(market_rates)
            ))
            
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    
    def get_user_results(self, user_id: int, limit: int = 50) -> List[Dict]:
        """Get user's analysis results"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT * FROM analysis_results 
                WHERE user_id = ? 
                ORDER BY analysis_date DESC 
                LIMIT ?
            """, (user_id, limit))
            
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def save_batch_result(self, user_id: int, batch_name: str, image_count: int,
                         total_coconuts: int, batch_grade: str, 
                         total_value: float, processing_time: float) -> int:
        """Save batch processing result"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO batch_history 
                (user_id, batch_name, image_count, total_coconuts, batch_grade, 
                 total_batch_value, processing_time)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, batch_name, image_count, total_coconuts, batch_grade, total_value, processing_time))
            
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    
    def update_user_settings(self, user_id: int, settings: Dict) -> bool:
        """Update user settings"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE user_settings 
                SET market_rate_dry = ?, 
                    market_rate_green = ?, 
                    market_rate_tender = ?,
                    confidence_threshold = ?
                WHERE user_id = ?
            """, (
                settings.get("dry_rate", 50.0),
                settings.get("green_rate", 35.0),
                settings.get("tender_rate", 25.0),
                settings.get("confidence", 0.25),
                user_id
            ))
            
            conn.commit()
            return True
        finally:
            conn.close()
    
    def get_user_statistics(self, user_id: int) -> Dict:
        """Get user statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_analyses,
                    SUM(total_coconuts) as total_coconuts_analyzed,
                    AVG(total_value) as avg_batch_value,
                    SUM(total_value) as total_value
                FROM analysis_results 
                WHERE user_id = ?
            """, (user_id,))
            
            row = cursor.fetchone()
            return dict(row) if row else {}
        finally:
            conn.close()
