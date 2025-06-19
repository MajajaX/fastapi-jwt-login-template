"""
工具函數和輔助類別
"""
from typing import Any, Optional, Dict, List, Union
from datetime import datetime, timezone, timedelta
try:
    # 嘗試使用 zoneinfo (Python 3.9+)
    from zoneinfo import ZoneInfo
    TAIWAN_TZ = ZoneInfo("Asia/Taipei")
except (ImportError, Exception):
    # 如果沒有 zoneinfo 或時區資料不可用，使用固定偏移 UTC+8
    # 這對於台灣是準確的，因為台灣不使用夏令時間
    TAIWAN_TZ = timezone(timedelta(hours=8))

from app.models import ApiSuccessResponse, ApiErrorResponse

# 時間處理函數 - 使用標準庫方法
def get_taiwan_now() -> datetime:
    """取得當前台灣時間"""
    return datetime.now(TAIWAN_TZ)

def get_utc_now() -> datetime:
    """取得當前 UTC 時間"""
    return datetime.now(timezone.utc)

def to_taiwan_time(dt: datetime) -> datetime:
    """將時間轉換為台灣時間"""
    if dt.tzinfo is None:
        # 如果是 naive datetime，假設為 UTC
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(TAIWAN_TZ)

def to_utc_time(dt: datetime) -> datetime:
    """將時間轉換為 UTC 時間"""
    if dt.tzinfo is None:
        # 如果是 naive datetime，假設為台灣時間
        dt = dt.replace(tzinfo=TAIWAN_TZ)
    return dt.astimezone(timezone.utc)

class ResponseHelper:
    """API 回應格式輔助類別"""
    
    @staticmethod
    def success(
        message: str = "操作成功",
        data: Optional[Union[Dict[str, Any], List[Any], Any]] = None,
        status_code: int = 200
    ) -> ApiSuccessResponse:
        """建立成功回應"""
        return ApiSuccessResponse(
            message=message,
            data=data,
            status_code=status_code,
            timestamp=get_taiwan_now()
        )
    
    @staticmethod
    def error(
        message: str = "操作失敗",
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 400
    ) -> ApiErrorResponse:
        """建立錯誤回應"""
        return ApiErrorResponse(
            message=message,
            error_code=error_code,
            details=details,
            status_code=status_code,
            timestamp=get_taiwan_now()
        )
    
    @staticmethod
    def login_success(access_token: str, user_info: Dict[str, Any]) -> ApiSuccessResponse:
        """登入成功回應 (不包含 refresh_token，將透過 cookie 設定)"""
        return ResponseHelper.success(
            message="登入成功",
            data={
                "access_token": access_token,
                "token_type": "bearer",
                "user": user_info,
                "expires_in": 30 * 60  # 30 分鐘，以秒為單位
            },
            status_code=200
        )
    
    @staticmethod
    def register_success(email: str) -> ApiSuccessResponse:
        """註冊成功回應"""
        return ResponseHelper.success(
            message="註冊成功",
            data={"email": email},
            status_code=201
        )
    
    @staticmethod
    def logout_success() -> ApiSuccessResponse:
        """登出成功回應"""
        return ResponseHelper.success(
            message="登出成功",
            status_code=200
        )
    
    @staticmethod
    def token_refresh_success(access_token: str) -> ApiSuccessResponse:
        """Token 重新整理成功回應"""
        return ResponseHelper.success(
            message="Token 重新整理成功",
            data={
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": 30 * 60  # 30 分鐘
            },
            status_code=200
        ) 