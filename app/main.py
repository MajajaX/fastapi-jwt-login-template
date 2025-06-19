"""
FastAPI JWT Authentication Server 主應用程式
"""
import os
import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.config import settings
from app.routers import auth

# 設定日誌記錄
if os.getenv("ENVIRONMENT", "development") == "development":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger(__name__)
    logger.debug("🔧 開發模式：啟用詳細日誌記錄")
else:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """應用程式生命週期管理"""
    # 啟動時執行
    if os.getenv("ENVIRONMENT", "development") == "development":
        logger.info("🚀 FastAPI JWT Authentication Server 啟動中 (開發模式)...")
        logger.debug(f"資料庫伺服器: {settings.DB_SERVER}")
        logger.debug(f"資料庫名稱: {settings.DB_DATABASE}")
        logger.debug(f"JWT 過期時間: {settings.ACCESS_TOKEN_EXPIRE_MINUTES} 分鐘")
    else:
        logger.info("🚀 FastAPI JWT Authentication Server 啟動中...")
    
    yield
    
    # 關閉時執行
    logger.info("📴 FastAPI JWT Authentication Server 關閉中...")


# 建立 FastAPI 應用程式實例
app = FastAPI(
    title="FastAPI JWT Authentication Server",
    description="使用 FastAPI 和 Authlib 的 JWT 認證服務器，支援 OAuth 整合",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 中間件設定
allowed_origins = [settings.FRONTEND_URL, "http://localhost:3000", "http://127.0.0.1:3000"]
if os.getenv("ENVIRONMENT", "development") == "development":
    allowed_origins.extend(["http://localhost:8080", "http://127.0.0.1:8080"])
    logger.debug(f"CORS 允許的來源: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 註冊路由
app.include_router(auth.router)


@app.get("/test-login", summary="測試登入頁面")
async def test_login_page():
    """測試登入頁面，包含所有認證功能的測試界面"""
    from fastapi.responses import HTMLResponse
    
    html_content = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>登入系統測試頁面</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .content {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 30px;
            padding: 30px;
        }
        
        .section {
            background: #f8f9fa;
            padding: 25px;
            border-radius: 10px;
            border: 1px solid #e9ecef;
        }
        
        .section h2 {
            color: #495057;
            margin-bottom: 20px;
            border-bottom: 2px solid #007bff;
            padding-bottom: 10px;
        }
        
        .input-group {
            margin-bottom: 15px;
        }
        
        .input-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
            color: #495057;
        }
        
        .input-group input, .input-group select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e9ecef;
            border-radius: 5px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        
        .input-group input:focus, .input-group select:focus {
            outline: none;
            border-color: #007bff;
        }
        
        .btn {
            background: linear-gradient(135deg, #007bff, #0056b3);
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            transition: transform 0.2s, box-shadow 0.2s;
            margin-right: 10px;
            margin-bottom: 10px;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,123,255,0.4);
        }
        
        .btn.danger {
            background: linear-gradient(135deg, #dc3545, #c82333);
        }
        
        .btn.success {
            background: linear-gradient(135deg, #28a745, #1e7e34);
        }
        
        .btn.warning {
            background: linear-gradient(135deg, #ffc107, #e0a800);
            color: #212529;
        }
        
        .response {
            margin-top: 20px;
            padding: 15px;
            border-radius: 5px;
            font-family: monospace;
            font-size: 14px;
            max-height: 300px;
            overflow-y: auto;
        }
        
        .response.success {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
        }
        
        .response.error {
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
        }
        
        .token-display {
            background: #e3f2fd;
            border: 1px solid #bbdefb;
            padding: 15px;
            border-radius: 5px;
            margin-top: 15px;
            word-break: break-all;
            font-family: monospace;
            font-size: 12px;
        }
        
        .oauth-buttons {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        .oauth-btn {
            flex: 1;
            min-width: 100px;
        }
        
        .oauth-btn.google {
            background: linear-gradient(135deg, #db4437, #c23321);
        }
        
        .oauth-btn.facebook {
            background: linear-gradient(135deg, #4267B2, #365899);
        }
        
        .oauth-btn.github {
            background: linear-gradient(135deg, #333, #24292e);
        }
        
        .user-info {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            padding: 15px;
            border-radius: 5px;
            margin-top: 15px;
        }
        
        .current-tokens {
            background: #d1ecf1;
            border: 1px solid #bee5eb;
            padding: 15px;
            border-radius: 5px;
            margin-top: 15px;
        }
        
        @media (max-width: 768px) {
            .content {
                grid-template-columns: 1fr;
            }
            
            .header h1 {
                font-size: 2em;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔐 登入系統測試頁面</h1>
            <p>測試所有認證功能的綜合界面</p>
        </div>
        
        <div class="content">
            <!-- 使用者註冊 -->
            <div class="section">
                <h2>📝 使用者註冊</h2>
                <div class="input-group">
                    <label for="register-email">電子郵件：</label>
                    <input type="email" id="register-email" placeholder="user@example.com">
                </div>
                <div class="input-group">
                    <label for="register-username">使用者名稱：</label>
                    <input type="text" id="register-username" placeholder="使用者名稱">
                </div>
                <div class="input-group">
                    <label for="register-password">密碼：</label>
                    <input type="password" id="register-password" placeholder="密碼">
                </div>
                <button class="btn success" onclick="registerUser()">註冊</button>
                <div id="register-response" class="response" style="display: none;"></div>
            </div>
            
            <!-- 使用者登入 -->
            <div class="section">
                <h2>🔑 使用者登入</h2>
                <div class="input-group">
                    <label for="login-email">電子郵件：</label>
                    <input type="email" id="login-email" placeholder="user@example.com">
                </div>
                <div class="input-group">
                    <label for="login-password">密碼：</label>
                    <input type="password" id="login-password" placeholder="密碼">
                </div>
                <button class="btn" onclick="loginUser()">登入</button>
                <div id="login-response" class="response" style="display: none;"></div>
                <div id="login-tokens" class="current-tokens" style="display: none;">
                    <h4>當前 Tokens：</h4>
                    <div id="access-token-display"></div>
                    <div id="refresh-token-display"></div>
                </div>
            </div>
            
            <!-- OAuth 登入 -->
            <div class="section">
                <h2>🌐 OAuth 登入</h2>
                <div class="input-group">
                    <label for="oauth-token">OAuth Access Token：</label>
                    <input type="text" id="oauth-token" placeholder="貼上 OAuth Token">
                </div>
                <div class="oauth-buttons">
                    <button class="btn oauth-btn google" onclick="oauthLogin('google')">Google</button>
                    <button class="btn oauth-btn facebook" onclick="oauthLogin('facebook')">Facebook</button>
                    <button class="btn oauth-btn github" onclick="oauthLogin('github')">GitHub</button>
                </div>
                <div id="oauth-response" class="response" style="display: none;"></div>
            </div>
            
            <!-- Token 重新整理 -->
            <div class="section">
                <h2>🔄 Token 重新整理</h2>
                <p><strong>說明：</strong>Refresh Token 現在自動從 httpOnly Cookie 讀取，無需手動輸入。</p>
                <button class="btn warning" onclick="manualRefreshToken()">重新整理 Access Token</button>
                <div id="refresh-response" class="response" style="display: none;"></div>
            </div>
            
            <!-- 取得使用者資訊 -->
            <div class="section">
                <h2>👤 使用者資訊</h2>
                <div class="input-group">
                    <label for="user-token">Access Token：</label>
                    <input type="text" id="user-token" placeholder="Access Token">
                </div>
                <button class="btn" onclick="getCurrentUser()">取得使用者資訊</button>
                <button class="btn" onclick="useStoredAccessToken()">使用儲存的 Access Token</button>
                <button class="btn warning" onclick="debugTokenValidation()">調試 Token 驗證</button>
                <div id="user-response" class="response" style="display: none;"></div>
                <div id="user-info-display" class="user-info" style="display: none;"></div>
            </div>
            
            <!-- 登出 -->
            <div class="section">
                <h2>🚪 登出</h2>
                <p><strong>說明：</strong>登出會自動處理 httpOnly Cookie 中的 Refresh Token。</p>
                <button class="btn danger" onclick="logoutUser()">安全登出</button>
                <button class="btn warning" onclick="clearStoredTokens()">清除本地 Access Token</button>
                <div id="logout-response" class="response" style="display: none;"></div>
            </div>
            
            <!-- 健康檢查 -->
            <div class="section">
                <h2>💚 系統狀態</h2>
                <button class="btn success" onclick="healthCheck()">健康檢查</button>
                <button class="btn" onclick="getApiInfo()">API 資訊</button>
                <button class="btn warning" onclick="showCurrentTokenStatus()">顯示 Token 狀態</button>
                <div id="health-response" class="response" style="display: none;"></div>
                <div id="token-status" class="current-tokens" style="display: none;">
                    <h4>當前 Token 狀態：</h4>
                    <div id="token-status-content"></div>
                </div>
            </div>
            
            <!-- Cookie 測試 -->
            <div class="section">
                <h2>🍪 Cookie 測試</h2>
                <p><strong>說明：</strong>測試 httpOnly Cookie 的設定和讀取。</p>
                <button class="btn" onclick="showAllCookies()">顯示所有 Cookies</button>
                <button class="btn warning" onclick="testRefreshTokenCookie()">測試 Refresh Token Cookie</button>
                <button class="btn danger" onclick="debugAuthHeader()">調試 Authorization Header</button>
                <button class="btn primary" onclick="debugCurrentToken()">檢查當前 Token</button>
                <div id="cookie-response" class="response" style="display: none;"></div>
            </div>
        </div>
    </div>

    <script>
        // Token 管理器
        class TokenManager {
            constructor() {
                this.accessToken = null;
                this.autoRefreshTimer = null;
            }
            
            setAccessToken(token) {
                this.accessToken = token;
                this.scheduleAutoRefresh();
            }
            
            getAccessToken() {
                return this.accessToken;
            }
            
            clearAccessToken() {
                this.accessToken = null;
                if (this.autoRefreshTimer) {
                    clearTimeout(this.autoRefreshTimer);
                    this.autoRefreshTimer = null;
                }
            }
            
            scheduleAutoRefresh() {
                // 在 Token 過期前 5 分鐘自動重新整理
                const refreshTime = (30 - 5) * 60 * 1000; // 25 分鐘
                if (this.autoRefreshTimer) {
                    clearTimeout(this.autoRefreshTimer);
                }
                this.autoRefreshTimer = setTimeout(() => {
                    this.refreshAccessToken();
                }, refreshTime);
            }
            
            async refreshAccessToken() {
                try {
                    const response = await fetch(`${API_BASE}/auth/refresh`, {
                        method: 'POST',
                        credentials: 'include' // 包含 cookies
                    });
                    
                    if (response.ok) {
                        const data = await response.json();
                        if (data.success && data.data.access_token) {
                            this.setAccessToken(data.data.access_token);
                            console.log('🔄 Access token 自動重新整理成功');
                        }
                    }
                } catch (error) {
                    console.error('❌ 自動重新整理失敗:', error);
                    this.clearAccessToken();
                }
            }
        }
        
        const tokenManager = new TokenManager();
        
        // API 基礎 URL
        const API_BASE = window.location.origin;
        
        // 顯示回應的通用函數
        function showResponse(elementId, data, isError = false) {
            const element = document.getElementById(elementId);
            element.style.display = 'block';
            element.className = isError ? 'response error' : 'response success';
            element.textContent = JSON.stringify(data, null, 2);
        }
        
        // 註冊使用者
        async function registerUser() {
            const email = document.getElementById('register-email').value;
            const username = document.getElementById('register-username').value;
            const password = document.getElementById('register-password').value;
            
            if (!email || !username || !password) {
                showResponse('register-response', { error: '請填寫所有欄位' }, true);
                return;
            }
            
            try {
                const response = await fetch(`${API_BASE}/auth/register`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, username, password })
                });
                
                const data = await response.json();
                showResponse('register-response', data, !response.ok);
            } catch (error) {
                showResponse('register-response', { error: error.message }, true);
            }
        }
        
        // 使用者登入
        async function loginUser() {
            const email = document.getElementById('login-email').value;
            const password = document.getElementById('login-password').value;
            
            if (!email || !password) {
                showResponse('login-response', { error: '請填寫電子郵件和密碼' }, true);
                return;
            }
            
            try {
                const response = await fetch(`${API_BASE}/auth/login`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include', // 包含 cookies
                    body: JSON.stringify({ email, password })
                });
                
                const data = await response.json();
                
                if (response.ok && data.success) {
                    // 儲存 access token 到記憶體
                    tokenManager.setAccessToken(data.data.access_token);
                    
                    // 顯示 tokens 和使用者資訊
                    document.getElementById('login-tokens').style.display = 'block';
                    document.getElementById('access-token-display').innerHTML = 
                        `<strong>Access Token:</strong><br><div class="token-display">${data.data.access_token}</div>`;
                    document.getElementById('refresh-token-display').innerHTML = 
                        `<strong>Refresh Token:</strong><br><div class="token-display">✅ 已存儲在 httpOnly Cookie 中</div>`;
                    
                    // 顯示使用者資訊
                    if (data.data.user) {
                        const userInfo = `
                            <h4>使用者資訊：</h4>
                            <p><strong>ID:</strong> ${data.data.user.id}</p>
                            <p><strong>電子郵件:</strong> ${data.data.user.email}</p>
                            <p><strong>使用者名稱:</strong> ${data.data.user.username}</p>
                            <p><strong>狀態:</strong> ${data.data.user.is_active ? '啟用' : '停用'}</p>
                        `;
                        document.getElementById('login-tokens').innerHTML += `<div class="user-info">${userInfo}</div>`;
                    }
                }
                
                showResponse('login-response', data, !response.ok || !data.success);
            } catch (error) {
                showResponse('login-response', { error: error.message }, true);
            }
        }
        
        // OAuth 登入
        async function oauthLogin(provider) {
            const token = document.getElementById('oauth-token').value;
            
            if (!token) {
                showResponse('oauth-response', { error: '請輸入 OAuth Token' }, true);
                return;
            }
            
            try {
                const response = await fetch(`${API_BASE}/auth/oauth/${provider}`, {
                    method: 'POST',
                    headers: { 
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    },
                    credentials: 'include' // 包含 cookies
                });
                
                const data = await response.json();
                
                if (response.ok && data.success) {
                    // 儲存 access token 到記憶體
                    tokenManager.setAccessToken(data.data.access_token);
                }
                
                showResponse('oauth-response', data, !response.ok || !data.success);
            } catch (error) {
                showResponse('oauth-response', { error: error.message }, true);
            }
        }
        
        // 重新整理 Token
        async function refreshToken() {
            try {
                const response = await fetch(`${API_BASE}/auth/refresh`, {
                    method: 'POST',
                    credentials: 'include' // 包含 cookies
                });
                
                const data = await response.json();
                
                if (response.ok && data.success) {
                    // 更新 access token
                    tokenManager.setAccessToken(data.data.access_token);
                    
                    // 更新顯示
                    document.getElementById('login-tokens').style.display = 'block';
                    document.getElementById('access-token-display').innerHTML = 
                        `<strong>新的 Access Token:</strong><br><div class="token-display">${data.data.access_token}</div>`;
                    document.getElementById('refresh-token-display').innerHTML = 
                        `<strong>Refresh Token:</strong><br><div class="token-display">✅ 已更新並存儲在 httpOnly Cookie 中</div>`;
                }
                
                showResponse('refresh-response', data, !response.ok || !data.success);
            } catch (error) {
                showResponse('refresh-response', { error: error.message }, true);
            }
        }
        
        // 手動重新整理按鈕
        function manualRefreshToken() {
            refreshToken();
        }
        
        // 取得當前使用者資訊
        async function getCurrentUser() {
            const token = document.getElementById('user-token').value || tokenManager.getAccessToken();
            
            if (!token) {
                showResponse('user-response', { error: '請先登入或輸入 Access Token' }, true);
                return;
            }
            
            try {
                const response = await fetch(`${API_BASE}/auth/me`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                
                const data = await response.json();
                
                if (response.ok && data.success) {
                    document.getElementById('user-info-display').style.display = 'block';
                    document.getElementById('user-info-display').innerHTML = `
                        <h4>使用者資訊：</h4>
                        <p><strong>ID:</strong> ${data.data.id}</p>
                        <p><strong>電子郵件:</strong> ${data.data.email}</p>
                        <p><strong>使用者名稱:</strong> ${data.data.username}</p>
                        <p><strong>狀態:</strong> ${data.data.is_active ? '啟用' : '停用'}</p>
                        <p><strong>建立時間:</strong> ${new Date(data.data.created_at).toLocaleString('zh-TW')}</p>
                        <p><strong>更新時間:</strong> ${new Date(data.data.updated_at).toLocaleString('zh-TW')}</p>
                    `;
                } else {
                    document.getElementById('user-info-display').style.display = 'none';
                }
                
                showResponse('user-response', data, !response.ok || !data.success);
            } catch (error) {
                showResponse('user-response', { error: error.message }, true);
            }
        }
        
        // 使用儲存的 Access Token
        function useStoredAccessToken() {
            const token = tokenManager.getAccessToken();
            if (token) {
                document.getElementById('user-token').value = token;
                getCurrentUser();
            } else {
                showResponse('user-response', { error: '沒有儲存的 Access Token，請先登入' }, true);
            }
        }
        
        // 調試 Token 驗證
        async function debugTokenValidation() {
            const token = tokenManager.getAccessToken();
            
            if (!token) {
                showResponse('user-response', { error: '沒有 Access Token，請先登入' }, true);
                return;
            }
            
            try {
                const response = await fetch(`${API_BASE}/auth/debug-token`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                
                const data = await response.json();
                showResponse('user-response', data, !response.ok || !data.success);
            } catch (error) {
                showResponse('user-response', { error: error.message }, true);
            }
        }
        
        // 登出使用者
        async function logoutUser() {
            const accessToken = tokenManager.getAccessToken();
            
            if (!accessToken) {
                showResponse('logout-response', { error: '需要先登入' }, true);
                return;
            }
            
            try {
                const response = await fetch(`${API_BASE}/auth/logout`, {
                    method: 'POST',
                    headers: { 
                        'Authorization': `Bearer ${accessToken}`
                    },
                    credentials: 'include' // 包含 cookies
                });
                
                const data = await response.json();
                
                if (response.ok && data.success) {
                    // 清除本地 access token
                    tokenManager.clearAccessToken();
                    
                    // 清除顯示
                    document.getElementById('login-tokens').style.display = 'none';
                    document.getElementById('user-info-display').style.display = 'none';
                }
                
                showResponse('logout-response', data, !response.ok || !data.success);
            } catch (error) {
                showResponse('logout-response', { error: error.message }, true);
            }
        }
        
        // 清除儲存的 Tokens
        function clearStoredTokens() {
            tokenManager.clearAccessToken();
            document.getElementById('login-tokens').style.display = 'none';
            document.getElementById('user-info-display').style.display = 'none';
            showResponse('logout-response', { 
                success: true, 
                message: '已清除本地 Access Token',
                timestamp: new Date().toISOString()
            });
        }
        
        // 健康檢查
        async function healthCheck() {
            try {
                const response = await fetch(`${API_BASE}/health`);
                const data = await response.json();
                showResponse('health-response', data, !response.ok);
            } catch (error) {
                showResponse('health-response', { error: error.message }, true);
            }
        }
        
        // 取得 API 資訊
        async function getApiInfo() {
            try {
                const response = await fetch(`${API_BASE}/`);
                const data = await response.json();
                showResponse('health-response', data, !response.ok);
            } catch (error) {
                showResponse('health-response', { error: error.message }, true);
            }
        }
        
        // 顯示當前 Token 狀態
        function showCurrentTokenStatus() {
            const accessToken = tokenManager.getAccessToken();
            const statusElement = document.getElementById('token-status');
            const contentElement = document.getElementById('token-status-content');
            
            statusElement.style.display = 'block';
            
            if (accessToken) {
                // 嘗試解析 JWT payload
                try {
                    const payload = JSON.parse(atob(accessToken.split('.')[1]));
                    const expiresAt = new Date(payload.exp * 1000);
                    const now = new Date();
                    const timeLeft = Math.max(0, Math.floor((expiresAt - now) / 1000));
                    
                    contentElement.innerHTML = `
                        <p><strong>✅ Access Token:</strong> 已存在</p>
                        <p><strong>使用者 ID:</strong> ${payload.sub}</p>
                        <p><strong>Email:</strong> ${payload.email}</p>
                        <p><strong>過期時間:</strong> ${expiresAt.toLocaleString('zh-TW')}</p>
                        <p><strong>剩餘時間:</strong> ${timeLeft} 秒</p>
                        <p><strong>🍪 Refresh Token:</strong> 存儲在 httpOnly Cookie 中</p>
                    `;
                } catch (e) {
                    contentElement.innerHTML = `
                        <p><strong>⚠️ Access Token:</strong> 格式無效</p>
                        <p><strong>🍪 Refresh Token:</strong> 存儲在 httpOnly Cookie 中</p>
                    `;
                }
            } else {
                contentElement.innerHTML = `
                    <p><strong>❌ Access Token:</strong> 不存在</p>
                    <p><strong>🍪 Refresh Token:</strong> 可能存在於 httpOnly Cookie 中</p>
                    <p><strong>建議:</strong> 先登入或使用重新整理功能</p>
                `;
            }
        }
        
        // 顯示所有 Cookies (只能顯示非 httpOnly 的)
        function showAllCookies() {
            const cookies = document.cookie.split(';').map(cookie => cookie.trim());
            showResponse('cookie-response', {
                message: '可見的 Cookies (httpOnly Cookie 無法透過 JavaScript 讀取)',
                cookies: cookies.length > 0 ? cookies : ['無可見的 cookies'],
                note: 'Refresh Token 存儲在 httpOnly Cookie 中，無法透過 JavaScript 直接讀取'
            });
        }
        
        // 測試 Refresh Token Cookie
        async function testRefreshTokenCookie() {
            showResponse('cookie-response', {
                message: '正在測試 Refresh Token Cookie...',
                info: 'httpOnly Cookie 只能透過伺服器端 API 讀取'
            });
            
            // 嘗試呼叫 refresh API 來測試 cookie
            try {
                const response = await fetch(`${API_BASE}/auth/refresh`, {
                    method: 'POST',
                    credentials: 'include'
                });
                
                const data = await response.json();
                
                if (response.ok && data.success) {
                    showResponse('cookie-response', {
                        message: '✅ Refresh Token Cookie 測試成功',
                        result: 'Cookie 存在且有效',
                        new_access_token: '已取得新的 Access Token'
                    });
                    
                    // 更新 access token
                    tokenManager.setAccessToken(data.data.access_token);
                } else {
                    showResponse('cookie-response', {
                        message: '❌ Refresh Token Cookie 測試失敗',
                        result: data.message || 'Cookie 不存在或已過期'
                    }, true);
                }
            } catch (error) {
                showResponse('cookie-response', {
                    message: '❌ 測試過程中發生錯誤',
                    error: error.message
                }, true);
            }
        }
        
        // 調試 Authorization Header
        async function debugAuthHeader() {
            const accessToken = tokenManager.getAccessToken();
            
            if (!accessToken) {
                showResponse('cookie-response', {
                    message: '❌ 沒有 Access Token',
                    suggestion: '請先登入'
                }, true);
                return;
            }
            
            try {
                // 解析 JWT payload
                const payload = JSON.parse(atob(accessToken.split('.')[1]));
                const now = Math.floor(Date.now() / 1000);
                const isExpired = payload.exp < now;
                
                showResponse('cookie-response', {
                    message: '🔍 Access Token 調試資訊',
                    token_preview: accessToken.substring(0, 50) + '...',
                    payload: {
                        user_id: payload.sub,
                        email: payload.email,
                        type: payload.type,
                        expires_at: new Date(payload.exp * 1000).toLocaleString('zh-TW'),
                        is_expired: isExpired,
                        time_left: isExpired ? 0 : payload.exp - now
                    },
                    headers_to_send: {
                        'Authorization': `Bearer ${accessToken.substring(0, 20)}...`
                    }
                });
                
                // 測試實際的 API 呼叫
                const response = await fetch(`${API_BASE}/auth/me`, {
                    headers: { 'Authorization': `Bearer ${accessToken}` }
                });
                
                const responseData = await response.json();
                
                showResponse('cookie-response', {
                    ...{
                        message: '🔍 Access Token 調試資訊',
                        token_preview: accessToken.substring(0, 50) + '...',
                        payload: {
                            user_id: payload.sub,
                            email: payload.email,
                            type: payload.type,
                            expires_at: new Date(payload.exp * 1000).toLocaleString('zh-TW'),
                            is_expired: isExpired,
                            time_left: isExpired ? 0 : payload.exp - now
                        },
                        headers_to_send: {
                            'Authorization': `Bearer ${accessToken.substring(0, 20)}...`
                        }
                    },
                    api_test_result: {
                        status_code: response.status,
                        success: response.ok,
                        response_data: responseData
                    }
                }, !response.ok);
                
            } catch (e) {
                showResponse('cookie-response', {
                    message: '❌ Token 解析失敗',
                    error: e.message,
                    token_preview: accessToken ? accessToken.substring(0, 50) + '...' : 'null'
                }, true);
            }
        }
        
        // 檢查當前 Token 狀態
        function debugCurrentToken() {
            const token = tokenManager.getAccessToken();
            
            if (!token) {
                showResponse('cookie-response', {
                    message: '❌ 沒有 Access Token',
                    suggestion: '請先登入以取得 Token',
                    refresh_token_status: '🍪 Refresh Token 可能存在於 httpOnly cookie 中',
                    next_steps: [
                        '1. 點擊「登入」按鈕進行登入',
                        '2. 或點擊「重新整理 Token」嘗試使用 Refresh Token'
                    ]
                }, true);
                return;
            }
            
            try {
                // 解析 JWT payload
                const parts = token.split('.');
                if (parts.length !== 3) {
                    throw new Error('JWT 格式不正確，應該有3個部分');
                }
                
                const header = JSON.parse(atob(parts[0]));
                const payload = JSON.parse(atob(parts[1]));
                const signature = parts[2];
                
                const now = new Date();
                const expiresAt = new Date(payload.exp * 1000);
                const issuedAt = new Date(payload.iat * 1000);
                const timeLeft = Math.max(0, Math.floor((expiresAt - now) / 1000));
                const isExpired = now > expiresAt;
                
                showResponse('cookie-response', {
                    message: '🔍 JWT Token 完整診斷',
                    token_status: isExpired ? '❌ 已過期' : '✅ 有效',
                    header: header,
                    payload: {
                        user_id: payload.sub,
                        email: payload.email,
                        token_type: payload.type,
                        issued_at: issuedAt.toLocaleString('zh-TW'),
                        expires_at: expiresAt.toLocaleString('zh-TW'),
                        time_left: isExpired ? '已過期' : `${timeLeft} 秒 (${Math.floor(timeLeft/60)} 分鐘)`
                    },
                    token_structure: {
                        header_length: parts[0].length,
                        payload_length: parts[1].length,
                        signature_length: signature.length,
                        total_length: token.length
                    },
                    warnings: isExpired ? ['⚠️ Token 已過期，需要重新整理'] : [],
                    suggestions: isExpired ? [
                        '點擊「重新整理 Token」按鈕',
                        '或重新登入取得新的 Token'
                    ] : [
                        'Token 狀態良好，可以正常使用 API'
                    ]
                }, isExpired);
            } catch (error) {
                showResponse('cookie-response', {
                    message: '❌ Token 解析失敗',
                    error: error.message,
                    token_preview: token.substring(0, 50) + '...',
                    token_length: token.length,
                    possible_causes: [
                        'Token 格式不正確',
                        'Token 被截斷或損壞',
                        'Base64 編碼問題'
                    ],
                    suggestions: [
                        '重新登入取得新的 Token',
                        '檢查 Token 是否完整'
                    ]
                }, true);
            }
        }
        
        // 頁面載入時自動執行健康檢查
        window.addEventListener('load', function() {
            healthCheck();
            showCurrentTokenStatus();
        });
    </script>
</body>
</html>
    """
    
    return HTMLResponse(content=html_content)


@app.get("/", summary="根路徑")
async def root():
    """API 根路徑，回傳服務狀態"""
    from app.utils import ResponseHelper
    return ResponseHelper.success(
        message="FastAPI JWT Authentication Server",
        data={
            "version": "1.0.0",
            "status": "running",
            "docs": "/docs",
            "redoc": "/redoc",
            "test_page": "/test-login"
        }
    )


@app.get("/health", summary="健康檢查")
async def health_check():
    """服務健康檢查端點"""
    from app.utils import ResponseHelper
    try:
        # 測試資料庫連接
        from app.database import DatabaseManager
        with DatabaseManager.get_connection():
            pass
        
        if os.getenv("ENVIRONMENT", "development") == "development":
            logger.debug("✅ 資料庫連接正常")
        
        return ResponseHelper.success(
            message="服務健康狀態良好",
            data={
                "status": "healthy",
                "database": "connected",
                "timestamp": datetime.now().isoformat()
            }
        )
    except Exception as e:
        logger.error(f"❌ 健康檢查失敗: {str(e)}")
        return ResponseHelper.error(
            message="服務健康檢查失敗",
            error_code="HEALTH_CHECK_FAILED",
            details={"error": str(e)},
            status_code=503
        )


# 全域異常處理器
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """HTTP 異常處理器 - 轉換為統一 API 格式"""
    from app.utils import ResponseHelper
    import json
    
    def json_serializer(obj):
        """自定義 JSON 序列化器，處理 datetime 對象"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    # 對於認證相關的錯誤，使用特殊處理
    if exc.status_code == 401:
        error_response = ResponseHelper.error(
            message="認證失敗",
            error_code="AUTHENTICATION_FAILED",
            details={"detail": exc.detail},
            status_code=401
        )
        return JSONResponse(
            status_code=401,
            content=json.loads(error_response.json()),
            headers=exc.headers
        )
    elif exc.status_code == 403:
        error_response = ResponseHelper.error(
            message="權限不足",
            error_code="AUTHORIZATION_FAILED", 
            details={"detail": exc.detail},
            status_code=403
        )
        return JSONResponse(
            status_code=403,
            content=json.loads(error_response.json())
        )
    else:
        error_response = ResponseHelper.error(
            message="請求處理失敗",
            error_code="REQUEST_FAILED",
            details={"detail": exc.detail},
            status_code=exc.status_code
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=json.loads(error_response.json()),
            headers=exc.headers
        )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全域異常處理器"""
    from app.utils import ResponseHelper
    import json
    
    if os.getenv("ENVIRONMENT", "development") == "development":
        logger.error(f"未處理的異常: {str(exc)}", exc_info=True)
        error_response = ResponseHelper.error(
            message="伺服器內部錯誤",
            error_code="INTERNAL_SERVER_ERROR",
            details={
                "error": str(exc),
                "type": type(exc).__name__
            },
            status_code=500
        )
        return JSONResponse(
            status_code=500,
            content=json.loads(error_response.json())
        )
    else:
        logger.error(f"伺服器錯誤: {type(exc).__name__}")
        error_response = ResponseHelper.error(
            message="伺服器內部錯誤",
            error_code="INTERNAL_SERVER_ERROR",
            status_code=500
        )
        return JSONResponse(
            status_code=500,
            content=json.loads(error_response.json())
        )


# 中間件：請求日誌記錄 (僅開發模式)
if os.getenv("ENVIRONMENT", "development") == "development":
    @app.middleware("http")
    async def log_requests(request, call_next):
        """記錄 HTTP 請求 (開發模式)"""
        logger.debug(f"📥 {request.method} {request.url}")
        response = await call_next(request)
        logger.debug(f"📤 回應狀態: {response.status_code}")
        return response 