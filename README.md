# FastAPI JWT Authentication Server

一個使用 FastAPI 和 Authlib 構建的現代化 JWT 認證服務器實踐模板，支援 OAuth 整合（Google、Facebook、GitHub）和 Azure SQL 資料庫。

## 📘 關於此專案

這是一個**即用型登入系統模板**，讓您能夠**快速啟用完整的認證服務**，無需從零開始建構：

- ⚡ **即開即用**: 幾分鐘內啟動完整的登入認證服務
- 🔧 **快速整合**: 為新專案提供現成的認證系統基礎架構
- 📚 **最佳實踐**: 採用業界標準的安全認證設計模式
- 🛠️ **高度可擴展**: 模組化設計，可根據業務需求自由調整

> **適用場景**: 適合需要快速建立使用者認證系統的專案，支援傳統登入和社群登入整合。建議依據具體需求進行安全性評估和功能調整。

## 🚀 功能特色

- **JWT 認證**: 完整的存取和重新整理 Token 機制
- **OAuth 整合**: 支援 Google、Facebook、GitHub 登入
- **Azure SQL**: 使用 pymssql 連接 Azure SQL Database
- **Clean Architecture**: 清晰的程式碼結構和模組化設計
- **自動文件**: FastAPI 自動生成的 API 文件
- **安全性**: 密碼雜湊、Token 撤銷、會話管理

## 📋 系統需求

- Python 3.8+
- Azure SQL Database 或 SQL Server
- ODBC Driver 18 for SQL Server

## 🛠️ 安裝步驟

### 1. 克隆專案

```bash
git clone <repository-url>
cd login-template
```

### 2. 建立虛擬環境

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. 安裝依賴

```bash
pip install -r requirements.txt
```

### 4. 設定環境變數

建立 `.env` 檔案並填入您的設定：

```env
# JWT 設定
SECRET_KEY=your-very-long-and-secure-secret-key-minimum-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Azure SQL 資料庫設定
DB_SERVER=your-server.database.windows.net
DB_DATABASE=your-database-name
DB_USERNAME=your-username
DB_PASSWORD=your-password

# OAuth 設定 (選填)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
FACEBOOK_CLIENT_ID=your-facebook-client-id
FACEBOOK_CLIENT_SECRET=your-facebook-client-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# 前端 URL
FRONTEND_URL=http://localhost:3000

# 環境設定 (development/production)
ENVIRONMENT=development
```

### 5. 建立資料庫表格

在您的 Azure SQL Database 中執行以下 SQL 語句：

```sql
-- FastAPI JWT Authentication Server 資料庫表格建立腳本
-- 適用於 Azure SQL Database

-- 建立使用者表格
CREATE TABLE users (
    id INT IDENTITY(1,1) PRIMARY KEY,
    email NVARCHAR(255) NOT NULL UNIQUE,
    username NVARCHAR(100) NOT NULL,
    password_hash NVARCHAR(255) NULL, -- OAuth 使用者可能沒有密碼
    provider NVARCHAR(50) NULL, -- OAuth 提供者 (google, facebook, github)
    provider_id NVARCHAR(255) NULL, -- OAuth 提供者的使用者 ID
    is_active BIT NOT NULL DEFAULT 1,
    created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    updated_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    last_login DATETIME2 NULL,
    
    -- 索引
    INDEX IX_users_email (email),
    INDEX IX_users_provider_provider_id (provider, provider_id),
    INDEX IX_users_created_at (created_at)
);

-- 建立重新整理 Token 表格
CREATE TABLE refresh_tokens (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    token_hash NVARCHAR(255) NOT NULL UNIQUE, -- Token 的 SHA-256 雜湊值
    expires_at DATETIME2 NOT NULL,
    is_revoked BIT NOT NULL DEFAULT 0,
    created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    
    -- 外鍵約束
    CONSTRAINT FK_refresh_tokens_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    
    -- 索引
    INDEX IX_refresh_tokens_user_id (user_id),
    INDEX IX_refresh_tokens_token_hash (token_hash),
    INDEX IX_refresh_tokens_expires_at (expires_at)
);

PRINT '核心資料庫表格建立完成！';
PRINT '已建立 users 和 refresh_tokens 表格';
```

