"""
utils/api.py
REST API utilities for Coconut Grading AI
Provides API endpoints for integration with external systems
Built with Flask as base structure (use Flask-CORS, Flask-JWT for full implementation)
"""

from typing import Dict, Any, Tuple
from datetime import datetime
import json


class APIResponse:
    """Standard API response format"""
    
    @staticmethod
    def success(data: Any = None, message: str = "Success", status_code: int = 200) -> Tuple[Dict, int]:
        """
        Generate success response
        
        Args:
            data: Response data
            message: Success message
            status_code: HTTP status code
        
        Returns:
            (response_dict, status_code)
        """
        return {
            "status": "success",
            "message": message,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }, status_code
    
    @staticmethod
    def error(error: str, details: str = "", status_code: int = 400) -> Tuple[Dict, int]:
        """
        Generate error response
        
        Args:
            error: Error message
            details: Additional error details
            status_code: HTTP status code
        
        Returns:
            (response_dict, status_code)
        """
        return {
            "status": "error",
            "error": error,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }, status_code
    
    @staticmethod
    def validation_error(field: str, message: str) -> Tuple[Dict, int]:
        """Generate validation error response"""
        return {
            "status": "error",
            "error": "Validation failed",
            "field": field,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }, 422


class APIEndpoints:
    """API endpoint definitions and documentation"""
    
    ENDPOINTS = {
        "auth": {
            "POST /api/auth/register": {
                "description": "Register new user",
                "body": {"username": str, "password": str, "email": str, "role": str},
                "response": {"user_id": int, "username": str}
            },
            "POST /api/auth/login": {
                "description": "Login user",
                "body": {"username": str, "password": str},
                "response": {"session_token": str, "user": dict}
            },
            "POST /api/auth/logout": {
                "description": "Logout user",
                "headers": {"Authorization": "Bearer <token>"},
                "response": {"message": str}
            }
        },
        "analysis": {
            "POST /api/analysis/single": {
                "description": "Analyze single image",
                "body": {"image": "base64", "confidence_threshold": float},
                "headers": {"Authorization": "Bearer <token>"},
                "response": {"counts": dict, "grade": str, "value": float}
            },
            "POST /api/analysis/batch": {
                "description": "Batch process multiple images",
                "body": {"images": [str], "batch_name": str},
                "headers": {"Authorization": "Bearer <token>"},
                "response": {"batch_id": str, "results": list}
            },
            "GET /api/analysis/history": {
                "description": "Get user analysis history",
                "headers": {"Authorization": "Bearer <token>"},
                "params": {"limit": int, "offset": int},
                "response": {"results": list, "total": int}
            }
        },
        "export": {
            "GET /api/export/report/<result_id>": {
                "description": "Export analysis as PDF/CSV",
                "headers": {"Authorization": "Bearer <token>"},
                "params": {"format": "pdf|csv"},
                "response": "File download"
            },
            "POST /api/export/batch": {
                "description": "Export batch results",
                "body": {"batch_id": str, "format": str},
                "headers": {"Authorization": "Bearer <token>"},
                "response": "File download"
            }
        },
        "stats": {
            "GET /api/stats/dashboard": {
                "description": "Get user dashboard statistics",
                "headers": {"Authorization": "Bearer <token>"},
                "response": {"total_analyses": int, "total_coconuts": int, "avg_grade": str}
            },
            "GET /api/stats/trends": {
                "description": "Get analysis trends",
                "headers": {"Authorization": "Bearer <token>"},
                "params": {"days": int},
                "response": {"trends": dict}
            }
        },
        "settings": {
            "GET /api/settings/profile": {
                "description": "Get user profile",
                "headers": {"Authorization": "Bearer <token>"},
                "response": {"username": str, "email": str, "role": str}
            },
            "PUT /api/settings/rates": {
                "description": "Update market rates",
                "body": {"dry": float, "green": float, "tender": float},
                "headers": {"Authorization": "Bearer <token>"},
                "response": {"message": str}
            }
        }
    }
    
    @staticmethod
    def get_endpoint_documentation() -> Dict[str, Any]:
        """Get full API documentation"""
        return APIEndpoints.ENDPOINTS
    
    @staticmethod
    def get_endpoints_by_category(category: str) -> Dict[str, Any]:
        """Get endpoints for specific category"""
        return APIEndpoints.ENDPOINTS.get(category, {})


class APIValidator:
    """Validate API requests"""
    
    @staticmethod
    def validate_auth_headers(headers: Dict) -> Tuple[bool, str]:
        """Validate authorization headers"""
        if "Authorization" not in headers:
            return False, "Missing Authorization header"
        
        auth_header = headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return False, "Invalid Authorization header format"
        
        return True, ""
    
    @staticmethod
    def extract_token(headers: Dict) -> str:
        """Extract token from Authorization header"""
        auth_header = headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            return auth_header[7:]
        return ""
    
    @staticmethod
    def validate_json_body(body: Dict, required_fields: list) -> Tuple[bool, str]:
        """Validate JSON request body"""
        missing_fields = [field for field in required_fields if field not in body]
        
        if missing_fields:
            return False, f"Missing required fields: {', '.join(missing_fields)}"
        
        return True, ""
