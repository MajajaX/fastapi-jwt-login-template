"""
認證和 JWT 處理模組
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, HashingError
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import hashlib
import secrets

from app.config import settings
from app.database import UserRepository, RefreshTokenRepository
from app.models import TokenData


# Argon2id 密碼雜湊器 - 使用推薦的安全參數
password_hasher = PasswordHasher(
    time_cost=3,        # 3 次迭代
    memory_cost=65536,  # 64 MB (64 * 1024 KB)
    parallelism=1,      # 1 個線程
    hash_len=32,        # 32 字節輸出
    salt_len=16         # 16 字節鹽值
)

# HTTP Bearer Token 認證
security = HTTPBearer()


class AuthService:
    """認證服務類別"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """驗證密碼"""
        try:
            password_hasher.verify(hashed_password, plain_password)
            return True
        except VerifyMismatchError:
            return False
        except Exception:
            return False
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """取得密碼雜湊值"""
        try:
            return password_hasher.hash(password)
        except HashingError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Password hashing failed: {str(e)}"
            )
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """建立存取 Token"""
        from app.utils import get_utc_now
        
        to_encode = data.copy()
        if expires_delta:
            expire = get_utc_now() + expires_delta
        else:
            expire = get_utc_now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        # 確保 sub (subject) 欄位是字符串類型，符合 JWT 標準
        if "sub" in to_encode and not isinstance(to_encode["sub"], str):
            to_encode["sub"] = str(to_encode["sub"])
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(user_id: int) -> str:
        """建立重新整理 Token"""
        from app.utils import get_utc_now
        
        # 產生隨機 Token
        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        # 設定過期時間 (使用 UTC 時間進行內部計算)
        expires_at = get_utc_now() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        # 儲存到資料庫
        RefreshTokenRepository.create_refresh_token(user_id, token_hash, expires_at)
        
        return token
    
    @staticmethod
    def verify_token(token: str) -> Optional[TokenData]:
        """驗證 Token"""
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            logger.debug(f"🔐 開始驗證 JWT Token (長度: {len(token)})")
            logger.debug(f"🔐 Token 前20字符: {token[:20]}...")
            logger.debug(f"🔐 使用密鑰: {settings.SECRET_KEY[:10]}...")
            logger.debug(f"🔐 使用算法: {settings.ALGORITHM}")
            
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            logger.debug(f"🔐 JWT 解碼成功，payload: {payload}")
            
            user_id_str: str = payload.get("sub")
            email: str = payload.get("email")
            token_type: str = payload.get("type")
            
            # 將字符串類型的 user_id 轉換為整數
            try:
                user_id: int = int(user_id_str) if user_id_str else None
            except (ValueError, TypeError):
                logger.error(f"🔐 無法轉換 user_id: {user_id_str}")
                return None
            
            logger.debug(f"🔐 提取資料 - user_id: {user_id}, email: {email}, type: {token_type}")
            
            if user_id is None or token_type != "access":
                logger.warning(f"🔐 Token 驗證失敗 - user_id: {user_id}, token_type: {token_type}")
                return None
                
            return TokenData(user_id=user_id, email=email)
            
        except JWTError as e:
            logger.error(f"🔐 JWT 解碼錯誤: {type(e).__name__} - {str(e)}")
            return None
        except Exception as e:
            logger.error(f"🔐 Token 驗證異常: {type(e).__name__} - {str(e)}")
            return None
    
    @staticmethod
    def refresh_access_token(refresh_token: str, rotate_refresh_token: bool = True) -> Optional[Dict[str, str]]:
        """使用重新整理 Token 取得新的存取 Token，並可選擇性地輪替 refresh token"""
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        token_data = RefreshTokenRepository.get_refresh_token(token_hash)
        
        if not token_data:
            return None
        
        # 建立新的存取 Token
        access_token = AuthService.create_access_token(
            data={"sub": token_data["user_id"], "email": token_data["email"]}
        )
        
        result = {
            "access_token": access_token,
            "token_type": "bearer"
        }
        
        # Token Rotation: 產生新的 refresh token 並撤銷舊的
        if rotate_refresh_token:
            # 撤銷舊的 refresh token
            RefreshTokenRepository.revoke_refresh_token(token_hash)
            
            # 建立新的 refresh token
            new_refresh_token = AuthService.create_refresh_token(token_data["user_id"])
            result["refresh_token"] = new_refresh_token
        
        return result
    
    @staticmethod
    def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
        """驗證使用者登入"""
        user = UserRepository.get_user_by_email(email)
        if not user:
            return None
        if not AuthService.verify_password(password, user["password_hash"]):
            return None
        return user


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """取得當前使用者依賴"""
    from app.utils import ResponseHelper
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        token = credentials.credentials
        logger.debug(f"👤 開始驗證使用者，Token 長度: {len(token)}")
        
        token_data = AuthService.verify_token(token)
        
        if token_data is None:
            logger.warning("👤 Token 驗證失敗 - 無效或過期的 Token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="JWT 解碼失敗",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.debug(f"👤 Token 驗證成功，查找使用者 ID: {token_data.user_id}")
        user = UserRepository.get_user_by_id(token_data.user_id)
        if user is None:
            logger.warning(f"👤 使用者不存在，ID: {token_data.user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="使用者不存在",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.debug(f"👤 使用者驗證成功: {user['email']}")
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"👤 Token 驗證異常: {type(e).__name__} - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token 驗證錯誤: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """取得當前活躍使用者依賴"""
    if not current_user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="User account is inactive"
        )
    return current_user 