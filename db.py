
import pymongo, os
import threading
import json
import base64
import bcrypt
from dotenv import load_dotenv
from datetime import datetime, timedelta

# ===============================
# MODEL LAYER
# ===============================



from datetime import datetime, timedelta
import hashlib

class DatabaseConnection:
    """Singleton class để quản lý kết nối MongoDB (thread-safe)"""
    _instance = None
    _client = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance

    def connect(self):
        if self._client is None:
            with self._lock:
                if self._client is None:
                    load_dotenv()
                    mongo_uri = "mongodb://seadragon:seadragon%40admin@crm.sdtc.vn:27017/"
                    self._client = pymongo.MongoClient(mongo_uri, maxPoolSize=50)
        return self._client

    def get_database(self, db_name="checktop_app"):
        client = self.connect()
        return client[db_name]

    def close(self):
        with self._lock:
            if self._client:
                self._client.close()
                self._client = None

class DomainManager:
    def __init__(self, db):
        self.collection = db["domains"]

    def add_domain(self, user_id, domain, sheet_id, worksheet):
        self.collection.insert_one({
            "user_id": user_id,
            "domain": domain,
            "sheet_id": sheet_id,
            "worksheet": worksheet,
            "created_at": datetime.utcnow()
        })

    def get_domains(self, user_id):
        return list(self.collection.find({"user_id": user_id}))

    def delete_domain(self, domain_id):
        self.collection.delete_one({"_id": domain_id})
class UserManager:
    def __init__(self, db_name="checktop_app"):
        self.db = DatabaseConnection().get_database(db_name)
        self.users = self.db["accounts"]

    def hash_password(self, password):
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()

    def register(self, username, password, role="user"):
        if self.users.find_one({"username": username}):
            return False, "Tên đăng nhập đã tồn tại!"

        from datetime import datetime, timedelta
        now = datetime.utcnow()

        user_doc = {
            "username": username,
            "password": self.hash_password(password),
            "role": role,
            "created_at": now,
        }

        if role == "user":
            user_doc["expired_at"] = now + timedelta(days=3)

        self.users.insert_one(user_doc)
        return True, "Đăng ký thành công!"

    def login(self, username, password):
        user = self.users.find_one({"username": username})
        if not user:
            return False, "Sai tài khoản hoặc mật khẩu!", None

        if user["password"] != self.hash_password(password):
            return False, "Sai tài khoản hoặc mật khẩu!", None

        return True, "OK", user["role"]

    def login_flex(self, username, password):
        user = self.users.find_one({"username": username})
        if not user:
            return False, "Sai tên đăng nhập hoặc mật khẩu!", None

        if user.get("password") != self.hash_password(password):
            return False, "Sai tên đăng nhập hoặc mật khẩu!", None

        profile = {
            "role": user.get("role"),
            "display_name": user.get("display_name", username),
            "sheets_config": user.get("sheets_config", []),
            "avatar_path": user.get("avatar_path")
        }

        return True, "Đăng nhập thành công!", profile

    def update_profile(self, username, display_name, sheets_config, avatar_path=None, *args):
        updates = {
            "display_name": display_name,
            "sheets_config": sheets_config
        }
        if avatar_path:
            updates["avatar_path"] = avatar_path

        self.users.update_one({"username": username}, {"$set": updates})
        return True, "Updated"

    def list_users(self):
        return list(self.users.find({}, {"_id": 0, "password": 0}))
    
       # Thêm vào class UserManager trong db.py
    def get_user(self, username):
        """Lấy thông tin user theo username"""
        return self.users.find_one({"username": username}, {"_id": 0, "password": 0})


class SessionsManager:
    """Quản lý session data per user (goals, snapshots, etc.)"""
    def __init__(self, db_name="checktop_app"):
        self.db = DatabaseConnection().get_database(db_name)
        self.sessions = self.db["sessions"]
        self.auth_sessions = self.db["auth_sessions"]
        # TTL index for auth_sessions (24h)
        try:
            self.auth_sessions.create_index("timestamp", expireAfterSeconds=86400)
        except:
            pass  # Index may exist

    def save_session(self, user_id, session_data):
        """Save full session data as JSON doc"""
        self.sessions.update_one(
            {"user_id": user_id},
            {"$set": {
                "user_id": user_id,
                "session_data": session_data,
                "updated_at": datetime.utcnow()
            }},
            upsert=True
        )

    def load_session(self, user_id):
        """Load session data"""
        doc = self.sessions.find_one({"user_id": user_id})
        return doc.get("session_data", {}) if doc else {}

    def save_auth_state(self, user_id):
        """Save auth state with TTL 24h"""
        self.auth_sessions.update_one(
            {"user_id": user_id},
            {"$set": {
                "user_id": user_id,
                "timestamp": datetime.utcnow()
            }},
            upsert=True
        )

    def load_auth_state(self, user_id):
        """Load and validate auth state <24h"""
        doc = self.auth_sessions.find_one({"user_id": user_id})
        if doc and (datetime.utcnow() - doc["timestamp"]) < timedelta(hours=24):
            return user_id
        self.auth_sessions.delete_one({"user_id": user_id})
        return None

    def save_marked_keywords(self, user_id, keywords):
        """Save user marked keywords as list of [keyword, day]"""
        self.sessions.update_one(
            {"user_id": user_id},
            {"$set": {"marked_keywords": keywords, "updated_at": datetime.utcnow()}},
            upsert=True
        )

    def load_marked_keywords(self, user_id):
        """Load user marked keywords"""
        doc = self.sessions.find_one({"user_id": user_id})
        return doc.get("marked_keywords", []) if doc else []

    def clear_user_sessions(self, user_id):
        """Clear all sessions for user"""
        self.sessions.delete_one({"user_id": user_id})
        self.auth_sessions.delete_one({"user_id": user_id})
    # Thêm vào class SessionsManager trong db.py

    def save_session_token(self, token: str, user_id: str, ttl_hours: int = 72):
        """Lưu session token → user_id mapping, TTL 72h"""
        from datetime import datetime, timedelta
        self.db['session_tokens'].update_one(
            {'token': token},
            {'$set': {
                'token': token,
                'user_id': user_id,
                'expires_at': datetime.utcnow() + timedelta(hours=ttl_hours)
            }},
            upsert=True
        )
        # Tạo TTL index nếu chưa có
        self.db['session_tokens'].create_index(
            'expires_at', expireAfterSeconds=0
        )

    def get_user_by_token(self, token: str):
        """Lấy user_id từ token, None nếu hết hạn hoặc không tồn tại"""
        from datetime import datetime
        doc = self.db['session_tokens'].find_one({
            'token': token,
            'expires_at': {'$gt': datetime.utcnow()}
        })
        return doc['user_id'] if doc else None

    def delete_session_token(self, token: str):
        """Xóa token khi logout"""
        self.db['session_tokens'].delete_one({'token': token})
 