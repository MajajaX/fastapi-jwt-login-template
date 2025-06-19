# FastAPI JWT Authentication Server

A modern JWT authentication server template built with FastAPI and Authlib, supporting OAuth integration (Google, Facebook, GitHub) and Azure SQL Database.

## 📘 About This Project

This is a **ready-to-use authentication system template** that allows you to **quickly deploy a complete authentication service** without building from scratch:

- ⚡ **Ready to Use**: Launch a complete authentication service in minutes
- 🔧 **Quick Integration**: Provides ready-made authentication infrastructure for new projects
- 📚 **Best Practices**: Adopts industry-standard secure authentication design patterns
- 🛠️ **Highly Scalable**: Modular design, freely adjustable according to business requirements

> **Use Cases**: Suitable for projects that need to quickly establish user authentication systems, supporting both traditional login and social login integration. Security assessment and functional adjustment according to specific requirements are recommended.

## 🚀 Key Features

- **JWT Authentication**: Complete access and refresh token mechanism
- **OAuth Integration**: Support for Google, Facebook, GitHub login
- **Azure SQL**: Connect to Azure SQL Database using pymssql
- **Clean Architecture**: Clear code structure and modular design
- **Auto Documentation**: FastAPI auto-generated API documentation
- **Security**: Password hashing, token revocation, session management

## 📋 System Requirements

- Python 3.8+
- Azure SQL Database or SQL Server
- ODBC Driver 18 for SQL Server

## 🛠️ Installation Steps

### 1. Clone the Project

```bash
git clone <repository-url>
cd login-template
```

### 2. Create Virtual Environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file and fill in your settings:

```env
# JWT Settings
SECRET_KEY=your-very-long-and-secure-secret-key-minimum-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Azure SQL Database Settings
DB_SERVER=your-server.database.windows.net
DB_DATABASE=your-database-name
DB_USERNAME=your-username
DB_PASSWORD=your-password

# OAuth Settings (Optional)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
FACEBOOK_CLIENT_ID=your-facebook-client-id
FACEBOOK_CLIENT_SECRET=your-facebook-client-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# Frontend URL
FRONTEND_URL=http://localhost:3000

# Environment Settings (development/production)
ENVIRONMENT=development
```

### 5. Create Database Tables

Execute the following SQL statements in your Azure SQL Database:

```sql
-- FastAPI JWT Authentication Server Database Table Creation Script
-- For Azure SQL Database

-- Create users table
CREATE TABLE users (
    id INT IDENTITY(1,1) PRIMARY KEY,
    email NVARCHAR(255) NOT NULL UNIQUE,
    username NVARCHAR(100) NOT NULL,
    password_hash NVARCHAR(255) NULL, -- OAuth users may not have password
    provider NVARCHAR(50) NULL, -- OAuth provider (google, facebook, github)
    provider_id NVARCHAR(255) NULL, -- OAuth provider user ID
    is_active BIT NOT NULL DEFAULT 1,
    created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    updated_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    last_login DATETIME2 NULL,
    
    -- Indexes
    INDEX IX_users_email (email),
    INDEX IX_users_provider_provider_id (provider, provider_id),
    INDEX IX_users_created_at (created_at)
);

-- Create refresh tokens table
CREATE TABLE refresh_tokens (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    token_hash NVARCHAR(255) NOT NULL UNIQUE, -- SHA-256 hash of token
    expires_at DATETIME2 NOT NULL,
    is_revoked BIT NOT NULL DEFAULT 0,
    created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    
    -- Foreign key constraints
    CONSTRAINT FK_refresh_tokens_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    
    -- Indexes
    INDEX IX_refresh_tokens_user_id (user_id),
    INDEX IX_refresh_tokens_token_hash (token_hash),
    INDEX IX_refresh_tokens_expires_at (expires_at)
);

PRINT 'Core database tables created successfully!';
PRINT 'Created users and refresh_tokens tables';
```

## 🚀 Start Service

### Development Mode (with detailed logging)

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
# Set environment variable
export ENVIRONMENT=production

# Start service
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The service will start at http://localhost:8000

## 📚 API Documentation

After starting the service, you can access:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Test Page**: http://localhost:8000/test-login

## 🔐 API Endpoints

