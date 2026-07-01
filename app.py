import streamlit as st
import pdfplumber
import io
import re
from docx import Document

st.set_page_config(
    page_title="Resume Analyzer",
    page_icon="📄",
    layout="wide",
)

TECHNICAL_SKILLS = {
    "Programming Languages": [
        "python", "java", "javascript", "typescript", "c++", "c#", "c", "ruby",
        "php", "swift", "kotlin", "go", "rust", "scala", "r", "matlab", "perl",
        "bash", "shell", "powershell", "dart", "lua", "haskell", "elixir",
    ],
    "Web & Frontend": [
        "html", "css", "react", "angular", "vue", "next.js", "nuxt", "svelte",
        "redux", "graphql", "rest api", "jquery", "bootstrap", "tailwind",
        "sass", "webpack", "vite", "figma", "ui/ux",
    ],
    "Backend & APIs": [
        "node.js", "express", "django", "flask", "fastapi", "spring", "rails",
        "laravel", "asp.net", "microservices", "grpc", "websockets", "oauth",
        "jwt", "restful", "api design",
    ],
    "Databases": [
        "sql", "mysql", "postgresql", "mongodb", "redis", "sqlite", "oracle",
        "dynamodb", "cassandra", "elasticsearch", "firebase", "supabase",
        "nosql", "database design", "orm",
    ],
    "Cloud & DevOps": [
        "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ansible",
        "jenkins", "github actions", "ci/cd", "linux", "nginx", "apache",
        "serverless", "lambda", "devops", "helm",
    ],
    "Data & ML": [
        "machine learning", "deep learning", "tensorflow", "pytorch", "keras",
        "scikit-learn", "pandas", "numpy", "data analysis", "nlp", "computer vision",
        "data science", "statistics", "tableau", "power bi", "spark", "hadoop",
    ],
    "Tools & Practices": [
        "git", "github", "gitlab", "bitbucket", "jira", "agile", "scrum",
        "tdd", "unit testing", "jest", "pytest", "selenium", "postman",
        "vs code", "intellij", "xcode", "linux", "bash",
    ],
}

SOFT_SKILLS = [
    "leadership", "communication", "teamwork", "problem solving", "critical thinking",
    "time management", "collaboration", "adaptability", "creativity", "attention to detail",
    "project management", "mentoring", "public speaking", "negotiation", "conflict resolution",
    "analytical", "strategic", "cross-functional", "stakeholder management",
]

ATS_KEYWORDS = [
    "achieved", "improved", "developed", "managed", "led", "created", "implemented",
    "designed", "launched", "delivered", "increased", "reduced", "optimized",
    "streamlined", "collaborated", "mentored", "built", "deployed", "maintained",
    "architected",
]

SECTION_HEADERS = [
    "experience", "education", "skills", "projects", "summary", "objective",
    "certifications", "achievements", "awards", "publications", "references",
    "work experience", "professional experience", "technical skills",
]


def extract_text_from_pdf(file_bytes):
    text = ""
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def extract_text_from_docx(file_bytes):
    doc = Document(io.BytesIO(file_bytes))
    return "\n".join([para.text for para in doc.paragraphs])


def detect_skills(text):
    text_lower = text.lower()
    detected = {}
    for category, skills in TECHNICAL_SKILLS.items():
        found = []
        for skill in skills:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                found.append(skill.title() if len(skill) > 3 else skill.upper())
        if found:
            detected[category] = found
    return detected


def detect_soft_skills(text):
    text_lower = text.lower()
    found = []
    for skill in SOFT_SKILLS:
        if skill in text_lower:
            found.append(skill.title())
    return found


def detect_action_verbs(text):
    text_lower = text.lower()
    found = []
    for verb in ATS_KEYWORDS:
        if re.search(r'\b' + verb + r'\b', text_lower):
            found.append(verb.capitalize())
    return found


def detect_sections(text):
    text_lower = text.lower()
    found = []
    for section in SECTION_HEADERS:
        if re.search(r'\b' + re.escape(section) + r'\b', text_lower):
            found.append(section.title())
    return found


def count_words(text):
    return len(text.split())


def has_email(text):
    return bool(re.search(r'[\w.+-]+@[\w-]+\.[a-z]{2,}', text, re.IGNORECASE))


def has_phone(text):
    return bool(re.search(r'(\+?\d[\d\s\-().]{7,}\d)', text))


def has_linkedin(text):
    return bool(re.search(r'linkedin\.com', text, re.IGNORECASE))


def has_github(text):
    return bool(re.search(r'github\.com', text, re.IGNORECASE))


