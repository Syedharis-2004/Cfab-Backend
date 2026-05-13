from google import genai
from app.core.config import settings
from app.utils.prompts import PYTHON_SOLVER_SYSTEM_PROMPT, POWERBI_RECOMMENDER_SYSTEM_PROMPT
from app.utils.logger import logger
import json
import asyncio
from fastapi import HTTPException

# Configure Gemini Client
client = None
if not settings.GEMINI_API_KEY:
    logger.error("GEMINI_API_KEY is not set in environment variables.")
else:
    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        logger.info("Gemini Client initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize Gemini Client: {str(e)}")

# Model ID - Updated to the latest recommended version
MODEL_ID = "gemini-2.0-flash"

async def generate_ai_response(prompt: str, system_instruction: str = None) -> str:
    """General purpose function to generate AI response using the new google-genai SDK."""
    if not client:
        logger.error("Gemini Client not initialized.")
        raise HTTPException(status_code=503, detail="AI Service is currently unavailable.")
    
    logger.info(f"Generating AI response with {MODEL_ID}")
    try:
        # The new SDK has a simpler generate_content method
        # Using asyncio.to_thread because the current SDK call is synchronous
        response = await asyncio.to_thread(
            client.models.generate_content,
            model=MODEL_ID,
            contents=prompt,
            config={"system_instruction": system_instruction} if system_instruction else None
        )
        
        if not response or not response.text:
            logger.warning("Gemini returned an empty response")
            return "I'm sorry, I couldn't generate a response at this time."
            
        return response.text
    except Exception as e:
        logger.error(f"Gemini API Error: {str(e)}")
        # Provide a graceful fallback or a proper HTTP exception
        raise HTTPException(
            status_code=500, 
            detail=f"Gemini API Error: {str(e)}"
        )


async def get_ai_answers(questions: list, dataset_context: str) -> list:
    logger.info(f"Requesting structured AI answers for {len(questions)} questions")
    
    prompt = f"Dataset Context:\n{dataset_context}\n\nQuestions to solve:\n{json.dumps(questions)}"
    response_text = await generate_ai_response(prompt, PYTHON_SOLVER_SYSTEM_PROMPT)
    
    try:
        clean_json = response_text.replace("```json", "").replace("```", "").strip()
        results = json.loads(clean_json)
        if isinstance(results, list):
            return results
        return []
    except Exception as e:
        logger.error(f"Error parsing AI answers: {str(e)}")
        # Fallback: try to generate one by one if bulk fails
        return [{"question": q, "explanation": "Error parsing AI response.", "code": "", "answer": "Error."} for q in questions]

async def get_visualization_recommendations(questions: list, dataset_context: str) -> list:
    logger.info("Requesting visualization recommendations using Gemini")
    try:
        prompt = f"Dataset Context:\n{dataset_context}\n\nAnalyze these questions and suggest visuals:\n{json.dumps(questions)}"
        response_text = await generate_ai_response(prompt, POWERBI_RECOMMENDER_SYSTEM_PROMPT)
        
        clean_json = response_text.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_json)
        
        if isinstance(data, list):
            return data
        return data.get("visuals", [])
    except Exception as e:
        logger.error(f"Error getting visualization recommendations: {str(e)}")
        return []
