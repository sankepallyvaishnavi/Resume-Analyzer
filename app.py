import os
import json
import time

import streamlit as st
import fitz
from google import genai


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)


# =========================================================
# CSS
# =========================================================

st.markdown("""
<style>

.main {
    background-color: #f5f7fb;
}

.header {
    background: linear-gradient(90deg, #4f46e5, #7c3aed);
    color: white;
    padding: 25px;
    border-radius: 15px;
    text-align: center;
    margin-bottom: 25px;
}

.header h1 {
    margin-bottom: 5px;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# HEADER
# =========================================================

st.markdown("""
<div class="header">
    <h1>📄 AI Resume Analyzer</h1>
    <p>Analyze your resume using Artificial Intelligence</p>
</div>
""", unsafe_allow_html=True)


# =========================================================
# GET API KEY
# =========================================================

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        api_key = None


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header("⚙️ Settings")

job_role = st.sidebar.selectbox(
    "Target Job Role",
    [
        "Data Analyst",
        "Data Scientist",
        "Machine Learning Engineer",
        "AI Engineer",
        "Python Developer",
        "Software Developer",
        "Web Developer",
        "Full Stack Developer",
        "Business Analyst"
    ]
)

model_name = "gemini-3.8-flash"

st.sidebar.markdown("---")

st.sidebar.info(
    "Upload your PDF resume and click Analyze Resume "
    "to receive AI-powered feedback."
)


# =========================================================
# API KEY CHECK
# =========================================================

if not api_key:

    st.error(
        "Gemini API key not found. "
        "Please set the GEMINI_API_KEY environment variable."
    )

    st.stop()


# =========================================================
# CREATE GEMINI CLIENT
# =========================================================

@st.cache_resource
def create_client(key):

    return genai.Client(api_key=key)


client = create_client(api_key)


# =========================================================
# EXTRACT TEXT FROM PDF
# =========================================================

def extract_text_from_pdf(uploaded_file):

    try:

        pdf_bytes = uploaded_file.read()

        document = fitz.open(
            stream=pdf_bytes,
            filetype="pdf"
        )

        text = ""

        for page in document:

            text += page.get_text()

        document.close()

        return text

    except Exception as e:

        st.error(
            f"Could not read the PDF: {e}"
        )

        return ""


# =========================================================
# ANALYZE RESUME
# =========================================================

def analyze_resume(resume_text, target_role):

    prompt = f"""
You are an expert resume analyzer and career advisor.

Analyze the following resume for the target job role.

TARGET JOB ROLE:
{target_role}

RESUME:
{resume_text}

Return ONLY valid JSON.

Use exactly this format:

{{
    "resume_score": 0,
    "summary": "",
    "technical_skills": [],
    "soft_skills": [],
    "strengths": [],
    "weaknesses": [],
    "missing_skills": [],
    "recommended_roles": [],
    "experience_analysis": "",
    "education_analysis": "",
    "ats_feedback": [],
    "improvements": [],
    "learning_roadmap": []
}}

Rules:

1. resume_score must be between 0 and 100.
2. Do not invent information that is not present in the resume.
3. Identify skills only from the resume.
4. Missing skills should be relevant to the selected target role.
5. Give practical suggestions.
6. Keep the answers simple and useful.
7. Return JSON only.
"""

    response = None

    # Retry temporary 503 errors
    for attempt in range(3):

        try:

            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )

            break

        except Exception as e:

            error_message = str(e)

            if "503" in error_message and attempt < 2:

                wait_time = 3 * (attempt + 1)

                st.warning(
                    f"Gemini is temporarily busy. "
                    f"Retrying in {wait_time} seconds..."
                )

                time.sleep(wait_time)

            else:

                raise


    if response is None:

        raise Exception(
            "No response received from Gemini."
        )


    result = response.text.strip()


    # Remove markdown code blocks
    if result.startswith("```json"):

        result = result[7:]

    if result.startswith("```"):

        result = result[3:]

    if result.endswith("```"):

        result = result[:-3]

    result = result.strip()


    # Convert response to JSON
    return json.loads(result)


# =========================================================
# RESUME UPLOAD
# =========================================================

st.subheader("📁 Upload Resume")

uploaded_file = st.file_uploader(
    "Choose your resume PDF",
    type=["pdf"]
)


# =========================================================
# MAIN APPLICATION
# =========================================================

if uploaded_file:

    st.success(
        f"Uploaded: {uploaded_file.name}"
    )

    resume_text = extract_text_from_pdf(
        uploaded_file
    )


    if not resume_text.strip():

        st.error(
            "No readable text was found in this PDF."
        )

        st.stop()


    # -----------------------------------------------------
    # SHOW EXTRACTED TEXT
    # -----------------------------------------------------

    with st.expander("📄 View Extracted Resume Text"):

        st.text_area(
            "Resume Text",
            resume_text,
            height=300
        )


    st.markdown("---")


    # -----------------------------------------------------
    # ANALYZE BUTTON
    # -----------------------------------------------------

    if st.button(
        "🤖 Analyze Resume",
        type="primary",
        use_container_width=True
    ):

        try:

            with st.spinner(
                "🤖 AI is analyzing your resume..."
            ):

                analysis = analyze_resume(
                    resume_text,
                    job_role
                )


            # =================================================
            # SCORE
            # =================================================

            st.markdown("---")

            st.subheader("📊 Resume Score")

            score = analysis.get(
                "resume_score",
                0
            )

            col1, col2, col3 = st.columns(3)


            with col1:

                st.metric(
                    "Resume Score",
                    f"{score}/100"
                )


            with col2:

                st.metric(
                    "Target Role",
                    job_role
                )


            with col3:

                if score >= 80:

                    status = "Excellent"

                elif score >= 60:

                    status = "Good"

                elif score >= 40:

                    status = "Needs Improvement"

                else:

                    status = "Needs Major Improvement"


                st.metric(
                    "Status",
                    status
                )


            st.progress(
                min(
                    max(
                        float(score) / 100,
                        0
                    ),
                    1
                )
            )


            # =================================================
            # SUMMARY
            # =================================================

            st.markdown("---")

            st.subheader("📝 Resume Summary")

            st.info(
                analysis.get(
                    "summary",
                    "No summary available."
                )
            )


            # =================================================
            # TECHNICAL SKILLS
            # =================================================

            st.subheader("💻 Technical Skills")

            technical_skills = analysis.get(
                "technical_skills",
                []
            )

            if technical_skills:

                for skill in technical_skills:

                    st.write(
                        f"🔹 {skill}"
                    )

            else:

                st.write(
                    "No technical skills detected."
                )


            # =================================================
            # SOFT SKILLS
            # =================================================

            st.subheader("🤝 Soft Skills")

            soft_skills = analysis.get(
                "soft_skills",
                []
            )

            if soft_skills:

                for skill in soft_skills:

                    st.write(
                        f"🔹 {skill}"
                    )

            else:

                st.write(
                    "No soft skills detected."
                )


            # =================================================
            # STRENGTHS
            # =================================================

            st.markdown("---")

            st.subheader("💪 Strengths")

            strengths = analysis.get(
                "strengths",
                []
            )

            for item in strengths:

                st.success(
                    f"✓ {item}"
                )


            # =================================================
            # WEAKNESSES
            # =================================================

            st.subheader("⚠️ Weaknesses")

            weaknesses = analysis.get(
                "weaknesses",
                []
            )

            for item in weaknesses:

                st.warning(
                    f"• {item}"
                )


            # =================================================
            # MISSING SKILLS
            # =================================================

            st.markdown("---")

            st.subheader("🎯 Missing Skills")

            missing_skills = analysis.get(
                "missing_skills",
                []
            )

            if missing_skills:

                for skill in missing_skills:

                    st.write(
                        f"🔸 {skill}"
                    )

            else:

                st.success(
                    "No major missing skills identified."
                )


            # =================================================
            # RECOMMENDED ROLES
            # =================================================

            st.subheader(
                "💼 Recommended Job Roles"
            )

            recommended_roles = analysis.get(
                "recommended_roles",
                []
            )

            for role in recommended_roles:

                st.info(
                    f"💼 {role}"
                )


            # =================================================
            # EXPERIENCE
            # =================================================

            st.markdown("---")

            st.subheader(
                "👨‍💻 Experience Analysis"
            )

            st.write(
                analysis.get(
                    "experience_analysis",
                    "No experience analysis available."
                )
            )


            # =================================================
            # EDUCATION
            # =================================================

            st.subheader(
                "🎓 Education Analysis"
            )

            st.write(
                analysis.get(
                    "education_analysis",
                    "No education analysis available."
                )
            )


            # =================================================
            # ATS
            # =================================================

            st.markdown("---")

            st.subheader(
                "🤖 ATS Feedback"
            )

            ats_feedback = analysis.get(
                "ats_feedback",
                []
            )

            for item in ats_feedback:

                st.write(
                    f"🔹 {item}"
                )


            # =================================================
            # IMPROVEMENTS
            # =================================================

            st.markdown("---")

            st.subheader(
                "🚀 Resume Improvement Suggestions"
            )

            improvements = analysis.get(
                "improvements",
                []
            )

            for i, item in enumerate(
                improvements,
                start=1
            ):

                st.write(
                    f"**{i}.** {item}"
                )


            # =================================================
            # LEARNING ROADMAP
            # =================================================

            st.markdown("---")

            st.subheader(
                "📚 Learning Roadmap"
            )

            roadmap = analysis.get(
                "learning_roadmap",
                []
            )

            for i, item in enumerate(
                roadmap,
                start=1
            ):

                st.write(
                    f"**Step {i}:** {item}"
                )


            # =================================================
            # DOWNLOAD
            # =================================================

            st.markdown("---")

            json_data = json.dumps(
                analysis,
                indent=4
            )

            st.download_button(
                label="📥 Download Analysis",
                data=json_data,
                file_name="resume_analysis.json",
                mime="application/json",
                use_container_width=True
            )


        except json.JSONDecodeError:

            st.error(
                "Gemini returned an invalid JSON response. "
                "Please click Analyze Resume again."
            )


        except Exception as e:

            error_message = str(e)

            if "503" in error_message:

                st.error(
                    "Gemini is temporarily unavailable "
                    "because of high demand. Please wait "
                    "a little and try again."
                )

            elif "404" in error_message:

                st.error(
                    "The selected Gemini model is unavailable. "
                    "Please check the current Gemini model settings."
                )

            elif "401" in error_message or "403" in error_message:

                st.error(
                    "Your Gemini API key was rejected. "
                    "Please check your API key."
                )

            else:

                st.error(
                    f"Something went wrong: {error_message}"
                )


else:

    st.info(
        "👆 Upload a PDF resume to get started."
    )


# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption(
    "AI Resume Analyzer | Python + Streamlit + Google Gemini"
)