def calculate_ats_score(text, detected_skills, soft_skills, action_verbs, sections):
    score = 0
    breakdown = {}

    skill_count = sum(len(v) for v in detected_skills.values())
    skill_score = min(30, skill_count * 2)
    score += skill_score
    breakdown["Technical Skills"] = (skill_score, 30, f"{skill_count} skills detected")

    soft_score = min(10, len(soft_skills) * 2)
    score += soft_score
    breakdown["Soft Skills"] = (soft_score, 10, f"{len(soft_skills)} soft skills detected")

    verb_score = min(20, len(action_verbs) * 2)
    score += verb_score
    breakdown["Action Verbs"] = (verb_score, 20, f"{len(action_verbs)} action verbs found")

    contact_score = 0
    contact_details = []
    if has_email(text):
        contact_score += 5
        contact_details.append("Email")
    if has_phone(text):
        contact_score += 5
        contact_details.append("Phone")
    if has_linkedin(text):
        contact_score += 3
        contact_details.append("LinkedIn")
    if has_github(text):
        contact_score += 2
        contact_details.append("GitHub")
    contact_score = min(15, contact_score)
    score += contact_score
    breakdown["Contact Info"] = (contact_score, 15, ", ".join(contact_details) if contact_details else "None found")

    key_sections = ["Experience", "Education", "Skills"]
    found_key = [s for s in key_sections if s in sections]
    section_score = min(15, len(found_key) * 5)
    score += section_score
    breakdown["Resume Sections"] = (section_score, 15, f"{len(sections)} sections found")

    word_count = count_words(text)
    if 300 <= word_count <= 800:
        length_score = 10
        length_note = f"{word_count} words (ideal range)"
    elif word_count < 300:
        length_score = 4
        length_note = f"{word_count} words (too short)"
    else:
        length_score = 6
        length_note = f"{word_count} words (too long)"
    score += length_score
    breakdown["Resume Length"] = (length_score, 10, length_note)

    return min(100, score), breakdown


def get_score_color(score):
    if score >= 80:
        return "green"
    elif score >= 60:
        return "orange"
    else:
        return "red"


def get_score_label(score):
    if score >= 80:
        return "Excellent — ATS Ready"
    elif score >= 60:
        return "Good — Minor Improvements Needed"
    elif score >= 40:
        return "Fair — Significant Improvements Needed"
    else:
        return "Poor — Major Revisions Required"


def build_suggestions(text, detected_skills, soft_skills, action_verbs, sections, score):
    suggestions = []
    word_count = count_words(text)

    if not has_email(text):
        suggestions.append("Add a professional email address to your contact section.")
    if not has_phone(text):
        suggestions.append("Include a phone number for recruiters to reach you.")
    if not has_linkedin(text):
        suggestions.append("Add your LinkedIn profile URL to increase credibility.")
    if not has_github(text) and "Programming Languages" in detected_skills:
        suggestions.append("Add your GitHub profile to showcase your code projects.")

    skill_count = sum(len(v) for v in detected_skills.values())
    if skill_count < 8:
        suggestions.append("List more technical skills — aim for at least 8–12 relevant skills.")

    if len(soft_skills) < 3:
        suggestions.append("Include soft skills like leadership, communication, and teamwork.")

    if len(action_verbs) < 5:
        suggestions.append("Use more action verbs (e.g., Developed, Implemented, Delivered) to describe your work.")

    if "Experience" not in sections and "Work Experience" not in sections:
        suggestions.append("Ensure your resume has a clear 'Work Experience' or 'Experience' section.")
    if "Education" not in sections:
        suggestions.append("Add an 'Education' section with your degrees and institutions.")
    if "Skills" not in sections and "Technical Skills" not in sections:
        suggestions.append("Add a dedicated 'Skills' section so ATS can parse your abilities.")

    if word_count < 300:
        suggestions.append(f"Your resume is too short ({word_count} words). Aim for 400–700 words.")
    elif word_count > 900:
        suggestions.append(f"Your resume is lengthy ({word_count} words). Try to keep it under 800 words for ATS.")

    if not suggestions:
        suggestions.append("Your resume looks strong! Keep it updated with recent accomplishments.")

    return suggestions


st.title("📄 Resume Analyzer")
st.markdown("Upload your resume (PDF or DOCX) to extract skills, detect gaps, and get your ATS score.")

st.markdown("---")

uploaded_file = st.file_uploader(
    "Upload your resume",
    type=["pdf", "docx"],
    help="Supported formats: PDF and DOCX",
)

