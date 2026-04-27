import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models.assignment import Assignment
from app.core.config import settings

async def show():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db_name = settings.MONGODB_URL.split('/')[-1].split('?')[0] or 'check_yourself'
    await init_beanie(database=client[db_name], document_models=[Assignment])
    assignments = await Assignment.find_all().to_list()
    print("\n--- ASSIGNMENTS IN DB ---")
    for a in assignments:
        print(f"- {a.title} ({a.assignment_type})")
    print("--------------------------")

if __name__ == "__main__":
    asyncio.run(show())
