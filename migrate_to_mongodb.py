# migrate_to_mongodb.py 
#!/usr/bin/env python3
"""
Migration script: JSON -> MongoDB
Run once to migrate existing data.
"""
from db import UserManager, SessionsManager
import json
import os
import glob
from datetime import datetime

print("🚀 Starting MongoDB migration...")

# 1. Migrate users.json
user_manager = UserManager()
user_manager.migrate_from_json()
print("✅ Users migrated")

# 2. Ensure default admins (safe idempotent)
from db import ensure_default_admins
ensure_default_admins()
print("✅ Admins ensured")

# 3. Migrate session files to MongoDB sessions
sessions_manager = SessionsManager()
session_files = glob.glob("dashboard_session_*.json")
migrated_sessions = 0
for session_file in session_files:
    try:
        user_id = session_file.replace('dashboard_session_', '').replace('.json', '')
        with open(session_file, 'r', encoding='utf-8') as f:
            session_data = json.load(f)
        sessions_manager.save_session(user_id, session_data)
        print(f"✅ Migrated session for {user_id}")
        migrated_sessions += 1
    except Exception as e:
        print(f"⚠️ Failed to migrate {session_file}: {e}")

print(f"✅ Migrated {migrated_sessions} sessions")

# 4. Migrate session_auth.json
auth_file = 'session_auth.json'
if os.path.exists(auth_file):
    try:
        with open(auth_file, 'r', encoding='utf-8') as f:
            auth_data = json.load(f)
        user_id = auth_data['user_id']
        sessions_manager.save_auth_state(user_id)
        print("✅ Auth state migrated")
    except Exception as e:
        print(f"⚠️ Failed to migrate auth: {e}")

print("🎉 Migration complete! Ready to delete JSON files.")
print("rm dashboard_session*.json users.json session_auth.json")

