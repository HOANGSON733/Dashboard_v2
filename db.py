def ensure_default_admins():
    """Tạo 2 tài khoản admin mặc định nếu chưa có admin nào."""
    user_manager = UserManager()
    admin_count = user_manager.users.count_documents({"role": "admin"})
    if admin_count == 0:
        # Tạo 2 admin mặc định
        user_manager.users.insert_one({
            "username": "admin1",
            "password": user_manager.hash_password("admin123"),
            "role": "admin",
            "created_at": datetime.utcnow()
        })
        user_manager.users.insert_one({
            "username": "admin2",
            "password": user_manager.hash_password("admin123"),
            "role": "admin",
            "created_at": datetime.utcnow()
        })
        print("Đã tạo 2 tài khoản admin mặc định: admin1/admin123, admin2/admin123")
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
class SessionsManager:
    """Quản lý session data per user (goals, snapshots, etc.)"""
    def __init__(self, db_name="checktop_app"):
        self.db = DatabaseConnection().get_database(db_name)
        self.sessions = self.db["sessions"]
        # TTL index for auth_sessions
        self.auth_sessions = self.db["auth_sessions"]

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
        return doc["session_data"] if doc else {}

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

    def clear_user_sessions(self, user_id):
        """Clear all sessions for user"""
        self.sessions.delete_one({"user_id": user_id})
        self.auth_sessions.delete_one({"user_id": user_id})

    def register(self, username, password, role="user", creator_role=None, machine_info=None):
        """
        Đăng ký user mới. Ai cũng đăng ký được user. Chỉ admin mới tạo được admin/tester.
        creator_role: role của người tạo (None nếu tự đăng ký)
        machine_info: dict thông tin máy (hostname, mac, os)
        """
        if self.users.find_one({"username": username}):
            return False, "Tên đăng nhập đã tồn tại!"
        if role in ["admin", "tester"] and creator_role != "admin":
            return False, "Chỉ admin mới tạo được tài khoản admin/tester."
        now = datetime.utcnow()
        user_doc = {
            "username": username,
            "password": self.hash_password(password),
            "role": role,
            "created_at": now,
        }
        if machine_info:
            user_doc["machine_info"] = machine_info
        if role == "user":
            user_doc["expired_at"] = now + timedelta(days=3)
        self.users.insert_one(user_doc)
        return True, "Đăng ký thành công!"

    def login(self, username, password):
        user = self.users.find_one({"username": username})
        if not user:
            return False, "Sai tên đăng nhập hoặc mật khẩu!", None
        if user["password"] != self.hash_password(password):
            return False, "Sai tên đăng nhập hoặc mật khẩu!", None
        # Kiểm tra hạn sử dụng nếu là user
        if user["role"] == "user":
            expired = user.get("expired_at")
            if not expired:
                # Nếu chưa có expired_at, fallback về created_at + 3 ngày
                created = user.get("created_at")
                if not created:
                    return False, "Tài khoản không hợp lệ!", None
                if isinstance(created, str):
                    created = datetime.fromisoformat(created)
                expired = created + timedelta(days=3)
            if isinstance(expired, str):
                expired = datetime.fromisoformat(expired)
            if datetime.utcnow() > expired:
                return False, "Tài khoản user đã hết hạn sử dụng (3 ngày)!", None
        return True, "Đăng nhập thành công!", user["role"]

    def get_user(self, username):
        return self.users.find_one({"username": username})

    def set_role(self, username, new_role, admin_username):
        admin = self.get_user(admin_username)
        if not admin or admin["role"] != "admin":
            return False, "Chỉ admin mới được đổi quyền."
        if new_role not in ["admin", "tester", "user"]:
            return False, "Role không hợp lệ."
        self.users.update_one({"username": username}, {"$set": {"role": new_role}})
        return True, "Đã đổi quyền thành công."

    def list_users(self):
        return list(self.users.find({}, {"_id": 0, "password": 0}))

    def login_flex(self, username, password):
        """Flexible login: SHA256 or bcrypt"""
        user = self.users.find_one({"username": username})
        if not user:
            return False, "Sai tên đăng nhập hoặc mật khẩu!", None

        # Try SHA256 first (native)
        if user.get("password") == self.hash_password(password):
            success_msg = "Đăng nhập thành công!"
        # Try bcrypt legacy
        elif self.verify_bcrypt(password, user.get("bcrypt_password", "")):
            success_msg = "Đăng nhập legacy thành công!"
        else:
            return False, "Sai tên đăng nhập hoặc mật khẩu!", None

        # Check expiration
        if user["role"] == "user":
            expired = user.get("expired_at")
            if not expired:
                created = user.get("created_at")
                if not created:
                    return False, "Tài khoản không hợp lệ!", None
                if isinstance(created, str):
                    created = datetime.fromisoformat(created)
                expired = created + timedelta(days=3)
            if isinstance(expired, str):
                expired = datetime.fromisoformat(expired)
            if datetime.utcnow() > expired:
                return False, "Tài khoản user đã hết hạn sử dụng (3 ngày)!", None

        # Return role + profile data
        profile = {
            "role": user.get("role"),
            "display_name": user.get("display_name", username),
            "sheets_config": user.get("sheets_config", []),
            "avatar_path": user.get("avatar_path")
        }
        return True, success_msg, profile

    def register_profile(self, username, password, display_name, sheets_config=[], role="user", avatar_path=None, creator_role=None, machine_info=None):
        """Register with profile data"""
        if self.users.find_one({"username": username}):
            return False, "Tên đăng nhập đã tồn tại!"
        if role in ["admin", "tester"] and creator_role != "admin":
            return False, "Chỉ admin mới tạo được tài khoản admin/tester."
        now = datetime.utcnow()
        user_doc = {
            "username": username,
            "password": self.hash_password(password),
            "bcrypt_password": base64.b64encode(self.hash_bcrypt(password)).decode('ascii'),
            "role": role,
            "display_name": display_name,
            "sheets_config": sheets_config,
            "avatar_path": avatar_path,
            "created_at": now,
        }
        if machine_info:
            user_doc["machine_info"] = machine_info
        if role == "user":
            user_doc["expired_at"] = now + timedelta(days=3)
        self.users.insert_one(user_doc)
        return True, "Đăng ký thành công!"

    def update_profile(self, username, display_name, sheets_config, avatar_path=None, old_password=None, new_password=None):
        """Update user profile"""
        user = self.users.find_one({"username": username})
        if not user:
            return False, "User not found"

        updates = {
            "display_name": display_name.strip(),
            "sheets_config": sheets_config
        }
        if avatar_path:
            updates["avatar_path"] = avatar_path

        if new_password:
            if not old_password or (user["password"] != self.hash_password(old_password) and not self.verify_bcrypt(old_password, user.get("bcrypt_password", ""))):
                return False, "Mật khẩu cũ không đúng"
            hashed_new = self.hash_password(new_password)
            bcrypt_new = base64.b64encode(self.hash_bcrypt(new_password)).decode('ascii')
            updates["password"] = hashed_new
            updates["bcrypt_password"] = bcrypt_new

        self.users.update_one({"username": username}, {"$set": updates})
        return True, "Cập nhật thành công"

    def migrate_from_json(self):
        """Migrate users.json to MongoDB"""
        users_file = "users.json"
        if not os.path.exists(users_file):
            print("No users.json found")
            return
        try:
            with open(users_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            json_users = data.get('users', [])
            migrated = 0
            for u in json_users:
                username = u['username']
                # Upsert with bcrypt hash preserved
                self.users.update_one(
                    {"username": username},
                    {"$set": {
                        "username": username,
                        "bcrypt_password": u['hashed_password'],
                        "display_name": u.get('display_name', username),
                        "sheets_config": u.get('sheets_config', []),
                        "avatar_path": u.get('avatar_path'),
                        "role": u.get('role', 'user'),
                        "migrated_at": datetime.utcnow()
                    }},
                    upsert=True
                )
                migrated += 1
            print(f"Migrated {migrated} users from JSON")
        except Exception as e:
            print(f"Migration error: {e}")
