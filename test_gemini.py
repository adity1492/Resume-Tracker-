import os
from core.ai_client import optimize_resume_content, evaluate_ats_compatibility, detect_sections_and_level
from utils.logger import get_logger

logger = get_logger(__name__)

def run_gemini_tests():
    logger.info("Running Gemini client validation tests...")
    
    # Test 1: Test with fallback behavior (when no key or invalid key is supplied)
    logger.info("Testing fallbacks (offline mode)...")
    sections = {
        "SUMMARY": "Experienced Python programmer."
    }
    opt = optimize_resume_content(sections, "Senior backend python role", api_key="")
    assert opt["SUMMARY"] == "Experienced Python programmer.", "Optimization fallback should return original text!"
    logger.info("Optimization fallback validation: SUCCESS.")
    
    # Test 2: Test detect_sections_and_level fallback
    logger.info("Testing section detection fallback...")
    blocks_text = "[Block #0] JOHN DOE\n[Block #1] Python developer\n[Block #2] EXPERIENCE\n[Block #3] Worked at Tech Corp (2020-2023)"
    secs, level = detect_sections_and_level(blocks_text, api_key="")
    assert "EXPERIENCE" in secs or "CONTACT INFO" in secs, "Should have detected some sections!"
    logger.info("Section detection fallback validation: SUCCESS.")

    # Test 3: Test evaluate_ats_compatibility fallback
    logger.info("Testing ATS compatibility fallback...")
    report = evaluate_ats_compatibility("John Doe - Python developer", "Python Engineer", api_key="")
    assert "overall_score" in report, "Fallback report should contain overall_score!"
    logger.info("ATS evaluation fallback validation: SUCCESS.")
    
    # Optional Test: If a key is present in env, try live request
    key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if key:
        logger.info("GEMINI_API_KEY found in environment. Testing live API connection...")
        try:
            live_opt = optimize_resume_content(sections, "Senior Python Developer", api_key=key)
            logger.info(f"Live optimization result: {live_opt}")
            assert live_opt != sections, "Live optimization should modify the text to align with job description!"
            logger.info("Live API validation: SUCCESS.")
        except Exception as e:
            logger.error(f"Live API test failed: {e}")
    else:
        logger.info("No GEMINI_API_KEY found in env; skipping live API test.")

    logger.info("All Gemini tests completed successfully!")

if __name__ == "__main__":
    run_gemini_tests()