## 🚀 啟動服務

### 開發模式（含詳細日誌）

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 生產模式

```bash
# 設定環境變數
export ENVIRONMENT=production

# 啟動服務
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

服務將在 http://localhost:8000 啟動

## 📚 API 文件

啟動服務後，您可以訪問：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **測試頁面**: http://localhost:8000/test-login

## 🔐 API 端點

### 認證相關

| 方法 | 端點 | 描述 |
|------|------|------|
| POST | `/auth/register` | 註冊新使用者 |
| POST | `/auth/login` | 使用者登入 |
| POST | `/auth/refresh` | 重新整理 Token |
| POST | `/auth/oauth/{provider}` | OAuth 登入 |
| GET | `/auth/me` | 取得當前使用者資訊 |
| POST | `/auth/logout` | 使用者登出 |

### 系統相關

| 方法 | 端點 | 描述 |
|------|------|------|
| GET | `/` | 服務根路徑 |
| GET | `/health` | 健康檢查 |
| GET | `/test-login` | 測試登入頁面 |

## 📊 統一 API 回應格式

所有 API 現在都回傳一致的格式：

### 成功回應格式
```json
{
  "success": true,
  "status_code": 200,
  "message": "操作成功",
  "data": { ... },
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### 錯誤回應格式
```json
{
  "success": false,
  "status_code": 400,
  "message": "操作失敗",
  "error_code": "ERROR_CODE",
  "details": { ... },
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

## 💡 使用範例

### 1. 註冊使用者

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "securepassword123"
  }'
```

### 2. 使用者登入

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

### 3. 使用 Token 訪問受保護的端點

```bash
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. 重新整理 Token

```bash
curl -X POST "http://localhost:8000/auth/refresh" \
  -H "Content-Type: application/json" \
  --cookie "refresh_token=YOUR_REFRESH_TOKEN"
```

## ✅ 已實現功能

### 核心認證功能
- ✅ **使用者註冊**: 電子郵件 + 密碼註冊
- ✅ **使用者登入**: 安全的密碼驗證
- ✅ **JWT Token 管理**: Access Token + Refresh Token 機制
- ✅ **Token 輪替**: 每次重新整理時產生新的 Refresh Token
- ✅ **使用者登出**: Token 撤銷功能
- ✅ **使用者資訊取得**: 受保護的使用者資料端點

### OAuth 社群登入
- ✅ **Google OAuth**: Google 帳戶登入整合
- ✅ **Facebook OAuth**: Facebook 帳戶登入整合
- ✅ **GitHub OAuth**: GitHub 帳戶登入整合
- ✅ **OAuth 使用者資料同步**: 自動建立和更新使用者資料

### 安全性功能
- ✅ **密碼安全雜湊**: Argon2id 算法加密
- ✅ **Token 安全存儲**: Refresh Token 雜湊存儲
- ✅ **httpOnly Cookie**: 防止 XSS 攻擊的 Cookie 設定
- ✅ **CORS 支援**: 跨域請求處理
- ✅ **環境變數配置**: 敏感資訊外部化管理

### 資料庫整合
- ✅ **Azure SQL Database**: 支援 Azure SQL 和 SQL Server
- ✅ **連接池管理**: 高效的資料庫連接管理
- ✅ **資料表設計**: 完整的使用者和 Token 管理表格
- ✅ **資料庫初始化**: 自動建立所需表格的 SQL 腳本

### API 和文件
- ✅ **RESTful API**: 標準的 REST API 設計
- ✅ **統一回應格式**: 一致的 API 回應結構
- ✅ **自動 API 文件**: Swagger UI 和 ReDoc
- ✅ **測試頁面**: 內建的登入測試介面

## 🚧 尚未實現功能

### 安全性增強
- ⏳ **Rate Limiting**: API 請求頻率限制
- ⏳ **Token 黑名單**: 立即撤銷 Access Token 機制
- ⏳ **多因素認證 (MFA)**: TOTP、SMS 或 Email 驗證
- ⏳ **密碼強度檢查**: 密碼複雜度驗證
- ⏳ **帳戶鎖定機制**: 多次失敗登入後暫時鎖定
- ⏳ **IP 白名單/黑名單**: 基於 IP 的存取控制

### 使用者管理
- ⏳ **電子郵件驗證**: 註冊後的電子郵件確認
- ⏳ **忘記密碼**: 密碼重設功能
- ⏳ **使用者個人資料管理**: 更新使用者資訊
- ⏳ **帳戶刪除**: 使用者帳戶刪除功能
- ⏳ **使用者角色管理**: RBAC (Role-Based Access Control)
- ⏳ **管理員介面**: 使用者管理後台

### 高級功能
- ⏳ **審計日誌**: 詳細的操作記錄和監控
- ⏳ **會話管理**: 多設備登入管理
- ⏳ **API 版本控制**: 向後相容的 API 版本管理
- ⏳ **內容快取**: Redis 快取機制
- ⏳ **背景任務**: Celery 非同步任務處理
- ⏳ **通知系統**: 電子郵件、推播通知

### 監控和維運
- ⏳ **健康檢查增強**: 詳細的系統狀態監控
- ⏳ **效能監控**: APM (Application Performance Monitoring)
- ⏳ **錯誤追蹤**: 詳細的錯誤報告和分析
- ⏳ **Prometheus 指標**: 系統指標收集
- ⏳ **日誌聚合**: 結構化日誌管理

### 部署和 DevOps
- ⏳ **Docker 容器化**: 完整的 Docker 部署配置
- ⏳ **CI/CD Pipeline**: 自動化部署流程
- ⏳ **Kubernetes 部署**: K8s 部署配置
- ⏳ **負載平衡**: 多實例部署支援
- ⏳ **自動化測試**: 單元測試、整合測試

### 文件和工具
- ⏳ **中文 API 文件**: 完整的中文 API 說明
- ⏳ **部署指南**: 詳細的生產環境部署說明
- ⏳ **開發工具**: 開發環境設置腳本
- ⏳ **程式碼生成器**: 自動生成 CRUD 程式碼
- ⏳ **遷移腳本**: 資料庫版本管理

> 💡 **開發建議**: 您可以根據專案需求選擇優先實現的功能。建議先從安全性增強和使用者管理功能開始。

## 🏗️ 專案結構

```
login-template/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 應用程式入口
│   ├── config.py            # 配置設定
│   ├── models.py            # Pydantic 模型
│   ├── database.py          # 資料庫操作
│   ├── auth.py              # 認證邏輯
│   ├── oauth.py             # OAuth 整合
│   ├── utils.py             # 工具函數
│   └── routers/
│       ├── __init__.py
│       └── auth.py          # 認證路由
├── requirements.txt         # Python 依賴
├── .env.example            # 環境變數範例 (需建立 .env 檔案)
├── .gitignore              # Git 忽略檔案
└── README.md               # 專案說明
```

> **注意**: 原本的 `database/` 資料夾已移除，SQL 建立脚本已整合到此 README 文件中。

## 🔧 OAuth 設定

### Google OAuth

1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 建立新專案或選擇現有專案
3. 啟用 Google+ API
4. 建立 OAuth 2.0 客戶端 ID
5. 設定重定向 URI

### Facebook OAuth

1. 前往 [Facebook Developers](https://developers.facebook.com/)
2. 建立新應用程式
3. 添加 Facebook Login 產品
4. 設定重定向 URI

### GitHub OAuth

1. 前往 [GitHub Settings > Developer settings](https://github.com/settings/developers)
2. 建立新的 OAuth App
3. 設定回調 URL

## 🗄️ 資料庫結構

### 主要資料表

- **users**: 儲存使用者基本資訊和 OAuth 資料
- **refresh_tokens**: 管理重新整理 Token

### 資料表詳細結構

#### users 表格
| 欄位 | 類型 | 說明 |
|------|------|------|
| id | INT IDENTITY | 主鍵，自動遞增 |
| email | NVARCHAR(255) | 使用者電子郵件，唯一索引 |
| username | NVARCHAR(100) | 使用者名稱 |
| password_hash | NVARCHAR(255) | 密碼雜湊值（OAuth 用戶可為 NULL） |
| provider | NVARCHAR(50) | OAuth 提供者（google、facebook、github） |
| provider_id | NVARCHAR(255) | OAuth 提供者的用戶 ID |
| is_active | BIT | 帳戶啟用狀態 |
| created_at | DATETIME2 | 建立時間 |
| updated_at | DATETIME2 | 更新時間 |
| last_login | DATETIME2 | 最後登入時間 |

#### refresh_tokens 表格
| 欄位 | 類型 | 說明 |
|------|------|------|
| id | INT IDENTITY | 主鍵，自動遞增 |
| user_id | INT | 使用者 ID，外鍵 |
| token_hash | NVARCHAR(255) | Token 的 SHA-256 雜湊值 |
| expires_at | DATETIME2 | 過期時間 |
| is_revoked | BIT | 是否已撤銷 |
| created_at | DATETIME2 | 建立時間 |

## 🔒 安全性功能

### 已實現的安全措施

1. **短期 Access Token**: 30 分鐘過期，降低被盜用風險
2. **Refresh Token 雜湊存儲**: 資料庫洩露時保護原始 Token
3. **Token 撤銷機制**: 支援登出時撤銷 Refresh Token
4. **密碼安全雜湊**: 使用 Argon2id 算法
5. **Token 輪替**: 每次重新整理時產生新的 Refresh Token
6. **httpOnly Cookie**: Refresh Token 透過 httpOnly Cookie 傳輸

### Token 安全性改善

#### 前端 Token 存儲策略
- **Access Token**: 存儲在記憶體中（防止 XSS 攻擊）
- **Refresh Token**: 存儲在 httpOnly Cookie 中（防止 XSS 攻擊）

#### Token 輪替機制
- 每次使用 Refresh Token 時自動產生新的 Refresh Token
- 舊的 Refresh Token 立即撤銷
- 提高安全性，防止 Token 重放攻擊

### Cookie 安全設定
```python
response.set_cookie(
    key="refresh_token",
    value=refresh_token,
    httponly=True,      # 防止 XSS
    secure=True,        # 生產環境使用 HTTPS
    samesite="lax",     # CSRF 保護
    max_age=7 * 24 * 60 * 60  # 7 天過期
)
```

## 🚨 安全建議

### 生產環境設定

1. **環境變數配置**
   - 使用強密碼作為 `SECRET_KEY`（至少 32 字符）
   - 設定 `ENVIRONMENT=production`
   - 絕不在程式碼中硬編碼敏感資訊

2. **HTTPS 配置**
   - 生產環境必須使用 HTTPS
   - 設定 `secure=True` 用於 cookies
   - 配置安全標頭（HSTS、CSP 等）

3. **資料庫安全**
   - 使用強密碼
   - 限制資料庫存取權限
   - 定期備份資料庫
   - 使用連接池

4. **監控和日誌**
   - 設定異常登入行為告警
   - 監控 API 使用量
   - 記錄重要安全事件

### 建議改善項目

1. **Rate Limiting**
   ```python
   from slowapi import Limiter, _rate_limit_exceeded_handler
   from slowapi.util import get_remote_address

   limiter = Limiter(key_func=get_remote_address)

   @router.post("/login")
   @limiter.limit("5/minute")  # 每分鐘最多 5 次登入嘗試
   async def login(request: Request, ...):
       pass
   ```

2. **Token 黑名單機制**
   - 考慮使用 Redis 儲存撤銷的 Access Token
   - 實現立即撤銷功能

3. **多因素認證 (MFA)**
   - 考慮添加 TOTP（Time-based One-Time Password）
   - 支援 SMS 或 Email 驗證

4. **審計日誌**
   ```python
   import logging

   audit_logger = logging.getLogger('audit')

   async def log_login_attempt(email: str, success: bool, ip_address: str):
       audit_logger.info(f"Login attempt - Email: {email}, Success: {success}, IP: {ip_address}")
   ```

## 📱 前端整合建議

### Token 管理器範例

```javascript
class TokenManager {
    constructor() {
        this.accessToken = null;
        this.autoRefreshTimer = null;
    }
    
    setAccessToken(token) {
        this.accessToken = token;
        this.scheduleAutoRefresh(); // 自動在過期前重新整理
    }
    
    scheduleAutoRefresh() {
        // 在 Token 過期前 5 分鐘自動重新整理
        const refreshTime = (30 - 5) * 60 * 1000; // 25 分鐘
        this.autoRefreshTimer = setTimeout(() => {
            this.refreshAccessToken();
        }, refreshTime);
    }
    
    async refreshAccessToken() {
        try {
            const response = await fetch('/auth/refresh', {
                method: 'POST',
                credentials: 'include' // 重要：包含 cookies
            });
            
            if (response.ok) {
                const data = await response.json();
                this.setAccessToken(data.data.access_token);
            }
        } catch (error) {
            console.error('Token refresh failed:', error);
        }
    }
}
```

### API 請求範例

```javascript
// 登入
const response = await fetch('/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include', // 重要：包含 cookies
    body: JSON.stringify({ email, password })
});

