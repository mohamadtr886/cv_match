# CV Match AI — Gemini Project Rules

## Project Identity
This project is a Streamlit MVP called CV Match AI.

CV Match AI helps university students and entry-level applicants create, organize, and tailor a professional CV for a specific target job description.

The app should be professional, clean, honest, and suitable for a university Vibe Coding project.

## Main Goal
The user provides:
1. A target job role
2. A current CV or student profile
3. A target job description
4. Optional answers to follow-up questions

The app then:
1. Validates the inputs
2. Compares the CV with the job description
3. Shows matching and missing keywords
4. Asks missing-information questions
5. Generates a clean final CV preview
6. Allows DOCX and TXT download

## Non-Negotiable Honesty Rule
Never invent, hallucinate, exaggerate, or create fake:
- skills
- experience
- jobs
- companies
- projects
- achievements
- metrics
- education
- certifications
- languages

Only use information explicitly provided by the user.

If something is missing, ask a follow-up question or suggest adding it only if true.

## Technical Rules
- Keep the app in Streamlit.
- Main file: app.py.
- Keep the project simple and demo-ready.
- Do not use paid APIs.
- Do not connect OpenAI, Anthropic, Gemini API, or external LLM services.
- The MVP should be local and rule-based.
- Do not create unnecessary files.
- Do not break existing working features.
- Add clear code comments for important pipeline steps.

## Required App Flow
The app should work like a step-by-step wizard:

1. Target Job Role
2. CV Information Input
3. Job Description
4. Validation and Match Analysis
5. Follow-up Questions
6. Final CV Preview
7. Download

The user should move through the app with clear Next and Back buttons.

## Input Methods
The app must support:

1. Upload an existing CV
   - PDF, DOCX, TXT

2. Paste CV text manually
   - Useful when upload extraction is bad

3. Build a CV from structured fields
   - Show manual CV sections only in this mode

4. Use demo data
   - For class demo and testing only

## Manual CV Sections
Use this section order:

1. Personal Details
2. Professional Summary
3. Education
4. Professional Experience
5. Projects
6. Courses & Training
7. Volunteering / Community
8. Languages
9. Skills
10. Additional Information, only if needed

## Validation Rules
Do not show score, analysis, final CV, or downloads unless:
- CV/profile is meaningful
- target job role is provided
- job description is meaningful

Reject:
- empty CV
- very short CV
- empty job role
- job descriptions under about 30 meaningful words
- nonsense input such as test, asdf, qwerty, whatever, nothing, random repeated words

Use professional warning messages.

## Keyword Matching Rules
The match score must be based on real meaningful keyword overlap.

Show:
- matching keywords
- missing meaningful keywords
- honest feedback

Do not show useless missing keywords such as:
ability, advanced, bachelor, common, core, critical, degree, entry, familiarity, field, foundation, job, knowledge, large, like, strong, excellent, good, responsible, requirement, requirements, responsibilities, candidate, company, team, work, working, looking, opportunity, motivated, passion

Prefer meaningful keywords:
- technical skills
- tools
- methods
- role-specific terms
- hard skills
- useful soft skills
- domain terms

Limit missing keywords to the most important items.

## Follow-up Questions
Follow-up questions should help the user add real missing information.

Each question must have its own answer box.

If the user answers, include the answer in the final CV only if relevant and clearly provided.

If the user leaves it empty, do not invent anything.

## CV Writing Rules
Follow professional CV rules:
- Clean and structured
- Easy to scan
- Targeted to the job role
- Short bullet points
- Action verbs
- Impact-focused when real impact is provided
- No fake metrics
- No fake experience
- No long messy paragraphs
- No random dots
- No emojis inside the final CV

## Final CV Layout
The final CV should look like a professional document:

- Name as the main header if detected
- Contact details under the name
- Dark blue section headings
- Thin divider lines
- Clean spacing
- Bullet points
- Compact grouped skills
- No giant empty boxes
- No messy extracted raw text

Preferred entry style:

Role / Project Title  
Organization | Dates  
- Bullet point  
- Bullet point  

Skills should be grouped when possible:

Technical: Python, R, SQL  
Tools: Git, GitHub, Jupyter, RStudio  
Analysis: Machine Learning, Statistical Modeling, Data Analysis  
Soft Skills: Communication, Mentoring, Problem Solving  

## Language and Direction Rules
Detect the main CV language:
- Hebrew if Hebrew letters appear
- Arabic if Arabic letters appear
- English otherwise

Default output language should be same as input.

Support:
- English: LTR, English headings
- Hebrew: RTL, Hebrew headings
- Arabic: RTL, Arabic headings

Important:
This is a local rule-based MVP, not a full translation engine.
If the user chooses another output language, translate section headings and structure only.
Do not pretend to fully translate all user content.

Hebrew headings:
- קורות חיים
- פרטים אישיים
- תמצית מקצועית
- השכלה
- ניסיון תעסוקתי
- פרויקטים
- קורסים והכשרות
- התנדבות / פעילות קהילתית
- שפות
- כישורים
- מידע נוסף

Arabic headings:
- السيرة الذاتية
- البيانات الشخصية
- الملخص المهني
- التعليم
- الخبرة العملية
- المشاريع
- الدورات والتدريب
- التطوع / النشاط المجتمعي
- اللغات
- المهارات
- معلومات إضافية

## Download Rules
The app should provide:
- DOCX download as the main option
- TXT download as a simple ATS-friendly option

PDF should only be added if it works reliably.
If Hebrew/Arabic PDF breaks, do not include PDF.

DOCX should be professional:
- clean title/name header
- section headings
- spacing
- bullet points
- grouped skills
- RTL alignment where possible for Hebrew/Arabic

## Design Rules
The app should look like a serious career tool:
- professional blue/dark gray theme
- white cards
- clear section headers
- clean spacing
- simple buttons
- no childish emojis
- no distracting colors
- no fake AI language

Use terms like:
- Rule-based CV analysis
- Local keyword comparison
- Final tailored CV preview

Avoid:
- fake AI analyzing
- magical claims
- overpromising
