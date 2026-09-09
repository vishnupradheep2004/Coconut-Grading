"""
utils/auth.py
Authentication and login management for Coconut Grading AI
Handles user registration, login, and session management
"""

import bcrypt
from datetime import datetime, timedelta
from typing import Tuple, Optional, Dict
import secrets


class AuthManager:
    """Manages user authentication and sessions"""
    
    def __init__(self, database, session_timeout_minutes: int = 60):
        """Initialize authentication manager"""
        self.db = database
        self.session_timeout = timedelta(minutes=session_timeout_minutes)
        self.sessions = {}  # In-memory session storage
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify password against bcrypt hash"""
        return bcrypt.checkpw(password.encode(), password_hash.encode())
    
    def register_user(self, username: str, password: str, email: str, role: str = "farmer") -> Tuple[bool, str]:
        """
        Register new user
        
        Args:
            username: Username
            password: Plain text password
            email: Email address
            role: User role ('farmer', 'agent', or 'dealer')
        
        Returns:
            (success, message)
        """
        from .validation import validate_username, validate_password, validate_email
        
        # Validate inputs
        valid_user, msg = validate_username(username)
        if not valid_user:
            return False, msg
        
        valid_pwd, msg = validate_password(password)
        if not valid_pwd:
            return False, msg
        
        valid_email, msg = validate_email(email)
        if not valid_email:
            return False, msg
        
        # Check if user exists
        if self.db.get_user(username):
            return False, "Username already exists"
        
        # Create user
        try:
            password_hash = self.hash_password(password)
            user_id = self.db.create_user(username, password_hash, email, role)
            return True, f"User '{username}' registered successfully"
        except Exception as e:
            return False, f"Registration failed: {str(e)}"
    
    def login(self, username: str, password: str) -> Tuple[bool, str, Optional[str]]:
        """
        Authenticate user and create session
        
        Args:
            username: Username
            password: Plain text password
        
        Returns:
            (success, message, session_token)
        """
        user = self.db.get_user(username)
        
        if not user:
            return False, "Invalid username or password", None
        
        if not self.verify_password(password, user["password_hash"]):
            return False, "Invalid username or password", None
        
        # Create session
        session_token = secrets.token_hex(32)
        self.sessions[session_token] = {
            "user_id": user["id"],
            "username": user["username"],
            "role": user["role"],
            "created_at": datetime.now(),
            "last_activity": datetime.now()
        }
        
        return True, f"Welcome, {username}!", session_token
    
    def logout(self, session_token: str) -> bool:
        """Logout user by removing session"""
        if session_token in self.sessions:
            del self.sessions[session_token]
            return True
        return False
    
    def validate_session(self, session_token: str) -> Tuple[bool, Optional[Dict]]:
        """
        Validate session token
        
        Returns:
            (is_valid, session_data)
        """
        if session_token not in self.sessions:
            return False, None
        
        session = self.sessions[session_token]
        
        # Check if session expired
        if datetime.now() - session["created_at"] > self.session_timeout:
            del self.sessions[session_token]
            return False, None
        
        # Update last activity
        session["last_activity"] = datetime.now()
        
        return True, session
    
    def get_current_user(self, session_token: str) -> Optional[Dict]:
        """Get current logged-in user info"""
        is_valid, session = self.validate_session(session_token)
        
        if is_valid:
            return {
                "user_id": session["user_id"],
                "username": session["username"],
                "role": session["role"]
            }
        
        return None
    
    def is_authorized(self, session_token: str, required_role: str = None) -> bool:
        """Check if user is authorized (optionally check role)"""
        is_valid, session = self.validate_session(session_token)
        
        if not is_valid:
            return False
        
        if required_role:
            return session["role"] == required_role
        
        return True
    
    def get_user_role(self, session_token: str) -> Optional[str]:
        """Get user role"""
        is_valid, session = self.validate_session(session_token)
        return session["role"] if is_valid else None


# User roles
USER_ROLES = {
    "farmer": {
        "description": "Coconut farmer - Can analyze own batches",
        "permissions": ["analyze", "view_history", "export_reports"]
    },
    "agent": {
        "description": "Authorized agent - Can manage multiple farmers",
        "permissions": ["analyze", "view_history", "export_reports", "manage_farmers"]
    },
    "dealer": {
        "description": "Coconut dealer - Can analyze and price batches",
        "permissions": ["analyze", "view_history", "export_reports", "set_prices", "manage_inventory"]
    },
    "admin": {
        "description": "Administrator - Full access",
        "permissions": ["all"]
    }
}
