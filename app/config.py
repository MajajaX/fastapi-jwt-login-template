"""
應用程式配置設定

此模組負責管理整個應用程式的配置設定，包括：
- JWT 認證相關設定
- 資料庫連接設定
- OAuth 第三方登入設定
- 安全性設定

所有敏感資訊應透過環境變數設定，避免硬編碼在程式碼中
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    應用程式設定類別
    
    使用 Pydantic Settings 自動處理環境變數讀取和型別轉換
    """
    
    # JWT 認證設定
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    """JWT 簽名密鑰，生產環境必須使用強密碼"""
    
    ALGORITHM: str = "HS256"
    """JWT 簽名演算法"""
    
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    """存取 Token 過期時間（分鐘）"""
    
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    """重新整理 Token 過期時間（天）"""
    
    # 資料庫連接設定
    DB_SERVER: str = os.getenv("DB_SERVER", "your-server.database.windows.net")
    """Azure SQL 資料庫伺服器位址"""
    
    DB_DATABASE: str = os.getenv("DB_DATABASE", "your-database-name")
    """資料庫名稱"""
    
    DB_USERNAME: str = os.getenv("DB_USERNAME", "your-username")
    """資料庫使用者名稱"""
    
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    """資料庫密碼 - 必須透過環境變數設定"""
    
    # OAuth 第三方登入設定（選填）
    GOOGLE_CLIENT_ID: Optional[str] = None
    """Google OAuth 客戶端 ID"""
    
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    """Google OAuth 客戶端密鑰"""
    
    FACEBOOK_CLIENT_ID: Optional[str] = None
    """Facebook OAuth 應用程式 ID"""
    
    FACEBOOK_CLIENT_SECRET: Optional[str] = None
    """Facebook OAuth 應用程式密鑰"""
    
    GITHUB_CLIENT_ID: Optional[str] = None
    """GitHub OAuth 應用程式 ID"""
    
    GITHUB_CLIENT_SECRET: Optional[str] = None
    """GitHub OAuth 應用程式密鑰"""
    
    # 應用程式 URL 設定
    FRONTEND_URL: str = "http://localhost:3000"
    """前端應用程式 URL，用於 CORS 設定"""
    
    # 若有需要，可以設定後端 API URL
    #BACKEND_URL: str = "http://localhost:8000"
    """後端 API URL"""
    
    class Config:
        """Pydantic 設定"""
        env_file = ".env"
        """自動從 .env 檔案讀取環境變數"""


# 全域設定實例
settings = Settings()
"""全域設定實例，可在整個應用程式中使用""" 