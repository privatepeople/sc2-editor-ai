# Python Standard Library imports
from typing import Annotated

# Third-party Library imports
# Dependency Injection imports
from dependency_injector.wiring import Provide, inject
# FastAPI imports
from fastapi import Depends, HTTPException, status, Cookie

# Custom Library imports
from app.containers import Container
from app.models.user import User, UserInDB
from app.core.security import get_password_hash, verify_password, verify_token


@inject
def get_user(
            username: str,
            admin_username: str = Provide[Container.config.admin_username],
            admin_password: str = Provide[Container.config.admin_password]
            ) -> UserInDB | None:
    """
    Retrieve user information from environment variables.
    
    Args:
        username: Username to look up
        admin_username: Admin username
        admin_password: Admin password
    
    Returns:
        UserInDB object containing admin account information if username matches, None if user not found
    """
    if username == admin_username:
        return UserInDB(
            username=admin_username,
            hashed_password=get_password_hash(admin_password)
        )
    return None


def authenticate_user(username: str, password: str) -> bool | UserInDB:
    """
    Authenticate user credentials against stored user data.
    
    Args:
        username: Username to authenticate
        password: Plain text password to verify
    
    Returns:
        UserInDB object if authentication successful, False if authentication fails
    """
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


async def get_current_user_from_token(token: str) -> UserInDB | None:
    """
    Extract and validate current user from JWT token.
    
    Args:
        token: JWT token
    
    Returns:
        Authenticated UserInDB object or None if invalid
    """
    token_data = verify_token(token)
    if not token_data:
        return None
    
    user = get_user(username=token_data.username)
    if user is None:
        return None
    return user


@inject
async def get_current_user(
                            authorization: Annotated[str, Depends(Provide[Container.oauth2_scheme])] = None,
                            session_token: Annotated[str, Cookie(alias="session_token")] = None
                        ) -> UserInDB:
    """
    Extract and validate current user from JWT token (either from Authorization header or session cookie).
    
    Args:
        authorization: JWT token from OAuth2 bearer scheme (Authorization header)
        session_token: JWT token from session cookie
    
    Returns:
        Authenticated UserInDB object
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Try session cookie first, then authorization header
    token = session_token or authorization
    
    if not token:
        raise credentials_exception
    
    user = await get_current_user_from_token(token)
    if not user:
        raise credentials_exception
    
    return user


async def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    """
    Get current active user (wrapper function for potential future user status checks).
    
    Args:
        current_user: Current authenticated user from get_current_user dependency
    
    Returns:
        Current active User object
    """
    return current_user