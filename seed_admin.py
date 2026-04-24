import asyncio
from app.core.database import init_db
from app.models.user import User
from app.core.security import get_password_hash

async def seed_admin():
    await init_db()
    
    admin = await User.find_one(User.role == "admin")
    if admin:
        print(f"Admin already exists: {admin.email}")
        return

    admin = User(
        name="Admin User",
        email="admin@example.com",
        hashed_password=get_password_hash("admin123"),
        role="admin"
    )
    await admin.insert()
    print("Admin user seeded: admin@example.com / admin123")

if __name__ == "__main__":
    asyncio.run(seed_admin())
