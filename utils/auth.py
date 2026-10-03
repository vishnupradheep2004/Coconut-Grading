"""
utils/auth.py
Authentication and login management for Coconut Grading AI
Handles user registration, login, role management, permissions,
and session management.
"""

import bcrypt
from datetime import datetime, timedelta
from typing import Tuple, Optional, Dict
import secrets


class AuthManager:
    """Manages user authentication, roles, permissions, and sessions."""

    def __init__(
        self,
        database,
        session_timeout_minutes: int = 60
    ):
        """Initialize authentication manager."""

        self.db = database

        self.session_timeout = timedelta(
            minutes=session_timeout_minutes
        )

        # In-memory session storage
        self.sessions = {}

    # ============================================================
    # PASSWORD MANAGEMENT
    # ============================================================

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt."""

        return bcrypt.hashpw(
            password.encode(),
            bcrypt.gensalt()
        ).decode()

    @staticmethod
    def verify_password(
        password: str,
        password_hash: str
    ) -> bool:
        """Verify password against bcrypt hash."""

        return bcrypt.checkpw(
            password.encode(),
            password_hash.encode()
        )

    # ============================================================
    # USER REGISTRATION
    # ============================================================

    def register_user(
        self,
        username: str,
        password: str,
        email: str,
        role: str = "farmer"
    ) -> Tuple[bool, str]:
        """
        Register a new public user.

        Public registration supports:
            - farmer
            - agent
            - dealer

        Admin accounts cannot be created through the
        normal registration page.

        Returns:
            (success, message)
        """

        from .validation import (
            validate_username,
            validate_password,
            validate_email
        )

        # --------------------------------------------------------
        # Validate Role
        # --------------------------------------------------------

        allowed_registration_roles = {
            "farmer",
            "agent",
            "dealer"
        }

        if role not in allowed_registration_roles:
            return (
                False,
                "Invalid registration role. "
                "Admin accounts must be created separately."
            )

        # --------------------------------------------------------
        # Validate Username
        # --------------------------------------------------------

        valid_user, msg = validate_username(
            username
        )

        if not valid_user:
            return False, msg

        # --------------------------------------------------------
        # Validate Password
        # --------------------------------------------------------

        valid_pwd, msg = validate_password(
            password
        )

        if not valid_pwd:
            return False, msg

        # --------------------------------------------------------
        # Validate Email
        # --------------------------------------------------------

        valid_email, msg = validate_email(
            email
        )

        if not valid_email:
            return False, msg

        # --------------------------------------------------------
        # Check Existing User
        # --------------------------------------------------------

        if self.db.get_user(username):
            return False, "Username already exists"

        # --------------------------------------------------------
        # Create User
        # --------------------------------------------------------

        try:

            password_hash = self.hash_password(
                password
            )

            user_id = self.db.create_user(
                username,
                password_hash,
                email,
                role
            )

            return (
                True,
                f"User '{username}' registered successfully"
            )

        except Exception as e:

            return (
                False,
                f"Registration failed: {str(e)}"
            )

    # ============================================================
    # ADMIN CREATION
    # ============================================================

    def create_admin_user(
        self,
        username: str,
        password: str,
        email: str
    ) -> Tuple[bool, str]:
        """
        Create an administrator account.

        This method is intentionally separate from the
        public registration flow.

        Admin creation should later be restricted to:
            - initial system setup
            - an existing administrator
            - secure deployment procedure
        """

        from .validation import (
            validate_username,
            validate_password,
            validate_email
        )

        # --------------------------------------------------------
        # Validate Username
        # --------------------------------------------------------

        valid_user, msg = validate_username(
            username
        )

        if not valid_user:
            return False, msg

        # --------------------------------------------------------
        # Validate Password
        # --------------------------------------------------------

        valid_pwd, msg = validate_password(
            password
        )

        if not valid_pwd:
            return False, msg

        # --------------------------------------------------------
        # Validate Email
        # --------------------------------------------------------

        valid_email, msg = validate_email(
            email
        )

        if not valid_email:
            return False, msg

        # --------------------------------------------------------
        # Check Existing User
        # --------------------------------------------------------

        if self.db.get_user(username):
            return False, "Username already exists"

        # --------------------------------------------------------
        # Create Admin
        # --------------------------------------------------------

        try:

            password_hash = self.hash_password(
                password
            )

            self.db.create_user(
                username,
                password_hash,
                email,
                "admin"
            )

            return (
                True,
                f"Administrator '{username}' created successfully"
            )

        except Exception as e:

            return (
                False,
                f"Admin creation failed: {str(e)}"
            )

    # ============================================================
    # LOGIN
    # ============================================================

    def login(
        self,
        username: str,
        password: str
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Authenticate user and create session.

        Returns:
            (success, message, session_token)
        """

        user = self.db.get_user(
            username
        )

        # --------------------------------------------------------
        # User Not Found
        # --------------------------------------------------------

        if not user:

            return (
                False,
                "Invalid username or password",
                None
            )

        # --------------------------------------------------------
        # Password Verification
        # --------------------------------------------------------

        if not self.verify_password(
            password,
            user["password_hash"]
        ):

            return (
                False,
                "Invalid username or password",
                None
            )

        # --------------------------------------------------------
        # Create Session
        # --------------------------------------------------------

        session_token = secrets.token_hex(
            32
        )

        self.sessions[session_token] = {

            "user_id": user["id"],

            "username": user["username"],

            "role": user["role"],

            "created_at": datetime.now(),

            "last_activity": datetime.now()
        }

        return (
            True,
            f"Welcome, {username}!",
            session_token
        )

    # ============================================================
    # LOGOUT
    # ============================================================

    def logout(
        self,
        session_token: str
    ) -> bool:
        """Logout user by removing session."""

        if session_token in self.sessions:

            del self.sessions[
                session_token
            ]

            return True

        return False

    # ============================================================
    # SESSION VALIDATION
    # ============================================================

    def validate_session(
        self,
        session_token: str
    ) -> Tuple[bool, Optional[Dict]]:
        """
        Validate session token.

        Returns:
            (is_valid, session_data)
        """

        if session_token not in self.sessions:

            return False, None

        session = self.sessions[
            session_token
        ]

        # --------------------------------------------------------
        # Check Session Expiry
        # --------------------------------------------------------

        if (
            datetime.now()
            - session["created_at"]
            > self.session_timeout
        ):

            del self.sessions[
                session_token
            ]

            return False, None

        # --------------------------------------------------------
        # Update Last Activity
        # --------------------------------------------------------

        session[
            "last_activity"
        ] = datetime.now()

        return True, session

    # ============================================================
    # CURRENT USER
    # ============================================================

    def get_current_user(
        self,
        session_token: str
    ) -> Optional[Dict]:
        """Get current logged-in user information."""

        is_valid, session = (
            self.validate_session(
                session_token
            )
        )

        if is_valid:

            return {

                "user_id":
                    session["user_id"],

                "username":
                    session["username"],

                "role":
                    session["role"]
            }

        return None

    # ============================================================
    # ROLE AUTHORIZATION
    # ============================================================

    def is_authorized(
        self,
        session_token: str,
        required_role: str = None
    ) -> bool:
        """
        Check whether the current user is authorized.

        If required_role is supplied, the user's role must
        match that role.
        """

        is_valid, session = (
            self.validate_session(
                session_token
            )
        )

        if not is_valid:

            return False

        # --------------------------------------------------------
        # No Specific Role Required
        # --------------------------------------------------------

        if required_role is None:

            return True

        # --------------------------------------------------------
        # Admin Has Access
        # --------------------------------------------------------

        if session["role"] == "admin":

            return True

        # --------------------------------------------------------
        # Check Required Role
        # --------------------------------------------------------

        return (
            session["role"]
            == required_role
        )

    # ============================================================
    # GET USER ROLE
    # ============================================================

    def get_user_role(
        self,
        session_token: str
    ) -> Optional[str]:
        """Get current user's role."""

        is_valid, session = (
            self.validate_session(
                session_token
            )
        )

        if is_valid:

            return session["role"]

        return None

    # ============================================================
    # PERMISSION CHECK
    # ============================================================

    def has_permission(
        self,
        session_token: str,
        permission: str
    ) -> bool:
        """
        Check whether the logged-in user has a
        specific permission.

        Example:

            auth_manager.has_permission(
                token,
                "manage_farmers"
            )
        """

        is_valid, session = (
            self.validate_session(
                session_token
            )
        )

        if not is_valid:

            return False

        role = session.get(
            "role"
        )

        role_data = USER_ROLES.get(
            role,
            {}
        )

        permissions = role_data.get(
            "permissions",
            []
        )

        # Admin has all permissions
        if "all" in permissions:

            return True

        return (
            permission
            in permissions
        )


# ================================================================
# USER ROLES
# ================================================================

USER_ROLES = {

    # ------------------------------------------------------------
    # FARMER
    # ------------------------------------------------------------

    "farmer": {

        "description":
            "Coconut farmer - "
            "Can analyze own batches",

        "permissions": [

            "analyze",

            "view_history",

            "export_reports"

        ]
    },

    # ------------------------------------------------------------
    # AGENT
    # ------------------------------------------------------------

    "agent": {

        "description":
            "Authorized agent - "
            "Can manage multiple farmers",

        "permissions": [

            "analyze",

            "view_history",

            "export_reports",

            "manage_farmers",

            "manage_batches"

        ]
    },

    # ------------------------------------------------------------
    # DEALER
    # ------------------------------------------------------------

    "dealer": {

        "description":
            "Coconut dealer - "
            "Can analyze and price batches",

        "permissions": [

            "analyze",

            "view_history",

            "export_reports",

            "set_prices",

            "manage_inventory",

            "manage_transactions"

        ]
    },

    # ------------------------------------------------------------
    # ADMIN
    # ------------------------------------------------------------

    "admin": {

        "description":
            "Administrator - Full system access",

        "permissions": [

            "all"

        ]
    }
}