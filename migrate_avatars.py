import json
import os
import base64

USERS_FILE = 'users.json'

def migrate_avatars():
    """Migrate base64 avatars to file storage"""
    if not os.path.exists(USERS_FILE):
        print("No users.json found")
        return
    
    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    users = data.get('users', [])
    migrated = False
    
    for user in users:
        if 'avatar' in user and user['avatar']:
            try:
                # Decode base64 avatar
                img_data = base64.b64decode(user['avatar'])
                os.makedirs('avatars', exist_ok=True)
                avatar_path = f'avatars/{user["username"]}.png'
                
                with open(avatar_path, 'wb') as img_file:
                    img_file.write(img_data)
                
                # Update user record
                user['avatar_path'] = avatar_path
                del user['avatar']
                migrated = True
                print(f"Migrated avatar for {user['username']} to {avatar_path}")
            except Exception as e:
                print(f"Failed to migrate avatar for {user['username']}: {e}")
    
    if migrated:
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Migration complete. Check users.json and avatars/ folder.")
    else:
        print("No base64 avatars found to migrate.")

if __name__ == "__main__":
    migrate_avatars()

