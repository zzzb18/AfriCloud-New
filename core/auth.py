"""User authentication module"""
import streamlit as st
import sqlite3
import hashlib
import secrets
from typing import Optional, Dict, Any
from pathlib import Path


class AuthManager:
    """User authentication manager"""
    
    def __init__(self, db_path: str = "cloud_storage/storage.db"):
        # 确保数据库目录存在
        db_path_obj = Path(db_path)
        db_path_obj.parent.mkdir(parents=True, exist_ok=True)
        
        self.db_path = str(db_path_obj)
        self._init_database()
    
    def _init_database(self):
        """Initialize authentication database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_token TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, username: str, password: str, email: str = "") -> Dict[str, Any]:
        """Register a new user"""
        try:
            if not username or not password:
                return {"success": False, "error": "Username and password are required"}
            
            if len(password) < 6:
                return {"success": False, "error": "Password must be at least 6 characters"}
            
            password_hash = self._hash_password(password)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    INSERT INTO users (username, password_hash, email)
                    VALUES (?, ?, ?)
                ''', (username, password_hash, email))
                
                user_id = cursor.lastrowid
                
                # 注册成功后自动创建session（自动登录）
                session_token = secrets.token_urlsafe(32)
                import datetime
                expires_at = datetime.datetime.now() + datetime.timedelta(days=7)
                
                cursor.execute('''
                    INSERT INTO sessions (user_id, session_token, expires_at)
                    VALUES (?, ?, ?)
                ''', (user_id, session_token, expires_at))
                
                conn.commit()
                conn.close()
                
                return {
                    "success": True,
                    "user_id": user_id,
                    "username": username,
                    "session_token": session_token,
                    "email": email
                }
            except sqlite3.IntegrityError:
                conn.close()
                return {"success": False, "error": "Username already exists"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def login_user(self, username: str, password: str) -> Dict[str, Any]:
        """Login user and create session"""
        try:
            password_hash = self._hash_password(password)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, username, email FROM users
                WHERE username = ? AND password_hash = ?
            ''', (username, password_hash))
            
            user = cursor.fetchone()
            
            if not user:
                conn.close()
                return {"success": False, "error": "Invalid username or password"}
            
            user_id, username, email = user
            
            # Create session token
            session_token = secrets.token_urlsafe(32)
            
            # Store session (expires in 7 days)
            import datetime
            expires_at = datetime.datetime.now() + datetime.timedelta(days=7)
            
            cursor.execute('''
                INSERT INTO sessions (user_id, session_token, expires_at)
                VALUES (?, ?, ?)
            ''', (user_id, session_token, expires_at))
            
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "session_token": session_token,
                "user_id": user_id,
                "username": username,
                "email": email
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def verify_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Verify session token and return user info"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT s.user_id, s.expires_at, u.username, u.email
                FROM sessions s
                JOIN users u ON s.user_id = u.id
                WHERE s.session_token = ? AND s.expires_at > datetime('now')
            ''', (session_token,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                user_id, expires_at, username, email = result
                return {
                    "user_id": user_id,
                    "username": username,
                    "email": email,
                    "expires_at": expires_at
                }
            return None
        except Exception as e:
            print(f"[DEBUG] verify_session error: {str(e)}")
            return None
    
    def logout_user(self, session_token: str) -> bool:
        """Logout user by deleting session"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM sessions WHERE session_token = ?', (session_token,))
            conn.commit()
            conn.close()
            
            return True
        except Exception as e:
            return False
    
    def get_user_info(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user information by ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, username, email, created_at
                FROM users WHERE id = ?
            ''', (user_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    "id": result[0],
                    "username": result[1],
                    "email": result[2],
                    "created_at": result[3]
                }
            return None
        except Exception as e:
            return None


