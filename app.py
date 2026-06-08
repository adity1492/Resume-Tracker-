import streamlit as st
import os
import io
import json
import base64
import re
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Dict, Any, Tuple

# Load environment variables
load_dotenv()

# Set up page config FIRST
st.set_page_config(
    page_title="AI ATS Resume Builder & Optimization Pro",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import builders and AI clients
from core.resume_pdf_builder import generate_pdf_from_resume_data, THEMES
from core.resume_docx_builder import generate_docx_from_resume_data
from core.ai_client import (
    ai_parse_resume_text,
    ai_optimize_structured_resume,
    evaluate_ats_compatibility,
    DEFAULT_MODEL
)
from core.ats_analyzer import get_integrated_ats_report
from core.pdf_processor import convert_pdf_to_images
from utils.logger import get_logger

logger = get_logger(__name__)

# Premium Styling Injection
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
        background-color: #F8FAFC;
    }
    
    /* Header Block */
    .header-container {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        color: white;
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
        text-align: center;
        border-bottom: 4px solid #C05621; /* Accent accent */
    }
    .header-title {
        font-size: 2.2rem;
        font-weight: 700;
        letter-spacing: -0.5px;
        margin-bottom: 0.5rem;
    }
    .header-subtitle {
        color: #94A3B8;
        font-weight: 300;
        font-size: 1.1rem;
    }
    
    /* Card design */
    .dashboard-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        border: 1px solid #E2E8F0;
        margin-bottom: 1.5rem;
    }
    
    /* Score display */
    .score-circle {
        display: flex;
        align-items: center;
        justify-content: center;
        flex-direction: column;
        border-radius: 50%;
        width: 130px;
        height: 130px;
        margin: 0 auto;
        border: 8px solid #E2E8F0;
    }
    .score-value {
        font-size: 2.5rem;
        font-weight: 700;
        line-height: 1;
    }
    
    .score-high { border-color: #10B981; color: #059669; }
    .score-med { border-color: #F59E0B; color: #D97706; }
    .score-low { border-color: #EF4444; color: #DC2626; }
    
    /* Badges */
    .pill-badge {
        padding: 0.3rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        margin: 4px;
        border: 1px solid transparent;
    }
    .badge-navy { background-color: #EFF6FF; color: #1E40AF; border-color: #BFDBFE; }
    .badge-success { background-color: #ECFDF5; color: #065F46; border-color: #A7F3D0; }
    .badge-warning { background-color: #FFF7ED; color: #9A3412; border-color: #FED7AA; }
    .badge-error { background-color: #FEF2F2; color: #991B1B; border-color: #FCA5A5; }
    
</style>
""", unsafe_allow_html=True)

# ----------------- SESSION STATE SETUP -----------------
# Groq Key backend setup
if "groq_api_key" not in st.session_state:
    st.session_state.groq_api_key = os.getenv("GROQ_API_KEY", "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")

# Prepopulate beautiful resume data
if "resume_data" not in st.session_state:
    st.session_state.resume_data = {
        "name": "Alexander Mercer",
        "title": "Senior Software Engineering Leader",
        "email": "alex.mercer@email.com",
        "phone": "+44 20 7946 0958",
        "linkedin": "linkedin.com/in/alexmercer",
        "github": "github.com/alexmercer",
        "location": "London, UK",
        "summary": "Results-driven Software Engineering Leader with over 10 years of experience architecting high-scale distributed systems. Specialized in cloud-native microservices, cloud migrations, DevOps automation, and building international teams.",
        "experience": [
            {
                "company": "Global Cloud Solutions Corp",
                "title": "Senior Staff Architect",
                "location": "London, UK",
                "start_date": "2020",
                "end_date": "Present",
                "description": "- Spearheaded cloud migration of billing monolith to Kubernetes, boosting API performance by 45%.\n- Directed cross-functional team of 12 senior engineers across DevOps, Backend, and QA squads.\n- Designed disaster recovery plans on AWS, achieving 99.99% availability."
            },
            {
                "company": "FinTech Labs International",
                "title": "Lead Backend Engineer",
                "location": "London, UK",
                "start_date": "2015",
                "end_date": "2020",
                "description": "- Programmed transaction processing APIs in Go and Python, handling $15M+ daily volume.\n- Automated testing and CI/CD pipelines using Docker, cutting release cycles from weeks to hours.\n- Optimized database queries on PostgreSQL, reducing query latencies by 35%."
            }
        ],
        "education": [
            {
                "school": "Imperial College London",
                "degree": "M.S. in Computer Science (Distributed Systems)",
                "location": "London, UK",
                "start_date": "2013",
                "end_date": "2015",
                "details": "Graduated with Distinction. Specialization in distributed algorithms."
            }
        ],
        "skills": "Python, Go, SQL, AWS (EC2, EKS, RDS, S3), Docker, Kubernetes, Terraform, Git, GitLab CI, Microservices Architecture, Agile Scrum",
        "projects": [
            {
                "name": "CloudScale Orchestrator",
                "role": "Lead Creator",
                "link": "github.com/alexmercer/cloudscale",
                "description": "An open-source autoscaling middleware that integrates with Kubernetes HPA to optimize resource allocation based on predictive request traffic patterns."
            }
        ]
    }

if "ats_report" not in st.session_state:
    st.session_state.ats_report = None

# Header Banner
st.markdown("""
<div class="header-container">
    <div class="header-title">💼 AI ATS Resume Builder & Optimization Pro</div>
    <div class="header-subtitle">Build, Audit, and Optimize Resume Documents in Real-Time</div>
</div>
""", unsafe_allow_html=True)

# ----------------- SIDEBAR CONFIGURATION -----------------
st.sidebar.markdown("### 🎯 Targeting Configuration")
desired_position = st.sidebar.text_input(
    "Desired Position Title",
    placeholder="e.g. Senior DevOps Engineer",
    help="Target job role alignment checks will compare your CV details with this title."
)

job_desc_input = st.sidebar.text_area(
    "Target Job Description",
    height=250,
    placeholder="Paste the target job requirements here to perform keyword matching & optimization...",
    help="ATS compatibility calculations will evaluate keyword match density against this text."
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📄 Parse Existing Resume")
uploaded_file = st.sidebar.file_uploader(
    "Upload Resume PDF",
    type=["pdf"],
    help="Upload your existing CV in PDF format to automatically extract details into the forms below."
)

if uploaded_file is not None:
    if st.sidebar.button("✨ Parse Uploaded Resume with AI", width="stretch"):
        with st.spinner("Extracting text and formatting structure..."):
            try:
                pdf_bytes = uploaded_file.read()
                import fitz
                doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                text = ""
                for page in doc:
                    text += page.get_text()
                doc.close()
                
                if text.strip():
                    parsed_data = ai_parse_resume_text(text, api_key=st.session_state.groq_api_key)
                    st.session_state.resume_data = parsed_data
                    st.sidebar.success("Resume parsed successfully! Forms populated.")
                    st.rerun()
                else:
                    st.sidebar.error("Could not extract readable text from PDF. It might be scanned.")
            except Exception as e:
                logger.error(f"Error parsing PDF: {e}")
                st.sidebar.error(f"Error parsing PDF: {e}")

# ----------------- MAIN PANEL TABS -----------------
tab_builder, tab_scorecard, tab_export = st.tabs([
    "✍️ Resume Builder & AI Optimizer", 
    "📊 ATS Scorecard & Hard Audits", 
    "👁️ Export Preview & Download templates"
])

# ----------------- TAB: RESUME BUILDER & FORMS -----------------
with tab_builder:
    st.subheader("Structured Resume Details")
    st.markdown("Modify your resume contents below. You can dynamically add jobs, degrees, or projects.")
    
    # 1. Contact Details
    st.markdown("#### 👤 Personal & Contact Information")
    col_name, col_title = st.columns(2)
    st.session_state.resume_data["name"] = col_name.text_input("Full Name", value=st.session_state.resume_data.get("name", ""))
    st.session_state.resume_data["title"] = col_title.text_input("Professional Subtitle / Role Name", value=st.session_state.resume_data.get("title", ""))
    
    col_em, col_ph, col_loc = st.columns(3)
    st.session_state.resume_data["email"] = col_em.text_input("Email Address", value=st.session_state.resume_data.get("email", ""))
    st.session_state.resume_data["phone"] = col_ph.text_input("Phone Number", value=st.session_state.resume_data.get("phone", ""))
    st.session_state.resume_data["location"] = col_loc.text_input("Location (City, Country)", value=st.session_state.resume_data.get("location", ""))
    
    col_li, col_gh = st.columns(2)
    st.session_state.resume_data["linkedin"] = col_li.text_input("LinkedIn URL", value=st.session_state.resume_data.get("linkedin", ""))
    st.session_state.resume_data["github"] = col_gh.text_input("GitHub Portfolio Link", value=st.session_state.resume_data.get("github", ""))
    
    # 2. Summary
    st.markdown("---")
    st.markdown("#### 📝 Professional Summary")
    st.session_state.resume_data["summary"] = st.text_area(
        "Write a brief executive summary of your core strengths & experience:",
        value=st.session_state.resume_data.get("summary", ""),
        height=100
    )
    
    # 3. Work Experience List
    st.markdown("---")
    st.markdown("#### 💼 Professional Work History")
    exp_list = st.session_state.resume_data.get("experience", [])
    
    for idx, job in enumerate(exp_list):
        with st.expander(f"Job #{idx+1}: {job.get('company', 'New Company')} - {job.get('title', 'New Role')}", expanded=True):
            col_comp, col_role = st.columns(2)
            c_val = col_comp.text_input("Company Name", value=job.get("company", ""), key=f"comp_{idx}")
            t_val = col_role.text_input("Job Title", value=job.get("title", ""), key=f"role_{idx}")
            
            col_l, col_sd, col_ed = st.columns(3)
            l_val = col_l.text_input("Location", value=job.get("location", ""), key=f"loc_{idx}")
            sd_val = col_sd.text_input("Start Date/Year", value=job.get("start_date", ""), key=f"sd_{idx}")
            ed_val = col_ed.text_input("End Date/Year", value=job.get("end_date", ""), key=f"ed_{idx}")
            
            desc_val = st.text_area("Job Description (Bullet points recommended)", value=job.get("description", ""), key=f"desc_{idx}", height=120)
            
            # Save value changes back
            st.session_state.resume_data["experience"][idx] = {
                "company": c_val,
                "title": t_val,
                "location": l_val,
                "start_date": sd_val,
                "end_date": ed_val,
                "description": desc_val
            }
            
            if st.button(f"❌ Remove Job #{idx+1}", key=f"rem_job_{idx}"):
                st.session_state.resume_data["experience"].pop(idx)
                st.rerun()
                
    if st.button("➕ Add Work Experience Block"):
        if "experience" not in st.session_state.resume_data:
            st.session_state.resume_data["experience"] = []
        st.session_state.resume_data["experience"].append({
            "company": "", "title": "", "location": "", "start_date": "", "end_date": "", "description": ""
        })
        st.rerun()
        
    # 4. Education
    st.markdown("---")
    st.markdown("#### 🎓 Academic Education History")
    edu_list = st.session_state.resume_data.get("education", [])
    
    for idx, edu in enumerate(edu_list):
        with st.expander(f"Education #{idx+1}: {edu.get('school', 'New Institution')}", expanded=True):
            col_sch, col_deg = st.columns(2)
            s_val = col_sch.text_input("School / University Name", value=edu.get("school", ""), key=f"sch_{idx}")
            d_val = col_deg.text_input("Degree & Major", value=edu.get("degree", ""), key=f"deg_{idx}")
            
            col_el, col_esd, col_eed = st.columns(3)
            el_val = col_el.text_input("School Location", value=edu.get("location", ""), key=f"eloc_{idx}")
            esd_val = col_esd.text_input("Start Year", value=edu.get("start_date", ""), key=f"esd_{idx}")
            eed_val = col_eed.text_input("End/Graduation Year", value=edu.get("end_date", ""), key=f"eed_{idx}")
            
            det_val = st.text_input("GPA / Academic Honors / Key Courses", value=edu.get("details", ""), key=f"edet_{idx}")
            
            # Save back
            st.session_state.resume_data["education"][idx] = {
                "school": s_val,
                "degree": d_val,
                "location": el_val,
                "start_date": esd_val,
                "end_date": eed_val,
                "details": det_val
            }
            
            if st.button(f"❌ Remove Education #{idx+1}", key=f"rem_edu_{idx}"):
                st.session_state.resume_data["education"].pop(idx)
                st.rerun()
                
    if st.button("➕ Add Education Block"):
        if "education" not in st.session_state.resume_data:
            st.session_state.resume_data["education"] = []
        st.session_state.resume_data["education"].append({
            "school": "", "degree": "", "location": "", "start_date": "", "end_date": "", "details": ""
        })
        st.rerun()
        
    # 5. Skills
    st.markdown("---")
    st.markdown("#### 🛠️ Technical Skills & Methodologies")
    st.session_state.resume_data["skills"] = st.text_area(
        "Enter comma-separated skills (e.g. Python, SQL, AWS, Kubernetes):",
        value=st.session_state.resume_data.get("skills", ""),
        height=80
    )
    
    # 6. Projects
    st.markdown("---")
    st.markdown("#### 📁 Projects & Open Source contributions")
    proj_list = st.session_state.resume_data.get("projects", [])
    
    for idx, proj in enumerate(proj_list):
        with st.expander(f"Project #{idx+1}: {proj.get('name', 'New Project')}", expanded=True):
            col_pn, col_pr = st.columns(2)
            pn_val = col_pn.text_input("Project Name", value=proj.get("name", ""), key=f"pn_{idx}")
            pr_val = col_pr.text_input("Role / Technologies used", value=proj.get("role", ""), key=f"pr_{idx}")
            pl_val = st.text_input("Project URL / Repository Link", value=proj.get("link", ""), key=f"pl_{idx}")
            pd_val = st.text_area("Project details / descriptions", value=proj.get("description", ""), key=f"pd_{idx}", height=80)
            
            # Save back
            st.session_state.resume_data["projects"][idx] = {
                "name": pn_val,
                "role": pr_val,
                "link": pl_val,
                "description": pd_val
            }
            
            if st.button(f"❌ Remove Project #{idx+1}", key=f"rem_proj_{idx}"):
                st.session_state.resume_data["projects"].pop(idx)
                st.rerun()
                
    if st.button("➕ Add Project Block"):
        if "projects" not in st.session_state.resume_data:
            st.session_state.resume_data["projects"] = []
        st.session_state.resume_data["projects"].append({
            "name": "", "role": "", "link": "", "description": ""
        })
        st.rerun()
        
    # AI Optimization action
    st.markdown("---")
    st.markdown("#### ✨ AI Optimization Suite")
    col_opt1, col_opt2 = st.columns([1, 4])
    with col_opt1:
        optimize_btn = st.button("✨ Optimize Content", type="primary", width="stretch")
    with col_opt2:
        if not job_desc_input:
            st.warning("⚠️ Paste target Job Description in the sidebar to auto-optimize content.")
            
    if optimize_btn:
        if not job_desc_input:
            st.error("Please enter a Target Job Description first.")
        else:
            with st.spinner("AI is rewording descriptions and injecting all missing keywords..."):
                optimized_data = ai_optimize_structured_resume(
                    resume_data=st.session_state.resume_data,
                    job_description=job_desc_input,
                    desired_position=desired_position,
                    api_key=st.session_state.groq_api_key
                )
                st.session_state.resume_data = optimized_data
                st.toast("AI Optimization Complete! Form values updated successfully.", icon="✨")
                st.rerun()

# ----------------- TAB: ATS SCORECARD & AUDITS -----------------
with tab_scorecard:
    st.subheader("ATS Scorecard & Hard System Audits")
    
    col_scan1, col_scan2 = st.columns([1, 4])
    with col_scan1:
        trigger_scan = st.button("🔍 Run Full ATS Scan", type="primary", width="stretch")
    with col_scan2:
        if not job_desc_input:
            st.warning("⚠️ Paste the target job description in the sidebar to evaluate score matches.")
            
    # Flatten structured data into flat text representation for compatibility scanning
    flat_text_list = []
    rd = st.session_state.resume_data
    flat_text_list.append(f"{rd.get('name')} - {rd.get('title')}")
    flat_text_list.append(rd.get("summary", ""))
    for job in rd.get("experience", []):
        flat_text_list.append(f"{job.get('company')} {job.get('title')} {job.get('description')}")
    for edu in rd.get("education", []):
        flat_text_list.append(f"{edu.get('school')} {edu.get('degree')} {edu.get('details')}")
    flat_text_list.append(rd.get("skills", ""))
    for proj in rd.get("projects", []):
        flat_text_list.append(f"{proj.get('name')} {proj.get('description')}")
    full_resume_text = "\n".join(flat_text_list)
    
    if trigger_scan:
        with st.spinner("Evaluating resume against Job Description..."):
            raw_ai_report = evaluate_ats_compatibility(
                resume_text=full_resume_text,
                job_description=job_desc_input or "Software Professional Position",
                api_key=st.session_state.groq_api_key
            )
            
            # Map structured data to dummy sections dict for compatibility with existing integrated analyzer
            sections_map = {
                "CONTACT": f"{rd.get('name')} {rd.get('email')} {rd.get('phone')}",
                "SUMMARY": rd.get("summary", ""),
                "EXPERIENCE": "\n".join([j.get("description", "") for j in rd.get("experience", [])]),
                "EDUCATION": "\n".join([e.get("degree", "") for e in rd.get("education", [])]),
                "SKILLS": rd.get("skills", "")
            }
            
            report = get_integrated_ats_report(
                resume_text=full_resume_text,
                sections=sections_map,
                ai_report=raw_ai_report
            )
            st.session_state.ats_report = report
            st.success("ATS Audit completed!")
            
    report = st.session_state.ats_report
    if report:
        score = report.get("overall_score", 0)
        score_class = "score-high" if score >= 80 else ("score-med" if score >= 60 else "score-low")
        
        col_score, col_metrics = st.columns([1, 2])
        with col_score:
            st.markdown(f"""
            <div class="dashboard-card" style="text-align: center;">
                <div style="font-size: 0.9rem; color: #64748B; text-transform: uppercase; font-weight: 600; margin-bottom: 0.75rem;">ATS Compatibility</div>
                <div class="score-circle {score_class}">
                    <div class="score-value">{score}%</div>
                    <div style="font-size: 0.75rem; text-transform: uppercase; font-weight: 600; margin-top: 2px;">Match Score</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_metrics:
            st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
            st.markdown("<b>Compatibility Breakdown:</b>", unsafe_allow_html=True)
            breakdown = report.get("breakdown", {})
            for key, val in breakdown.items():
                label = key.replace("_", " ").title()
                st.progress(val / 100.0, text=f"{label}: {val}%")
            
            st.markdown(f"""
                <div style="margin-top: 1rem;">
                    <span class="pill-badge badge-success">Action Verb Density: {report.get('action_verb_density', 0)}%</span>
                </div>
            """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        # Hard System Checks Block
        st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
        st.markdown("### 🛡️ System Audit Hard Checks")
        
        # Hard check 1: Page limits / word count
        char_count = len(full_resume_text)
        if char_count < 400:
            st.markdown("❌ **Document Length**: Very short (under 400 chars). Add details. (Impact: Critical)", unsafe_allow_html=True)
        elif char_count > 10000:
            st.markdown("⚠️ **Document Length**: Very long (over 10,000 chars). Condense to 1-2 pages. (Impact: Medium)", unsafe_allow_html=True)
        else:
            st.markdown("✅ **Document Length**: Ideal length for a standard 1-2 page resume.", unsafe_allow_html=True)
            
        # Hard check 2: Essential contact info presence
        if not rd.get("email") or not rd.get("phone"):
            st.markdown("❌ **Contact Information**: Missing Email or Phone Number. Recruiter search blocks will fail. (Impact: Critical)", unsafe_allow_html=True)
        else:
            st.markdown("✅ **Contact Information**: Essential details (Email, Phone) found.", unsafe_allow_html=True)
            
        # Hard check 3: Action verb density check
        verb_density = report.get('action_verb_density', 0)
        if verb_density < 4:
            st.markdown(f"❌ **Action Verb Density**: Weak verb density ({verb_density}%). Integrate active verbs like 'Spearheaded' or 'Optimized'. (Impact: High)", unsafe_allow_html=True)
        else:
            st.markdown(f"✅ **Action Verb Density**: Strong verb usage ({verb_density}%) parsed.", unsafe_allow_html=True)
            
        # Hard check 4: Special Characters scan
        special_chars = re.findall(r'[\u202a-\u202e\u200b-\u200d\u200f]', full_resume_text)
        if special_chars:
            st.markdown(f"❌ **Hidden Characters Check**: Detected {len(special_chars)} hidden/directional Unicode characters. This can cause ATS parser indexing breaks. (Impact: Critical)", unsafe_allow_html=True)
        else:
            st.markdown("✅ **Hidden Characters Check**: Clean Unicode characters without hidden parsing blocks.", unsafe_allow_html=True)
            
        st.markdown("</div>", unsafe_allow_html=True)
            
        # Skills & Keyword Gaps Analysis
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.markdown("<div class='dashboard-card' style='height: 100%;'>", unsafe_allow_html=True)
            st.markdown("### 🛠️ Skills Analysis")
            
            st.markdown("**Matched Technical Skills:**")
            common_skills = report.get("common_skills", [])
            if common_skills:
                for s in common_skills:
                    st.markdown(f'<span class="pill-badge badge-success">✓ {s}</span>', unsafe_allow_html=True)
            else:
                st.info("No matching target skills found.")
                
            st.markdown("<br>**Missing Target Skills:**", unsafe_allow_html=True)
            missing_skills = report.get("missing_skills", [])
            if missing_skills:
                for s in missing_skills:
                    st.markdown(f'<span class="pill-badge badge-warning">⚠ {s}</span>', unsafe_allow_html=True)
            else:
                st.success("Perfect! No critical target skills missing.")
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col_g2:
            st.markdown("<div class='dashboard-card' style='height: 100%;'>", unsafe_allow_html=True)
            st.markdown("### 📝 Keyword Alignments")
            
            st.markdown("**Missing Critical Keywords:**")
            missing_kw = report.get("missing_keywords", [])
            if missing_kw:
                for kw in missing_kw:
                    st.markdown(f'<span class="pill-badge badge-error">⚠ {kw}</span>', unsafe_allow_html=True)
            else:
                st.success("Excellent keyword coverage.")
                
            st.markdown("<br>**Recommended Contextual Terms:**", unsafe_allow_html=True)
            recommended_skills = report.get("recommended_skills", [])
            if recommended_skills:
                for kw in recommended_skills:
                    st.markdown(f'<span class="pill-badge badge-navy">{kw}</span>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        # Strategic recommendations
        st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
        st.markdown("### 💡 Recommended Structural Changes")
        recs = report.get("recommendations", [])
        for idx, r in enumerate(recs):
            st.markdown(f"{idx+1}. {r}")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("📊 Fill out the resume form and target job description, then click 'Run Full ATS Scan' to audit your score.")

# ----------------- TAB: EXPORT PREVIEW & DOWNLOADS -----------------
with tab_export:
    st.subheader("Live Export Preview & Download templates")
    st.markdown("Choose a design template theme, verify structural scaling, and download your production-ready PDF or Word Document.")
    
    selected_theme = st.selectbox(
        "Choose PDF Visual Style Theme",
        options=["Classic Corporate (Navy)", "Modern Minimalist (Slate)", "Creative Executive (Rust)"],
        help="ReportLab flowable coordinates will be styled and built according to this palette."
    )
    
    # Generate resume documents
    pdf_bytes = generate_pdf_from_resume_data(st.session_state.resume_data, selected_theme)
    docx_bytes = generate_docx_from_resume_data(st.session_state.resume_data, f"{st.session_state.resume_data.get('name', 'Resume')}.docx")
    
    # Download Buttons
    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        if pdf_bytes:
            st.download_button(
                label=f"📥 Download PDF ({selected_theme})",
                data=pdf_bytes,
                file_name=f"Resume_{st.session_state.resume_data.get('name', 'CV')}.pdf",
                mime="application/pdf",
                width="stretch"
            )
        else:
            st.button("📥 Download PDF", disabled=True, width="stretch")
            
    with col_dl2:
        if docx_bytes:
            st.download_button(
                label="📥 Download Word (.docx) Format",
                data=docx_bytes,
                file_name=f"Resume_{st.session_state.resume_data.get('name', 'CV')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                width="stretch"
            )
        else:
            st.button("📥 Download Word (.docx) Format", disabled=True, width="stretch")
            
    st.markdown("---")
    
    # Render PDF preview to PNG for local visualization
    st.markdown("#### Page Layout Rendering Output")
    preview_images = convert_pdf_to_images(pdf_bytes)
    if preview_images:
        for page_idx, img_bytes in enumerate(preview_images):
            st.markdown(f"**Page {page_idx + 1}**")
            st.image(img_bytes, width="stretch")
    else:
        st.warning("Failed to render dynamic layout preview.")
