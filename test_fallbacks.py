import sys
from core.ai_client import estimate_career_level_fallback, local_ats_evaluation_fallback
from core.pdf_processor import fallback_parse_sections

def run_tests():
    print("Starting Fallback Engine Tests...")
    
    # 1. Test Career Level Estimation Fallback
    print("\n[1] Testing Career Level Detection Fallback...")
    sample_texts = {
        "Executive Director of Software with 18 years of experience leading engineering departments.": "Executive",
        "Senior Developer with 5 years experience in python microservices.": "Senior",
        "Junior Associate engineer with 1 year experience.": "Junior",
        "Student intern studying Computer Science.": "Student",
        "University graduate fresher looking for entry level software engineer role.": "Fresher",
        "Product Manager with 9 years of experience.": "Manager"
    }
    
    for text, expected in sample_texts.items():
        result = estimate_career_level_fallback(text)
        print(f"  Text: '{text[:40]}...' -> Detected: {result} (Expected: {expected})")
        assert result == expected, f"Failed: Expected {expected}, got {result}"
    print("Career Level Detection Fallback: SUCCESS")
    
    # 2. Test Deterministic Fallback Parser
    print("\n[2] Testing Deterministic Section Parser Fallback...")
    # Mock blocks layout
    mock_blocks = [
        {"id": 0, "text": "Alexander Mercer\nalex@email.com", "font": "Helvetica", "size": 10.0},
        {"id": 1, "text": "PROFESSIONAL SUMMARY", "font": "Helvetica-Bold", "size": 12.0},
        {"id": 2, "text": "Results-driven Software Engineering Leader.", "font": "Helvetica", "size": 10.0},
        {"id": 3, "text": "WORK EXPERIENCE", "font": "Helvetica-Bold", "size": 12.0},
        {"id": 4, "text": "Senior Architect - Global Tech Systems (2020-Present)", "font": "Helvetica-Bold", "size": 10.0},
        {"id": 5, "text": "- Designed high-scale microservices.", "font": "Helvetica", "size": 10.0},
        {"id": 6, "text": "EDUCATION", "font": "Helvetica-Bold", "size": 12.0},
        {"id": 7, "text": "B.S. in Computer Science - University of Washington", "font": "Helvetica", "size": 10.0}
    ]
    
    parsed = fallback_parse_sections(mock_blocks)
    print("  Detected Sections:")
    for sec, data in parsed.items():
        print(f"    - {sec}: Block IDs {data['block_ids']}")
        
    assert "CONTACT INFO" in parsed, "Missing default contact section!"
    assert "PROFESSIONAL SUMMARY" in parsed, "Failed to parse SUMMARY heading!"
    assert "WORK EXPERIENCE" in parsed, "Failed to parse WORK EXPERIENCE heading!"
    assert "EDUCATION" in parsed, "Failed to parse EDUCATION heading!"
    print("Deterministic Section Parser Fallback: SUCCESS")
    
    # 3. Test Local Keyword-Matching Fallback
    print("\n[3] Testing Local ATS Evaluation Fallback...")
    mock_resume = "Highly analytical senior Python developer experienced in AWS, Docker, and Kubernetes. Built PostgreSQL databases."
    mock_jd = "Looking for a Python software engineer with AWS, Docker, Kubernetes, Terraform, and PostgreSQL skills."
    
    analysis = local_ats_evaluation_fallback(mock_resume, mock_jd)
    print(f"  Overall Score: {analysis['overall_score']}%")
    print(f"  Common Skills: {analysis['common_skills']}")
    print(f"  Missing Skills: {analysis['missing_skills']}")
    
    assert "Python" in analysis['common_skills'], "Failed to identify Python as a common skill!"
    assert "Docker" in analysis['common_skills'], "Failed to identify Docker as a common skill!"
    assert "Terraform" in analysis['missing_skills'], "Failed to identify Terraform as a missing skill!"
    assert analysis['overall_score'] > 0, "ATS Score cannot be zero!"
    print("Local ATS Evaluation Fallback: SUCCESS")
    
    print("\nAll fallback tests completed successfully!")

if __name__ == "__main__":
    run_tests()