// 使用 Access Token 訪問受保護的端點
const response = await fetch('/auth/me', {
    headers: { 
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
    },
    credentials: 'include'
});

// 登出
const response = await fetch('/auth/logout', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${accessToken}` },
    credentials: 'include' // 重要：包含 cookies
});
```

## 🧪 測試建議

### 基本功能測試
1. 註冊新使用者
2. 登入並檢查 Token 狀態
3. 使用 Access Token 取得使用者資訊
4. 手動重新整理 Token
5. 登出並確認 Token 清除

### 安全性測試
1. 檢查 httpOnly Cookie 設定
2. 測試 XSS 攻擊防護（JavaScript 無法讀取 refresh token）
3. 測試 Token 過期處理
4. 測試自動 Token 重新整理

## 🚀 部署建議

### Docker 部署

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 環境變數設定

```bash
# .env 檔案範例
SECRET_KEY=your-very-long-and-secure-secret-key-minimum-32-characters
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
DB_SERVER=your-server.database.windows.net
DB_DATABASE=your-database-name
DB_USERNAME=your-username
DB_PASSWORD=your-secure-database-password
FRONTEND_URL=https://your-frontend-domain.com
ENVIRONMENT=production
```

## 📄 更新紀錄

### v1.0.0 - 主要功能
- ✅ JWT 認證系統
- ✅ OAuth 整合（Google、Facebook、GitHub）
- ✅ 統一 API 回應格式
- ✅ Token 輪替機制
- ✅ httpOnly Cookie 支援
- ✅ 詳細的程式碼註解
- ✅ 完整的安全性措施

### 主要改善項目
- **安全性改善**: 移除硬編碼密碼，使用環境變數
- **Token 管理**: 實現 Token 輪替和 httpOnly Cookie
- **API 統一**: 所有回應使用統一格式
- **程式碼品質**: 添加詳細中文註解
- **技術文件**: 整合所有說明文件

## 📄 授權

本專案使用 MIT 授權條款。 