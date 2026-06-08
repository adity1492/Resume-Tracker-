import os
import json
from core.ai_client import ai_parse_resume_text, ai_optimize_structured_resume
from utils.logger import get_logger

logger = get_logger(__name__)

def test_structured_ai():
    logger.info("Starting structured Groq AI testing...")
    
    key = os.getenv("GROQ_API_KEY", "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")
    
    # 1. Test raw text parsing
    raw_text = (
        "John Doe\nSoftware Engineer\nEmail: john@email.com\n"
        "Experience:\nTech Corp (2020-Present) - Senior Developer\n- Programmed backend in Python\n"
        "Education:\nUniversity of Washington - B.S. CS\n"
        "Skills: Python, SQL"
    )
    
    logger.info("Testing structured AI parsing...")
    parsed_json = ai_parse_resume_text(raw_text, api_key=key)
    logger.info(f"Parsed output: {json.dumps(parsed_json, indent=2)}")
    
    assert "name" in parsed_json, "Parsed JSON should contain name!"
    assert "experience" in parsed_json, "Parsed JSON should contain experience!"
    logger.info("Structured AI parsing: SUCCESS.")
    
    # 2. Test structured optimization
    logger.info("Testing structured AI optimization...")
    jd = "Looking for a Python Engineer with Kubernetes experience. Emphasize metrics and scaling."
    opt_json = ai_optimize_structured_resume(parsed_json, job_description=jd, desired_position="DevOps Python Engineer", api_key=key)
    logger.info(f"Optimized output: {json.dumps(opt_json, indent=2)}")
    
    assert "skills" in opt_json, "Optimized JSON should contain skills!"
    logger.info("Structured AI optimization: SUCCESS.")
    
    logger.info("All structured AI tests completed successfully!")

if __name__ == "__main__":
    test_structured_ai()
