"""
Authentication and security utilities for CANS API.
"""

import os
import jwt
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from fastapi import HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
import logging

logger = logging.getLogger(__name__)

# Security configuration
SECRET_KEY = os.getenv("CANS_SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
API_KEY_EXPIRE_DAYS = int(os.getenv("API_KEY_EXPIRE_DAYS", 30))

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security scheme
security = HTTPBearer()


class APIKey:
    """API Key management."""
    
    def __init__(self, key: str, name: str, permissions: List[str], expires_at: Optional[datetime] = None):
        self.key = key
        self.name = name
        self.permissions = permissions
        self.expires_at = expires_at or datetime.utcnow() + timedelta(days=API_KEY_EXPIRE_DAYS)
        self.created_at = datetime.utcnow()
        self.last_used = None
        self.usage_count = 0
    
    def is_expired(self) -> bool:
        """Check if API key is expired."""
        return datetime.utcnow() > self.expires_at
    
    def has_permission(self, permission: str) -> bool:
        """Check if API key has specific permission."""
        return permission in self.permissions or "admin" in self.permissions
    
    def use(self):
        """Mark API key as used."""
        self.last_used = datetime.utcnow()
        self.usage_count += 1


class APIKeyManager:
    """Manager for API keys."""
    
    def __init__(self):
        self.keys: Dict[str, APIKey] = {}
        self._create_default_key()
    
    def _create_default_key(self):
        """Create default admin API key if none exists."""
        default_key = os.getenv("CANS_DEFAULT_API_KEY")
        if default_key:
            self.keys[default_key] = APIKey(
                key=default_key,
                name="default-admin",
                permissions=["admin"]
            )
    
    def create_key(self, name: str, permissions: List[str], expires_days: int = API_KEY_EXPIRE_DAYS) -> str:
        """Create a new API key."""
        key = f"cans_{secrets.token_urlsafe(32)}"
        expires_at = datetime.utcnow() + timedelta(days=expires_days)
        
        self.keys[key] = APIKey(
            key=key,
            name=name,
            permissions=permissions,
            expires_at=expires_at
        )
        
        logger.info(f"Created API key '{name}' with permissions: {permissions}")
        return key
    
    def get_key(self, key: str) -> Optional[APIKey]:
        """Get API key object."""
        api_key = self.keys.get(key)
        if api_key and not api_key.is_expired():
            return api_key
        return None
    
    def revoke_key(self, key: str) -> bool:
        """Revoke an API key."""
        if key in self.keys:
            del self.keys[key]
            logger.info(f"Revoked API key: {key[:12]}...")
            return True
        return False
    
    def list_keys(self) -> List[Dict]:
        """List all active API keys (without the actual key)."""
        result = []
        for key, api_key in self.keys.items():
            if not api_key.is_expired():
                result.append({
                    "key_preview": key[:12] + "...",
                    "name": api_key.name,
                    "permissions": api_key.permissions,
                    "created_at": api_key.created_at.isoformat(),
                    "expires_at": api_key.expires_at.isoformat(),
                    "last_used": api_key.last_used.isoformat() if api_key.last_used else None,
                    "usage_count": api_key.usage_count
                })
        return result


class RateLimiter:
    """Simple rate limiter."""
    
    def __init__(self, max_requests: int = 100, window_minutes: int = 60):
        self.max_requests = max_requests
        self.window_minutes = window_minutes
        self.requests: Dict[str, List[datetime]] = {}
    
    def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed."""
        now = datetime.utcnow()
        window_start = now - timedelta(minutes=self.window_minutes)
        
        # Clean old requests
        if identifier in self.requests:
            self.requests[identifier] = [
                req_time for req_time in self.requests[identifier]
                if req_time > window_start
            ]
        else:
            self.requests[identifier] = []
        
        # Check limit
        if len(self.requests[identifier]) >= self.max_requests:
            return False
        
        # Add current request
        self.requests[identifier].append(now)
        return True


# Global instances
api_key_manager = APIKeyManager()
rate_limiter = RateLimiter()


def verify_api_key(credentials: HTTPAuthorizationCredentials = Security(security)) -> APIKey:
    """Verify API key from Authorization header."""
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="API key required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract token from credentials
    token = credentials.credentials
    
    # Get API key
    api_key = api_key_manager.get_key(token)
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check rate limit
    if not rate_limiter.is_allowed(token):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded"
        )
    
    # Mark as used
    api_key.use()
    
    return api_key


def require_permission(permission: str):
    """Decorator to require specific permission."""
    def permission_checker(api_key: APIKey = Depends(verify_api_key)) -> APIKey:
        if not api_key.has_permission(permission):
            raise HTTPException(
                status_code=403,
                detail=f"Permission '{permission}' required"
            )
        return api_key
    return permission_checker


def create_jwt_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_jwt_token(token: str):
    """Verify JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def hash_password(password: str) -> str:
    """Hash password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password."""
    return pwd_context.verify(plain_password, hashed_password)


def generate_api_key(name: str, permissions: List[str]) -> str:
    """Generate new API key."""
    return api_key_manager.create_key(name, permissions)


# Security middleware functions
def get_client_ip(request):
    """Get client IP address for rate limiting."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0]
    return request.client.host


def log_security_event(event: str, details: dict):
    """Log security events."""
    logger.warning(f"Security Event: {event} - {details}")


# Permission constants
class Permissions:
    VALIDATE = "validate"
    TRAIN = "train" 
    PREDICT = "predict"
    EVALUATE = "evaluate"
    ANALYZE = "analyze"
    MANAGE_MODELS = "manage_models"
    ADMIN = "admin"