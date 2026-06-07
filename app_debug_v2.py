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
    initial_sidebar_state="collapsed",
)

# --- INITIALIZE SESSION STATE ---
defaults = {
    'active_tab': 0,
    'job_role': "",
    'cv_full_text': "",
    'job_desc': "",
    'input_method': "Upload File",
    'manual_cv_data': {},
    'follow_up_answers': {},
    'analysis_results': {"matches": [], "missing": [], "score": 0},
    'final_cv_data': {},
    'adjusted_cv_data': {},
    'active_lang': "English",
    'cv_uploaded': False,
    'analysis_done': False,
    'cv_adjusted': False,
    'show_landing': True,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    /* ── VARIABLES ── */
    :root {
        --pink: #be185d;
        --pink-light: #fce7f3;
        --pink-mid: #f9a8d4;
        --dark: #191919;
        --muted: #6b6b6b;
        --border: #e9e9e7;
        --bg: #f8f8f7;
    }

    /* ── STREAMLIT OVERRIDES ── */
    .block-container {
        padding-top: 0 !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 860px !important;
    }
    #MainMenu, footer, header { visibility: hidden; }
    div[data-testid="stTabs"] { display: none; }

    /* ── STEP BAR ── */
    .rp-step-bar {
        display: flex;
        align-items: center;
        background: var(--bg);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 12px 16px;
        margin-bottom: 28px;
        gap: 0;
    }
    .rp-step-item { display: flex; align-items: center; gap: 8px; flex: 1; }
    .rp-step-dot {
        width: 22px; height: 22px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 10px; font-weight: 700; flex-shrink: 0;
        transition: all 0.2s;
    }
    .rp-dot-done   { background: var(--pink); color: white; }
    .rp-dot-active { background: var(--dark); color: white; }
    .rp-dot-todo   { background: var(--border); color: #9b9b9b; }
    .rp-step-name { font-size: 12px; font-weight: 500; }
    .rp-name-done   { color: var(--pink); font-weight: 600; }
    .rp-name-active { color: var(--dark); font-weight: 600; }
    .rp-name-todo   { color: #9b9b9b; }
    .rp-connector { height: 2px; width: 20px; flex-shrink: 0; }
    .rp-conn-done { background: var(--pink); }
    .rp-conn-todo { background: var(--border); }

    /* ── LOGO / HEADER ── */
    .rp-header {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 18px 0 16px;
        border-bottom: 1px solid var(--border);
        margin-bottom: 28px;
    }
    .rp-logo-box {
        width: 32px; height: 32px;
        flex-shrink: 0;
    }
    .rp-brand { font-size: 17px; font-weight: 700; letter-spacing: -0.4px; color: var(--dark); }
    .rp-tagline { font-size: 13px; color: var(--muted); margin-left: auto; }

    /* ── PAGE TITLES ── */
    .rp-page-badge { font-size: 11px; color: #9b9b9b; font-weight: 500; letter-spacing: 0.3px; margin-bottom: 6px; }
    .rp-page-title { font-size: 26px; font-weight: 700; letter-spacing: -0.6px; color: var(--dark); margin-bottom: 5px; }
    .rp-page-sub   { font-size: 13px; color: var(--muted); margin-bottom: 24px; line-height: 1.5; }

    /* ── CARDS ── */
    .rp-card {
        background: var(--bg);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 20px 22px;
        margin-bottom: 16px;
    }
    .rp-card-white {
        background: white;
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 20px 22px;
        margin-bottom: 16px;
    }

    /* ── SCORE DARK ── */
    .rp-score-dark {
        background: var(--dark);
        color: white;
        border-radius: 12px;
        padding: 22px 26px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 14px;
    }
    .rp-score-num { font-size: 48px; font-weight: 800; letter-spacing: -2px; line-height: 1; }
    .rp-score-label { font-size: 11px; color: rgba(255,255,255,0.4); margin-bottom: 3px; letter-spacing: 0.4px; }
    .rp-score-desc { font-size: 12px; color: rgba(255,255,255,0.5); margin-top: 4px; }
    .rp-score-right { text-align: right; font-size: 12px; line-height: 2.2; }
    .rp-score-s { color: #86efac; }
    .rp-score-p { color: rgba(255,255,255,0.5); }
    .rp-score-m { color: rgba(255,255,255,0.3); }

    /* ── ANALYSIS ITEMS ── */
    .rp-analysis-item {
        display: flex; align-items: center; justify-content: space-between;
        padding: 9px 13px; border-radius: 7px;
        background: var(--bg); border: 1px solid var(--border);
        margin-bottom: 5px; font-size: 13px;
    }
    .rp-pill {
        font-size: 11px; font-weight: 500;
        padding: 2px 9px; border-radius: 9999px;
    }
    .rp-pill-strong  { background: #dcfce7; color: #166534; }
    .rp-pill-partial { background: #fef9c3; color: #92400e; }
    .rp-pill-missing { background: #fee2e2; color: #991b1b; }

    /* ── TIP BOX ── */
    .rp-tip {
        background: var(--pink-light);
        border: 1px solid var(--pink-mid);
        border-radius: 10px;
        padding: 14px 16px;
        font-size: 13px;
        color: #831843;
        line-height: 1.6;
        margin-top: 14px;
    }

    /* ── REFINEMENT Q ── */
    .rp-q-num {
        display: inline-flex; align-items: center; justify-content: center;
        background: var(--pink); color: white;
        width: 20px; height: 20px; border-radius: 50%;
        font-size: 10px; font-weight: 700;
        margin-right: 6px;
    }
    .rp-q-text { font-size: 13px; font-weight: 500; color: var(--dark); margin-bottom: 8px; }

    /* ── LANG TABS ── */
    .rp-lang-tab {
        display: inline-block;
        padding: 6px 16px;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 500;
        cursor: pointer;
        margin-right: 6px;
        border: 1px solid var(--border);
        color: var(--muted);
    }
    .rp-lang-tab-active {
        background: var(--pink);
        color: white;
        border-color: var(--pink);
    }

    /* ── DOWNLOAD CARDS ── */
    .rp-dl-fmt  { font-weight: 700; font-size: 15px; margin-bottom: 3px; }
    .rp-dl-desc { font-size: 12px; color: #9b9b9b; margin-bottom: 14px; }

    /* ── CHECKLIST ── */
    .rp-checklist { border: 1px solid var(--border); border-radius: 10px; padding: 18px 20px; background: white; }
    .rp-checklist-title { font-weight: 600; font-size: 13px; margin-bottom: 10px; }
    .rp-check-item { font-size: 12px; color: var(--muted); padding: 4px 0; }

    /* ── BUTTON OVERRIDES ── */
    .stButton > button {
        border-radius: 7px !important;
        font-weight: 500 !important;
        font-size: 13px !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.15s !important;
    }
    .stButton > button[kind="primary"] {
        background: var(--dark) !important;
        color: white !important;
        border: none !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: #333 !important;
    }
    /* Pink primary button via class trick */
    .btn-pink-wrapper .stButton > button {
        background: var(--pink) !important;
        color: white !important;
        border: none !important;
    }

    /* ── INPUT OVERRIDES ── */
    .stTextInput input, .stTextArea textarea {
        border-radius: 7px !important;
        border: 1px solid var(--border) !important;
        background: #fafafa !important;
        font-size: 13px !important;
        font-family: 'Inter', sans-serif !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: var(--dark) !important;
        background: white !important;
        box-shadow: none !important;
    }

    /* ── ALERT OVERRIDES ── */
    .alert-green  { background: #dcfce7; color: #166534; padding:12px 16px; border-radius:8px; font-size:13px; }
    .alert-orange { background: #ffedd5; color: #9a3412; padding:12px 16px; border-radius:8px; font-size:13px; }
    .alert-red    { background: #fee2e2; color: #991b1b; padding:12px 16px; border-radius:8px; font-size:13px; }

    /* ── LANDING PAGE ── */
    .rp-landing {
        min-height: 100vh;
        background: radial-gradient(ellipse 90% 50% at 50% -5%, #fce7f3 0%, #fff 60%);
    }
    .rp-hero { max-width: 640px; margin: 0 auto; padding: 80px 32px 56px; text-align: center; }
    .rp-hero-badge {
        display: inline-flex; align-items: center; gap: 6px;
        background: var(--pink-light); color: var(--pink);
        border-radius: 20px; padding: 5px 14px;
        font-size: 12px; font-weight: 600; margin-bottom: 24px;
    }
    .rp-hero h1 {
        font-size: 52px; font-weight: 800; line-height: 1.08;
        letter-spacing: -2.5px; margin-bottom: 18px; color: var(--dark);
    }
    .rp-hero h1 span { color: var(--pink); }
    .rp-hero p { font-size: 16px; color: var(--muted); line-height: 1.65; max-width: 420px; margin: 0 auto 32px; }
    .rp-social-proof { text-align: center; font-size: 12px; color: #9b9b9b; padding: 16px 0 0; }
    .rp-features { max-width: 840px; margin: 48px auto 0; padding: 0 32px 64px; display: grid; grid-template-columns: repeat(3,1fr); gap: 14px; }
    .rp-feature {
        background: white; border: 1px solid var(--border);
        border-radius: 12px; padding: 22px;
        position: relative; overflow: hidden;
        transition: box-shadow 0.2s;
    }
    .rp-feature::before {
        content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
        background: var(--pink); transform: scaleX(0); transition: transform 0.2s;
    }
    .rp-feature:hover::before { transform: scaleX(1); }
    .rp-feature:hover { box-shadow: 0 4px 20px rgba(0,0,0,0.06); }
    .rp-feature-icon { font-size: 18px; font-weight: 800; color: var(--dark); margin-bottom: 10px; }
    .rp-feature-title { font-size: 13px; font-weight: 600; margin-bottom: 5px; }
    .rp-feature-desc { font-size: 12px; color: var(--muted); line-height: 1.55; }
    .rp-how { background: var(--bg); border-top: 1px solid var(--border); border-bottom: 1px solid var(--border); padding: 64px 32px; }
    .rp-how-inner { max-width: 700px; margin: 0 auto; }
    .rp-how-label { font-size: 11px; font-weight: 600; color: #9b9b9b; letter-spacing: 1px; text-align: center; margin-bottom: 10px; }
    .rp-how-title { font-size: 28px; font-weight: 700; letter-spacing: -0.8px; text-align: center; margin-bottom: 40px; }
    .rp-how-steps { display: grid; grid-template-columns: repeat(3,1fr); gap: 28px; }
    .rp-how-step { text-align: center; }
    .rp-how-num { width: 32px; height: 32px; border-radius: 50%; background: var(--pink); color: white; font-size: 13px; font-weight: 700; display: flex; align-items: center; justify-content: center; margin: 0 auto 12px; }
    .rp-how-step-title { font-size: 14px; font-weight: 600; margin-bottom: 5px; }
    .rp-how-step-desc { font-size: 12px; color: var(--muted); line-height: 1.55; }
    .rp-cta { max-width: 560px; margin: 0 auto; padding: 72px 32px; text-align: center; }
    .rp-cta h2 { font-size: 32px; font-weight: 700; letter-spacing: -1px; margin-bottom: 12px; }
    .rp-cta p { font-size: 14px; color: var(--muted); margin-bottom: 24px; }
    .rp-footer { border-top: 1px solid var(--border); padding: 20px 48px; display: flex; align-items: center; justify-content: space-between; }
    .rp-footer-brand { display: flex; align-items: center; gap: 8px; font-weight: 600; font-size: 13px; }
    .rp-footer-p { font-size: 12px; color: #9b9b9b; }

    /* Score preview on landing */
    .rp-demo-card { border: 1px solid var(--border); border-radius: 14px; padding: 24px 28px; background: white; max-width: 780px; margin: 0 auto; }
    .rp-demo-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
    .rp-demo-score-badge { background: var(--dark); color: white; border-radius: 8px; padding: 9px 18px; font-size: 22px; font-weight: 800; letter-spacing: -1px; }
    .rp-score-row { display: flex; align-items: center; justify-content: space-between; padding: 7px 11px; border-radius: 6px; background: var(--bg); border: 1px solid var(--border); margin-bottom: 4px; font-size: 13px; }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# CONSTANTS & DICTIONARIES (unchanged from original)
# ============================================================

STOPWORDS = {
    "a","an","the","and","or","but","if","then","else","when","at","from","by",
    "for","with","about","against","between","into","through","during","before",
    "after","above","below","to","up","down","in","out","on","off","over","under",
    "again","further","once","here","there","all","any","both","each","few","more",
    "most","other","some","such","no","nor","not","only","own","same","so","than",
    "too","very","s","t","can","will","just","don","should","now","i","me","my",
    "myself","we","our","ours","ourselves","you","your","yours","yourself",
    "yourselves","he","him","his","himself","she","her","hers","herself","it","its",
    "itself","they","them","their","theirs","themselves","what","which","who","whom",
    "this","that","these","those","am","is","are","was","were","be","been","being",
    "have","has","had","having","do","does","did","doing"
}

SKILL_KEYWORDS = {
    "python","sql","java","javascript","react","node","html","css","git","github",
    "r","matlab","tableau","powerbi","power bi","excel","bigquery","pandas","numpy",
    "scikit-learn","tensorflow","pytorch","aws","azure","docker","kubernetes","unix",
    "linux","bash","spark","hadoop","c++","c#","php","ruby","swift","kotlin",
    "typescript","scala","go","rust","mongodb","postgresql","mysql","redis","kafka",
    "airflow","dbt","looker","databricks","snowflake","jira","confluence","jenkins",
}

# ============================================================
# SKILL GROUPS — Heart of the hybrid matching engine
# Each group has: trigger patterns (what to look for in JD),
# strong keywords (direct CV match), partial keywords (related),
# weight (importance), and a display label.
# ============================================================

SKILL_GROUPS = [
    # ── Programming Languages ──
    {
        "label": "Python",
        "weight": 3,
        "jd_patterns": [r'\bpython\b'],
        "strong": ["python", "pandas", "numpy", "scipy", "flask", "django", "scikit"],
        "partial": ["programming", "scripting", "automation", "jupyter"],
        "category": "Technical"
    },
    {
        "label": "SQL / Databases",
        "weight": 3,
        "jd_patterns": [r'\bsql\b', r'\bdatabase', r'\bqueries\b'],
        "strong": ["sql", "mysql", "postgresql", "sqlite", "bigquery", "database", "queries"],
        "partial": ["data manipulation", "data extraction", "spreadsheet", "excel"],
        "category": "Technical"
    },
    {
        "label": "R / Statistical Computing",
        "weight": 2,
        "jd_patterns": [r'\br\b(?:\s+programming|\s+language|\s+studio)?', r'\brstudio\b', r'\bggplot\b'],
        "strong": ["r", "rstudio", "ggplot", "tidyverse", "dplyr", "r programming"],
        "partial": ["statistics", "statistical analysis", "spss", "matlab", "python"],
        "category": "Technical"
    },
    {
        "label": "Data Visualization",
        "weight": 2,
        "jd_patterns": [r'\bvisuali', r'\btableau\b', r'\bpower\s*bi\b', r'\bdashboard'],
        "strong": ["tableau", "power bi", "powerbi", "matplotlib", "plotly", "seaborn", "ggplot", "dashboard", "visualization"],
        "partial": ["charts", "graphs", "reports", "excel", "presentations", "plots"],
        "category": "Technical"
    },
    {
        "label": "Machine Learning",
        "weight": 2,
        "jd_patterns": [r'\bmachine\s+learning\b', r'\bml\b', r'\bai\b', r'\bclassif', r'\bcluster'],
        "strong": ["machine learning", "ml", "scikit-learn", "sklearn", "tensorflow", "pytorch", "classification", "clustering", "neural"],
        "partial": ["predictive", "modeling", "statistical modeling", "regression", "deep learning", "ai"],
        "category": "Technical"
    },
    {
        "label": "Statistical Analysis",
        "weight": 2,
        "jd_patterns": [r'\bstatistic', r'\bregression\b', r'\bhypothesis', r'\bmodeling\b|\bmodelling\b'],
        "strong": ["statistics", "statistical", "regression", "hypothesis testing", "modeling", "quantitative", "spss", "anova"],
        "partial": ["data analysis", "analytics", "r", "python", "research", "math"],
        "category": "Technical"
    },
    {
        "label": "Git / Version Control",
        "weight": 1,
        "jd_patterns": [r'\bgit\b', r'\bversion\s+control\b', r'\bgithub\b'],
        "strong": ["git", "github", "gitlab", "version control", "bitbucket"],
        "partial": ["code", "repository", "collaboration", "open source"],
        "category": "Technical"
    },
    {
        "label": "Linux / Unix",
        "weight": 1,
        "jd_patterns": [r'\blinux\b', r'\bunix\b', r'\bbash\b', r'\bshell\b'],
        "strong": ["linux", "unix", "bash", "shell", "terminal", "command line"],
        "partial": ["scripting", "automation", "python", "programming"],
        "category": "Technical"
    },
    {
        "label": "Cloud (AWS / Azure / GCP)",
        "weight": 2,
        "jd_patterns": [r'\baws\b', r'\bazure\b', r'\bgcp\b', r'\bcloud\b'],
        "strong": ["aws", "azure", "gcp", "cloud", "s3", "lambda", "google cloud"],
        "partial": ["deployment", "docker", "kubernetes", "devops"],
        "category": "Technical"
    },
    {
        "label": "Excel / Spreadsheets",
        "weight": 1,
        "jd_patterns": [r'\bexcel\b', r'\bspreadsheet\b'],
        "strong": ["excel", "spreadsheet", "pivot", "vlookup", "google sheets"],
        "partial": ["data analysis", "reporting", "sql", "tables"],
        "category": "Technical"
    },
    {
        "label": "NLP / Text Analysis",
        "weight": 2,
        "jd_patterns": [r'\bnlp\b', r'\bnatural\s+language', r'\btext\s+(?:mining|analysis|processing)'],
        "strong": ["nlp", "natural language processing", "spacy", "nltk", "bert", "transformers", "text mining"],
        "partial": ["python", "machine learning", "classification", "text"],
        "category": "Technical"
    },
    {
        "label": "Network / Graph Analysis",
        "weight": 2,
        "jd_patterns": [r'\bnetwork\s+analysis\b', r'\bgraph\s+(?:theory|analysis)\b', r'\bnetworkx\b'],
        "strong": ["network analysis", "networkx", "graph", "nodes", "edges", "clustering coefficient"],
        "partial": ["python", "data analysis", "algorithms"],
        "category": "Technical"
    },
    {
        "label": "Agile / Scrum",
        "weight": 1,
        "jd_patterns": [r'\bagile\b', r'\bscrum\b', r'\bsprint\b', r'\bkanban\b'],
        "strong": ["agile", "scrum", "sprint", "kanban", "jira"],
        "partial": ["project management", "teamwork", "collaboration"],
        "category": "Technical"
    },
    # ── Education ──
    {
        "label": "Bachelor's Degree",
        "weight": 2,
        "jd_patterns": [r'\bbachelor', r'\bb\.?sc\b', r'\bundergraduate\b', r'\bdegree\b'],
        "strong": ["bachelor", "bsc", "b.sc", "undergraduate", "university", "college", "degree"],
        "partial": ["studying", "student", "final year", "graduate"],
        "category": "Education"
    },
    {
        "label": "Master's Degree",
        "weight": 2,
        "jd_patterns": [r'\bmaster', r'\bm\.?sc\b', r'\bmba\b', r'\bpostgraduate\b'],
        "strong": ["master", "msc", "m.sc", "mba", "postgraduate"],
        "partial": ["bachelor", "university", "advanced degree"],
        "category": "Education"
    },
    {
        "label": "Computer Science Degree",
        "weight": 2,
        "jd_patterns": [r'\bcomputer\s+science\b', r'\bcs\s+degree\b', r'\bsoftware\s+engineering\s+degree\b'],
        "strong": ["computer science", "cs degree", "software engineering", "information systems"],
        "partial": ["programming", "algorithms", "data structures", "university"],
        "category": "Education"
    },
    {
        "label": "Statistics / Math Degree",
        "weight": 2,
        "jd_patterns": [r'\bstatistics\s+degree\b', r'\bmathematic', r'\bquantitative\s+field\b'],
        "strong": ["statistics", "mathematics", "math", "quantitative", "data science degree"],
        "partial": ["engineering", "physics", "economics", "university"],
        "category": "Education"
    },
    # ── Languages ──
    {
        "label": "English",
        "weight": 1,
        "jd_patterns": [r'\benglish\b'],
        "strong": ["english"],
        "partial": ["fluent", "bilingual", "native"],
        "category": "Languages"
    },
    {
        "label": "Hebrew",
        "weight": 2,
        "jd_patterns": [r'\bhebrew\b'],
        "strong": ["hebrew"],
        "partial": ["fluent", "native", "israel"],
        "category": "Languages"
    },
    {
        "label": "Arabic",
        "weight": 1,
        "jd_patterns": [r'\barabic\b'],
        "strong": ["arabic"],
        "partial": ["fluent", "native"],
        "category": "Languages"
    },
    # ── Soft Skills ──
    {
        "label": "Communication Skills",
        "weight": 1,
        "jd_patterns": [r'\bcommunication\b', r'\bpresent', r'\bstakeholder'],
        "strong": ["communication", "presented", "presentation", "stakeholders", "written", "verbal", "public speaking"],
        "partial": ["tutoring", "teaching", "teamwork", "reporting", "documentation", "mentoring"],
        "category": "Soft Skills"
    },
    {
        "label": "Teamwork / Collaboration",
        "weight": 1,
        "jd_patterns": [r'\bteamwork\b', r'\bcollaborat', r'\bteam\s+player\b', r'\bcross.functional\b'],
        "strong": ["teamwork", "collaboration", "team player", "cross-functional", "worked with team"],
        "partial": ["project", "group", "together", "hackathon", "volunteer", "committee"],
        "category": "Soft Skills"
    },
    {
        "label": "Problem Solving",
        "weight": 1,
        "jd_patterns": [r'\bproblem.solv', r'\banalytical\b', r'\bcritical\s+think'],
        "strong": ["problem solving", "analytical", "critical thinking", "solutions"],
        "partial": ["research", "debugging", "algorithms", "optimized", "improved"],
        "category": "Soft Skills"
    },
    {
        "label": "Project Management",
        "weight": 1,
        "jd_patterns": [r'\bproject\s+management\b', r'\bproject\s+lead', r'\bcoordinat'],
        "strong": ["project management", "project lead", "coordinated", "managed project"],
        "partial": ["organized", "planned", "delivered", "timeline", "agile"],
        "category": "Soft Skills"
    },
]

# Words to NEVER treat as requirements — noise filter
NOISE_WORDS = {
    "junior","senior","analyst","engineer","developer","manager","associate","intern",
    "looking","seeking","hiring","join","growing","excited","dynamic","innovative",
    "responsibilities","requirements","qualifications","preferred","required","needed",
    "must","should","will","would","please","submit","apply","resume","cv",
    "company","team","organization","department","role","position","opportunity",
    "years","experience","background","foundation","ability","understanding",
    "familiarity","exposure","proficiency","minimum","maximum","ideally",
    "various","multiple","several","including","following","related","relevant",
    "excellent","strong","good","great","proven","demonstrated","solid",
    "work","working","use","using","used","provide","support","help","ensure",
    "maintain","create","build","deliver","drive","focus","based","given",
    "also","well","both","other","such","like","example","etc","ie","eg",
}


# ============================================================
# HYBRID ANALYSIS ENGINE
# ============================================================

def extract_active_skill_groups(job_text):
    """Find which skill groups are actually required by this job description."""
    job_lower = job_text.lower()
    active = []
    for group in SKILL_GROUPS:
        for pattern in group["jd_patterns"]:
            if re.search(pattern, job_lower):
                active.append(group)
                break
    return active


def match_group_against_cv(group, cv_text):
    """
    For one skill group, check the CV.
    Returns: "strong", "partial", or "missing"
    Also returns evidence (what was found).
    """
    cv_lower = cv_text.lower()
    # Check strong keywords
    found_strong = [kw for kw in group["strong"] if kw in cv_lower]
    if found_strong:
        return "strong", found_strong[0]
    # Check partial keywords
    found_partial = [kw for kw in group["partial"] if kw in cv_lower]
    if found_partial:
        return "partial", found_partial[0]
    return "missing", None


def run_rule_based_analysis(cv_text, job_desc):
    """
    Full rule-based hybrid analysis.
    Returns dict with strong, partial, missing lists + weighted score.
    """
    active_groups = extract_active_skill_groups(job_desc)
    if not active_groups:
        return {"strong": [], "partial": [], "missing": [], "score": 0, "groups": []}

    strong, partial, missing = [], [], []
    total_weight = 0
    earned_weight = 0

    for group in active_groups:
        result, evidence = match_group_against_cv(group, cv_text)
        w = group["weight"]
        total_weight += w
        entry = {"label": group["label"], "evidence": evidence, "category": group["category"], "weight": w}
        if result == "strong":
            strong.append(entry)
            earned_weight += w
        elif result == "partial":
            partial.append(entry)
            earned_weight += w * 0.5   # partial = 50% credit
        else:
            missing.append(entry)

    raw_score = (earned_weight / total_weight * 100) if total_weight > 0 else 0
    # Realistic cap: partial matches penalise slightly, cap at 88
    score = round(min(88, max(20, raw_score)))

    return {
        "strong": strong,
        "partial": partial,
        "missing": missing,
        "score": score,
        "total_reqs": len(active_groups),
        "groups": active_groups,
    }


def call_claude_for_semantic_boost(cv_text, job_desc, job_role, rule_results):
    """
    Optional Claude API call for semantic insight layer.
    Sends only the partial + missing items to Claude for a smarter verdict.
    Falls back gracefully if API is unavailable.
    Returns: dict with ai_insight string, adjusted_score, reclassified items.
    """
    import json

    partial_labels = [g["label"] for g in rule_results["partial"]]
    missing_labels = [g["label"] for g in rule_results["missing"]]

    if not partial_labels and not missing_labels:
        return None   # Nothing uncertain to send

    prompt = f"""You are an expert CV analyst. A student is applying for: {job_role}

RULE-BASED SYSTEM already confirmed these as STRONG matches (do not re-evaluate):
{", ".join(g["label"] for g in rule_results["strong"])}

UNCERTAIN items (partial or missing from rule-based system):
Partial: {", ".join(partial_labels) if partial_labels else "none"}
Missing: {", ".join(missing_labels) if missing_labels else "none"}

CV TEXT (abbreviated):
{cv_text[:2500]}

JOB DESCRIPTION (abbreviated):
{job_desc[:1500]}

Your task:
1. For each PARTIAL item: decide if it should be upgraded to "strong" or stay "partial"
2. For each MISSING item: decide if the CV actually shows this skill indirectly (upgrade to "partial") or it is truly missing
3. Write 2-3 sentences of honest, specific feedback for this student
4. Suggest 2 concrete things they should add to their CV

Respond in JSON only, no markdown:
{{
  "upgrades_to_strong": ["label1", "label2"],
  "upgrades_to_partial": ["label3"],
  "truly_missing": ["label4"],
  "feedback": "2-3 sentence honest assessment",
  "suggestions": ["suggestion1", "suggestion2"]
}}"""

    try:
        import urllib.request
        payload = json.dumps({
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 1000,
            "messages": [{"role": "user", "content": prompt}]
        }).encode()

        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01",
                "x-api-key": "placeholder"   # Handled by Streamlit's proxy
            }
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            text = data["content"][0]["text"]
            # Strip markdown code fences if present
            text = re.sub(r'```(?:json)?', '', text).strip()
            return json.loads(text)
    except Exception:
        return None   # Silent fail — rule-based result stands

GENERIC_IGNORE_WORDS = NOISE_WORDS  # alias for backward compat

ACTION_VERBS = {
    "assisted": "Engineered","helped": "Optimized","did": "Developed",
    "worked on": "Spearheaded","responsible for": "Directed","learned": "Mastered",
    "managed": "Architected","wrote": "Formulated"
}

HEADINGS_MAP = {
    "English": ["Personal Details","Professional Summary","Education","Professional Experience",
                "Projects","Courses & Training","Volunteering / Community","Languages","Skills","Additional Information"],
    "Hebrew":  ["פרטים אישיים","תמצית מקצועית","השכלה","ניסיון תעסוקתי","פרויקטים",
                "קורסים והכשרות","התנדבות / קהילה","שפות","כישורים","מידע נוסף"],
    "Arabic":  ["البيانات الشخصية","الملخص المهني","التعليم","الخبرة العملية","المشاريع",
                "الدورات والتدريب","التطوع / المجتمع","اللغات","المهارات","معلومات إضافية"]
}

SECTION_REGEX = {
    "personal_details": r"(personal details|contact|contact info|פרטים אישיים|البيانات الشخصية)",
    "summary": r"(summary|profile|about me|professional summary|תמצית|פרופיל|תמצית מקצועית|الملخص|ملخص مهني)",
    "education": r"(education|academic|degrees|השכלה|לימודים|التعليم|المؤهلات العلمية)",
    "experience": r"(experience|work|employment|history|professional experience|ניסיון|ניסיון תעסוקתי|الخبرة|الخبرة العملية)",
    "projects": r"(projects|key projects|academic projects|פרויקטים|פרוייקטים|المشاريع)",
    "courses_training": r"(courses|training|certification|certifications|קורסים|הכשרות|הסמכות|الدورات|التدريب)",
    "volunteering": r"(volunteering|community|extracurricular|volunteer|leadership|activities|התנדבות|פעילות קהילתית|التطوع)",
    "languages": r"(languages|שפות|اللغات)",
    "skills": r"(skills|competencies|technologies|technical skills|כישורים|מיומנויות|יכולות|المهارات)"
}


# ============================================================
# CORE FUNCTIONS
# ============================================================

def detect_language(text):
    if re.search(r'[\u0590-\u05FF]', text): return "Hebrew"
    if re.search(r'[\u0600-\u06FF]', text): return "Arabic"
    return "English"


def validate_job_description(job_text):
    words = job_text.strip().split()
    if len(words) < 30:
        return False, "Please paste a real job description (at least a few sentences with requirements)."
    unique_words = {w.lower() for w in words if len(w) > 2}
    if len(unique_words) < 10:
        return False, "Please paste a real job description with responsibilities and requirements."
    return True, ""


def extract_text_from_pdf(file):
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except:
        return ""


def extract_text_from_docx(file):
    try:
        doc = docx.Document(file)
        return "\n".join([para.text for para in doc.paragraphs])
    except:
        return ""


def classify_sections_refined(text):
    sections = {
        "personal_details":"","summary":"","education":"","experience":"",
        "projects":"","courses_training":"","volunteering":"","languages":"",
        "skills":"","additional_information":""
    }
    # Insert newlines before known section headers (handles flat PDF)
    ALL_CAPS_HEADERS = [
        "PROFESSIONAL SUMMARY","PROFESSIONAL EXPERIENCE","WORK EXPERIENCE",
        "EDUCATION","PROJECTS","TECHNICAL SKILLS","SKILLS","LANGUAGES",
        "COURSES","VOLUNTEERING","LEADERSHIP & ACTIVITIES","LEADERSHIP",
        "ACTIVITIES","CERTIFICATIONS","TRAINING","ACADEMIC BACKGROUND",
        "תמצית מקצועית","השכלה","ניסיון תעסוקתי","פרויקטים","כישורים","שפות","התנדבות",
        "الملخص المهني","التعليم","الخبرة العملية","المشاريع","المهارات","اللغات","التطوع",
    ]
    for hw in sorted(ALL_CAPS_HEADERS, key=len, reverse=True):
        text = text.replace(hw, f"\n\n{hw}\n")
    current_section = "personal_details"
    lines = text.split('\n')
    for line in lines:
        clean_line = line.strip()
        if not clean_line: continue
        low_line = clean_line.lower()
        found_header = False
        if len(clean_line) < 70:
            for key, pattern in SECTION_REGEX.items():
                if re.search(pattern, low_line):
                    current_section = key
                    found_header = True
                    break
        if not found_header:
            sections[current_section] += clean_line + "\n"
    # Trim personal_details to just name + contact (max 5 lines)
    pd_lines = [l for l in sections["personal_details"].split('\n') if l.strip()]
    if len(pd_lines) > 5:
        sections["personal_details"] = "\n".join(pd_lines[:5])
    for k in sections:
        sections[k] = re.sub(r'\n{3,}', '\n\n', sections[k].strip())
    return sections


def format_contact_info(text):
    if not text: return "CANDIDATE", ""
    # Normalize separators
    text_clean = re.sub(r'\s*[|·•]\s*', '\n', text)
    lines = [l.strip() for l in text_clean.split('\n') if l.strip()]
    name, contact_parts = "", []
    for i, line in enumerate(lines):
        low = line.lower()
        is_contact = (any(k in low for k in ['email','phone','@','linkedin','github','israel','jerusalem','city','tel aviv'])
                      or re.search(r'\d{3}', line) or '@' in line)
        if i == 0 and not is_contact and len(line.split()) <= 6:
            name = line
        else:
            contact_parts.append(line)
    if not name and lines:
        m = re.match(r'^([A-Za-z\u0590-\u05FF\u0600-\u06FF ]{2,40}?)(?=\s+\S*[@\d])', text)
        name = m.group(1).strip() if m else lines[0]
        if not contact_parts: contact_parts = lines[1:]
    contact_str = " | ".join(contact_parts)
    contact_str = re.sub(r'\b(Email|Phone|Tel|Mobile|LinkedIn|Address)\s*:\s*', '', contact_str, flags=re.IGNORECASE)
    return name.strip(), contact_str.strip()


def group_skills_segregated(skills_text):
    if not skills_text: return {"PROFESSIONAL": [], "TECHNICAL": []}
    # Remove subheading labels that bleed in from PDF
    cleaned = re.sub(r'(Technical Skills|Business & Professional Skills|Professional Skills)\s*[,\n]?', '', skills_text, flags=re.IGNORECASE)
    skills = [s.strip() for s in re.split(r'[,\n•|]', cleaned) if s.strip() and len(s.strip()) > 1]
    tech_kw = set(list(SKILL_KEYWORDS) + ["sql","python","aws","docker","git","react","tableau","powerbi",
                                           "excel","data analysis","r","networkx","pandas","numpy","scipy",
                                           "matplotlib","unix","bash","bigquery","spss","statistical modeling",
                                           "machine learning","network analysis","rstudio","bigquery"])
    technical, professional = [], []
    for s in skills:
        sl = s.lower()
        if any(kw in sl for kw in tech_kw):
            technical.append(s)
        else:
            professional.append(s)
    return {"PROFESSIONAL": list(dict.fromkeys(professional)), "TECHNICAL": list(dict.fromkeys(technical))}


def call_claude_cv_adjustment(cv_sections, job_role, job_desc, analysis_results, follow_up_answers):
    """
    Calls Claude API to intelligently rewrite CV sections based on:
    - The job description requirements
    - What was matched / missing in analysis
    - The user's refinement answers
    - The original CV content (NO hallucination — only uses provided info)

    Returns adjusted cv_sections dict, or None if API unavailable.
    """
    import json

    strong  = analysis_results.get("matches", [])
    partial = analysis_results.get("partial", [])
    missing = analysis_results.get("missing", [])
    score   = analysis_results.get("score", 0)

    answers_text = "\n".join([f"- {v}" for v in follow_up_answers.values() if v.strip()])

    # Build a clean text summary of each section for Claude
    sections_text = ""
    for key in ["summary","experience","projects","education","skills","volunteering","courses_training","languages"]:
        val = cv_sections.get(key,"").strip()
        if val:
            sections_text += f"\n[{key.upper()}]\n{val[:600]}\n"

    prompt = f"""You are a professional CV editor helping a student tailor their CV for a specific job.

JOB ROLE: {job_role}

JOB DESCRIPTION (key parts):
{job_desc[:1200]}

ANALYSIS RESULTS:
- Already strong: {", ".join(strong) if strong else "none"}
- Partial matches (present but weak): {", ".join(partial) if partial else "none"}
- Missing requirements: {", ".join(missing) if missing else "none"}
- Current match score: {score}%

USER'S ADDITIONAL INFORMATION (from their answers — use this to strengthen the CV):
{answers_text if answers_text else "No additional answers provided."}

CURRENT CV SECTIONS:
{sections_text}

YOUR TASK — Rewrite each section to better match the job. STRICT RULES:
1. NEVER invent jobs, degrees, skills, or experiences that are not in the original CV
2. Only use information from the CV sections and the user's answers above
3. Strengthen the SUMMARY to mention the job role and highlight relevant skills
4. Improve bullet points in EXPERIENCE and PROJECTS to use stronger action verbs and highlight relevant skills
5. Reorder SKILLS to put the most job-relevant skills first
6. If the user provided answers about missing skills — incorporate that naturally (e.g., "Familiar with X through coursework")
7. Keep the same structure — do not add new sections that don't exist
8. Write in the same language as the original CV (English unless otherwise)
9. Keep all dates, company names, university names exactly as they are

Return ONLY a JSON object with these keys (include only sections that exist in the original):
{{
  "summary": "improved summary paragraph",
  "experience": "improved experience text — keep same entries, improve bullet wording",
  "projects": "improved projects text — keep same projects, improve descriptions",
  "skills": "reordered and clean skills list",
  "education": "education unchanged or minor wording improvement",
  "volunteering": "volunteering unchanged or minor improvement",
  "courses_training": "courses unchanged",
  "languages": "languages unchanged"
}}

Return ONLY valid JSON. No explanation, no markdown fences."""

    try:
        import json as json_mod
        import urllib.request

        payload = json_mod.dumps({
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 2000,
            "messages": [{"role": "user", "content": prompt}]
        }).encode()

        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01",
                "x-api-key": "placeholder"
            }
        )
        with urllib.request.urlopen(req, timeout=25) as resp:
            data = json_mod.loads(resp.read())
            raw = data["content"][0]["text"]
            raw = re.sub(r'```(?:json)?', '', raw).strip().strip('`')
            adjusted = json_mod.loads(raw)
            return adjusted
    except Exception as e:
        return None


def build_final_cv(cv_sections, adjusted_sections, job_role):
    """
    Merges adjusted sections back into cv_sections.
    Falls back to original section if adjustment is missing or empty.
    Always preserves: personal_details exactly as-is.
    """
    final = cv_sections.copy()
    if adjusted_sections:
        for key, val in adjusted_sections.items():
            if val and val.strip() and key != "personal_details":
                final[key] = val.strip()
    # Always keep personal_details untouched
    final["personal_details"] = cv_sections.get("personal_details", "")
    return final


def split_cv_entries(text):
    """Split flat CV text into separate entries, handling inline • bullets."""
    if not text: return []
    # Expand inline bullets to newlines
    text = re.sub(r'\s*•\s*', '\n• ', text)
    # If double newlines exist, use them
    if '\n\n' in text:
        return [b.strip() for b in text.split('\n\n') if b.strip()]
    # Otherwise split: new entry starts when a non-bullet line follows bullet lines
    lines = text.split('\n')
    blocks, current = [], []
    for line in lines:
        stripped = line.strip()
        if not stripped: continue
        is_bullet = stripped.startswith(('•','-','*','·'))
        if current and not is_bullet and not current[-1].startswith('•'):
            blocks.append('\n'.join(current))
            current = [stripped]
        else:
            current.append(stripped)
    if current: blocks.append('\n'.join(current))
    return [b for b in blocks if b.strip()] or [text]


def render_entry(block, show_subtitle=True):
    """Render one CV entry block → HTML."""
    block = re.sub(r'\s*•\s*', '\n• ', block)
    lines = [l.strip() for l in block.split('\n') if l.strip()]
    if not lines: return ""
    title = lines[0].lstrip('•-* ')
    html_out = f'<div class="cv-entry"><div class="cv-entry-title">{title}</div>'
    subtitle_done = False
    bullets = []
    for line in lines[1:]:
        is_bullet = line.startswith(('•','-','*'))
        clean = line.lstrip('•-* ').strip()
        if not clean: continue
        if is_bullet:
            bullets.append(clean)
        elif not subtitle_done and show_subtitle:
            html_out += f'<div class="cv-entry-sub">{clean}</div>'
            subtitle_done = True
        else:
            bullets.append(clean)
    if bullets:
        html_out += '<ul class="cv-bullets">' + ''.join(f'<li>{b}</li>' for b in bullets) + '</ul>'
    html_out += '</div>'
    return html_out


def translate_cv_googletrans(cv_data, target_lang):
    """
    Translates CV sections using deep-translator.
    Uses word-boundary-safe placeholders to avoid bugs like comMUNication.
    """
    try:
        from deep_translator import GoogleTranslator
    except ImportError:
        return cv_data

    lang_code = "iw" if target_lang == "Hebrew" else "ar"

    # Ordered longest-first to avoid partial matches
    PRESERVE = [
        "Hebrew University of Jerusalem",
        "Red Sea Candles",
        "Rosary Sisters High School",
        "Nayzak Program",
        "HUBS Aid Program",
        "Model United Nations",
        "scikit-learn", "RStudio", "BigQuery", "NetworkX",
        "NumPy", "matplotlib", "scipy", "pandas",
        "TensorFlow", "PyTorch", "GitHub", "GitLab",
        "Streamlit", "Jupyter", "Mechina", "Tawjihi", "IGCSE",
        "Python", "Unix", "Bash", "Linux", "Docker",
        "Excel", "Tableau", "Azure", "HUJI", "HUBS",
        "Git", "AWS", "GPA", "MVP", "CLI",
        "Facebook", "LinkedIn",
    ]

    def protect_and_translate(text):
        if not text or not text.strip():
            return text

        placeholders = {}
        protected = text
        counter = 0

        # Step 1: protect multi-word phrases and tools using word boundaries
        for word in PRESERVE:
            # Use word boundary only for short single words, not phrases
            if ' ' in word:
                pattern = re.escape(word)
            else:
                pattern = r'\b' + re.escape(word) + r'\b'
            ph = f"KEEP{counter}KEEP"
            new_protected = re.sub(pattern, ph, protected, flags=re.IGNORECASE)
            if new_protected != protected:
                placeholders[ph] = word
                protected = new_protected
                counter += 1

        # Step 2: protect dates like "2025–Present", "2025-2026", "2025"
        for m in re.finditer(r'\d{4}[–\-](?:Present|\d{4})|\b\d{4}\b', protected):
            ph = f"DATE{counter}DATE"
            placeholders[ph] = m.group()
            protected = protected[:m.start()] + ph + protected[m.end():]
            counter += 1
            # Restart after modification to avoid index issues
            break
        # Simpler date protection — replace all at once
        def replace_date(m):
            nonlocal counter
            ph = f"DATE{counter}DATE"
            placeholders[ph] = m.group()
            counter += 1
            return ph
        protected = re.sub(r'\d{4}[–\-](?:Present|\d{4})|\b\d{4}\b', replace_date, protected)

        # Step 3: protect score numbers like "90.4", "96"
        protected = re.sub(r'\b\d+\.\d+\b|\b\d{2,3}\b',
                           lambda m: (placeholders.__setitem__(f"NUM{counter}NUM", m.group()) or f"NUM{counter}NUM"),
                           protected)

        # Step 4: translate line by line
        lines = protected.split('\n')
        translated_lines = []
        translator = GoogleTranslator(source='auto', target=lang_code)

        for line in lines:
            stripped = line.strip()
            if not stripped:
                translated_lines.append('')
                continue
            # Skip if line has no real content after removing placeholders
            content_only = re.sub(r'\w+\d+\w+', '', stripped).strip('•-* \t|·–—:,.')
            if not content_only:
                translated_lines.append(line)
                continue
            try:
                if len(stripped) > 4500:
                    translated_lines.append(line)
                    continue
                t = translator.translate(stripped)
                translated_lines.append(t if t and t.strip() else line)
            except Exception:
                translated_lines.append(line)

        result = '\n'.join(translated_lines)

        # Step 5: restore all placeholders
        for ph, original in placeholders.items():
            result = result.replace(ph, original)

        return result

    result = cv_data.copy()
    for key in ["summary", "education", "experience", "projects",
                "courses_training", "volunteering", "languages", "skills"]:
        val = cv_data.get(key, "").strip()
        if not val:
            continue
        try:
            translated = protect_and_translate(val)
            if translated and translated.strip():
                result[key] = translated
        except Exception:
            pass

    return result


def extract_name_and_contact(personal_details_text):
    """
    Robustly extracts name and contact line from personal_details.
    Handles flat PDF text, structured text, and pipe-separated formats.
    Returns (name, contact_line) — name is NEVER repeated in contact_line.
    """
    text = personal_details_text.strip()
    if not text:
        return "CANDIDATE", ""

    CONTACT_KEYWORDS = ['email', 'phone', 'tel', 'mobile', '@', 'linkedin',
                        'github', 'israel', 'jerusalem', 'city', 'address',
                        'ירושלים', 'תל אביב', 'القدس', 'إسرائيل']

    # ── Strategy 1: newline-separated (clean PDF/manual) ──
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    if len(lines) >= 2:
        first = lines[0]
        low = first.lower()
        has_contact = any(k in low for k in CONTACT_KEYWORDS) or '@' in first
        is_name_length = len(first.split()) <= 5 and len(first) <= 45
        if not has_contact and is_name_length:
            name = first
            # Contact = everything after first line, joined
            rest = " | ".join(lines[1:])
            rest = re.sub(r'\b(Email|Phone|Tel|Mobile|E-mail)\s*:\s*', '', rest, flags=re.IGNORECASE)
            # Remove name if it appears at start of contact line
            if rest.upper().startswith(name.upper()):
                rest = rest[len(name):].strip(' |·,')
            contact = rest.strip(' |·')
            return name.strip(), contact

    # ── Strategy 2: flat single line — extract name from beginning ──
    # Pattern: "FIRSTNAME LASTNAME City, Country Email: ... Phone: ..."
    flat = text.replace('\n', ' ')

    # Try: name = first all-caps word(s) before a city/country keyword
    m = re.match(
        r'^([A-Z][A-Z\s]{2,30}?)(?=\s+(?:Jerusalem|Israel|Tel Aviv|Haifa|Email|Phone|\d{3}|ירושלים|القدس))',
        flat
    )
    if m:
        name = m.group(1).strip()
        rest = flat[len(name):].strip()
        rest = re.sub(r'\b(Email|Phone|Tel|Mobile|E-mail)\s*:\s*', '', rest, flags=re.IGNORECASE)
        # Remove leading duplicate of name
        if rest.upper().startswith(name.upper()):
            rest = rest[len(name):].strip(' |·,')
        # Build clean contact from rest
        parts = re.split(r'\s*[|·•]\s*', rest)
        parts = [p.strip() for p in parts if p.strip() and p.strip().upper() != name.upper()]
        return name, " | ".join(parts)

    # ── Strategy 3: pipe-separated "Name | City | Email | Phone" ──
    if '|' in flat:
        parts = [p.strip() for p in flat.split('|')]
        if parts:
            name = parts[0]
            contact = " | ".join(parts[1:])
            contact = re.sub(r'\b(Email|Phone|Tel|Mobile)\s*:\s*', '', contact, flags=re.IGNORECASE)
            return name.strip(), contact.strip()

    # ── Strategy 4: last resort — first 2-3 words as name ──
    words = flat.split()
    name = ' '.join(words[:3]) if len(words) >= 3 else flat
    rest = ' '.join(words[3:]) if len(words) > 3 else ''
    rest = re.sub(r'\b(Email|Phone|Tel|Mobile)\s*:\s*', '', rest, flags=re.IGNORECASE)
    return name.strip(), rest.strip()


def render_cv_html(cv_data, lang="English"):
    """
    Renders CV as clean Israeli-professional HTML.
    Section order: Summary → Education → Technical Skills → Projects → Experience → Volunteering → Languages
    """
    is_rtl = lang in ["Hebrew", "Arabic"]
    dir_attr = 'dir="rtl"' if is_rtl else 'dir="ltr"'
    text_align = 'right' if is_rtl else 'left'
    h = HEADINGS_MAP[lang]

    name, contact = extract_name_and_contact(cv_data.get("personal_details", ""))
    if not name: name = "CANDIDATE"

    # ── CSS embedded in the CV page ──
    cv_css = f"""
    <style>
    .isr-cv {{
        background: white;
        max-width: 780px;
        margin: 0 auto;
        padding: 40px 50px;
        font-family: 'Calibri', 'Arial', sans-serif;
        font-size: 10.5pt;
        color: #111;
        line-height: 1.45;
        direction: {('rtl' if is_rtl else 'ltr')};
        text-align: {text_align};
        box-shadow: 0 4px 24px rgba(0,0,0,0.10);
    }}
    .isr-name {{
        font-size: 20pt;
        font-weight: 700;
        text-align: center;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
        color: #0f172a;
        text-transform: uppercase;
    }}
    .isr-contact {{
        font-size: 10pt;
        text-align: center;
        color: #334155;
        margin-bottom: 10px;
    }}
    .isr-divider {{
        border: none;
        border-top: 1.5px solid #0f172a;
        margin: 8px 0 14px 0;
    }}
    .isr-section-title {{
        font-size: 11.5pt;
        font-weight: 700;
        color: #1e293b;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        border-bottom: 1px solid #94a3b8;
        padding-bottom: 2px;
        margin-top: 14px;
        margin-bottom: 6px;
    }}
    .isr-entry {{ margin-bottom: 8px; }}
    .isr-entry-header {{
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        flex-direction: {'row-reverse' if is_rtl else 'row'};
    }}
    .isr-entry-title {{ font-weight: 700; font-size: 10.5pt; color: #0f172a; }}
    .isr-entry-date  {{ font-size: 9.5pt; color: #475569; font-weight: 600; white-space: nowrap; }}
    .isr-entry-sub   {{ font-size: 10pt; color: #475569; font-style: italic; margin-bottom: 3px; }}
    .isr-bullets     {{ margin: 3px 0; {'padding-right:16px;padding-left:0;' if is_rtl else 'padding-left:16px;'} }}
    .isr-bullets li  {{ font-size: 10pt; color: #1e293b; margin-bottom: 2px; }}
    .isr-skills-row  {{ margin-bottom: 4px; font-size: 10pt; }}
    .isr-skills-label{{ font-weight: 700; color: #1e293b; }}
    </style>
    """

    def sec(title):
        return f'<div class="isr-section-title">{title}</div>'

    def parse_date_from_title(title):
        """Extract trailing date from title like 'Company Name | 2025–Present'"""
        m = re.search(r'[\|｜]\s*(\d{4}[–\-]\w+|\d{4})\s*$', title)
        if m:
            date = m.group(1)
            clean_title = title[:m.start()].strip()
            return clean_title, date
        return title, ""

    def render_entries_html(content, show_date=True):
        out = ""
        for block in split_cv_entries(content):
            block = re.sub(r'\s*•\s*', '\n• ', block)
            lines = [l.strip() for l in block.split('\n') if l.strip()]
            if not lines: continue

            raw_title = lines[0].lstrip('•-* ')
            title, date = parse_date_from_title(raw_title)

            out += '<div class="isr-entry">'
            out += '<div class="isr-entry-header">'
            out += f'<span class="isr-entry-title">{title}</span>'
            if date:
                out += f'<span class="isr-entry-date">{date}</span>'
            out += '</div>'

            subtitle_done = False
            bullets = []
            for line in lines[1:]:
                is_bullet = line.startswith(('•','-','*'))
                clean = line.lstrip('•-* ').strip()
                if not clean: continue
                if is_bullet:
                    bullets.append(clean)
                elif not subtitle_done:
                    out += f'<div class="isr-entry-sub">{clean}</div>'
                    subtitle_done = True
                else:
                    bullets.append(clean)

            if bullets:
                out += '<ul class="isr-bullets">' + ''.join(f'<li>{b}</li>' for b in bullets) + '</ul>'
            out += '</div>'
        return out

    # ── BUILD HTML ──
    html = f'{cv_css}<div class="isr-cv" {dir_attr}>'

    # Header
    html += f'<div class="isr-name">{name}</div>'
    if contact:
        html += f'<div class="isr-contact">{contact}</div>'
    html += '<hr class="isr-divider">'

    # 1. SUMMARY
    if cv_data.get("summary"):
        html += sec(h[1])
        summary = cv_data["summary"].replace('\n', ' ').strip()
        html += f'<div style="font-size:10.5pt;color:#1e293b;line-height:1.5;margin-bottom:8px;">{summary}</div>'

    # 2. EDUCATION
    if cv_data.get("education"):
        html += sec(h[2])
        edu = re.sub(r'\s*•\s*', '\n• ', cv_data["education"])
        # Split on lines that start with a capital and look like institution names
        edu_blocks = re.split(r'\n(?=[A-Z\u0590-\u05FF\u0600-\u06FF])', edu)
        for block in edu_blocks:
            lines = [l.strip() for l in block.split('\n') if l.strip()]
            if not lines: continue
            raw_title = lines[0].lstrip('•-* ')
            title, date = parse_date_from_title(raw_title)
            html += '<div class="isr-entry">'
            html += '<div class="isr-entry-header">'
            html += f'<span class="isr-entry-title">{title}</span>'
            if date: html += f'<span class="isr-entry-date">{date}</span>'
            html += '</div>'
            for l in lines[1:]:
                clean = l.lstrip('•-* ').strip()
                if clean:
                    html += f'<div class="isr-entry-sub">{clean}</div>'
            html += '</div>'

    # 3. TECHNICAL SKILLS (high on page — recruiters scan this)
    raw_skills = cv_data.get("skills", "")
    if raw_skills:
        raw_skills_clean = re.sub(
            r'(Technical Skills|Business & Professional Skills|Professional Skills|'
            r'כישורים טכניים|כישורים מקצועיים|المهارات التقنية|المهارات المهنية)\s*[,\n]?',
            '', raw_skills, flags=re.IGNORECASE)
        skills_data = group_skills_segregated(raw_skills_clean)

        # Skills section title
        skills_title = h[8] if len(h) > 8 else ("כישורים" if lang == "Hebrew" else "المهارات" if lang == "Arabic" else "Skills")
        html += sec(skills_title)

        if skills_data["TECHNICAL"]:
            tech_label = ("תכנות וכלים" if lang == "Hebrew" else "البرمجة والأدوات" if lang == "Arabic" else "Technical")
            html += f'<div class="isr-skills-row"><span class="isr-skills-label">{tech_label}:</span> {" · ".join(skills_data["TECHNICAL"])}</div>'
        if skills_data["PROFESSIONAL"]:
            prof_label = ("כישורים מקצועיים" if lang == "Hebrew" else "المهارات المهنية" if lang == "Arabic" else "Professional")
            html += f'<div class="isr-skills-row"><span class="isr-skills-label">{prof_label}:</span> {" · ".join(skills_data["PROFESSIONAL"])}</div>'

    # 4. PROJECTS
    if cv_data.get("projects"):
        html += sec(h[4])
        html += render_entries_html(cv_data["projects"])

    # 5. EXPERIENCE
    if cv_data.get("experience"):
        html += sec(h[3])
        html += render_entries_html(cv_data["experience"])

    # 6. VOLUNTEERING / LEADERSHIP
    if cv_data.get("volunteering"):
        html += sec(h[6])
        vol = re.sub(r'^\s*[&\*]\s*$', '', cv_data["volunteering"], flags=re.MULTILINE)
        html += render_entries_html(vol)

    # 7. LANGUAGES
    if cv_data.get("languages"):
        html += sec(h[7])
        langs = re.sub(r'\s*•\s*', ' · ', cv_data["languages"]).strip(' ·')
        html += f'<div style="font-size:10pt;color:#1e293b;">{langs}</div>'

    # 8. COURSES (if exists)
    if cv_data.get("courses_training"):
        html += sec(h[5])
        items = [c.strip() for c in re.split(r'[,\n]', cv_data["courses_training"]) if c.strip() and len(c.strip()) > 3]
        html += '<ul class="isr-bullets">' + ''.join(f'<li>{i}</li>' for i in items) + '</ul>'

    html += '</div>'
    return html


def generate_docx(cv_data, output_lang):
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement

    doc = Document()
    for sec in doc.sections:
        sec.top_margin  = docx.shared.Cm(1.8)
        sec.bottom_margin = docx.shared.Cm(1.8)
        sec.left_margin  = docx.shared.Cm(2.0)
        sec.right_margin = docx.shared.Cm(2.0)

    is_rtl = output_lang in ["Hebrew","Arabic"]
    h = HEADINGS_MAP[output_lang]
    font_name = 'Arial' if is_rtl else 'Calibri'

    style = doc.styles['Normal']
    style.font.name = font_name
    style.font.size = Pt(10.5)

    def set_para_format(para, rtl=False):
        if rtl:
            pPr = para._p.get_or_add_pPr()
            bidi = OxmlElement('w:bidi')
            pPr.append(bidi)
            jc = OxmlElement('w:jc')
            jc.set(qn('w:val'), 'right')
            pPr.append(jc)

    def add_para(text, bold=False, italic=False, size=10.5, align="left", color_rgb=None, space_before=0, space_after=2):
        p = doc.add_paragraph()
        if align == "center": p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif align == "right" or is_rtl: p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        else: p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        set_para_format(p, is_rtl)
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after  = Pt(space_after)
        run = p.add_run(str(text))
        run.bold = bold; run.italic = italic
        run.font.name = font_name
        run.font.size = Pt(size)
        if color_rgb:
            run.font.color.rgb = RGBColor(*color_rgb)
        return p

    def add_section_heading(title):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT if is_rtl else WD_ALIGN_PARAGRAPH.LEFT
        set_para_format(p, is_rtl)
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after  = Pt(2)
        run = p.add_run(title.upper())
        run.bold = True; run.font.size = Pt(11)
        run.font.name = font_name
        run.font.color.rgb = RGBColor(30, 41, 59)
        # Bottom border
        pPr = p._p.get_or_add_pPr()
        pBdr = OxmlElement('w:pBdr')
        bottom = OxmlElement('w:bottom')
        bottom.set(qn('w:val'), 'single')
        bottom.set(qn('w:sz'), '4')
        bottom.set(qn('w:space'), '1')
        bottom.set(qn('w:color'), '94a3b8')
        pBdr.append(bottom)
        pPr.append(pBdr)

    def add_bullet_item(text):
        p = doc.add_paragraph(style='List Bullet')
        set_para_format(p, is_rtl)
        if is_rtl: p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        run = p.add_run(text.lstrip('•-* ').strip())
        run.font.size = Pt(10); run.font.name = font_name
        p.paragraph_format.space_after = Pt(1)

    def parse_date_from_title(title):
        m = re.search(r'[\|｜]\s*(\d{4}[–\-]\w+|\d{4})\s*$', title)
        if m:
            return title[:m.start()].strip(), m.group(1)
        return title, ""

    # ── NAME ──
    name, contact = extract_name_and_contact(cv_data.get("personal_details",""))
    if not name: name = "CANDIDATE"
    name_p = add_para(name.upper(), bold=True, size=18, align="center", space_after=2)
    if contact:
        contact_clean = re.sub(r'\b(Email|Phone|Tel)\s*:\s*', '', contact, flags=re.IGNORECASE)
        add_para(contact_clean, size=10, align="center", space_after=4)

    # Divider line (using a paragraph with border)
    div_p = doc.add_paragraph()
    div_p.paragraph_format.space_before = Pt(2)
    div_p.paragraph_format.space_after  = Pt(4)
    pPr = div_p._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bot = OxmlElement('w:bottom')
    bot.set(qn('w:val'),'single'); bot.set(qn('w:sz'),'12')
    bot.set(qn('w:space'),'1'); bot.set(qn('w:color'),'0f172a')
    pBdr.append(bot); pPr.append(pBdr)

    # ── SUMMARY ──
    if cv_data.get("summary"):
        add_section_heading(h[1])
        add_para(cv_data["summary"].replace('\n',' ').strip(), size=10.5)

    # ── EDUCATION ──
    if cv_data.get("education"):
        add_section_heading(h[2])
        edu = re.sub(r'\s*•\s*', '\n• ', cv_data["education"])
        edu_blocks = re.split(r'\n(?=[A-Z\u0590-\u05FF\u0600-\u06FF])', edu)
        for block in edu_blocks:
            lines = [l.strip() for l in block.split('\n') if l.strip()]
            if not lines: continue
            raw_title = lines[0].lstrip('•-* ')
            title, date = parse_date_from_title(raw_title)
            entry_text = f"{title}   {date}" if date else title
            add_para(entry_text, bold=True, size=10.5, space_before=4, space_after=1)
            for l in lines[1:]:
                clean = l.lstrip('•-* ').strip()
                if clean: add_para(clean, italic=True, size=10, space_after=1)

    # ── SKILLS ──
    raw_skills = cv_data.get("skills","")
    if raw_skills:
        raw_skills_clean = re.sub(
            r'(Technical Skills|Business & Professional Skills|Professional Skills|'
            r'כישורים טכניים|כישורים מקצועיים|المهارات التقنية|المهارات المهنية)\s*[,\n]?',
            '', raw_skills, flags=re.IGNORECASE)
        skills_data = group_skills_segregated(raw_skills_clean)
        skills_title = h[8] if len(h) > 8 else ("כישורים" if output_lang=="Hebrew" else "المهارات" if output_lang=="Arabic" else "Skills")
        add_section_heading(skills_title)
        if skills_data["TECHNICAL"]:
            tech_label = "תכנות וכלים" if output_lang=="Hebrew" else "البرمجة والأدوات" if output_lang=="Arabic" else "Technical"
            p = doc.add_paragraph()
            set_para_format(p, is_rtl)
            r1 = p.add_run(f"{tech_label}: "); r1.bold=True; r1.font.size=Pt(10); r1.font.name=font_name
            r2 = p.add_run(" · ".join(skills_data["TECHNICAL"])); r2.font.size=Pt(10); r2.font.name=font_name
        if skills_data["PROFESSIONAL"]:
            prof_label = "כישורים מקצועיים" if output_lang=="Hebrew" else "المهارات المهنية" if output_lang=="Arabic" else "Professional"
            p = doc.add_paragraph()
            set_para_format(p, is_rtl)
            r1 = p.add_run(f"{prof_label}: "); r1.bold=True; r1.font.size=Pt(10); r1.font.name=font_name
            r2 = p.add_run(" · ".join(skills_data["PROFESSIONAL"])); r2.font.size=Pt(10); r2.font.name=font_name

    # ── PROJECTS ──
    if cv_data.get("projects"):
        add_section_heading(h[4])
        for block in split_cv_entries(cv_data["projects"]):
            block = re.sub(r'\s*•\s*', '\n• ', block)
            lines = [l.strip() for l in block.split('\n') if l.strip()]
            if not lines: continue
            raw_title = lines[0].lstrip('•-* ')
            title, date = parse_date_from_title(raw_title)
            entry_text = f"{title}   {date}" if date else title
            add_para(entry_text, bold=True, size=10.5, space_before=4, space_after=1)
            for line in lines[1:]:
                clean = line.lstrip('•-* ').strip()
                if not clean: continue
                if line.startswith(('•','-','*')): add_bullet_item(clean)
                else: add_para(clean, italic=True, size=10, space_after=1)

    # ── EXPERIENCE ──
    if cv_data.get("experience"):
        add_section_heading(h[3])
        for block in split_cv_entries(cv_data["experience"]):
            block = re.sub(r'\s*•\s*', '\n• ', block)
            lines = [l.strip() for l in block.split('\n') if l.strip()]
            if not lines: continue
            raw_title = lines[0].lstrip('•-* ')
            title, date = parse_date_from_title(raw_title)
            entry_text = f"{title}   {date}" if date else title
            add_para(entry_text, bold=True, size=10.5, space_before=4, space_after=1)
            sub_done = False
            for line in lines[1:]:
                clean = line.lstrip('•-* ').strip()
                if not clean: continue
                if line.startswith(('•','-','*')): add_bullet_item(clean)
                elif not sub_done:
                    add_para(clean, italic=True, size=10, space_after=1); sub_done=True
                else: add_bullet_item(clean)

    # ── VOLUNTEERING ──
    if cv_data.get("volunteering"):
        add_section_heading(h[6])
        vol = re.sub(r'^\s*[&\*]\s*$','', cv_data["volunteering"], flags=re.MULTILINE)
        for block in split_cv_entries(vol):
            block = re.sub(r'\s*•\s*', '\n• ', block)
            lines = [l.strip() for l in block.split('\n') if l.strip()]
            if not lines: continue
            raw_title = lines[0].lstrip('•-* ')
            title, date = parse_date_from_title(raw_title)
            add_para(f"{title}   {date}" if date else title, bold=True, size=10.5, space_before=4, space_after=1)
            for line in lines[1:]:
                clean = line.lstrip('•-* ').strip()
                if clean and line.startswith(('•','-','*')): add_bullet_item(clean)
                elif clean: add_para(clean, size=10, space_after=1)

    # ── LANGUAGES ──
    if cv_data.get("languages"):
        add_section_heading(h[7])
        langs_clean = re.sub(r'\s*•\s*', ' · ', cv_data["languages"]).strip(' ·')
        add_para(langs_clean, size=10)

    # ── COURSES ──
    if cv_data.get("courses_training"):
        add_section_heading(h[5])
        items = [c.strip() for c in re.split(r'[,\n]', cv_data["courses_training"]) if c.strip() and len(c.strip()) > 3]
        for item in items: add_bullet_item(item)

    buf = BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf

    is_rtl = output_lang in ["Hebrew", "Arabic"]
    h = HEADINGS_MAP[output_lang]

    # Set default font
    style = doc.styles['Normal']
    style.font.name = 'Arial' if is_rtl else 'Calibri'
    style.font.size = Pt(11)

    def set_rtl_para(para):
        """Apply RTL formatting to a paragraph."""
        if is_rtl:
            pPr = para._p.get_or_add_pPr()
            bidi = OxmlElement('w:bidi')
            pPr.append(bidi)
            jc = OxmlElement('w:jc')
            jc.set(qn('w:val'), 'right')
            pPr.append(jc)

    def add_para(text, bold=False, italic=False, size=11, align="left", color=None):
        p = doc.add_paragraph()
        if align == "center":
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif align == "right" or is_rtl:
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        else:
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        set_rtl_para(p)
        run = p.add_run(text)
        run.bold = bold
        run.italic = italic
        run.font.size = Pt(size)
        if color:
            run.font.color.rgb = RGBColor(*color)
        return p

    def add_section_heading(title):
        p = add_para(title.upper(), bold=True, size=10, color=(30, 41, 59))
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(2)
        # Add bottom border
        pPr = p._p.get_or_add_pPr()
        pBdr = OxmlElement('w:pBdr')
        bottom = OxmlElement('w:bottom')
        bottom.set(qn('w:val'), 'single')
        bottom.set(qn('w:sz'), '4')
        bottom.set(qn('w:space'), '1')
        bottom.set(qn('w:color'), '94a3b8')
        pBdr.append(bottom)
        pPr.append(pBdr)
        return p

    def add_bullet(text):
        p = doc.add_paragraph(style='List Bullet')
        set_rtl_para(p)
        if is_rtl:
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        run = p.add_run(text.lstrip('•-* ').strip())
        run.font.size = Pt(10)
        return p

    # ── NAME & CONTACT ──
    name, contact = format_contact_info(cv_data.get("personal_details",""))
    if not name: name = "CANDIDATE"
    name_p = add_para(name.upper(), bold=True, size=20, align="center")
    name_p.paragraph_format.space_after = Pt(2)
    if contact:
        contact_clean = re.sub(r'(Email|Phone|Tel)\s*:\s*', '', contact, flags=re.IGNORECASE)
        add_para(contact_clean, size=10, align="center")

    # ── SECTIONS ──
    section_order = [
        ("summary",          h[1]),
        ("education",        h[2]),
        ("experience",       h[3]),
        ("projects",         h[4]),
        ("courses_training", h[5]),
        ("volunteering",     h[6]),
        ("languages",        h[7]),
    ]

    for key, heading in section_order:
        content = cv_data.get(key, "").strip()
        if not content:
            continue

        add_section_heading(heading)

        if key in ["experience", "projects", "volunteering"]:
            for block in split_cv_entries(content):
                block = re.sub(r'\s*•\s*', '\n• ', block)
                lines = [l.strip() for l in block.split('\n') if l.strip()]
                for i, line in enumerate(lines):
                    clean = line.lstrip('•-* ').strip()
                    if not clean:
                        continue
                    if i == 0:
                        add_para(clean, bold=True, size=10.5)
                    elif line.startswith(('•', '-', '*')):
                        add_bullet(clean)
                    else:
                        add_para(clean, italic=True, size=10)

        elif key == "education":
            # Each school on its own
            edu_entries = re.split(r'\n(?=[A-Z])', re.sub(r'\s*•\s*', '\n• ', content))
            for entry in edu_entries:
                lines = [l.strip() for l in entry.split('\n') if l.strip()]
                if not lines:
                    continue
                add_para(lines[0].lstrip('•-* '), bold=True, size=10.5)
                for l in lines[1:]:
                    add_para(l.lstrip('•-* '), italic=True, size=10)

        elif key == "courses_training":
            items = [c.strip() for c in re.split(r'[,\n]', content) if c.strip() and len(c.strip()) > 3]
            for item in items:
                add_bullet(item)

        elif key == "languages":
            langs_clean = re.sub(r'\s*•\s*', ' · ', content).strip(' ·')
            add_para(langs_clean, size=10)

        elif key == "summary":
            summary = content.replace('\n', ' ').strip()
            add_para(summary, size=10.5)

        else:
            add_para(content, size=10)

    # ── SKILLS ──
    raw_skills = cv_data.get("skills", "")
    if raw_skills:
        raw_skills = re.sub(r'(Technical Skills|Business & Professional Skills|Professional Skills)\s*[,\n]?', '', raw_skills, flags=re.IGNORECASE)
        skills_data = group_skills_segregated(raw_skills)

        if skills_data["TECHNICAL"]:
            add_section_heading(h[8] if len(h) > 8 else "Technical Skills")
            add_para(" · ".join(skills_data["TECHNICAL"]), size=10)
        if skills_data["PROFESSIONAL"]:
            add_section_heading("Professional Skills")
            add_para(" · ".join(skills_data["PROFESSIONAL"]), size=10)

    buf = BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf


# ============================================================
# NAVIGATION HELPERS
# ============================================================

TAB_NAMES = ["The Job", "CV Content", "Analysis", "Refinement", "Preview", "Export"]
TAB_ICONS = ["🎯", "📄", "📊", "✏️", "👁️", "⬇️"]

def go_to(tab_index):
    st.session_state.active_tab = tab_index
    # If user goes back before Preview, reset adjustment so it re-runs fresh
    if tab_index < 4:
        st.session_state.cv_adjusted = False
        st.session_state.adjusted_cv_data = {}
    st.rerun()

LOGO_SVG = """<svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect x="5" y="2" width="18" height="24" rx="2" stroke="#191919" stroke-width="1.8" fill="white"/>
  <line x1="9" y1="9" x2="19" y2="9" stroke="#e9e9e7" stroke-width="1.2"/>
  <line x1="9" y1="13" x2="19" y2="13" stroke="#e9e9e7" stroke-width="1.2"/>
  <line x1="9" y1="17" x2="15" y2="17" stroke="#e9e9e7" stroke-width="1.2"/>
  <circle cx="22" cy="22" r="7" fill="white" stroke="#191919" stroke-width="1.8"/>
  <line x1="22" y1="17" x2="22" y2="22" stroke="#191919" stroke-width="2" stroke-linecap="round"/>
  <line x1="22" y1="22" x2="25.5" y2="25.5" stroke="#be185d" stroke-width="2" stroke-linecap="round"/>
  <circle cx="22" cy="22" r="1.2" fill="#191919"/>
</svg>"""

LOGO_SVG_SM = """<svg width="24" height="24" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect x="5" y="2" width="18" height="24" rx="2" stroke="#191919" stroke-width="1.8" fill="white"/>
  <circle cx="22" cy="22" r="7" fill="white" stroke="#191919" stroke-width="1.8"/>
  <line x1="22" y1="17" x2="22" y2="22" stroke="#191919" stroke-width="2" stroke-linecap="round"/>
  <line x1="22" y1="22" x2="25.5" y2="25.5" stroke="#be185d" stroke-width="2" stroke-linecap="round"/>
  <circle cx="22" cy="22" r="1.2" fill="#191919"/>
</svg>"""


def render_header():
    st.markdown(f"""
    <div class="rp-header">
        {LOGO_SVG}
        <span class="rp-brand">ResumePilot</span>
        <span class="rp-tagline">Land more interviews.</span>
    </div>
    """, unsafe_allow_html=True)


def render_step_bar(current):
    html = '<div class="rp-step-bar">'
    for i, name in enumerate(TAB_NAMES):
        if i < current:
            dot_cls, name_cls, icon = "rp-dot-done", "rp-name-done", "✓"
        elif i == current:
            dot_cls, name_cls, icon = "rp-dot-active", "rp-name-active", str(i+1)
        else:
            dot_cls, name_cls, icon = "rp-dot-todo", "rp-name-todo", str(i+1)
        html += f'<div class="rp-step-item"><div class="rp-step-dot {dot_cls}">{icon}</div><span class="rp-step-name {name_cls}">{name}</span></div>'
        if i < len(TAB_NAMES) - 1:
            conn = "rp-conn-done" if i < current else "rp-conn-todo"
            html += f'<div class="rp-connector {conn}"></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


def render_landing():
    """Full ResumePilot landing page shown before user starts."""

    # HERO section
    st.markdown(f"""
<div style="background:radial-gradient(ellipse 90% 50% at 50% -5%, #fce7f3 0%, #fff 60%);padding-bottom:20px;">
  <div class="rp-hero">
    <div class="rp-hero-badge">&#10022; Free for students &amp; graduates</div>
    <h1>Land more<br><span>interviews.</span></h1>
    <p>ResumePilot analyzes your resume against job requirements and helps you build stronger, more targeted applications in minutes.</p>
  </div>
  <div class="rp-social-proof">No account needed &nbsp;&middot;&nbsp; No credit card &nbsp;&middot;&nbsp; <strong style="color:#191919;">English, Hebrew &amp; Arabic</strong> supported</div>
</div>
    """, unsafe_allow_html=True)

    # START BUTTON — real Streamlit button
    st.markdown("<div style='height:32px;'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("Start for free →", type="primary", use_container_width=True):
            st.session_state.show_landing = False
            st.rerun()
    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

    # FEATURES
    st.markdown("""
<div class="rp-features">
  <div class="rp-feature">
    <div class="rp-feature-icon">&#8594;</div>
    <div class="rp-feature-title">Semantic job matching</div>
    <div class="rp-feature-desc">We don't just scan for keywords. We understand what the job actually requires.</div>
  </div>
  <div class="rp-feature">
    <div class="rp-feature-icon">&#8593;</div>
    <div class="rp-feature-title">Honest AI tailoring</div>
    <div class="rp-feature-desc">Your resume is rewritten using only your real experience. No invented skills, ever.</div>
  </div>
  <div class="rp-feature">
    <div class="rp-feature-icon">&#9711;</div>
    <div class="rp-feature-title">3-language output</div>
    <div class="rp-feature-desc">Download in English, Hebrew, or Arabic, formatted for the Israeli job market.</div>
  </div>
</div>
    """, unsafe_allow_html=True)

    # HOW IT WORKS
    st.markdown("""
<div class="rp-how">
  <div class="rp-how-inner">
    <div class="rp-how-label">HOW IT WORKS</div>
    <div class="rp-how-title">Three steps to a stronger application.</div>
    <div class="rp-how-steps">
      <div class="rp-how-step">
        <div class="rp-how-num">1</div>
        <div class="rp-how-step-title">Paste the job</div>
        <div class="rp-how-step-desc">Drop in any job description from LinkedIn, a company site, or anywhere else.</div>
      </div>
      <div class="rp-how-step">
        <div class="rp-how-num">2</div>
        <div class="rp-how-step-title">Upload your resume</div>
        <div class="rp-how-step-desc">We analyze it against the job and show you exactly what's strong, partial, or missing.</div>
      </div>
      <div class="rp-how-step">
        <div class="rp-how-num">3</div>
        <div class="rp-how-step-title">Download &amp; apply</div>
        <div class="rp-how-step-desc">Get a tailored resume in English, Hebrew, or Arabic, ready to send.</div>
      </div>
    </div>
  </div>
</div>
    """, unsafe_allow_html=True)

    # CTA + FOOTER
    st.markdown("""
<div class="rp-cta">
  <h2>Ready to land more interviews?</h2>
  <p>It takes less than 5 minutes. No account needed.</p>
</div>
<div class="rp-footer">
  <div class="rp-footer-brand">ResumePilot</div>
  <p class="rp-footer-p">Built for students. Free forever.</p>
</div>
    """, unsafe_allow_html=True)


def nav_buttons(current, can_proceed=True, proceed_label="Continue →", back_label="← Back"):
    st.markdown("<div style='margin-top:24px;'>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 6, 1])
    with col1:
        if current > 0:
            if st.button(back_label, key=f"back_{current}", use_container_width=True):
                go_to(current - 1)
    with col3:
        if current < len(TAB_NAMES) - 1:
            btn = st.button(
                proceed_label,
                key=f"next_{current}",
                use_container_width=True,
                disabled=not can_proceed,
                type="primary"
            )
            if btn:
                go_to(current + 1)
    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# APP HEADER + LANDING PAGE
# ============================================================

# Show landing page if not started
if st.session_state.show_landing:
    render_landing()
    st.stop()

# Otherwise show the app
render_header()
current_tab = st.session_state.active_tab
render_step_bar(current_tab)
st.markdown("<hr style='border:none;border-top:1px solid #e9e9e7;margin-bottom:28px;'>", unsafe_allow_html=True)


# ============================================================
# TAB 0 — THE JOB
# ============================================================

if current_tab == 0:
    st.markdown('<div class="rp-page-badge">STEP 1 OF 6</div>', unsafe_allow_html=True)
    st.markdown('<div class="rp-page-title">Target Position</div>', unsafe_allow_html=True)
    st.markdown('<div class="rp-page-sub">Tell us the role you\'re going for. We\'ll use it to match and tailor everything.</div>', unsafe_allow_html=True)

    st.session_state.job_role = st.text_input(
        "Target Job Title",
        value=st.session_state.job_role,
        placeholder="e.g., Data Analyst Intern, Software Engineer, Marketing Associate"
    )

    st.session_state.job_desc = st.text_area(
        "Job Description",
        value=st.session_state.job_desc,
        height=280,
        placeholder="Paste the full job description here — include responsibilities, requirements, and qualifications..."
    )

    col_demo, _ = st.columns([1, 3])
    with col_demo:
        if st.button("Load demo job", use_container_width=True):
            st.session_state.job_role = "Junior Data Analyst"
            st.session_state.job_desc = """We are looking for a Junior Data Analyst to join our growing team.

Responsibilities:
- Analyze large datasets using Python and SQL
- Build dashboards and reports using Tableau or Power BI
- Apply statistical methods including regression and modeling
- Collaborate with cross-functional teams to deliver insights
- Present findings to stakeholders

Requirements:
- Bachelor's degree in Statistics, Mathematics, Computer Science or related field
- Proficiency in Python and SQL
- Experience with data visualization tools (Tableau, Power BI, or Matplotlib)
- Strong analytical and problem-solving skills
- Knowledge of machine learning concepts
- Git version control experience
- Excellent communication and teamwork skills
- Hebrew and English required"""
            st.rerun()

    # Validation feedback
    job_ready = bool(st.session_state.job_role.strip() and st.session_state.job_desc.strip())
    if st.session_state.job_desc.strip():
        is_valid, err = validate_job_description(st.session_state.job_desc)
        if not is_valid:
            st.error(f"⚠️ {err}")
            job_ready = False
        else:
            st.markdown('<div class="alert-green">Job description looks good.</div>', unsafe_allow_html=True)

    nav_buttons(0, can_proceed=job_ready, proceed_label="Continue →")


# ============================================================
# TAB 1 — CV CONTENT
# ============================================================

elif current_tab == 1:
    st.markdown('<div class="rp-page-badge">STEP 2 OF 6</div>', unsafe_allow_html=True)
    st.markdown('<div class="rp-page-title">CV Content</div>', unsafe_allow_html=True)
    st.markdown('<div class="rp-page-sub">Upload or paste your resume in English. Hebrew and Arabic output available in Preview.</div>', unsafe_allow_html=True)

    # English-only notice
    st.info("Please enter your CV in English. You can choose Hebrew or Arabic output in the Preview tab.")

    method = st.radio(
        "How would you like to provide your CV?",
        ["Upload File (PDF/DOCX/TXT)", "Paste Text", "Manual Entry"],
        horizontal=True,
        key="cv_method_radio"
    )
    st.session_state.input_method = method

    st.markdown("---")

    # ---- UPLOAD ----
    if method == "Upload File (PDF/DOCX/TXT)":
        uploaded_file = st.file_uploader("Upload your CV", type=["pdf","docx","txt"], label_visibility="collapsed")
        if uploaded_file:
            with st.spinner("Reading your CV..."):
                if uploaded_file.type == "application/pdf":
                    text = extract_text_from_pdf(uploaded_file)
                elif "wordprocessingml" in uploaded_file.type:
                    text = extract_text_from_docx(uploaded_file)
                else:
                    text = str(uploaded_file.read(), "utf-8")

            if text.strip():
                # Detect if uploaded CV is in Hebrew or Arabic
                detected_lang = detect_language(text)
                if detected_lang in ["Hebrew", "Arabic"]:
                    st.warning(f"⚠️ Your uploaded CV appears to be in **{detected_lang}**. For best results, please upload an English version of your CV. The app needs English text for accurate analysis and job matching.")
                    st.markdown("**You can still continue**, but the analysis accuracy may be lower.")

                st.session_state.cv_full_text = text
                st.session_state.manual_cv_data = classify_sections_refined(text)
                st.session_state.cv_uploaded = True
                st.success(f"✅ CV uploaded and parsed! ({len(text.split())} words detected)")

                with st.expander("👀 Preview detected sections"):
                    for k, v in st.session_state.manual_cv_data.items():
                        if v.strip():
                            st.markdown(f"**{k.replace('_',' ').title()}**")
                            st.text(v[:300] + ("..." if len(v) > 300 else ""))
            else:
                st.error("❌ Could not extract text from this file. Try copy-pasting instead.")

    # ---- PASTE TEXT ----
    elif method == "Paste Text":
        pasted = st.text_area(
            "Paste your CV text here (in English):",
            value=st.session_state.cv_full_text,
            height=320,
            placeholder="Copy and paste your full CV content here in English..."
        )
        st.session_state.cv_full_text = pasted

        if pasted.strip():
            detected_lang = detect_language(pasted)
            if detected_lang in ["Hebrew", "Arabic"]:
                st.warning(f"⚠️ This text appears to be in **{detected_lang}**. Please paste your CV in English for best results.")

        if st.button("🔍 Auto-Structure Text", type="primary"):
            if pasted.strip():
                st.session_state.manual_cv_data = classify_sections_refined(pasted)
                st.session_state.cv_uploaded = True
                st.success("✅ Text structured into sections!")
                with st.expander("👀 Preview detected sections"):
                    for k, v in st.session_state.manual_cv_data.items():
                        if v.strip():
                            st.markdown(f"**{k.replace('_',' ').title()}**")
                            st.text(v[:300] + ("..." if len(v) > 300 else ""))
            else:
                st.warning("Please paste your CV text first.")

        if st.session_state.cv_full_text.strip():
            st.session_state.cv_uploaded = True

    # ---- MANUAL ENTRY ----
    elif method == "Manual Entry":
        st.markdown("**Fill in each section in English below:**")
        fields = [
            ("personal_details", "👤 Full Name & Contact Info",
             "Your Full Name\nyour.email@example.com | +000-000-0000 | City, Country | linkedin.com/in/yourprofile"),
            ("summary",          "💡 Professional Summary",
             "e.g., Final-year Computer Science student with experience in data analysis and software development. Passionate about turning data into actionable insights."),
            ("education",        "🎓 Education",
             "e.g., University Name\nBSc in Your Major\n2022–2025 | GPA: 3.8"),
            ("experience",       "💼 Work Experience",
             "e.g., Job Title – Company Name\nMonth Year – Month Year\n- What you did and achieved\n- Another responsibility or result"),
            ("projects",         "🚀 Projects",
             "e.g., Project Name – Brief description\n- Tools used: Python, SQL, etc.\n- What problem it solved or result it produced"),
            ("skills",           "🛠️ Skills",
             "e.g., Python, SQL, Excel, Git, Data Analysis, Communication, Problem Solving, Teamwork"),
            ("courses_training", "📚 Courses & Certifications",
             "e.g., Google Data Analytics Certificate (Coursera, 2024)\nAdvanced Excel for Data Analysis (LinkedIn Learning)"),
            ("languages",        "🌐 Languages",
             "e.g., English (Native), Arabic (Fluent), French (Intermediate)"),
            ("volunteering",     "🤝 Volunteering & Activities",
             "e.g., Volunteer Tutor – Local NGO | 2023–Present\n- Helped 20+ students with math and science\nUniversity Student Council – Events Coordinator"),
        ]
        c1, c2 = st.columns(2)
        any_filled = False
        for i, (key, label, placeholder) in enumerate(fields):
            col = c1 if i % 2 == 0 else c2
            with col:
                st.markdown(f"**{label}**")
                val = st.text_area(
                    label, value=st.session_state.manual_cv_data.get(key,""),
                    placeholder=placeholder, key=f"manual_{key}",
                    label_visibility="collapsed", height=110
                )
                st.session_state.manual_cv_data[key] = val
                if val.strip(): any_filled = True

        if any_filled:
            st.session_state.cv_full_text = "\n".join(st.session_state.manual_cv_data.values())
            st.session_state.cv_uploaded = True

    cv_ready = bool(
        st.session_state.cv_full_text.strip() or
        any(v.strip() for v in st.session_state.manual_cv_data.values())
    )
    nav_buttons(1, can_proceed=cv_ready, proceed_label="Continue →")


# ============================================================
# TAB 2 — ANALYSIS
# ============================================================

elif current_tab == 2:
    st.markdown('<div class="rp-page-badge">STEP 3 OF 6</div>', unsafe_allow_html=True)
    st.markdown('<div class="rp-page-title">Match Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="rp-page-sub">We compared your resume against the job requirements. Here\'s what we found.</div>', unsafe_allow_html=True)

    cv_text = st.session_state.cv_full_text or "\n".join(st.session_state.manual_cv_data.values())
    job_ok = bool(st.session_state.job_desc.strip())
    cv_ok  = bool(cv_text.strip())

    if not job_ok or not cv_ok:
        st.warning("Please complete The Job and CV Content steps first.")
        nav_buttons(2, can_proceed=False)
    else:
        is_valid, err = validate_job_description(st.session_state.job_desc)
        if not is_valid:
            st.error(f"⚠️ {err}")
            nav_buttons(2, can_proceed=False)
        else:
            # ── Run rule-based analysis ──
            rule_results = run_rule_based_analysis(cv_text, st.session_state.job_desc)
            strong  = rule_results["strong"]
            partial = rule_results["partial"]
            missing = rule_results["missing"]
            score   = rule_results["score"]

            # ── Optional Claude semantic boost ──
            ai_boost = None
            if strong or partial or missing:
                with st.spinner("🤖 Running semantic analysis..."):
                    ai_boost = call_claude_for_semantic_boost(
                        cv_text, st.session_state.job_desc,
                        st.session_state.job_role, rule_results
                    )

            # Apply Claude upgrades if available
            if ai_boost:
                upgrades_strong  = set(ai_boost.get("upgrades_to_strong", []))
                upgrades_partial = set(ai_boost.get("upgrades_to_partial", []))
                truly_missing    = set(ai_boost.get("truly_missing", []))

                new_partial, new_missing = [], []
                for item in partial:
                    if item["label"] in upgrades_strong:
                        item["ai_upgraded"] = True
                        strong.append(item)
                    else:
                        new_partial.append(item)
                partial = new_partial

                for item in missing:
                    if item["label"] in upgrades_partial:
                        item["ai_upgraded"] = True
                        partial.append(item)
                    elif item["label"] not in truly_missing:
                        item["ai_upgraded"] = True
                        partial.append(item)
                    else:
                        new_missing.append(item)
                missing = new_missing

                # Recalculate score with upgrades
                total_w = sum(g["weight"] for g in rule_results["groups"])
                earned_w = (sum(g["weight"] for g in strong) +
                            sum(g["weight"] * 0.5 for g in partial))
                if total_w > 0:
                    score = round(min(88, max(20, earned_w / total_w * 100)))

            # Save to session
            st.session_state.analysis_results = {
                "matches": [g["label"] for g in strong],
                "partial": [g["label"] for g in partial],
                "missing": [g["label"] for g in missing],
                "score": score,
                "ai_boost": ai_boost,
            }
            st.session_state.analysis_done = True

            # ════════════════════════════════
            # UI RENDERING
            # ════════════════════════════════

            # ── Score header ──
            score_color = "#16a34a" if score >= 70 else "#ea580c" if score >= 45 else "#dc2626"
            score_label = "Strong Match 🟢" if score >= 70 else "Moderate Match 🟡" if score >= 45 else "Weak Match 🔴"
            score_msg   = ("Your CV aligns well with this role. A few refinements could make it even stronger."
                           if score >= 70 else
                           "You have relevant experience but some gaps to address before applying."
                           if score >= 45 else
                           "There are significant gaps between your CV and this role. Focus on the missing items below.")

            st.markdown(f"""
            <div class="content-card" style="text-align:center; padding: 2rem;">
                <div style="font-size:5rem; font-weight:900; color:{score_color}; line-height:1;">{score}%</div>
                <div style="font-size:1.3rem; font-weight:700; color:{score_color}; margin:8px 0;">{score_label}</div>
                <div style="color:#64748b; font-size:0.95rem; max-width:500px; margin:0 auto;">{score_msg}</div>
                <div style="margin-top:1rem; color:#94a3b8; font-size:0.85rem;">
                    ✅ {len(strong)} strong &nbsp;·&nbsp; 〰️ {len(partial)} partial &nbsp;·&nbsp; ❌ {len(missing)} missing
                    {"&nbsp;·&nbsp; 🤖 AI-enhanced" if ai_boost else ""}
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("---")

            # ── Three columns: Strong / Partial / Missing ──
            col_s, col_p, col_m = st.columns(3)

            with col_s:
                st.markdown(f"""<div style="background:#f0fdf4; border:1px solid #bbf7d0;
                    border-radius:12px; padding:1.2rem;">
                    <div style="font-weight:700; color:#16a34a; font-size:1rem; margin-bottom:0.8rem;">
                    ✅ Strong Match ({len(strong)})</div>""", unsafe_allow_html=True)
                if strong:
                    for item in strong:
                        ai_badge = ' <span style="font-size:0.7rem;background:#dbeafe;color:#1e40af;padding:1px 6px;border-radius:9999px;">AI</span>' if item.get("ai_upgraded") else ""
                        ev = f'<span style="color:#6b7280;font-size:0.75rem;"> ({item["evidence"]})</span>' if item.get("evidence") else ""
                        st.markdown(f'<div style="margin-bottom:6px;font-size:0.88rem;font-weight:600;color:#166534;">✓ {item["label"]}{ai_badge}{ev}</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div style="color:#6b7280;font-size:0.85rem;">None yet — add more skills to your CV</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with col_p:
                st.markdown(f"""<div style="background:#fffbeb; border:1px solid #fde68a;
                    border-radius:12px; padding:1.2rem;">
                    <div style="font-weight:700; color:#b45309; font-size:1rem; margin-bottom:0.8rem;">
                    〰️ Partial Match ({len(partial)})</div>""", unsafe_allow_html=True)
                if partial:
                    for item in partial:
                        ai_badge = ' <span style="font-size:0.7rem;background:#dbeafe;color:#1e40af;padding:1px 6px;border-radius:9999px;">AI</span>' if item.get("ai_upgraded") else ""
                        ev = f'<span style="color:#6b7280;font-size:0.75rem;"> (found: {item["evidence"]})</span>' if item.get("evidence") else ""
                        st.markdown(f'<div style="margin-bottom:6px;font-size:0.88rem;font-weight:600;color:#92400e;">〰 {item["label"]}{ai_badge}{ev}</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div style="color:#6b7280;font-size:0.85rem;">No partial matches</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with col_m:
                st.markdown(f"""<div style="background:#fff1f2; border:1px solid #fecdd3;
                    border-radius:12px; padding:1.2rem;">
                    <div style="font-weight:700; color:#be123c; font-size:1rem; margin-bottom:0.8rem;">
                    ❌ Missing ({len(missing)})</div>""", unsafe_allow_html=True)
                if missing:
                    for item in missing:
                        st.markdown(f'<div style="margin-bottom:6px;font-size:0.88rem;font-weight:600;color:#9f1239;">✗ {item["label"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div style="color:#16a34a;font-size:0.85rem;font-weight:600;">🎉 No critical gaps!</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # ── AI Feedback block ──
            if ai_boost and ai_boost.get("feedback"):
                st.markdown("---")
                st.markdown(f"""
                <div style="background:#f0f9ff; border:1px solid #bae6fd; border-radius:12px; padding:1.5rem; margin-top:1rem;">
                    <div style="font-weight:700; color:#0369a1; margin-bottom:0.5rem;">🤖 AI Assessment</div>
                    <div style="color:#334155; font-size:0.95rem; line-height:1.6;">{ai_boost["feedback"]}</div>
                </div>
                """, unsafe_allow_html=True)

                if ai_boost.get("suggestions"):
                    st.markdown("**💡 What to add to your CV:**")
                    for s in ai_boost["suggestions"]:
                        st.markdown(f"- {s}")

            # ── Actionable tips for missing items ──
            elif missing:
                st.markdown("---")
                st.markdown("**💡 Action Plan — what to add to your CV:**")
                for item in missing[:4]:
                    st.markdown(f"- If you have any experience with **{item['label']}** — add it. Even coursework or self-study counts.")

            st.markdown("---")
            nav_buttons(2, can_proceed=True, proceed_label="Next: Refine CV →")


# ============================================================
# TAB 3 — REFINEMENT
# ============================================================

elif current_tab == 3:
    st.markdown('<div class="rp-page-badge">STEP 4 OF 6</div>', unsafe_allow_html=True)
    st.markdown('<div class="rp-page-title">Refinement</div>', unsafe_allow_html=True)
    st.markdown('<div class="rp-page-sub">Two quick questions. Your answers will strengthen the tailored resume.</div>', unsafe_allow_html=True)

    missing = st.session_state.analysis_results.get("missing", [])
    matches = st.session_state.analysis_results.get("matches", [])
    partial = st.session_state.analysis_results.get("partial", [])
    score   = st.session_state.analysis_results.get("score", 0)

    if not st.session_state.analysis_done:
        st.info("ℹ️ Run the analysis first (go to the Analysis tab).")
    else:
        if score >= 70:
            st.success(f"🎉 Great news! Your CV already scores **{score}%** — strong match. Answer the questions below to make it even better.")
        elif score >= 40:
            st.warning(f"Your CV scores **{score}%**. Let's fill the gaps to strengthen your application.")
        else:
            st.error(f"Your CV scores **{score}%**. There are gaps to address — answer the questions below honestly.")

        st.markdown("---")

        if missing:
            st.markdown("**Based on what's missing, answer these to improve your CV:**")
            questions = []
            for i, gap in enumerate(missing[:5]):
                gap_label = gap if isinstance(gap, str) else gap.get("label", str(gap))
                questions.append((
                    f"q_gap_{i}",
                    f"The role requires **{gap_label}**. Do you have any experience, coursework, or projects related to this? Describe briefly.",
                    f"e.g., I studied {gap_label} in my university course / used it in a project / I don't have this yet"
                ))
        else:
            st.success("✅ No critical gaps! Answer these to add more depth:")
            questions = [
                ("q_achievement", "What is your biggest achievement relevant to this role? Include any numbers or results.", "e.g., Built a model that improved prediction accuracy by 15%"),
                ("q_motivation",  "Why do you want this specific role? (Used to improve your summary)", "e.g., Passionate about data-driven decision making..."),
            ]

        for key, question, placeholder in questions:
            st.markdown(f"**{question}**")
            st.session_state.follow_up_answers[key] = st.text_area(
                question,
                value=st.session_state.follow_up_answers.get(key,""),
                placeholder=placeholder,
                key=f"refine_{key}",
                label_visibility="collapsed",
                height=90
            )

        st.markdown("---")
        st.markdown("**🔧 Wording Improvements (applied automatically):**")
        improvements = [
            ("❌ Weak", "✅ Stronger"),
            ("assisted with...", "Engineered / Developed..."),
            ("helped the team", "Optimized team outcomes"),
            ("responsible for", "Directed / Led"),
            ("worked on project", "Spearheaded project"),
        ]
        df = pd.DataFrame(improvements[1:], columns=improvements[0])
        st.table(df)

    st.markdown('</div>', unsafe_allow_html=True)
    nav_buttons(3, can_proceed=True, proceed_label="Next: Preview CV →")


# ============================================================
# TAB 4 — PREVIEW
# ============================================================

elif current_tab == 4:
    st.markdown('<div class="rp-page-badge">STEP 5 OF 6</div>', unsafe_allow_html=True)
    st.markdown('<div class="rp-page-title">Preview</div>', unsafe_allow_html=True)
    st.markdown('<div class="rp-page-sub">Your tailored resume. Choose output language and review before downloading.</div>', unsafe_allow_html=True)

    lang = st.radio("Output language:", ["English","Hebrew","Arabic"], horizontal=True, key="lang_select")
    st.session_state.active_lang = lang

    # ── Get base CV sections ──
    base_data = st.session_state.manual_cv_data.copy()
    if not any(v.strip() for v in base_data.values()):
        base_data = classify_sections_refined(st.session_state.cv_full_text)

    has_content = any(v.strip() for v in base_data.values())

    if not has_content:
        st.warning("⚠️ No CV content found. Please go back to **CV Content** and add your information.")
        nav_buttons(4, can_proceed=False)
    else:
        # ── Step 1: Claude CV Adjustment (English, run once) ──
        if not st.session_state.cv_adjusted:
            with st.spinner("✨ Tailoring your CV for this role... (~10 seconds)"):
                adjusted = call_claude_cv_adjustment(
                    base_data,
                    st.session_state.job_role,
                    st.session_state.job_desc,
                    st.session_state.analysis_results,
                    st.session_state.follow_up_answers,
                )
            if adjusted:
                st.session_state.adjusted_cv_data = build_final_cv(base_data, adjusted, st.session_state.job_role)
                st.session_state.cv_adjusted = True
                st.success("✅ CV tailored successfully!")
            else:
                fallback = base_data.copy()
                if st.session_state.job_role and fallback.get("summary"):
                    if st.session_state.job_role.lower() not in fallback["summary"].lower():
                        fallback["summary"] = f"Motivated professional targeting a {st.session_state.job_role} role. " + fallback["summary"]
                st.session_state.adjusted_cv_data = fallback
                st.session_state.cv_adjusted = True
                st.info("ℹ️ Showing CV with basic improvements (AI tailoring unavailable).")

        english_cv = st.session_state.adjusted_cv_data or base_data

        # ── Step 2: Translation for Hebrew/Arabic ──
        if lang in ["Hebrew", "Arabic"]:
            cache_key = f"translated_{lang}"
            if cache_key not in st.session_state:
                st.session_state[cache_key] = {}

            cached = st.session_state.get(cache_key, {})
            if not cached:
                with st.spinner(f"🌐 Translating CV to {'Hebrew' if lang == 'Hebrew' else 'Arabic'}... (~15 seconds)"):
                    translated = translate_cv_googletrans(english_cv, lang)
                st.session_state[cache_key] = translated
                final_cv = translated
            else:
                final_cv = cached
        else:
            final_cv = english_cv

        st.session_state.final_cv_data = final_cv

        # ── What changed panel ──
        original_summary = base_data.get("summary","")
        adjusted_summary = english_cv.get("summary","")
        if original_summary and adjusted_summary and original_summary.strip() != adjusted_summary.strip():
            with st.expander("👀 See what was improved in your CV"):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**Original:**")
                    st.markdown(f'<div style="background:#fff1f2;padding:12px;border-radius:8px;font-size:0.88rem;color:#334155;">{original_summary}</div>', unsafe_allow_html=True)
                with c2:
                    st.markdown("**Tailored:**")
                    st.markdown(f'<div style="background:#f0fdf4;padding:12px;border-radius:8px;font-size:0.88rem;color:#166534;">{adjusted_summary}</div>', unsafe_allow_html=True)

        # ── Regenerate button ──
        col_regen, _ = st.columns([1,4])
        with col_regen:
            if st.button("🔄 Re-tailor CV"):
                st.session_state.cv_adjusted = False
                st.session_state.adjusted_cv_data = {}
                for k in ["translated_Hebrew","translated_Arabic"]:
                    if k in st.session_state:
                        del st.session_state[k]
                st.rerun()

        st.markdown("---")

        # ── CV Preview ──
        st.markdown('<div style="background:#f1f5f9;padding:30px 15px;border-radius:12px;">', unsafe_allow_html=True)
        st.markdown(render_cv_html(final_cv, lang), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div style="margin-top:1rem;padding:1rem;background:#f0fdf4;border-radius:10px;border:1px solid #bbf7d0;">', unsafe_allow_html=True)
        st.markdown("✅ **Your tailored CV is ready!** Download it in the next tab.")
        st.markdown('</div>', unsafe_allow_html=True)

        nav_buttons(4, can_proceed=True, proceed_label="Next: Download →")


# ============================================================
# TAB 5 — EXPORT
# ============================================================

elif current_tab == 5:
    st.markdown('<div class="rp-page-badge">STEP 6 OF 6</div>', unsafe_allow_html=True)
    st.markdown('<div class="rp-page-title">Download</div>', unsafe_allow_html=True)
    st.markdown('<div class="rp-page-sub">Your tailored resume is ready to send.</div>', unsafe_allow_html=True)

    cv_f = st.session_state.final_cv_data
    has_content = bool(cv_f and any(v.strip() for v in cv_f.values()))

    if not has_content:
        st.warning("Please complete the Preview step first.")
        nav_buttons(5, can_proceed=False)
    else:
        active_lang = st.session_state.active_lang

        # Score badge
        score = st.session_state.analysis_results.get("score", 0)
        if score:
            score_class = "alert-green" if score >= 70 else "alert-orange" if score >= 40 else "alert-red"
            st.markdown(f'<div class="alert-box {score_class}">Match Score: {score}% for {st.session_state.job_role}</div>', unsafe_allow_html=True)

        # File name
        pd_raw = cv_f.get("personal_details","Candidate")
        name_part, _ = format_contact_info(pd_raw)
        first_name = name_part.split()[0] if name_part else "Candidate"
        job_slug = re.sub(r'[^a-zA-Z0-9]', '_', st.session_state.job_role) if st.session_state.job_role else "CV"
        f_name = f"{first_name}_{job_slug}_CV"

        st.markdown("<hr style='border:none;border-top:1px solid #e9e9e7;margin:20px 0;'>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)

        with c1:
            st.markdown('<div class="rp-dl-fmt">TXT</div><div class="rp-dl-desc">For online forms and portals</div>', unsafe_allow_html=True)
            h_map = HEADINGS_MAP[active_lang]
            section_order = [
                ("personal_details", h_map[0]),
                ("summary",          h_map[1]),
                ("education",        h_map[2]),
                ("experience",       h_map[3]),
                ("projects",         h_map[4]),
                ("courses_training", h_map[5]),
                ("volunteering",     h_map[6]),
                ("languages",        h_map[7]),
                ("skills",           h_map[8]),
            ]
            txt_out = f"{st.session_state.job_role} — CV\n{'='*50}\n\n"
            for key, title in section_order:
                v = cv_f.get(key,"").strip()
                if v:
                    # Clean skills subheadings
                    if key == "skills":
                        v = re.sub(r'(Technical Skills|Business & Professional Skills|Professional Skills)\s*[,\n]?', '', v, flags=re.IGNORECASE)
                    # Expand inline bullets
                    v = re.sub(r'\s*•\s*', '\n  • ', v)
                    txt_out += f"{title.upper()}\n{'-'*len(title)}\n{v.strip()}\n\n"
            st.download_button(
                "📄 Download TXT",
                txt_out,
                file_name=f"{f_name}.txt",
                mime="text/plain",
                use_container_width=True,
                type="primary"
            )

        with c2:
            st.markdown('<div class="rp-dl-fmt">DOCX</div><div class="rp-dl-desc">Recommended — send directly to employers</div>', unsafe_allow_html=True)
            docx_buf = generate_docx(cv_f, active_lang)
            st.download_button(
                "📁 Download DOCX",
                docx_buf,
                file_name=f"{f_name}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
                type="primary"
            )

        st.markdown("""
        <div class="rp-checklist" style="margin-top:20px;">
            <div class="rp-checklist-title">Before you send</div>
            <div class="rp-check-item">Review every line — make sure everything is accurate.</div>
            <div class="rp-check-item">Never include anything you cannot back up in an interview.</div>
            <div class="rp-check-item">Customize the summary for each job you apply to.</div>
            <div class="rp-check-item">Good luck. You've got this. 🍀</div>
        </div>
        """, unsafe_allow_html=True)
        nav_buttons(5, can_proceed=False)
