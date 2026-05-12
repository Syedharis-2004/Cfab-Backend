from fastapi import APIRouter
from app.services.llm_service import generate_ai_response
from app.utils.logger import logger

router = APIRouter(prefix="/api", tags=["Gemini Test"])

@router.get("/test-gemini")
async def test_gemini():
    """Endpoint to test Gemini API connectivity."""
    logger.info("Test Gemini endpoint called")
    try:
        response = await generate_ai_response("Hello! Please reply with 'Gemini is active and ready!'")
        return {
            "success": True,
            "response": response.strip()
        }
    except Exception as e:
        logger.error(f"Test Gemini failed: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }
