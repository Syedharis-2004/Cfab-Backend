import asyncio
import os
import sys

# Add the project root to sys.path
sys.path.append(os.getcwd())

async def verify_auth_bypass():
    print("Testing authentication bypass...")
    try:
        # Import after setting sys.path
        from app.api.auth import get_current_user
        from app.models.user import User
        
        # We need to mock Beanie initialization or just catch the error
        # Since we added a try-except in get_current_user, it should return the mock user
        user = await get_current_user()
        print(f"Mock user returned: {user.email} (Role: {user.role})")
        
        if user.email == "admin@example.com" or user.role == "admin":
            print("SUCCESS: Authentication bypass is working.")
        else:
            print("FAILURE: Unexpected user returned.")
            
    except Exception as e:
        import traceback
        print("ERROR: Verification failed:")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(verify_auth_bypass())
