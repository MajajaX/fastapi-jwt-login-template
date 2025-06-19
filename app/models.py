"""
Pydantic 模型定義

此模組定義了整個應用程式使用的資料模型，包括：
- 使用者相關模型（註冊、登入、回應）
- JWT Token 相關模型
- OAuth 使用者模型
- 統一 API 回應格式模型

使用 Pydantic 提供資料驗證、序列化和文件生成功能
"""
from datetime import datetime
from typing import Optional, Any, Dict, List, Union
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """
    使用者基礎模型
    
    包含使用者的基本資訊，用作其他使用者模型的基礎類別
    """
    email: EmailStr  # 使用 EmailStr 自動驗證電子郵件格式
    username: str    # 使用者名稱
    is_active: bool = True  # 帳戶啟用狀態，預設為啟用


class UserCreate(UserBase):
    """
    建立使用者模型
    
    用於使用者註冊時的資料驗證
    繼承 UserBase 並添加密碼欄位
    """
    password: str  # 明文密碼，將在處理時進行雜湊


class UserResponse(UserBase):
    """
    使用者回應模型
    
    用於 API 回應時回傳使用者資訊
    包含資料庫中的時間戳記欄位
    """
    id: int  # 使用者 ID
    created_at: datetime  # 建立時間
    updated_at: datetime  # 更新時間

    class Config:
        """Pydantic 配置"""
        from_attributes = True  # 允許從 ORM 物件建立


class UserLogin(BaseModel):
    """
    使用者登入模型
    
    用於登入請求的資料驗證
    只包含登入所需的基本資訊
    """
    email: EmailStr  # 電子郵件地址
    password: str    # 密碼


class Token(BaseModel):
    """
    JWT Token 模型
    
    用於回傳認證 Token 的標準格式
    包含存取和重新整理 Token
    """
    access_token: str   # 存取 Token
    refresh_token: str  # 重新整理 Token
    token_type: str = "bearer"  # Token 類型，預設為 Bearer


class TokenData(BaseModel):
    """
    Token 資料模型
    
    用於儲存從 JWT Token 解析出的使用者資訊
    在 Token 驗證過程中使用
    """
    user_id: Optional[int] = None  # 使用者 ID
    email: Optional[str] = None    # 電子郵件地址


class RefreshTokenRequest(BaseModel):
    """
    重新整理 Token 請求模型
    
    用於接收重新整理 Token 的請求
    現在主要透過 httpOnly Cookie 傳輸，此模型保留用於向下相容
    """
    refresh_token: str  # 重新整理 Token


class OAuthUser(BaseModel):
    """
    OAuth 使用者資料模型
    
    用於儲存從 OAuth 提供者取得的使用者資訊
    支援 Google、Facebook、GitHub 等提供者
    """
    email: EmailStr  # 電子郵件地址
    username: str    # 使用者名稱
    provider: str    # OAuth 提供者名稱（google、facebook、github）
    provider_id: str # OAuth 提供者的使用者唯一識別碼


# 統一 API 回應格式模型
class ApiResponse(BaseModel):
    """
    統一 API 回應格式基礎模型
    
    定義所有 API 回應的統一結構，包括：
    - 成功/失敗狀態
    - HTTP 狀態碼
    - 訊息內容
    - 資料內容
    - 時間戳記
    """
    success: bool  # 操作是否成功
    status_code: int  # HTTP 狀態碼
    message: str  # 回應訊息
    data: Optional[Union[Dict[str, Any], List[Any], Any]] = None  # 回應資料
    timestamp: datetime  # 回應時間戳記
    
    class Config:
        """Pydantic 配置"""
        json_encoders = {
            datetime: lambda v: v.isoformat()  # 將 datetime 轉換為 ISO 格式字串
        }


class ApiSuccessResponse(ApiResponse):
    """
    成功回應模型
    
    用於建立成功的 API 回應
    預設 success 為 True，status_code 為 200
    """
    success: bool = True  # 預設為成功
    status_code: int = 200  # 預設 HTTP 200 OK


class ApiErrorResponse(ApiResponse):
    """
    錯誤回應模型
    
    用於建立錯誤的 API 回應
    預設 success 為 False，status_code 為 400
    包含額外的錯誤代碼和詳細資訊欄位
    """
    success: bool = False  # 預設為失敗
    status_code: int = 400  # 預設 HTTP 400 Bad Request
    error_code: Optional[str] = None  # 錯誤代碼，用於程式化處理
    details: Optional[Dict[str, Any]] = None  # 錯誤詳細資訊 