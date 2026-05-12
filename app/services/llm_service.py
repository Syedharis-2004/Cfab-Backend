import google.generativeai as genai
from app.core.config import settings
from app.utils.prompts import PYTHON_SOLVER_SYSTEM_PROMPT, POWERBI_RECOMMENDER_SYSTEM_PROMPT
from app.utils.logger import logger
import json
import asyncio
from fastapi import HTTPException

# Configure Gemini
if not settings.GEMINI_API_KEY:
    logger.error("GEMINI_API_KEY is not set in environment variables.")
else:
    genai.configure(api_key=settings.GEMINI_API_KEY)

# Initialize Model
model = genai.GenerativeModel('gemini-1.5-flash')

async def generate_ai_response(prompt: str, system_instruction: str = None) -> str:
    """General purpose function to generate AI response using Gemini."""
    logger.info("Generating AI response with Gemini")
    try:
        full_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt
        response = await asyncio.to_thread(model.generate_content, full_prompt)
        
        if not response.text:
            logger.warning("Gemini returned an empty response")
            return ""
            
        return response.text
    except Exception as e:
        logger.error(f"Gemini API Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Gemini API Error: {str(e)}")

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