### Authentication Related

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | User login |
| POST | `/auth/refresh` | Refresh token |
| POST | `/auth/oauth/{provider}` | OAuth login |
| GET | `/auth/me` | Get current user info |
| POST | `/auth/logout` | User logout |

### System Related

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Service root path |
| GET | `/health` | Health check |
| GET | `/test-login` | Test login page |

## 📊 Unified API Response Format

All APIs now return a consistent format:

### Success Response Format
```json
{
  "success": true,
  "status_code": 200,
  "message": "Operation successful",
  "data": { ... },
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### Error Response Format
```json
{
  "success": false,
  "status_code": 400,
  "message": "Operation failed",
  "error_code": "ERROR_CODE",
  "details": { ... },
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

## 💡 Usage Examples

### 1. Register User

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "securepassword123"
  }'
```

### 2. User Login

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

### 3. Access Protected Endpoint with Token

```bash
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. Refresh Token

```bash
curl -X POST "http://localhost:8000/auth/refresh" \
  -H "Content-Type: application/json" \
  --cookie "refresh_token=YOUR_REFRESH_TOKEN"
```

## ✅ Implemented Features

### Core Authentication Features
- ✅ **User Registration**: Email + password registration
- ✅ **User Login**: Secure password verification
- ✅ **JWT Token Management**: Access Token + Refresh Token mechanism
- ✅ **Token Rotation**: Generate new Refresh Token each time refreshed
- ✅ **User Logout**: Token revocation functionality
- ✅ **User Info Retrieval**: Protected user data endpoint

### OAuth Social Login
- ✅ **Google OAuth**: Google account login integration
- ✅ **Facebook OAuth**: Facebook account login integration
- ✅ **GitHub OAuth**: GitHub account login integration
- ✅ **OAuth User Data Sync**: Automatic user data creation and updates

### Security Features
- ✅ **Password Security Hashing**: Argon2id algorithm encryption
- ✅ **Token Secure Storage**: Refresh Token hash storage
- ✅ **httpOnly Cookie**: Cookie settings to prevent XSS attacks
- ✅ **CORS Support**: Cross-origin request handling
- ✅ **Environment Variable Configuration**: External management of sensitive information

### Database Integration
- ✅ **Azure SQL Database**: Support for Azure SQL and SQL Server
- ✅ **Connection Pool Management**: Efficient database connection management
- ✅ **Database Table Design**: Complete user and token management tables
- ✅ **Database Initialization**: SQL scripts to automatically create required tables

### API and Documentation
- ✅ **RESTful API**: Standard REST API design
- ✅ **Unified Response Format**: Consistent API response structure
- ✅ **Auto API Documentation**: Swagger UI and ReDoc
- ✅ **Test Page**: Built-in login test interface

## 🚧 Features Not Yet Implemented

### Security Enhancements
- ⏳ **Rate Limiting**: API request frequency limiting
- ⏳ **Token Blacklist**: Immediate Access Token revocation mechanism
- ⏳ **Multi-Factor Authentication (MFA)**: TOTP, SMS or Email verification
- ⏳ **Password Strength Check**: Password complexity validation
- ⏳ **Account Lockout Mechanism**: Temporary lockout after multiple failed logins
- ⏳ **IP Whitelist/Blacklist**: IP-based access control

### User Management
- ⏳ **Email Verification**: Email confirmation after registration
- ⏳ **Forgot Password**: Password reset functionality
- ⏳ **User Profile Management**: Update user information
- ⏳ **Account Deletion**: User account deletion functionality
- ⏳ **User Role Management**: RBAC (Role-Based Access Control)
- ⏳ **Admin Interface**: User management backend

### Advanced Features
- ⏳ **Audit Logging**: Detailed operation recording and monitoring
- ⏳ **Session Management**: Multi-device login management
- ⏳ **API Version Control**: Backward compatible API version management
- ⏳ **Content Caching**: Redis caching mechanism
- ⏳ **Background Tasks**: Celery asynchronous task processing
- ⏳ **Notification System**: Email, push notifications

### Monitoring and Operations
- ⏳ **Enhanced Health Checks**: Detailed system status monitoring
- ⏳ **Performance Monitoring**: APM (Application Performance Monitoring)
- ⏳ **Error Tracking**: Detailed error reporting and analysis
- ⏳ **Prometheus Metrics**: System metrics collection
- ⏳ **Log Aggregation**: Structured log management

