"""
OAuth 整合模組

此模組提供第三方 OAuth 認證服務的整合功能，包括：
- Google OAuth 2.0 認證
- Facebook OAuth 認證
- GitHub OAuth 認證
- OAuth 使用者資訊取得
- OAuth 登入流程處理

支援多種主流 OAuth 提供者，提供統一的認證介面
"""
from typing import Dict, Any, Optional
from authlib.integrations.starlette_client import OAuth
from starlette.requests import Request
from fastapi import HTTPException, status
import httpx

from app.config import settings
from app.database import UserRepository
from app.auth import AuthService
from app.models import OAuthUser


# OAuth 客戶端配置
oauth = OAuth()

# 根據環境變數註冊 OAuth 提供者
if settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET:
    """註冊 Google OAuth 客戶端"""
    oauth.register(
        name='google',
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        server_metadata_url='https://accounts.google.com/.well-known/openid_configuration',
        client_kwargs={
            'scope': 'openid email profile'  # 請求的權限範圍
        }
    )

if settings.FACEBOOK_CLIENT_ID and settings.FACEBOOK_CLIENT_SECRET:
    """註冊 Facebook OAuth 客戶端"""
    oauth.register(
        name='facebook',
        client_id=settings.FACEBOOK_CLIENT_ID,
        client_secret=settings.FACEBOOK_CLIENT_SECRET,
        access_token_url='https://graph.facebook.com/oauth/access_token',
        authorize_url='https://www.facebook.com/dialog/oauth',
        api_base_url='https://graph.facebook.com/',
        client_kwargs={'scope': 'email'},  # 只請求電子郵件權限
    )

if settings.GITHUB_CLIENT_ID and settings.GITHUB_CLIENT_SECRET:
    """註冊 GitHub OAuth 客戶端"""
    oauth.register(
        name='github',
        client_id=settings.GITHUB_CLIENT_ID,
        client_secret=settings.GITHUB_CLIENT_SECRET,
        access_token_url='https://github.com/login/oauth/access_token',
        authorize_url='https://github.com/login/oauth/authorize',
        api_base_url='https://api.github.com/',
        client_kwargs={'scope': 'user:email'},  # 請求使用者和電子郵件權限
    )


