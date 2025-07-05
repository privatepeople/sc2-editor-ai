# Python Standard Library imports
from datetime import timedelta
from typing import Annotated

# Third-party Library imports
# Dependency Injection imports
from dependency_injector.wiring import Provide, inject
# FastAPI imports
from fastapi import Depends, APIRouter, Response, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

# Custom Library imports
from app.logging import ApplicationLogging
from app.containers import Container
from app.models.auth import Token
from app.core.auth import authenticate_user
from app.core.security import create_access_token


authentication_router = APIRouter(prefix="/token", tags=["Authentication"])

# Authentication endpoints
@authentication_router.post("", response_model=Token)
@inject
async def login_for_access_token(
                                    response: Response,
                                    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                    access_token_expire: Annotated[int, Depends(Provide[Container.config.fastapi.access_token_expire])],
                                    app_logging: Annotated[ApplicationLogging, Depends(Provide[Container.app_logging])],
                                ):
    """
    Login endpoint to get JWT access token and set session cookie
    
    Args:
        response: FastAPI Response object to set jwt access token
        form_data: OAuth2PasswordRequestForm containing username and password
        access_token_expire: Expiration time for access token in minutes
        app_logging: Application logging instance
    """
    logger = app_logging.logger

    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=access_token_expire)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    
    # Set session cookie (httpOnly, secure, sameSite)
    # Session cookie - no max_age means it expires when browser closes
    response.set_cookie(
                        key="session_token",
                        value=access_token,
                        httponly=True,  # Prevent JavaScript access
                        secure=False,   # Set to True in production with HTTPS
                        samesite="lax", # CSRF protection
                    )
    
    logger.info(f"User {user.username} logged in successfully")
    return {"access_token": access_token, "token_type": "bearer"}


@authentication_router.post("/logout")
async def logout(response: Response):
    """
    Logout endpoint to clear session cookie
    
    Args:
        response: FastAPI Response object to clear cookies
    """
    response.delete_cookie(key="session_token")
    return {"message": "Successfully logged out"}