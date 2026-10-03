"""
utils/database.py
Database management for Coconut Grading AI
Stores analysis results, user data, role profiles, batches,
transactions, and history using SQLite.
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

        # ============================================================
        # USERS TABLE
        # ============================================================

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

        # ============================================================
        # ANALYSIS RESULTS TABLE
        # ============================================================

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

        # ============================================================
        # BATCH PROCESSING HISTORY TABLE
        # ============================================================

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

        # ============================================================
        # USER SETTINGS TABLE
        # ============================================================

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

        # ============================================================
        # PHASE 1 - FARMER PROFILE
        # ============================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS farmer_profiles (
                id INTEGER PRIMARY KEY,
                user_id INTEGER UNIQUE NOT NULL,
                farm_name TEXT,
                farm_location TEXT,
                total_area REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        # ============================================================
        # PHASE 1 - AGENT PROFILE
        # ============================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_profiles (
                id INTEGER PRIMARY KEY,
                user_id INTEGER UNIQUE NOT NULL,
                agent_code TEXT UNIQUE,
                service_area TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        # ============================================================
        # PHASE 1 - DEALER PROFILE
        # ============================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dealer_profiles (
                id INTEGER PRIMARY KEY,
                user_id INTEGER UNIQUE NOT NULL,
                dealer_code TEXT UNIQUE,
                business_name TEXT,
                business_location TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        # ============================================================
        # PHASE 1 - COCONUT BATCHES
        # ============================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS coconut_batches (
                id INTEGER PRIMARY KEY,
                created_by INTEGER NOT NULL,
                farmer_id INTEGER,
                agent_id INTEGER,
                batch_name TEXT NOT NULL,
                total_coconuts INTEGER DEFAULT 0,
                dry_count INTEGER DEFAULT 0,
                green_count INTEGER DEFAULT 0,
                tender_count INTEGER DEFAULT 0,
                estimated_value REAL DEFAULT 0,
                status TEXT DEFAULT 'created',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (created_by)
                    REFERENCES users(id),

                FOREIGN KEY (farmer_id)
                    REFERENCES farmer_profiles(id),

                FOREIGN KEY (agent_id)
                    REFERENCES agent_profiles(id)
            )
        """)

        # ============================================================
        # PHASE 1 - DEALER TRANSACTIONS
        # ============================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY,
                dealer_id INTEGER NOT NULL,
                batch_id INTEGER,
                transaction_type TEXT NOT NULL,
                quantity INTEGER DEFAULT 0,
                dry_count INTEGER DEFAULT 0,
                green_count INTEGER DEFAULT 0,
                tender_count INTEGER DEFAULT 0,
                total_amount REAL DEFAULT 0,
                price_per_coconut REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (dealer_id)
                    REFERENCES dealer_profiles(id),

                FOREIGN KEY (batch_id)
                    REFERENCES coconut_batches(id)
            )
        """)

        conn.commit()
        conn.close()

    # ================================================================
    # USER MANAGEMENT
    # ================================================================

    def create_user(
        self,
        username: str,
        password_hash: str,
        email: str,
        role: str = "farmer"
    ) -> int:
        """Create a new user"""

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO users
                (username, password_hash, email, role)
                VALUES (?, ?, ?, ?)
            """, (
                username,
                password_hash,
                email,
                role
            ))

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
            cursor.execute(
                "SELECT * FROM users WHERE username = ?",
                (username,)
            )

            row = cursor.fetchone()

            return dict(row) if row else None

        finally:
            conn.close()

    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT * FROM users WHERE id = ?",
                (user_id,)
            )

            row = cursor.fetchone()

            return dict(row) if row else None

        finally:
            conn.close()

    def get_users_by_role(self, role: str) -> List[Dict]:
        """Get all users belonging to a specific role"""

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT *
                FROM users
                WHERE role = ?
                ORDER BY created_at DESC
            """, (role,))

            return [dict(row) for row in cursor.fetchall()]

        finally:
            conn.close()

    # ================================================================
    # ANALYSIS RESULTS
    # ================================================================

    def save_analysis_result(
        self,
        user_id: int,
        filename: str,
        counts: Dict,
        grade: str,
        confidence: float,
        total_value: float,
        market_rates: Dict
    ) -> int:
        """Save analysis result to database"""

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO analysis_results
                (
                    user_id,
                    filename,
                    total_coconuts,
                    dry_count,
                    green_count,
                    tender_count,
                    grade,
                    avg_confidence,
                    total_value,
                    market_rates
                )
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

    def get_user_results(
        self,
        user_id: int,
        limit: int = 50
    ) -> List[Dict]:
        """Get user's analysis results"""

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT *
                FROM analysis_results
                WHERE user_id = ?
                ORDER BY analysis_date DESC
                LIMIT ?
            """, (
                user_id,
                limit
            ))

            return [dict(row) for row in cursor.fetchall()]

        finally:
            conn.close()

    # ================================================================
    # BATCH HISTORY
    # ================================================================

    def save_batch_result(
        self,
        user_id: int,
        batch_name: str,
        image_count: int,
        total_coconuts: int,
        batch_grade: str,
        total_value: float,
        processing_time: float
    ) -> int:
        """Save batch processing result"""

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO batch_history
                (
                    user_id,
                    batch_name,
                    image_count,
                    total_coconuts,
                    batch_grade,
                    total_batch_value,
                    processing_time
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                batch_name,
                image_count,
                total_coconuts,
                batch_grade,
                total_value,
                processing_time
            ))

            conn.commit()

            return cursor.lastrowid

        finally:
            conn.close()

    # ================================================================
    # USER SETTINGS
    # ================================================================

    def update_user_settings(
        self,
        user_id: int,
        settings: Dict
    ) -> bool:
        """Update user settings"""

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                UPDATE user_settings
                SET market_rate_dry = ?,
                    market_rate_green = ?,
                    market_rate_tender = ?,
                    confidence_threshold = ?,
                    updated_at = CURRENT_TIMESTAMP
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

    def get_user_settings(self, user_id: int) -> Dict:
        """Get user settings"""

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT *
                FROM user_settings
                WHERE user_id = ?
            """, (user_id,))

            row = cursor.fetchone()

            return dict(row) if row else {}

        finally:
            conn.close()

    # ================================================================
    # FARMER PROFILE
    # ================================================================

    def create_farmer_profile(
        self,
        user_id: int,
        farm_name: str = "",
        farm_location: str = "",
        total_area: float = 0
    ) -> int:
        """Create farmer profile"""

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO farmer_profiles
                (
                    user_id,
                    farm_name,
                    farm_location,
                    total_area
                )
                VALUES (?, ?, ?, ?)
            """, (
                user_id,
                farm_name,
                farm_location,
                total_area
            ))

            conn.commit()

            return cursor.lastrowid

        finally:
            conn.close()

    def get_farmer_profile(
        self,
        user_id: int
    ) -> Optional[Dict]:
        """Get farmer profile"""

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT *
                FROM farmer_profiles
                WHERE user_id = ?
            """, (user_id,))

            row = cursor.fetchone()

            return dict(row) if row else None

        finally:
            conn.close()

    # ================================================================
    # AGENT PROFILE
    # ================================================================

    def create_agent_profile(
        self,
        user_id: int,
        agent_code: str = "",
        service_area: str = ""
    ) -> int:
        """Create agent profile"""

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO agent_profiles
                (
                    user_id,
                    agent_code,
                    service_area
                )
                VALUES (?, ?, ?)
            """, (
                user_id,
                agent_code,
                service_area
            ))

            conn.commit()

            return cursor.lastrowid

        finally:
            conn.close()

    def get_agent_profile(
        self,
        user_id: int
    ) -> Optional[Dict]:
        """Get agent profile"""

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT *
                FROM agent_profiles
                WHERE user_id = ?
            """, (user_id,))

            row = cursor.fetchone()

            return dict(row) if row else None

        finally:
            conn.close()

    # ================================================================
    # DEALER PROFILE
    # ================================================================

    def create_dealer_profile(
        self,
        user_id: int,
        dealer_code: str = "",
        business_name: str = "",
        business_location: str = ""
    ) -> int:
        """Create dealer profile"""

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO dealer_profiles
                (
                    user_id,
                    dealer_code,
                    business_name,
                    business_location
                )
                VALUES (?, ?, ?, ?)
            """, (
                user_id,
                dealer_code,
                business_name,
                business_location
            ))

            conn.commit()

            return cursor.lastrowid

        finally:
            conn.close()

    def get_dealer_profile(
        self,
        user_id: int
    ) -> Optional[Dict]:
        """Get dealer profile"""

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT *
                FROM dealer_profiles
                WHERE user_id = ?
            """, (user_id,))

            row = cursor.fetchone()

            return dict(row) if row else None

        finally:
            conn.close()

    # ================================================================
    # COCONUT BATCH MANAGEMENT
    # ================================================================

    def create_coconut_batch(
        self,
        created_by: int,
        batch_name: str,
        farmer_id: Optional[int] = None,
        agent_id: Optional[int] = None,
        total_coconuts: int = 0,
        dry_count: int = 0,
        green_count: int = 0,
        tender_count: int = 0,
        estimated_value: float = 0,
        status: str = "created"
    ) -> int:
        """Create a coconut batch"""

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO coconut_batches
                (
                    created_by,
                    farmer_id,
                    agent_id,
                    batch_name,
                    total_coconuts,
                    dry_count,
                    green_count,
                    tender_count,
                    estimated_value,
                    status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                created_by,
                farmer_id,
                agent_id,
                batch_name,
                total_coconuts,
                dry_count,
                green_count,
                tender_count,
                estimated_value,
                status
            ))

            conn.commit()

            return cursor.lastrowid

        finally:
            conn.close()

    def get_batches(
        self,
        user_id: Optional[int] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Get coconut batches"""

        conn = self.get_connection()
        cursor = conn.cursor()

        try:

            if user_id is not None:

                cursor.execute("""
                    SELECT *
                    FROM coconut_batches
                    WHERE created_by = ?
                       OR farmer_id IN (
                           SELECT id
                           FROM farmer_profiles
                           WHERE user_id = ?
                       )
                       OR agent_id IN (
                           SELECT id
                           FROM agent_profiles
                           WHERE user_id = ?
                       )
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (
                    user_id,
                    user_id,
                    user_id,
                    limit
                ))

            else:

                cursor.execute("""
                    SELECT *
                    FROM coconut_batches
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (limit,))

            return [dict(row) for row in cursor.fetchall()]

        finally:
            conn.close()

    def get_batch(
        self,
        batch_id: int
    ) -> Optional[Dict]:
        """Get a single coconut batch"""

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT *
                FROM coconut_batches
                WHERE id = ?
            """, (batch_id,))

            row = cursor.fetchone()

            return dict(row) if row else None

        finally:
            conn.close()

    # ================================================================
    # DEALER TRANSACTIONS
    # ================================================================

    def create_transaction(
        self,
        dealer_id: int,
        transaction_type: str,
        batch_id: Optional[int] = None,
        quantity: int = 0,
        dry_count: int = 0,
        green_count: int = 0,
        tender_count: int = 0,
        total_amount: float = 0,
        price_per_coconut: float = 0
    ) -> int:
        """Create dealer transaction"""

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO transactions
                (
                    dealer_id,
                    batch_id,
                    transaction_type,
                    quantity,
                    dry_count,
                    green_count,
                    tender_count,
                    total_amount,
                    price_per_coconut
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                dealer_id,
                batch_id,
                transaction_type,
                quantity,
                dry_count,
                green_count,
                tender_count,
                total_amount,
                price_per_coconut
            ))

            conn.commit()

            return cursor.lastrowid

        finally:
            conn.close()

    def get_dealer_transactions(
        self,
        dealer_id: int,
        limit: int = 100
    ) -> List[Dict]:
        """Get dealer transactions"""

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT *
                FROM transactions
                WHERE dealer_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (
                dealer_id,
                limit
            ))

            return [dict(row) for row in cursor.fetchall()]

        finally:
            conn.close()

    # ================================================================
    # USER STATISTICS
    # ================================================================

    def get_user_statistics(
        self,
        user_id: int
    ) -> Dict:
        """Get user statistics"""

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT
                    COUNT(*) as total_analyses,
                    COALESCE(SUM(total_coconuts), 0)
                        as total_coconuts_analyzed,
                    COALESCE(AVG(total_value), 0)
                        as avg_batch_value,
                    COALESCE(SUM(total_value), 0)
                        as total_value
                FROM analysis_results
                WHERE user_id = ?
            """, (user_id,))

            row = cursor.fetchone()

            return dict(row) if row else {}

        finally:
            conn.close()