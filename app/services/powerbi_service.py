from typing import List, Dict
from app.services.llm_service import get_visualization_recommendations
from app.utils.logger import logger

async def generate_powerbi_config(questions: List[str], dataset_context: str) -> List[Dict]:
    logger.info("Generating Power BI visualization config")
    
    # Rule-based fallback or AI-enhanced detection
    visuals = await get_visualization_recommendations(questions, dataset_context)
    
    if not visuals:
        logger.warning("No visuals generated, creating basic table visuals")
        visuals = [{"question": q, "visual": "table", "columns": []} for q in questions]
        
    return visuals