### Deployment and DevOps
- ⏳ **Docker Containerization**: Complete Docker deployment configuration
- ⏳ **CI/CD Pipeline**: Automated deployment process
- ⏳ **Kubernetes Deployment**: K8s deployment configuration
- ⏳ **Load Balancing**: Multi-instance deployment support
- ⏳ **Automated Testing**: Unit tests, integration tests

### Documentation and Tools
- ⏳ **English API Documentation**: Complete English API documentation
- ⏳ **Deployment Guide**: Detailed production environment deployment guide
- ⏳ **Development Tools**: Development environment setup scripts
- ⏳ **Code Generator**: Automatic CRUD code generation
- ⏳ **Migration Scripts**: Database version management

> 💡 **Development Suggestions**: You can choose features to implement based on project requirements. It's recommended to start with security enhancements and user management features.

## 🏗️ Project Structure

```
login-template/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration settings
│   ├── models.py            # Pydantic models
│   ├── database.py          # Database operations
│   ├── auth.py              # Authentication logic
│   ├── oauth.py             # OAuth integration
│   ├── utils.py             # Utility functions
│   └── routers/
│       ├── __init__.py
│       └── auth.py          # Authentication routes
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables example (need to create .env file)
├── .gitignore              # Git ignore file
└── README.md               # Project documentation
```

> **Note**: The original `database/` folder has been removed, and SQL creation scripts have been integrated into this README file.

## 🔧 OAuth Setup

### Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing project
3. Enable Google+ API
4. Create OAuth 2.0 client ID
5. Set redirect URI

### Facebook OAuth

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create a new app
3. Add Facebook Login product
4. Set redirect URI

### GitHub OAuth

