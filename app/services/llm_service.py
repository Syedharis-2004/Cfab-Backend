import google.generativeai as genai
from app.core.config import settings
from app.utils.prompts import PYTHON_SOLVER_SYSTEM_PROMPT
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
# Using gemini-2.5-flash as requested
model = genai.GenerativeModel('gemini-2.5-flash')

async def generate_ai_response(prompt: str, system_instruction: str = None) -> str:
    """General purpose function to generate AI response using Gemini."""
    logger.info("Generating AI response with Gemini")
    try:
        # Gemini 1.5 supports system_instruction in GenerativeModel constructor, 
        # but for simplicity we can prepend it to the prompt or use chat session.
        full_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt
        
        # genai library calls are synchronous, wrapping in thread for async compatibility
        response = await asyncio.to_thread(model.generate_content, full_prompt)
        
        if not response.text:
            logger.warning("Gemini returned an empty response")
            return ""
            
        return response.text
    except Exception as e:
        logger.error(f"Gemini API Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Gemini API Error: {str(e)}")

async def get_ai_answers(questions: list, dataset_context: str) -> list:
    logger.info(f"Requesting AI answers for {len(questions)} questions using Gemini")
    
    results = []
    for question in questions:
        try:
            prompt = f"Dataset Context:\n{dataset_context}\n\nQuestion: {question}"
            answer = await generate_ai_response(prompt, PYTHON_SOLVER_SYSTEM_PROMPT)
            results.append({"question": question, "answer": answer})
        except Exception as e:
            logger.error(f"Error getting AI answer for '{question}': {str(e)}")
            results.append({"question": question, "answer": "Error generating answer."})
            
    return results

async def get_visualization_recommendations(questions: list, dataset_context: str) -> list:
    logger.info("Requesting visualization recommendations using Gemini")
    try:
        system_prompt = "You are a Power BI expert. Return ONLY a valid JSON array of visualization objects. Format: [{\"question\": \"...\", \"visual\": \"...\", \"columns\": [...]}]"
        prompt = f"Dataset Context:\n{dataset_context}\n\nAnalyze these questions and suggest visuals:\n{json.dumps(questions)}"
        
        response_text = await generate_ai_response(prompt, system_prompt)
        
        # Clean response text in case Gemini adds markdown code blocks
        clean_json = response_text.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_json)
        
        # If Gemini returns a list directly or wrapped in an object
        if isinstance(data, list):
            return data
        return data.get("visuals", [])
    except Exception as e:
        logger.error(f"Error getting visualization recommendations: {str(e)}")
        return []
