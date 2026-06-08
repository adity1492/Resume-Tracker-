from core.resume_pdf_builder import generate_pdf_from_resume_data
from core.resume_docx_builder import generate_docx_from_resume_data
from utils.logger import get_logger

logger = get_logger(__name__)

def run_builder_tests():
    logger.info("Starting structured resume builders testing...")
    
    sample_data = {
        "name": "Alex Mercer",
        "title": "Software Engineer",
        "email": "alex@email.com",
        "phone": "+12345678",
        "location": "London, UK",
        "summary": "Specialist in distributed cloud architectures.",
        "experience": [
            {
                "company": "Tech Corp",
                "title": "Senior Architect",
                "location": "London",
                "start_date": "2020",
                "end_date": "Present",
                "description": "- Led migrations of microservices.\n- Scaled DB capacity by 40%."
            }
        ],
        "education": [
            {
                "school": "Imperial College",
                "degree": "B.S. CS",
                "location": "London",
                "start_date": "2015",
                "end_date": "2019",
                "details": "First class honors."
            }
        ],
        "skills": "Python, Go, Docker, Kubernetes, AWS",
        "projects": [
            {
                "name": "Autoscaler",
                "role": "Creator",
                "link": "github.com/alex/autoscaler",
                "description": "An open source middleware."
            }
        ]
    }
    
    # 1. Test PDF generation (Classic Navy theme)
    logger.info("Testing structured PDF generation...")
    pdf_bytes = generate_pdf_from_resume_data(sample_data, "Classic Corporate (Navy)")
    assert len(pdf_bytes) > 0, "PDF bytes should not be empty!"
    with open("test_resume_built.pdf", "wb") as f:
        f.write(pdf_bytes)
    logger.info("Structured PDF generation: SUCCESS.")
    
    # 2. Test Word document generation
    logger.info("Testing structured DOCX generation...")
    docx_bytes = generate_docx_from_resume_data(sample_data, "test_resume_built.docx")
    assert len(docx_bytes) > 0, "DOCX bytes should not be empty!"
    with open("test_resume_built.docx", "wb") as f:
        f.write(docx_bytes)
    logger.info("Structured DOCX generation: SUCCESS.")
    
    logger.info("All builder tests completed successfully!")

if __name__ == "__main__":
    run_builder_tests()
