"""
認證相關的 API 路由
"""
from fastapi import APIRouter, HTTPException, status, Depends, Response, Request
from fastapi.security import HTTPAuthorizationCredentials
from typing import Dict, Any
import logging

from app.models import (
    UserLogin, UserCreate, UserResponse, Token, RefreshTokenRequest,
    ApiSuccessResponse, ApiErrorResponse
)
from app.auth import AuthService, get_current_active_user, security
from app.database import UserRepository
from app.oauth import OAuthService
from app.utils import ResponseHelper
from app.config import settings
import hashlib

router = APIRouter(prefix="/auth", tags=["認證"])
logger = logging.getLogger(__name__)


@router.post("/register", response_model=ApiSuccessResponse, summary="註冊新使用者")
async def register(user_data: UserCreate):
    """
    註冊新使用者
    
    - **email**: 電子郵件地址
    - **username**: 使用者名稱
    - **password**: 密碼
    """
    try:
        # 檢查使用者是否已存在
        existing_user = UserRepository.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # 建立新使用者
        password_hash = AuthService.get_password_hash(user_data.password)
        success = UserRepository.create_user(
            email=user_data.email,
            username=user_data.username,
            password_hash=password_hash
        )
        
        if not success:
            logger.error(f"建立使用者失敗 (email: {user_data.email})")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user."
            )
        
        return ResponseHelper.register_success(user_data.email)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"註冊時發生未預期錯誤 (email: {user_data.email}): {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during registration."
        )


@router.post("/login", response_model=ApiSuccessResponse, summary="使用者登入")
async def login(user_credentials: UserLogin, response: Response):
    """
    使用者登入
    
    - **email**: 電子郵件地址
    - **password**: 密碼
    
    回傳 JWT access token，refresh token 透過 httpOnly cookie 設定
    """
    user = AuthService.authenticate_user(user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 更新登入時間
    UserRepository.update_user_login_time(user["id"])
    
    # 建立 Token
    access_token = AuthService.create_access_token(
        data={"sub": user["id"], "email": user["email"]}
    )
    refresh_token = AuthService.create_refresh_token(user["id"])
    
    # 設定 httpOnly cookie for refresh token
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,  # 開發環境設為 False，生產環境應為 True
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60  # 7天
    )
    
    # 準備使用者資訊 (排除敏感資料)，轉換為台灣時間顯示
    from app.utils import to_taiwan_time
    user_info = {
        "id": user["id"],
        "email": user["email"],
        "username": user["username"],
        "is_active": user["is_active"],
        "created_at": to_taiwan_time(user["created_at"]).isoformat() if user.get("created_at") else None
    }
    
    return ResponseHelper.login_success(access_token, user_info)


@router.post("/refresh", response_model=ApiSuccessResponse, summary="重新整理 Token")
async def refresh_token(request: Request, response: Response):
    """
    使用 refresh token 取得新的 access token
    
    從 httpOnly cookie 讀取 refresh token
    """
    # 從 cookie 讀取 refresh token
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found in cookies"
        )
    
    token_data = AuthService.refresh_access_token(refresh_token, rotate_refresh_token=True)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # 如果有新的 refresh token，更新 cookie
    if "refresh_token" in token_data:
        response.set_cookie(
            key="refresh_token",
            value=token_data["refresh_token"],
            httponly=True,
            secure=False,  # 開發環境設為 False，生產環境應為 True
            samesite="lax",
            max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60  # 7天
        )
    
    return ResponseHelper.token_refresh_success(token_data["access_token"])


@router.post("/oauth/{provider}", response_model=ApiSuccessResponse, summary="OAuth 登入")
async def oauth_login(provider: str, response: Response, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    OAuth 提供者登入
    
    - **provider**: OAuth 提供者 (google, facebook, github)
    - **Authorization**: Bearer token (OAuth access token)
    """
    if provider not in ["google", "facebook", "github"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported OAuth provider"
        )
    
    # 處理 OAuth 登入
    token_data = await OAuthService.process_oauth_login(provider, credentials.credentials)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="OAuth authentication failed"
        )
    
    # 設定 httpOnly cookie for refresh token
    if "refresh_token" in token_data:
        response.set_cookie(
            key="refresh_token",
            value=token_data["refresh_token"],
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        )
    
    return ResponseHelper.success(
        message="OAuth 登入成功",
        data={
            "access_token": token_data["access_token"],
            "token_type": token_data.get("token_type", "bearer"),
            "expires_in": 30 * 60
        },
        status_code=200
    )


@router.get("/me", response_model=ApiSuccessResponse, summary="取得當前使用者資訊")
async def get_current_user_info(current_user: Dict[str, Any] = Depends(get_current_active_user)):
    """
    取得當前登入使用者的資訊
    
    需要有效的 JWT token
    """
    from app.utils import to_taiwan_time
    
    # 準備使用者資訊 (排除敏感資料)，轉換為台灣時間顯示
    user_data = {
        "id": current_user["id"],
        "email": current_user["email"],
        "username": current_user["username"],
        "is_active": current_user["is_active"],
        "created_at": to_taiwan_time(current_user["created_at"]).isoformat() if current_user.get("created_at") else None,
        "updated_at": to_taiwan_time(current_user["updated_at"]).isoformat() if current_user.get("updated_at") else None,
        "last_login": to_taiwan_time(current_user["last_login"]).isoformat() if current_user.get("last_login") else None
    }
    
    return ResponseHelper.success(
        message="取得使用者資訊成功",
        data=user_data,
        status_code=200
    )


@router.post("/logout", response_model=ApiSuccessResponse, summary="登出")
async def logout(
    request: Request,
    response: Response,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    使用者登出，撤銷 refresh token
    
    從 httpOnly cookie 讀取並撤銷 refresh token
    """
    # 從 cookie 讀取 refresh token
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        from app.database import RefreshTokenRepository
        RefreshTokenRepository.revoke_refresh_token(token_hash)
    
    # 清除 refresh token cookie
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=False,  # 開發環境設為 False，生產環境應為 True
        samesite="lax"
    )
    
    return ResponseHelper.logout_success()


@router.get("/debug-token", response_model=ApiSuccessResponse, summary="調試 Token")
async def debug_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    調試 Token 驗證問題
    
    需要有效的 JWT token
    """
    try:
        token = credentials.credentials
        
        # 先驗證 token 本身
        from jose import jwt
        from app.config import settings
        
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        except Exception as jwt_error:
            return ResponseHelper.error(
                message="JWT 解碼失敗",
                error_code="JWT_DECODE_ERROR",
                details={"error": str(jwt_error)},
                status_code=400
            )
        
        # 檢查 token 內容
        token_data = AuthService.verify_token(token)
        if token_data is None:
            return ResponseHelper.error(
                message="Token 驗證失敗",
                error_code="TOKEN_VALIDATION_FAILED",
                details={"payload": payload},
                status_code=401
            )
        
        # 檢查使用者
        user = UserRepository.get_user_by_id(token_data.user_id)
        if user is None:
            return ResponseHelper.error(
                message="使用者不存在",
                error_code="USER_NOT_FOUND",
                details={"user_id": token_data.user_id},
                status_code=401
            )
        
        return ResponseHelper.success(
            message="Token 驗證成功",
            data={
                "token_valid": True,
                "payload": payload,
                "token_data": {
                    "user_id": token_data.user_id,
                    "email": token_data.email
                },
                "user_found": True,
                "user_active": user["is_active"]
            }
        )
        
    except Exception as e:
        return ResponseHelper.error(
            message="調試過程中發生錯誤",
            error_code="DEBUG_ERROR",
            details={"error": str(e)},
            status_code=500
        )