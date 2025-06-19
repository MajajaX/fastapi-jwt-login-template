"""
資料庫連接和操作模組

此模組提供與 Azure SQL Database 的連接和操作功能，包括：
- 資料庫連接管理
- 使用者資料存取
- 重新整理 Token 管理
- 查詢執行和結果處理

使用 pymssql 驅動程式連接 SQL Server，並提供安全的參數化查詢功能
"""
import pymssql
from typing import Optional, Dict, Any, List
from contextlib import contextmanager
from app.config import settings
import hashlib
from datetime import datetime


class DatabaseManager:
    """
    資料庫管理類別
    
    提供資料庫連接、查詢執行等核心功能
    使用上下文管理器確保連接的正確開啟和關閉
    """
    
    @staticmethod
    @contextmanager
    def get_connection():
        """
        取得資料庫連接的上下文管理器
        
        使用 contextmanager 裝飾器確保資料庫連接在使用後正確關閉
        出現異常時會自動回滾交易
        
        Yields:
            pymssql.Connection: 資料庫連接物件
            
        Raises:
            Exception: 資料庫連接失敗時拋出異常
        """
        connection = None
        try:
            connection = pymssql.connect(
                server=settings.DB_SERVER,
                user=settings.DB_USERNAME,
                password=settings.DB_PASSWORD,
                database=settings.DB_DATABASE,
                charset='UTF-8'  # 確保支援中文字符
            )
            yield connection
        except Exception as e:
            if connection:
                connection.rollback()  # 發生錯誤時回滾交易
            raise e
        finally:
            if connection:
                connection.close()  # 確保連接被正確關閉
    
    @staticmethod
    def execute_query(query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """
        執行查詢並回傳結果
        
        Args:
            query (str): SQL 查詢語句，使用 %s 作為參數佔位符
            params (tuple, optional): 查詢參數元組
            
        Returns:
            List[Dict[str, Any]]: 查詢結果列表，每個元素為一個字典
            
        Note:
            使用參數化查詢防止 SQL 注入攻擊
        """
        with DatabaseManager.get_connection() as conn:
            cursor = conn.cursor(as_dict=True)  # 以字典格式回傳結果
            cursor.execute(query, params or ())
            return cursor.fetchall()
    
    @staticmethod
    def execute_non_query(query: str, params: tuple = None) -> int:
        """
        執行非查詢語句（INSERT、UPDATE、DELETE）並回傳受影響的行數
        
        Args:
            query (str): SQL 語句
            params (tuple, optional): 查詢參數元組
            
        Returns:
            int: 受影響的行數
            
        Note:
            自動提交交易，適用於資料修改操作
        """
        with DatabaseManager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            conn.commit()  # 提交交易
            return cursor.rowcount
    
    @staticmethod
    def execute_scalar(query: str, params: tuple = None) -> Any:
        """
        執行查詢並回傳單一值
        
        Args:
            query (str): SQL 查詢語句
            params (tuple, optional): 查詢參數元組
            
        Returns:
            Any: 查詢結果的第一行第一列的值，如果沒有結果則回傳 None
            
        Note:
            適用於計數查詢或取得單一值的場景
        """
        with DatabaseManager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            result = cursor.fetchone()
            return result[0] if result else None


class UserRepository:
    """
    使用者資料存取類別
    
    提供使用者相關的資料庫操作，包括：
    - 建立新使用者
    - 查詢使用者資訊
    - 更新使用者資料
    - OAuth 使用者管理
    """
    
    @staticmethod
    def create_user(email: str, username: str, password_hash: str, provider: str = None, provider_id: str = None) -> bool:
        """
        建立新使用者
        
        Args:
            email (str): 使用者電子郵件地址
            username (str): 使用者名稱
            password_hash (str): 密碼雜湊值（使用 Argon2 雜湊）
            provider (str, optional): OAuth 提供者名稱（google, facebook, github）
            provider_id (str, optional): OAuth 提供者的使用者 ID
            
        Returns:
            bool: 建立成功回傳 True，失敗回傳 False
            
        Note:
            - 一般註冊使用者：provider 和 provider_id 為 None
            - OAuth 使用者：password_hash 可為空字串
        """
        query = """
        INSERT INTO users (email, username, password_hash, provider, provider_id)
        VALUES (%s, %s, %s, %s, %s)
        """
        try:
            rows_affected = DatabaseManager.execute_non_query(
                query, 
                (email, username, password_hash, provider, provider_id)
            )
            return rows_affected > 0
        except Exception:
            # 建立失败时回傳 False（可能是重複的 email）
            return False
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
        """
        根據電子郵件地址取得使用者資訊
        
        Args:
            email (str): 使用者電子郵件地址
            
        Returns:
            Optional[Dict[str, Any]]: 使用者資訊字典，找不到則回傳 None
            
        Note:
            只回傳啟用狀態的使用者（is_active = 1）
        """
        query = "SELECT * FROM users WHERE email = %s AND is_active = 1"
        users = DatabaseManager.execute_query(query, (email,))
        return users[0] if users else None
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
        """
        根據使用者 ID 取得使用者資訊
        
        Args:
            user_id (int): 使用者 ID
            
        Returns:
            Optional[Dict[str, Any]]: 使用者資訊字典，找不到則回傳 None
            
        Note:
            只回傳啟用狀態的使用者（is_active = 1）
        """
        query = "SELECT * FROM users WHERE id = %s AND is_active = 1"
        users = DatabaseManager.execute_query(query, (user_id,))
        return users[0] if users else None
    
    @staticmethod
    def get_user_by_provider(provider: str, provider_id: str) -> Optional[Dict[str, Any]]:
        """
        根據 OAuth 提供者資訊取得使用者
        
        Args:
            provider (str): OAuth 提供者名稱（google, facebook, github）
            provider_id (str): OAuth 提供者的使用者 ID
            
        Returns:
            Optional[Dict[str, Any]]: 使用者資訊字典，找不到則回傳 None
            
        Note:
            用於 OAuth 登入時查找對應的使用者帳戶
        """
        query = "SELECT * FROM users WHERE provider = %s AND provider_id = %s AND is_active = 1"
        users = DatabaseManager.execute_query(query, (provider, provider_id))
        return users[0] if users else None
    
    @staticmethod
    def update_user_login_time(user_id: int):
        """
        更新使用者最後登入時間
        
        Args:
            user_id (int): 使用者 ID
            
        Note:
            同時更新 last_login 和 updated_at 欄位
        """
        from app.utils import get_utc_now
        
        query = "UPDATE users SET last_login = %s, updated_at = %s WHERE id = %s"
        now = get_utc_now()  # 使用 UTC 時間統一時區
        DatabaseManager.execute_non_query(query, (now, now, user_id))


class RefreshTokenRepository:
    """
    重新整理 Token 資料存取類別
    
    管理重新整理 Token 的生命週期，包括：
    - 建立新的 Token
    - 驗證 Token 有效性
    - 撤銷 Token
    - Token 輪替機制
    """
    
    @staticmethod
    def create_refresh_token(user_id: int, token_hash: str, expires_at: datetime):
        """
        建立新的重新整理 Token
        
        Args:
            user_id (int): 使用者 ID
            token_hash (str): Token 的 SHA-256 雜湊值
            expires_at (datetime): Token 過期時間
            
        Note:
            - Token 以雜湊值形式儲存，增強安全性
            - 過期時間使用 UTC 時間
        """
        query = """
        INSERT INTO refresh_tokens (user_id, token_hash, expires_at, created_at)
        VALUES (%s, %s, %s, %s)
        """
        from app.utils import get_utc_now
        DatabaseManager.execute_non_query(query, (user_id, token_hash, expires_at, get_utc_now()))
    
    @staticmethod
    def get_refresh_token(token_hash: str) -> Optional[Dict[str, Any]]:
        """
        取得有效的重新整理 Token 資訊
        
        Args:
            token_hash (str): Token 的 SHA-256 雜湊值
            
        Returns:
            Optional[Dict[str, Any]]: Token 資訊及關聯的使用者資訊，無效則回傳 None
            
        Note:
            - 檢查 Token 是否過期
            - 檢查 Token 是否已被撤銷
            - 同時回傳使用者的 email 和 username
        """
        query = """
        SELECT rt.*, u.email, u.username 
        FROM refresh_tokens rt
        JOIN users u ON rt.user_id = u.id
        WHERE rt.token_hash = %s AND rt.expires_at > %s AND rt.is_revoked = 0
        """
        from app.utils import get_utc_now
        tokens = DatabaseManager.execute_query(query, (token_hash, get_utc_now()))
        return tokens[0] if tokens else None
    
    @staticmethod
    def revoke_refresh_token(token_hash: str):
        """
        撤銷重新整理 Token
        
        Args:
            token_hash (str): 要撤銷的 Token 雜湊值
            
        Note:
            將 is_revoked 欄位設為 1，Token 立即失效
        """
        query = "UPDATE refresh_tokens SET is_revoked = 1 WHERE token_hash = %s"
        DatabaseManager.execute_non_query(query, (token_hash,))
    
    @staticmethod
    def revoke_all_user_tokens(user_id: int):
        """
        撤銷使用者的所有重新整理 Token
        
        Args:
            user_id (int): 使用者 ID
            
        Note:
            用於使用者登出時撤銷所有 Token，或安全事件發生時強制登出
        """
        query = "UPDATE refresh_tokens SET is_revoked = 1 WHERE user_id = %s"
        DatabaseManager.execute_non_query(query, (user_id,)) 