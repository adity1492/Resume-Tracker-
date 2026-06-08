import os
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from core.pdf_processor import extract_pdf_layout, replace_text_in_pdf
from core.docx_generator import generate_docx_from_sections
from utils.logger import get_logger

logger = get_logger(__name__)

def create_sample_resume_pdf() -> bytes:
    """Generates a structured multi-column dummy PDF for testing coordinates."""
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Header
    p.setFont("Helvetica-Bold", 20)
    p.drawString(100, 700, "Johnathan Doe")
    p.setFont("Helvetica", 10)
    p.drawString(100, 680, "Software Architect | Seattle, WA | john.doe@email.com")
    
    # Section: Summary
    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, 640, "PROFILE SUMMARY")
    p.setFont("Helvetica", 10)
    p.drawString(100, 620, "Highly analytical software engineering leader with over 8 years of experience.")
    p.drawString(100, 605, "Specialized in cloud architecture, distributed systems, and Python microservices.")
    
    # Section: Experience
    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, 560, "WORK EXPERIENCE")
    p.setFont("Helvetica-Bold", 10)
    p.drawString(100, 540, "Lead Architect - Cloud Systems Co. (2021 - Present)")
    p.setFont("Helvetica", 10)
    p.drawString(120, 520, "- Spearheaded design of highly scalable database migrations on AWS.")
    p.drawString(120, 505, "- Managed a cross-functional development squad of 10 senior designers.")
    
    # Section: Education
    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, 460, "EDUCATION")
    p.setFont("Helvetica", 10)
    p.drawString(100, 440, "B.S. Computer Science - University of Washington (2012-2016)")
    
    p.showPage()
    p.save()
    
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

def run_test():
    logger.info("Starting local PDF flow testing...")
    
    # 1. Create sample PDF
    pdf_bytes = create_sample_resume_pdf()
    
    # 2. Extract Layout
    blocks, full_text = extract_pdf_layout(pdf_bytes)
    logger.info(f"Extracted {len(blocks)} layout blocks.")
    for b in blocks:
        logger.info(f"Block #{b['id']}: '{b['text'][:50]}...' font: {b['font']} size: {b['size']} color: {b['color']}")
        
    assert len(blocks) > 0, "No blocks extracted!"
    
    # 3. Simulate replacement of block #3 (the profile summary text)
    # Let's find the block containing "Highly analytical software engineering"
    target_block_id = None
    for b in blocks:
        if "Highly analytical" in b["text"]:
            target_block_id = b["id"]
            break
            
    if target_block_id is not None:
        replacements = {
            target_block_id: "AI OPTIMIZED: Highly analytical software engineering director. Led 15+ microservices transitions on Kubernetes."
        }
        
        logger.info(f"Simulating replacement on block #{target_block_id}...")
        updated_pdf = replace_text_in_pdf(pdf_bytes, blocks, replacements)
        
        # Verify text was written
        new_blocks, new_text = extract_pdf_layout(updated_pdf)
        logger.info("Updated PDF parsed successfully.")
        
        # Check if replacement string is present
        assert "AI OPTIMIZED" in new_text, "Replacement string not found in updated PDF!"
        logger.info("PDF replacement validation: SUCCESS.")
        
        # Save output PDFs for visual inspection
        with open("sample_resume.pdf", "wb") as f:
            f.write(pdf_bytes)
        with open("updated_resume.pdf", "wb") as f:
            f.write(updated_pdf)
        logger.info("Saved sample_resume.pdf and updated_resume.pdf for review.")
    else:
        logger.warning("Target block for replacement not found in layout.")
        
    # 4. Generate DOCX from sections
    sections = {
        "CONTACT INFO": "Johnathan Doe\njohn.doe@email.com",
        "PROFILE SUMMARY": "Highly analytical software engineering leader.",
        "WORK EXPERIENCE": "- Spearheaded design of highly scalable database migrations on AWS.\n- Managed a cross-functional development squad of 10 senior designers."
    }
    
    logger.info("Generating sample DOCX document...")
    docx_bytes = generate_docx_from_sections(sections, "test.docx")
    assert len(docx_bytes) > 0, "Generated DOCX was empty!"
    
    with open("updated_resume.docx", "wb") as f:
        f.write(docx_bytes)
    logger.info("Saved updated_resume.docx for review.")
    
    logger.info("All local verification tests completed successfully!")

if __name__ == "__main__":
    run_test()