1. Go to [GitHub Settings > Developer settings](https://github.com/settings/developers)
2. Create a new OAuth App
3. Set callback URL

## 🗄️ Database Structure

### Main Tables

- **users**: Store basic user information and OAuth data
- **refresh_tokens**: Manage refresh tokens

### Detailed Table Structure

#### users Table
| Field | Type | Description |
|-------|------|-------------|
| id | INT IDENTITY | Primary key, auto-increment |
| email | NVARCHAR(255) | User email, unique index |
| username | NVARCHAR(100) | Username |
| password_hash | NVARCHAR(255) | Password hash (can be NULL for OAuth users) |
| provider | NVARCHAR(50) | OAuth provider (google, facebook, github) |
| provider_id | NVARCHAR(255) | OAuth provider user ID |
| is_active | BIT | Account active status |
| created_at | DATETIME2 | Creation time |
| updated_at | DATETIME2 | Update time |
| last_login | DATETIME2 | Last login time |

#### refresh_tokens Table
| Field | Type | Description |
|-------|------|-------------|
| id | INT IDENTITY | Primary key, auto-increment |
| user_id | INT | User ID, foreign key |
| token_hash | NVARCHAR(255) | SHA-256 hash of token |
| expires_at | DATETIME2 | Expiration time |
| is_revoked | BIT | Whether revoked |
| created_at | DATETIME2 | Creation time |

## 🔒 Security Features

### Implemented Security Measures

1. **Short-term Access Token**: 30-minute expiration, reducing theft risk
2. **Refresh Token Hash Storage**: Protect original tokens when database is compromised
3. **Token Revocation Mechanism**: Support revoking Refresh Token on logout
4. **Password Security Hashing**: Using Argon2id algorithm
5. **Token Rotation**: Generate new Refresh Token each time refreshed
6. **httpOnly Cookie**: Refresh Token transmitted via httpOnly Cookie

### Token Security Improvements

#### Frontend Token Storage Strategy
- **Access Token**: Stored in memory (prevent XSS attacks)
- **Refresh Token**: Stored in httpOnly Cookie (prevent XSS attacks)

#### Token Rotation Mechanism
- Automatically generate new Refresh Token each time Refresh Token is used
- Immediately revoke old Refresh Token
- Improve security, prevent token replay attacks

### Cookie Security Settings
```python
response.set_cookie(
    key="refresh_token",
    value=refresh_token,
    httponly=True,      # Prevent XSS
    secure=True,        # Use HTTPS in production
    samesite="lax",     # CSRF protection
    max_age=7 * 24 * 60 * 60  # 7 days expiration
)
```

## 🚨 Security Recommendations

### Production Environment Settings

1. **Environment Variable Configuration**
   - Use strong password as `SECRET_KEY` (at least 32 characters)
   - Set `ENVIRONMENT=production`
   - Never hardcode sensitive information in code

2. **HTTPS Configuration**
   - Production environment must use HTTPS
   - Set `secure=True` for cookies
   - Configure security headers (HSTS, CSP, etc.)

3. **Database Security**
   - Use strong passwords
   - Limit database access permissions
   - Regular database backups
   - Use connection pooling

4. **Monitoring and Logging**
   - Set up abnormal login behavior alerts
   - Monitor API usage
   - Log important security events

### Recommended Improvements

1. **Rate Limiting**
   ```python
   from slowapi import Limiter, _rate_limit_exceeded_handler
   from slowapi.util import get_remote_address

   limiter = Limiter(key_func=get_remote_address)

   @router.post("/login")
   @limiter.limit("5/minute")  # Maximum 5 login attempts per minute
   async def login(request: Request, ...):
       pass
   ```

2. **Token Blacklist Mechanism**
   - Consider using Redis to store revoked Access Tokens
   - Implement immediate revocation functionality

3. **Multi-Factor Authentication (MFA)**
   - Consider adding TOTP (Time-based One-Time Password)
   - Support SMS or Email verification

4. **Audit Logging**
   ```python
   import logging

   audit_logger = logging.getLogger('audit')

   async def log_login_attempt(email: str, success: bool, ip_address: str):
       audit_logger.info(f"Login attempt - Email: {email}, Success: {success}, IP: {ip_address}")
   ```

## 📱 Frontend Integration Suggestions

### Token Manager Example

```javascript
class TokenManager {
    constructor() {
        this.accessToken = null;
        this.autoRefreshTimer = null;
    }
    
    setAccessToken(token) {
        this.accessToken = token;
        this.scheduleAutoRefresh(); // Auto refresh before expiration
    }
    
    scheduleAutoRefresh() {
        // Auto refresh 5 minutes before token expires
        const refreshTime = (30 - 5) * 60 * 1000; // 25 minutes
        this.autoRefreshTimer = setTimeout(() => {
            this.refreshAccessToken();
        }, refreshTime);
    }
    
    async refreshAccessToken() {
        try {
            const response = await fetch('/auth/refresh', {
                method: 'POST',
                credentials: 'include' // Important: include cookies
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

### API Request Examples

```javascript
// Login
const response = await fetch('/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include', // Important: include cookies
    body: JSON.stringify({ email, password })
});

// Access protected endpoint with Access Token
const response = await fetch('/auth/me', {
    headers: { 
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
    },
    credentials: 'include'
});

// Logout
const response = await fetch('/auth/logout', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${accessToken}` },
    credentials: 'include' // Important: include cookies
});
```

## 🧪 Testing Recommendations

### Basic Functionality Testing
1. Register new user
2. Login and check token status
3. Use Access Token to get user information
4. Manually refresh token
5. Logout and confirm token cleanup

### Security Testing
1. Check httpOnly Cookie settings
2. Test XSS attack protection (JavaScript cannot read refresh token)
3. Test token expiration handling
4. Test automatic token refresh

## 🚀 Deployment Recommendations

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variable Settings

```bash
# .env file example
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

## 📄 Update History

### v1.0.0 - Main Features
- ✅ JWT authentication system
- ✅ OAuth integration (Google, Facebook, GitHub)
- ✅ Unified API response format
- ✅ Token rotation mechanism
- ✅ httpOnly Cookie support
- ✅ Detailed code comments
- ✅ Complete security measures

### Main Improvements
- **Security Improvements**: Removed hardcoded passwords, use environment variables
- **Token Management**: Implemented token rotation and httpOnly Cookie
- **API Unification**: All responses use unified format
- **Code Quality**: Added detailed comments
- **Technical Documentation**: Integrated all documentation

## 📄 License

This project is licensed under the MIT License. 