if uploaded_file is not None:
    file_bytes = uploaded_file.read()
    file_name = uploaded_file.name

    with st.spinner("Extracting text from your resume..."):
        try:
            if file_name.lower().endswith(".pdf"):
                text = extract_text_from_pdf(file_bytes)
                file_type = "PDF"
            else:
                text = extract_text_from_docx(file_bytes)
                file_type = "DOCX"
        except Exception as e:
            st.error(f"Could not read the file: {e}")
            st.stop()

    if not text.strip():
        st.error("No text could be extracted. The file may be scanned/image-based. Please use a text-based PDF.")
        st.stop()

    detected_skills = detect_skills(text)
    soft_skills = detect_soft_skills(text)
    action_verbs = detect_action_verbs(text)
    sections = detect_sections(text)
    ats_score, breakdown = calculate_ats_score(text, detected_skills, soft_skills, action_verbs, sections)
    suggestions = build_suggestions(text, detected_skills, soft_skills, action_verbs, sections, ats_score)

    col_score, col_label = st.columns([1, 3])

    with col_score:
        color = get_score_color(ats_score)
        st.markdown(
            f"<div style='text-align:center; padding: 20px; border-radius: 12px; "
            f"background-color: {'#e6f4ea' if color == 'green' else '#fff3e0' if color == 'orange' else '#fce8e8'};"
            f"border: 2px solid {'#34a853' if color == 'green' else '#fb8c00' if color == 'orange' else '#e53935'};'>"
            f"<span style='font-size: 52px; font-weight: bold; color: "
            f"{'#34a853' if color == 'green' else '#fb8c00' if color == 'orange' else '#e53935'};'>"
            f"{ats_score}</span><br>"
            f"<span style='font-size: 14px; color: #666;'>out of 100</span></div>",
            unsafe_allow_html=True,
        )

    with col_label:
        st.markdown(f"### {get_score_label(ats_score)}")
        st.markdown(f"**File:** {file_name} ({file_type}) &nbsp;|&nbsp; **Words:** {count_words(text)}")
        st.progress(ats_score / 100)

    st.markdown("---")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Score Breakdown",
        "🛠 Technical Skills",
        "💡 Soft Skills & Verbs",
        "📋 Extracted Text",
        "✅ Suggestions",
    ])

    with tab1:
        st.subheader("ATS Score Breakdown")
        for criterion, (earned, total, note) in breakdown.items():
            pct = earned / total if total else 0
            col_a, col_b, col_c = st.columns([2, 3, 1])
            with col_a:
                st.markdown(f"**{criterion}**")
                st.caption(note)
            with col_b:
                st.progress(pct)
            with col_c:
                st.markdown(f"**{earned}/{total}**")

    with tab2:
        st.subheader("Technical Skills Detected")
        if detected_skills:
            total_tech = sum(len(v) for v in detected_skills.values())
            st.info(f"Found **{total_tech} technical skills** across {len(detected_skills)} categories.")
            for category, skills in detected_skills.items():
                with st.expander(f"**{category}** — {len(skills)} skill(s)", expanded=True):
                    cols = st.columns(min(4, len(skills)))
                    for i, skill in enumerate(skills):
                        with cols[i % len(cols)]:
                            st.success(skill)
        else:
            st.warning("No technical skills detected. Add a dedicated Skills section with specific technologies.")

    with tab3:
        col_soft, col_verbs = st.columns(2)

        with col_soft:
            st.subheader("Soft Skills")
            if soft_skills:
                for skill in soft_skills:
                    st.markdown(f"✔ {skill}")
            else:
                st.warning("No soft skills detected.")

        with col_verbs:
            st.subheader("Action Verbs")
            if action_verbs:
                for verb in action_verbs:
                    st.markdown(f"▶ {verb}")
            else:
                st.warning("No strong action verbs detected. Use verbs like Developed, Led, Implemented.")

        st.markdown("---")
        st.subheader("Resume Sections Found")
        if sections:
            cols = st.columns(min(4, len(sections)))
            for i, section in enumerate(sections):
                with cols[i % len(cols)]:
                    st.info(section)
        else:
            st.warning("No standard resume sections detected.")

    with tab4:
        st.subheader("Extracted Resume Text")
        st.text_area("Full text extracted from your resume:", value=text, height=400)

    with tab5:
        st.subheader("Improvement Suggestions")
        for i, suggestion in enumerate(suggestions, 1):
            st.markdown(f"**{i}.** {suggestion}")

else:
    st.info("👆 Upload a PDF or DOCX resume above to get started.")

    with st.expander("How the ATS Score is calculated"):
        st.markdown("""
        The ATS (Applicant Tracking System) score is computed across 6 dimensions:

        | Criterion | Max Points | What We Check |
        |---|---|---|
        | Technical Skills | 30 | Programming languages, frameworks, tools, cloud, databases |
        | Soft Skills | 10 | Leadership, communication, teamwork, etc. |
        | Action Verbs | 20 | Strong verbs like Developed, Implemented, Delivered |
        | Contact Info | 15 | Email, phone, LinkedIn, GitHub |
        | Resume Sections | 15 | Experience, Education, Skills, etc. |
        | Resume Length | 10 | Ideal range: 300–800 words |

        **Score Guide:**
        - 80–100: Excellent — ATS Ready
        - 60–79: Good — Minor improvements needed
        - 40–59: Fair — Needs work
        - 0–39: Poor — Major revisions required
        """)
