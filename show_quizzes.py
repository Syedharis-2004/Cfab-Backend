import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models.quiz import Quiz
from app.core.config import settings

async def show():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db_name = settings.MONGODB_URL.split('/')[-1].split('?')[0] or 'check_yourself'
    await init_beanie(database=client[db_name], document_models=[Quiz])
    quizzes = await Quiz.find_all().to_list()
    print("\n--- QUIZZES IN DB ---")
    for q in quizzes:
        print(f"- {q.title}")
    print("--------------------------")

if __name__ == "__main__":
    asyncio.run(show())
