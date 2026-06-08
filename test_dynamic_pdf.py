from core.dynamic_pdf_generator import generate_dynamic_pdf_from_sections
from utils.logger import get_logger

logger = get_logger(__name__)

def test_generation():
    logger.info("Running dynamic PDF generation test...")
    sample_sections = {
        "CONTACT INFO": "ADITYA RAJ\nB.Tech Computer Science Student\nPhone: +91 9234940357 | Email: aditya@email.com | Location: Bihar, India",
        "SUMMARY": "Computer Science student with a unique blend of skills. Seeking an internship at DRDO to apply my knowledge of Python and System Design.",
        "PROJECTS": "- Garuda 1.0 - The RC Plane: Designed and fabricated a radio-controlled aircraft.\n- ATS Optimizer: Built a Streamlit application connected to Google Gemini API.",
        "EDUCATION": "Muzaffarpur Institute of Technology | 2024 - 2028\nB.Tech in Computer Science Engineering (CGPA: 7.55)"
    }
    
    pdf_bytes = generate_dynamic_pdf_from_sections(sample_sections, "test_dynamic.pdf")
    assert len(pdf_bytes) > 0, "PDF bytes should not be empty!"
    
    with open("test_dynamic.pdf", "wb") as f:
        f.write(pdf_bytes)
        
    logger.info("Successfully generated test_dynamic.pdf for visual verification.")

if __name__ == "__main__":
    test_generation()
