import streamlit as st
import pandas as pd
from io import BytesIO
import docx
import PyPDF2
import time

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="CV Match AI | Tailor Your Future",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CUSTOM CSS FOR MODERN DESIGN ---
st.markdown("""
    <style>
    /* Main Background and Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Blue Theme Colors */
    :root {
        --primary-blue: #2563eb;
        --light-blue: #eff6ff;
        --dark-blue: #1e40af;
        --card-bg: #ffffff;
    }

    /* Modern Card Container */
    .stCard {
        background-color: var(--card-bg);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border: 1px solid #f3f4f6;
        margin-bottom: 20px;
    }

    /* Custom Headers */
    .main-header {
        color: var(--primary-blue);
        font-weight: 700;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    
    .sub-header {
        color: #64748b;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }

    /* Sidebar Styling */
    .css-1d391kg {
        background-color: var(--light-blue);
    }

    /* Buttons */
    .stButton>button {
        background-color: var(--primary-blue);
        color: white;
        border-radius: 8px;
        padding: 0.6rem 2rem;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: var(--dark-blue);
        box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.4);
        transform: translateY(-1px);
    }

    /* Sections */
    .section-title {
        color: var(--dark-blue);
        font-weight: 600;
        font-size: 1.4rem;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid var(--primary-blue);
        padding-left: 10px;
    }

    /* Success Results Card */
    .result-card {
        background-color: #f8fafc;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid var(--light-blue);
        margin-top: 1rem;
    }
    
    .keyword-tag {
        display: inline-block;
        background-color: var(--light-blue);
        color: var(--primary-blue);
        padding: 4px 12px;
        border-radius: 20px;
        margin: 4px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---

def extract_text_from_pdf(file):
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        return f"Error reading PDF: {e}"

def extract_text_from_docx(file):
    try:
        doc = docx.Document(file)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    except Exception as e:
        return f"Error reading DOCX: {e}"

def mock_ai_analysis(user_data, job_role, job_desc):
    """
    Simulates a sophisticated AI analysis of the CV vs Job Description.
    In a real app, this would call OpenAI, Anthropic, or similar.
    """
    # Simulate processing time
    time.sleep(2.5)
    
    # Logic to "find" missing keywords based on common job roles
    all_keywords = ["Python", "SQL", "Communication", "Teamwork", "Agile", "Tableau", "Machine Learning", "Excel", "Public Speaking", "Problem Solving"]
    job_lower = job_desc.lower()
    user_skills_lower = user_data['skills'].lower()
    
    found_keywords = [k for k in all_keywords if k.lower() in job_lower]
    missing_keywords = [k for k in found_keywords if k.lower() not in user_skills_lower]
    
    # Fallback if no keywords found
    if not missing_keywords:
        missing_keywords = ["Data Storytelling", "Strategic Planning", "Cross-functional Collaboration"]

    # Mocking tailored bullet points
    tailored_bullets = [
        f"Leveraged core {job_role} principles to optimize project outcomes by 20%.",
        f"Collaborated with cross-functional teams to deliver {user_data['projects'][:20]}... initiatives.",
        f"Applied technical proficiency in {user_data['skills'].split(',')[0]} to solve complex stakeholder requirements."
    ]

    results = {
        "score": 82,
        "adjusted_summary": f"Aspiring {job_role} with a strong foundation in {user_data['education']}. Proven ability to handle complex projects like '{user_data['projects'][:30]}...' while utilizing {user_data['skills'].split(',')[0] if user_data['skills'] else 'key industry tools'}. Dedicated to driving value through data-driven decisions and professional excellence.",
        "recommendations": [
            "Quantify your achievements: Instead of 'Helped team', use 'Increased efficiency by 15%'.",
            "Move your 'Skills' section higher up to catch the recruiter's eye immediately.",
            "Tailor your project descriptions to highlight 'Impact' rather than just 'Tasks'.",
            f"Explicitly mention your experience with {missing_keywords[0]} if you have any foundation in it."
        ],
        "missing_keywords": missing_keywords,
        "tailored_bullets": tailored_bullets,
        "cover_letter": f"Dear Hiring Manager,\n\nI am writing to express my strong interest in the {job_role} position. With a background in {user_data['education']} and hands-on experience in projects involving {user_data['skills'][:50]}, I am confident in my ability to contribute effectively to your team. My proactive approach and technical skills align perfectly with the requirements mentioned in your job description..."
    }
    return results

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=80)
    st.title("CV Match AI")
    st.info("Tailor your CV to perfection using AI-driven insights.")
    st.divider()
    st.markdown("### How it works")
    st.markdown("""
    1. **Upload** your current CV
    2. **Fill** in your details
    3. **Paste** the Job Description
    4. **Generate** a tailored version
    """)
    st.divider()
    st.caption("v1.0.0 | University Project")

# --- MAIN CONTENT ---
st.markdown('<div class="main-header">CV Match AI 🚀</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Bridge the gap between your experience and your dream job.</div>', unsafe_allow_html=True)

# Main Grid Layout
col1, col2 = st.columns([1.2, 1])

with col1:
    st.markdown('<div class="section-title">1. Upload & Basic Info</div>', unsafe_allow_html=True)
    with st.container():
        uploaded_file = st.file_uploader("Upload your CV (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt"])
        
        extracted_text = ""
        if uploaded_file:
            if uploaded_file.type == "application/pdf":
                extracted_text = extract_text_from_pdf(uploaded_file)
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                extracted_text = extract_text_from_docx(uploaded_file)
            else:
                extracted_text = str(uploaded_file.read(), "utf-8")
            st.success("File uploaded and parsed successfully!")

        with st.expander("👤 Applicant Personal Information", expanded=True):
            c1, c2 = st.columns(2)
            name = c1.text_input("Full Name", placeholder="Jane Doe")
            email = c2.text_input("Email Address", placeholder="jane@example.com")
            phone = c1.text_input("Phone Number")
            link = c2.text_input("LinkedIn / Portfolio Link")

        with st.expander("🎓 Education & Skills"):
            education = st.text_area("Education", placeholder="B.Sc. Computer Science, University of Technology, 2025")
            skills = st.text_area("Skills (Comma separated)", placeholder="Python, SQL, Project Management, Public Speaking")

        with st.expander("💼 Experience & Projects"):
            experience = st.text_area("Professional Experience", help="Include roles, companies, and dates.")
            projects = st.text_area("Key Projects", help="Describe 2-3 significant projects.")
            languages = st.text_input("Languages", placeholder="English (Native), Hebrew (Fluent)")

with col2:
    st.markdown('<div class="section-title">2. Target Job Details</div>', unsafe_allow_html=True)
    job_role = st.text_input("Target Job Role Name", placeholder="e.g. Data Analyst Intern")
    job_desc = st.text_area("Job Description / Requirements", height=300, placeholder="Paste the job description here...")

    st.divider()
    
    generate_btn = st.button("✨ Generate Tailored CV", use_container_width=True)

# --- GENERATION LOGIC ---
if generate_btn:
    if not job_role or not job_desc or not name:
        st.error("Please fill in at least your Name, Job Role, and Job Description.")
    else:
        with st.spinner("AI is analyzing your profile and the job requirements..."):
            user_data = {
                "name": name,
                "email": email,
                "education": education,
                "skills": skills,
                "experience": experience,
                "projects": projects
            }
            results = mock_ai_analysis(user_data, job_role, job_desc)
            
            st.toast("Analysis Complete!", icon="✅")
            
            st.divider()
            st.markdown('<div class="section-title">3. Analysis & Tailored Results</div>', unsafe_allow_html=True)
            
            # Results Metrics
            m1, m2, m3 = st.columns(3)
            m1.metric("Match Score", f"{results['score']}%", "+5% vs average")
            m2.metric("Keywords Found", len(results['missing_keywords']) + 4)
            m3.metric("Recruiter Appeal", "High")

            # Result Tabs
            tab1, tab2, tab3 = st.tabs(["📄 Adjusted Content", "💡 Recommendations", "✉️ Cover Letter"])

            with tab1:
                st.markdown("### Tailored Summary")
                st.info(results['adjusted_summary'])
                
                st.markdown("### Suggested Bullet Points for this Role")
                for bullet in results['tailored_bullets']:
                    st.write(f"• {bullet}")
                
                st.markdown("### Missing Keywords to Add")
                kw_html = "".join([f'<span class="keyword-tag">{kw}</span>' for kw in results['missing_keywords']])
                st.markdown(kw_html, unsafe_allow_html=True)

            with tab2:
                st.markdown("### How to Improve Your CV")
                for rec in results['recommendations']:
                    st.success(rec)
                
                st.markdown("### Next Steps")
                st.markdown("""
                1. **Update your LinkedIn** with the missing keywords found.
                2. **Re-word your top project** using the suggested bullet points.
                3. **Check formatting**: Ensure your contact info is easy to find.
                """)

            with tab3:
                st.text_area("Generated Short Cover Letter Summary", value=results['cover_letter'], height=250)
                st.caption("Pro tip: Personalize the first paragraph with a specific detail about the company.")

# --- FOOTER ---
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #94a3b8; font-size: 0.8rem;'>"
    "CV Match AI - University Project Prototype<br>"
    "Built with Streamlit & ❤️"
    "</div>", 
    unsafe_allow_html=True
)
