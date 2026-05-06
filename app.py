import streamlit as st
import pandas as pd
from io import BytesIO
import docx
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, RGBColor
import PyPDF2
import re
from collections import Counter

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="CV Match AI",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- INITIALIZE SESSION STATE ---
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'job_role' not in st.session_state:
    st.session_state.job_role = ""
if 'cv_full_text' not in st.session_state:
    st.session_state.cv_full_text = ""
if 'job_desc' not in st.session_state:
    st.session_state.job_desc = ""
if 'input_method' not in st.session_state:
    st.session_state.input_method = "Upload an existing CV"
if 'manual_cv_data' not in st.session_state:
    st.session_state.manual_cv_data = {}
if 'follow_up_answers' not in st.session_state:
    st.session_state.follow_up_answers = {}
if 'missing_keywords' not in st.session_state:
    st.session_state.missing_keywords = []
if 'matching_keywords' not in st.session_state:
    st.session_state.matching_keywords = []
if 'match_score' not in st.session_state:
    st.session_state.match_score = 0

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    :root {
        --primary-blue: #1e3a8a;
        --secondary-gray: #475569;
        --light-bg: #f8fafc;
        --border-color: #e2e8f0;
        --white: #ffffff;
    }

    .main-header {
        color: var(--primary-blue);
        font-weight: 700;
        font-size: 2.2rem;
        margin-bottom: 0.1rem;
    }
    
    .sub-header {
        color: var(--secondary-gray);
        font-size: 1.1rem;
        margin-bottom: 1.5rem;
    }

    .pipeline-container {
        display: flex;
        justify-content: space-between;
        background-color: var(--white);
        padding: 1rem 1.5rem;
        border-radius: 8px;
        border: 1px solid var(--border-color);
        margin-bottom: 2rem;
    }

    .pipeline-step {
        font-size: 0.8rem;
        font-weight: 500;
        color: #94a3b8;
        text-align: center;
        flex: 1;
        position: relative;
    }

    .pipeline-step.active {
        color: var(--primary-blue);
        font-weight: 700;
        border-bottom: 3px solid var(--primary-blue);
        padding-bottom: 5px;
    }

    .content-card {
        background-color: var(--white);
        padding: 2rem;
        border-radius: 12px;
        border: 1px solid var(--border-color);
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 1.5rem;
    }

    /* CV Preview Page */
    .cv-page {
        background-color: white;
        width: 100%;
        max-width: 800px;
        margin: 0 auto;
        padding: 40px 60px;
        border: 1px solid #d1d5db;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        color: #1f2937;
    }

    .cv-header-name {
        font-size: 2rem;
        font-weight: 700;
        color: var(--primary-blue);
        text-align: center;
        margin-bottom: 8px;
        line-height: 1.2;
    }

    .cv-header-contact {
        text-align: center;
        font-size: 0.9rem;
        color: #4b5563;
        margin-bottom: 30px;
    }

    .cv-section-title {
        color: var(--primary-blue);
        border-bottom: 1px solid #cbd5e1;
        font-weight: 700;
        margin-top: 22px;
        margin-bottom: 10px;
        text-transform: uppercase;
        font-size: 0.95rem;
        letter-spacing: 0.5px;
    }

    .cv-item-title {
        font-weight: 700;
        font-size: 1rem;
        color: #111827;
    }

    .cv-item-sub {
        font-weight: 500;
        font-size: 0.9rem;
        color: #4b5563;
        font-style: italic;
    }

    .cv-content {
        font-size: 0.9rem;
        line-height: 1.5;
        margin-bottom: 8px;
    }

    .cv-skills-group {
        margin-bottom: 5px;
    }

    .cv-skills-label {
        font-weight: 700;
        color: #374151;
    }

    .keyword-tag {
        display: inline-block;
        background-color: #f1f5f9;
        color: #1e3a8a;
        padding: 3px 10px;
        border-radius: 4px;
        margin: 3px;
        font-size: 0.8rem;
        font-weight: 600;
        border: 1px solid #cbd5e1;
    }

    .missing-tag {
        display: inline-block;
        background-color: #fef2f2;
        color: #991b1b;
        padding: 3px 10px;
        border-radius: 4px;
        margin: 3px;
        font-size: 0.8rem;
        font-weight: 600;
        border: 1px solid #fecaca;
    }

    .rtl { direction: rtl; text-align: right; }
    .ltr { direction: ltr; text-align: left; }
    
    .stButton > button {
        border-radius: 6px;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONSTANTS & DICTIONARIES ---

STOPWORDS = {"a", "an", "the", "and", "or", "but", "if", "then", "else", "when", "at", "from", "by", "for", "with", "about", "against", "between", "into", "through", "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here", "there", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now", "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves", "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing"}

GENERIC_TERMS = {"ability", "advanced", "bachelor", "common", "core", "critical", "degree", "entry", "familiarity", "field", "fields", "foundation", "job", "knowledge", "large", "like", "strong", "excellent", "good", "responsible", "requirement", "requirements", "responsibilities", "candidate", "company", "team", "work", "working", "looking", "opportunity", "motivated", "passion", "years", "experience", "role", "position", "plus", "must", "needed", "required", "preferred"}

# Technical Skill Keywords for improved parsing
SKILL_KEYWORDS = {
    "python", "sql", "java", "javascript", "react", "node", "html", "css", "git", "github", 
    "r", "matlab", "tableau", "powerbi", "power bi", "excel", "bigquery", "pandas", "numpy", 
    "scikit-learn", "tensorflow", "pytorch", "aws", "azure", "docker", "kubernetes", "unix", 
    "linux", "bash", "spark", "hadoop", "c++", "c#", "php", "ruby", "swift", "kotlin", "typescript"
}

HEADINGS_MAP = {
    "English": ["Personal Details", "Professional Summary", "Education", "Professional Experience", "Projects", "Courses & Training", "Volunteering / Community", "Languages", "Skills", "Additional Information"],
    "Hebrew": ["פרטים אישיים", "תמצית מקצועית", "השכלה", "ניסיון תעסוקתי", "פרויקטים", "קורסים והכשרות", "התנדבות / קהילה", "שפות", "כישורים", "מידע נוסף"],
    "Arabic": ["البيانات الشخصية", "الملخص المهني", "التعليم", "الخبرة العملية", "المشاريع", "الدورات والتدريب", "التطوع / المجتمع", "اللغات", "المهارات", "معلومات إضافية"]
}

CV_TITLES = {"English": "Curriculum Vitae", "Hebrew": "קורות חיים", "Arabic": "السيرة الذاتية"}

SECTION_REGEX = {
    "personal_details": r"(personal details|contact|contact info|פרטים אישיים|البيانات الشخصية)",
    "summary": r"(summary|profile|about me|professional summary|תמצית|פרופיל|תמצית מקצועית|الملخص|ملخص مهني)",
    "education": r"(education|academic|degrees|השכלה|לימודים|التعليم|المؤهلات العلمية)",
    "experience": r"(experience|work|employment|history|professional experience|ניסיון|ניסיון תעסוקתי|الخبرة|الخبرة العملية)",
    "projects": r"(projects|key projects|academic projects|פרויקטים|פרוייקטים|المشاريع)",
    "courses_training": r"(courses|training|certification|certifications|קורסים|הכשרות|הסמכות|الدورات|التدريب)",
    "volunteering": r"(volunteering|community|extracurricular|volunteer|התנדבות|פעילות קהילתית|التطوع)",
    "languages": r"(languages|שפות|اللغات)",
    "skills": r"(skills|competencies|technologies|technical skills|כישורים|מיומנויות|יכולות|المهارات)"
}

SAMPLE_CV_DATA = {
    "personal_details": "Jane Doe | jane.doe@email.com | +1 234 567 890 | linkedin.com/in/janedoe",
    "summary": "Motivated Computer Science student with a passion for software development and data analysis. Seeking an internship to apply my skills in Python and SQL to real-world problems.",
    "education": "B.Sc. in Computer Engineering, University of Technology (Expected 2025)\nGPA: 3.8/4.0",
    "experience": "Software Intern at TechCorp (Summer 2023)\n- Developed automated scripts using Python.\n- Collaborated with the QA team to identify bugs.\n- Optimized SQL queries, reducing database load by 15%.",
    "projects": "Local Library Management System - Built a full-stack app using React and Node.js.",
    "courses_training": "Full Stack Web Development, Data Structures & Algorithms, Machine Learning Basics",
    "volunteering": "Code Club Mentor - Taught basic programming to high school students.",
    "languages": "English (Native), Hebrew (Fluent), Spanish (Beginner)",
    "skills": "Python, Java, SQL, Git, Microsoft Excel, Teamwork, Problem Solving"
}

# --- CORE FUNCTIONS ---

def detect_language(text):
    if re.search(r'[\u0590-\u05FF]', text): return "Hebrew"
    if re.search(r'[\u0600-\u06FF]', text): return "Arabic"
    return "English"

def clean_text_simple(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\u0590-\u05FF\u0600-\u06FF\s]', ' ', text)
    return text

def extract_keywords(text):
    cleaned = clean_text_simple(text)
    words = cleaned.split()
    return [w for w in words if w not in STOPWORDS and w not in GENERIC_TERMS and len(w) > 2]

def extract_text_from_pdf(file):
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except: return ""

def extract_text_from_docx(file):
    try:
        doc = docx.Document(file)
        return "\n".join([para.text for para in doc.paragraphs])
    except: return ""

def classify_sections_refined(text):
    sections = {"personal_details": "", "summary": "", "education": "", "experience": "", "projects": "", "courses_training": "", "volunteering": "", "languages": "", "skills": "", "additional_information": ""}
    
    current_section = "personal_details"
    lines = text.split('\n')
    
    for line in lines:
        clean_line = line.strip()
        if not clean_line: continue
        
        low_line = clean_line.lower()
        found_header = False
        
        # Header Detection
        if len(clean_line) < 35:
            for key, pattern in SECTION_REGEX.items():
                if re.search(pattern, low_line):
                    current_section = key
                    found_header = True
                    break
        
        if not found_header:
            # Skill line heuristic: if line is short and contains known skill keywords, move to skills
            if current_section in ["experience", "education", "personal_details"] and len(clean_line) < 60:
                line_words = set(re.findall(r'\w+', low_line))
                if line_words.intersection(SKILL_KEYWORDS) and len(line_words) < 8:
                    sections["skills"] += clean_line + ", "
                    continue
            
            sections[current_section] += clean_line + "\n"
            
    # Final cleanup
    for k in sections:
        sections[k] = re.sub(r'\n{2,}', '\n', sections[k].strip())
        if k == "skills":
            sections[k] = sections[k].strip(", ")
            
    return sections

def format_contact_info(text):
    lines = text.split('\n')
    if not lines: return "", ""
    name = lines[0].strip()
    rest = " · ".join([l.strip() for l in lines[1:] if l.strip()])
    return name, rest

def group_skills(skills_text):
    if not skills_text: return []
    skills = [s.strip() for s in re.split(r'[,|\n]', skills_text) if s.strip()]
    # Simple grouping by keyword sets
    groups = {
        "Technical": [],
        "Tools & Technologies": [],
        "Other Skills": []
    }
    for s in skills:
        sl = s.lower()
        if any(kw in sl for kw in ["python", "sql", "java", "r", "javascript", "c++", "c#", "data", "analysis", "learning", "statistics"]):
            groups["Technical"].append(s)
        elif any(kw in sl for kw in ["git", "github", "docker", "excel", "tableau", "powerbi", "jira", "aws", "azure"]):
            groups["Tools & Technologies"].append(s)
        else:
            groups["Other Skills"].append(s)
    
    result = []
    for label, items in groups.items():
        if items:
            result.append(f"**{label}:** " + ", ".join(sorted(list(set(items)))))
    return result

def generate_docx_pro(cv_data, output_lang):
    doc = Document()
    is_rtl = output_lang in ["Hebrew", "Arabic"]
    headings = HEADINGS_MAP[output_lang]
    
    # Styles
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Arial' if is_rtl else 'Calibri'
    font.size = Pt(11)
    
    # Name Header
    name, contact = format_contact_info(cv_data.get("personal_details", ""))
    p_name = doc.add_heading(name if name else CV_TITLES[output_lang], 0)
    if is_rtl: p_name.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    
    if contact:
        p_contact = doc.add_paragraph(contact)
        p_contact.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    sections_keys = ["summary", "education", "experience", "projects", "courses_training", "volunteering", "languages", "skills", "additional_information"]
    
    for i, key in enumerate(sections_keys):
        content = cv_data.get(key, "").strip()
        if content:
            h = doc.add_heading(headings[i+1], level=1)
            # Custom blue color for headings
            run = h.runs[0]
            run.font.color.rgb = RGBColor(30, 58, 138)
            if is_rtl: h.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            
            if key == "skills":
                # Grouped skills
                for sg in group_skills(content):
                    p = doc.add_paragraph(sg.replace("**", ""))
                    if is_rtl: p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            else:
                lines = content.split('\n')
                for line in lines:
                    if line.startswith('-') or line.startswith('•'):
                        p = doc.add_paragraph(line.strip('- •'), style='List Bullet')
                    else:
                        p = doc.add_paragraph(line)
                    if is_rtl: p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- NAVIGATION ---

def next_step(): st.session_state.step += 1
def prev_step(): st.session_state.step -= 1

# --- APP LAYOUT ---

st.markdown('<div class="main-header">CV Match AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Professional Wizard-Based CV Tailoring System</div>', unsafe_allow_html=True)

# Pipeline Indicator
steps = ["1. Job Role", "2. CV Input", "3. Job Description", "4. Analysis", "5. Follow-up", "6. Preview", "7. Download"]
st.markdown('<div class="pipeline-container">', unsafe_allow_html=True)
cols = st.columns(len(steps))
for i, s in enumerate(steps):
    active_class = "active" if st.session_state.step == i + 1 else ""
    cols[i].markdown(f'<div class="pipeline-step {active_class}">{s}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- STEP 1: JOB ROLE ---
if st.session_state.step == 1:
    st.markdown("### Step 1: Target Job Role")
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.session_state.job_role = st.text_input(
        "Enter the job role you are applying for:",
        value=st.session_state.job_role,
        placeholder="e.g. Data Analyst Intern, Software Developer Student Position, Business Analyst Intern"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    if st.button("Next ➔", use_container_width=True):
        if not st.session_state.job_role: st.error("Please enter a job role.")
        else: next_step()

# --- STEP 2: CV INPUT ---
elif st.session_state.step == 2:
    st.markdown("### Step 2: CV Information Input")
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.session_state.input_method = st.selectbox(
        "How would you like to provide your CV?",
        ["Upload an existing CV", "Paste CV text manually", "Build a CV from structured fields", "Use demo data"],
        index=["Upload an existing CV", "Paste CV text manually", "Build a CV from structured fields", "Use demo data"].index(st.session_state.input_method)
    )
    
    if st.session_state.input_method == "Upload an existing CV":
        st.info("Upload your current CV (PDF, DOCX, TXT).")
        uploaded_file = st.file_uploader("Choose File", type=["pdf", "docx", "txt"], label_visibility="collapsed")
        if uploaded_file:
            if uploaded_file.type == "application/pdf": st.session_state.cv_full_text = extract_text_from_pdf(uploaded_file)
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document": st.session_state.cv_full_text = extract_text_from_docx(uploaded_file)
            else: st.session_state.cv_full_text = str(uploaded_file.read(), "utf-8")
            if st.session_state.cv_full_text: st.success("File uploaded successfully.")

    elif st.session_state.input_method == "Paste CV text manually":
        st.session_state.cv_full_text = st.text_area("Paste CV text:", value=st.session_state.cv_full_text, height=300)

    elif st.session_state.input_method == "Build a CV from structured fields":
        c1, c2 = st.columns(2)
        with c1:
            st.session_state.manual_cv_data["personal_details"] = st.text_input("Personal Details", value=st.session_state.manual_cv_data.get("personal_details", ""))
            st.session_state.manual_cv_data["summary"] = st.text_area("Summary", value=st.session_state.manual_cv_data.get("summary", ""))
            st.session_state.manual_cv_data["education"] = st.text_area("Education", value=st.session_state.manual_cv_data.get("education", ""))
        with c2:
            st.session_state.manual_cv_data["experience"] = st.text_area("Experience", value=st.session_state.manual_cv_data.get("experience", ""))
            st.session_state.manual_cv_data["projects"] = st.text_area("Projects", value=st.session_state.manual_cv_data.get("projects", ""))
            st.session_state.manual_cv_data["skills"] = st.text_area("Skills", value=st.session_state.manual_cv_data.get("skills", ""))
        st.session_state.cv_full_text = "\n".join(st.session_state.manual_cv_data.values())

    elif st.session_state.input_method == "Use demo data":
        st.info("Demo student CV loaded.")
        st.session_state.manual_cv_data = SAMPLE_CV_DATA
        st.session_state.cv_full_text = "\n".join(SAMPLE_CV_DATA.values())
    st.markdown('</div>', unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    if c1.button("⬅ Back", use_container_width=True): prev_step()
    if c2.button("Next ➔", use_container_width=True):
        if len(st.session_state.cv_full_text.split()) < 20: st.error("CV content is too short.")
        else: next_step()

# --- STEP 3: JOB DESCRIPTION ---
elif st.session_state.step == 3:
    st.markdown("### Step 3: Job Description")
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.session_state.job_desc = st.text_area(
        "Paste the full job description here:",
        value=st.session_state.job_desc,
        height=300,
        placeholder="Responsibilities, requirements, skills..."
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    if c1.button("⬅ Back", use_container_width=True): prev_step()
    if c2.button("Validate and Analyze ➔", use_container_width=True):
        jd_words = st.session_state.job_desc.split()
        if len(jd_words) < 30: st.error("Job description is too short (min 30 words).")
        elif len(set(jd_words)) < 15: st.error("Job description appears invalid.")
        else:
            # Run Analysis
            cv_kw = set(extract_keywords(st.session_state.cv_full_text))
            job_kw = set(extract_keywords(st.session_state.job_desc))
            st.session_state.matching_keywords = list(job_kw.intersection(cv_kw))
            st.session_state.missing_keywords = sorted(list(job_kw.difference(cv_kw)))[:12]
            st.session_state.match_score = int((len(st.session_state.matching_keywords) / len(job_kw)) * 100) if job_kw else 0
            next_step()

# --- STEP 4: ANALYSIS ---
elif st.session_state.step == 4:
    st.markdown("### Step 4: Validation & Match Analysis")
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    col1.metric("Local Match Score", f"{st.session_state.match_score}%")
    col2.metric("Matching Terms", len(st.session_state.matching_keywords))
    col3.metric("Actionable Gaps", len(st.session_state.missing_keywords))
    
    st.write("**Matching Keywords:**")
    st.markdown("".join([f'<span class="keyword-tag">{k}</span>' for k in st.session_state.matching_keywords[:20]]), unsafe_allow_html=True)
    st.write("**Missing Critical Keywords:**")
    st.markdown("".join([f'<span class="missing-tag">{k}</span>' for k in st.session_state.missing_keywords]), unsafe_allow_html=True)
    
    st.info("**Tailored Feedback:** Based on your target role as a " + st.session_state.job_role + ", consider emphasizing your experience with the missing keywords in your projects or summary.")
    st.markdown('</div>', unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    if c1.button("⬅ Back", use_container_width=True): prev_step()
    if c2.button("Continue to Follow-up Questions ➔", use_container_width=True): next_step()

# --- STEP 5: FOLLOW-UP ---
elif st.session_state.step == 5:
    st.markdown("### Step 5: Information That Could Improve Your CV")
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    
    q1 = f"Do you have real experience with {', '.join(st.session_state.missing_keywords[:4])}?"
    q2 = f"Have you completed an academic project related to {st.session_state.job_role}?"
    q3 = "Do you have any certifications or tools not mentioned in your initial CV?"
    q4 = "Do you have measurable achievements (e.g., 'Improved performance by 20%')?"
    
    topics = ["Skill Experience", "Academic Projects", "Certifications", "Measurable Achievements"]
    qs = [q1, q2, q3, q4]
    
    for i, q in enumerate(qs):
        st.write(f"**Question {i+1}:** {q}")
        st.session_state.follow_up_answers[topics[i]] = st.text_area(f"Answer for {topics[i]}", value=st.session_state.follow_up_answers.get(topics[i], ""), key=f"q_{i}", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    if c1.button("⬅ Back", use_container_width=True): prev_step()
    if c2.button("Generate Final CV ➔", use_container_width=True): next_step()

# --- STEP 6: PREVIEW ---
elif st.session_state.step == 6:
    st.markdown("### Step 6: Final CV Preview")
    
    out_lang = st.radio("Output CV Language:", ["Same as input", "English", "Hebrew", "Arabic"], horizontal=True)
    det_lang = detect_language(st.session_state.cv_full_text)
    active_lang = det_lang if out_lang == "Same as input" else out_lang
    
    if out_lang != "Same as input" and out_lang != det_lang:
        st.warning("Note: Local MVP only translates headings and structure. Content remains in its original language.")
    
    # Process CV Data
    if st.session_state.input_method in ["Build a CV from structured fields", "Use demo data"]:
        cv_data = st.session_state.manual_cv_data.copy()
    else:
        cv_data = classify_sections_refined(st.session_state.cv_full_text)
    
    # Add Follow-up Answers
    add_info = ""
    for topic, ans in st.session_state.follow_up_answers.items():
        if ans.strip():
            add_info += f"{topic}\n- {ans.strip()}\n"
    if add_info:
        cv_data["additional_information"] = (cv_data.get("additional_information", "") + "\n" + add_info).strip()

    # Visual Preview
    is_rtl = active_lang in ["Hebrew", "Arabic"]
    lang_class = "rtl" if is_rtl else "ltr"
    headings = HEADINGS_MAP[active_lang]
    
    st.markdown(f'<div class="cv-page {lang_class}">', unsafe_allow_html=True)
    
    name, contact = format_contact_info(cv_data.get("personal_details", ""))
    st.markdown(f'<div class="cv-header-name">{name if name else CV_TITLES[active_lang]}</div>', unsafe_allow_html=True)
    if contact: st.markdown(f'<div class="cv-header-contact">{contact}</div>', unsafe_allow_html=True)
    
    order = ["summary", "education", "experience", "projects", "courses_training", "volunteering", "languages", "skills", "additional_information"]
    for i, key in enumerate(order):
        content = cv_data.get(key, "").strip()
        if content:
            st.markdown(f'<div class="cv-section-title">{headings[i+1]}</div>', unsafe_allow_html=True)
            if key == "skills":
                for sg in group_skills(content):
                    st.markdown(f'<div class="cv-content">{sg}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="cv-content">{content.replace("\n", "<br>")}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    if c1.button("⬅ Back", use_container_width=True): prev_step()
    if c2.button("Continue to Download ➔", use_container_width=True):
        st.session_state.final_cv_data = cv_data
        st.session_state.active_lang = active_lang
        next_step()

# --- STEP 7: DOWNLOAD ---
elif st.session_state.step == 7:
    st.markdown("### Step 7: Download Final CV")
    st.markdown('<div class="content-card" style="text-align:center;">', unsafe_allow_html=True)
    st.write("Your tailored CV is ready for download.")
    
    # TXT Export
    active_lang = st.session_state.active_lang
    headings = HEADINGS_MAP[active_lang]
    cv_data = st.session_state.final_cv_data
    
    txt_out = f"{CV_TITLES[active_lang].upper()}\n{'='*20}\n"
    name, contact = format_contact_info(cv_data.get("personal_details", ""))
    txt_out += f"{name}\n{contact}\n"
    
    order = ["summary", "education", "experience", "projects", "courses_training", "volunteering", "languages", "skills", "additional_information"]
    for i, key in enumerate(order):
        content = cv_data.get(key, "").strip()
        if content:
            txt_out += f"\n{headings[i+1].upper()}\n{'-'*len(headings[i+1])}\n{content}\n"
            
    c1, c2 = st.columns(2)
    c1.download_button("📄 Download as TXT", txt_out, file_name="tailored_cv.txt", use_container_width=True)
    
    docx_buf = generate_docx_pro(cv_data, active_lang)
    c2.download_button("📁 Download as DOCX", docx_buf, file_name="tailored_cv.docx", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("⬅ Back to Preview", use_container_width=True): prev_step()

# --- FOOTER ---
st.markdown("---")
st.markdown("<div style='text-align: center; color: #94a3b8; font-size: 0.8rem;'>CV Match AI - Professional University MVP | Local Rule-Based System</div>", unsafe_allow_html=True)