class OAuthService:
    """
    OAuth 服務類別
    
    提供與各種 OAuth 提供者的整合服務，包括：
    - 使用者資訊取得
    - 登入流程處理
    - 使用者帳戶建立/連結
    """
    
    @staticmethod
    async def get_google_user_info(token: str) -> Optional[OAuthUser]:
        """
        從 Google OAuth API 取得使用者資訊
        
        Args:
            token (str): Google OAuth access token
            
        Returns:
            Optional[OAuthUser]: 使用者資訊模型，失敗時回傳 None
            
        Note:
            使用 Google UserInfo API v2 取得基本使用者資訊
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    'https://www.googleapis.com/oauth2/v2/userinfo',
                    headers={'Authorization': f'Bearer {token}'}
                )
                if response.status_code == 200:
                    user_data = response.json()
                    return OAuthUser(
                        email=user_data.get('email'),
                        username=user_data.get('name', user_data.get('email').split('@')[0]),
                        provider='google',
                        provider_id=user_data.get('id')
                    )
        except Exception:
            # 發生任何錯誤時回傳 None，讓呼叫方處理
            pass
        return None
    
    @staticmethod
    async def get_facebook_user_info(token: str) -> Optional[OAuthUser]:
        """
        從 Facebook Graph API 取得使用者資訊
        
        Args:
            token (str): Facebook OAuth access token
            
        Returns:
            Optional[OAuthUser]: 使用者資訊模型，失敗時回傳 None
            
        Note:
            使用 Facebook Graph API 取得 id、name、email 欄位
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    'https://graph.facebook.com/me',
                    params={
                        'fields': 'id,name,email',  # 指定需要的欄位
                        'access_token': token
                    }
                )
                if response.status_code == 200:
                    user_data = response.json()
                    return OAuthUser(
                        email=user_data.get('email'),
                        username=user_data.get('name', user_data.get('email', '').split('@')[0]),
                        provider='facebook',
                        provider_id=user_data.get('id')
                    )
        except Exception:
            # 發生任何錯誤時回傳 None
            pass
        return None
    
    @staticmethod
    async def get_github_user_info(token: str) -> Optional[OAuthUser]:
        """
        從 GitHub API 取得使用者資訊
        
        Args:
            token (str): GitHub OAuth access token
            
        Returns:
            Optional[OAuthUser]: 使用者資訊模型，失敗時回傳 None
            
        Note:
            需要分別呼叫使用者 API 和電子郵件 API
            GitHub 的電子郵件可能不在基本使用者資訊中
        """
        try:
            async with httpx.AsyncClient() as client:
                # 取得使用者基本資訊
                user_response = await client.get(
                    'https://api.github.com/user',
                    headers={'Authorization': f'token {token}'}
                )
                
                if user_response.status_code == 200:
                    user_data = user_response.json()
                    
                    # 取得使用者電子郵件列表
                    email_response = await client.get(
                        'https://api.github.com/user/emails',
                        headers={'Authorization': f'token {token}'}
                    )
                    
                    # 先嘗試從使用者資料中取得公開電子郵件
                    email = user_data.get('email')
                    
                    # 如果沒有公開電子郵件，從電子郵件列表中取得主要電子郵件
                    if not email and email_response.status_code == 200:
                        emails = email_response.json()
                        primary_email = next((e for e in emails if e.get('primary')), None)
                        email = primary_email.get('email') if primary_email else None
                    
                    if email:
                        return OAuthUser(
                            email=email,
                            username=user_data.get('login', email.split('@')[0]),
                            provider='github',
                            provider_id=str(user_data.get('id'))  # GitHub ID 是數字，轉為字串
                        )
        except Exception:
            # 發生任何錯誤時回傳 None
            pass
        return None
    
    @staticmethod
    async def process_oauth_login(provider: str, token: str) -> Optional[Dict[str, str]]:
        """
        處理 OAuth 登入流程
        
        Args:
            provider (str): OAuth 提供者名稱（google、facebook、github）
            token (str): OAuth access token
            
        Returns:
            Optional[Dict[str, str]]: 包含 access_token 和 refresh_token 的字典，失敗時回傳 None
            
        Flow:
            1. 根據提供者取得使用者資訊
            2. 檢查使用者是否已存在
            3. 如果不存在則建立新使用者
            4. 更新登入時間
            5. 產生 JWT Token
            
        Note:
            如果相同電子郵件已存在但使用不同登入方式，目前不會自動連結帳戶
        """
        # 根據不同的 OAuth 提供者取得使用者資訊
        oauth_user = None
        if provider == 'google':
            oauth_user = await OAuthService.get_google_user_info(token)
        elif provider == 'facebook':
            oauth_user = await OAuthService.get_facebook_user_info(token)
        elif provider == 'github':
            oauth_user = await OAuthService.get_github_user_info(token)
        
        # 如果無法取得使用者資訊或電子郵件為空，則登入失敗
        if not oauth_user or not oauth_user.email:
            return None
        
        # 檢查是否已有相同 OAuth 提供者的使用者
        existing_user = UserRepository.get_user_by_provider(provider, oauth_user.provider_id)
        
        if not existing_user:
            # 檢查是否有相同電子郵件的使用者（可能是其他登入方式）
            email_user = UserRepository.get_user_by_email(oauth_user.email)
            if email_user:
                # 如果有相同電子郵件的使用者，目前不自動連結帳戶
                # 這裡可以根據業務需求決定是否允許帳戶連結
                return None
            
            # 建立新的 OAuth 使用者
            success = UserRepository.create_user(
                email=oauth_user.email,
                username=oauth_user.username,
                password_hash='',  # OAuth 使用者沒有密碼
                provider=provider,
                provider_id=oauth_user.provider_id
            )
            
            if not success:
                return None
                
            # 重新取得新建立的使用者資訊
            user = UserRepository.get_user_by_email(oauth_user.email)
        else:
            # 使用現有的使用者
            user = existing_user
        
        if not user:
            return None
        
        # 更新最後登入時間
        UserRepository.update_user_login_time(user["id"])
        
        # 建立 JWT Token
        access_token = AuthService.create_access_token(
            data={"sub": user["id"], "email": user["email"]}
        )
        refresh_token = AuthService.create_refresh_token(user["id"])
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        } 