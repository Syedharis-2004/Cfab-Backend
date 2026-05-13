import asyncio
import os
import sys

# Add the project root to sys.path
sys.path.append(os.getcwd())

from app.core.database import init_db
from app.models.quiz import Quiz, QuizQuestion
from app.utils.mongo_serializer import serialize_list

async def test_quiz_list():
    print("Testing Quiz List logic...")
    try:
        await init_db()
        from app.core.database import _db_initialized
        print(f"DB Initialized: {_db_initialized}")
        
        if not _db_initialized:
            print("DB failed to initialize. Cannot test.")
            return

        quizzes = await Quiz.find_all().to_list()
        print(f"Found {len(quizzes)} quizzes")
        
        async def _get_quiz_response(quiz):
            questions = await QuizQuestion.find(QuizQuestion.quiz_id == quiz.id).to_list()
            return {
                "id": str(quiz.id),
                "title": quiz.title,
                "questions": [
                    {
                        "id": str(q.id),
                        "question": q.question,
                        "option_a": q.option_a,
                        "option_b": q.option_b,
                        "option_c": q.option_c,
                        "option_d": q.option_d,
                    }
                    for q in questions
                ],
            }
            
        results = [await _get_quiz_response(q) for q in quizzes]
        serialized = serialize_list(results)
        print("Serialization success!")
        print(f"Results: {len(serialized)}")
        
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_quiz_list())
