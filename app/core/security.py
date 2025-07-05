# Python Standard Library imports
from typing import Optional
from datetime import datetime, timedelta

# Third-party Library imports
# Password hashing and JWT imports
import bcrypt
import jwt
from jwt import PyJWTError
# Dependency Injection imports
from dependency_injector.wiring import Provide, inject

# Custom Library imports
from app.containers import Container
from app.models.auth import TokenData


def get_password_hash(password: str) -> bytes:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password to be hashed
    
    Returns:
        Bcrypt hashed password
    """
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    return hashed_password


def verify_password(plain_password: str, hashed_password: bytes) -> bool:
    """
    Verify a plain password against its bcrypt hash.
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Bcrypt hashed password to compare against
    
    Returns:
        True if password matches hash, False otherwise
    """
    password_byte_enc = plain_password.encode('utf-8')
    return bcrypt.checkpw(password=password_byte_enc , hashed_password=hashed_password)


@inject
def create_access_token(
                        data: dict, expires_delta: Optional[timedelta] = None,
                        jwt_secret_key: str = Provide[Container.config.jwt_secret_key],
                        algorithm: str = Provide[Container.config.algorithm]
                        ) -> str:
    """
    Create a JWT access token with expiration.
    
    Args:
        data: Data to encode in the JWT payload
        expires_delta: Custom expiration time delta. Defaults to 15 minutes if None
        jwt_secret_key: Secret key for signing the JWT
        algorithm: Algorithm used for signing the JWT
    
    Returns:
        Encoded JWT access token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, jwt_secret_key, algorithm=algorithm)
    return encoded_jwt


@inject
def verify_token(
                token: str,
                jwt_secret_key: str = Provide[Container.config.jwt_secret_key],
                algorithm: str = Provide[Container.config.algorithm]
                ) -> TokenData | None:
    """
    Verify and decode JWT token.
    
    Args:
        token: JWT token to verify
        jwt_secret_key: Secret key used to sign the JWT
        algorithm: Algorithm used for signing the JWT
    
    Returns:
        TokenData if token is valid, None if invalid
    """
    try:
        payload = jwt.decode(token, jwt_secret_key, algorithms=[algorithm])
        username: str = payload.get("sub")
        if username is None:
            return None
        return TokenData(username=username)
    except PyJWTError:
        return None