# 📄 AI Resume Analyzer

Analyze resumes using **Google Gemini AI**. Upload a PDF resume and get a resume score, skills, strengths, weaknesses, missing skills, job recommendations, ATS feedback, and improvement suggestions.

## Features

* Upload a resume in **PDF format**
* Select a target job role
* Extract resume text automatically
* Analyze the resume using **Google Gemini AI**
* Get an overall resume score
* Identify technical and soft skills
* Shows resume strengths and weaknesses
* Identifies missing skills
* Recommends suitable job roles
* Provides ATS compatibility feedback
* Gives resume improvement suggestions
* Generates a personalized learning roadmap
* Download the analysis as a JSON file

## Tech Stack

| Part           | Tool          |
| -------------- | ------------- |
| UI             | Streamlit     |
| AI Model       | Google Gemini |
| Programming    | Python        |
| PDF Processing | PyMuPDF       |
| AI SDK         | Google GenAI  |
| Output         | JSON          |

## Setup

```bash
# 1. Create a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt
```

Set your Gemini API key:

```text
GEMINI_API_KEY=your_api_key_here
```

Then run:

```bash
streamlit run app.py
```

App opens at http://localhost:8501

## How It Works

1. User uploads a PDF resume.
2. PyMuPDF extracts the text from the resume.
3. User selects the target job role.
4. Resume text is sent to Google Gemini AI.
5. Gemini analyzes the resume and generates structured results.
6. The application displays the resume score, skills, strengths, weaknesses, and recommendations.
7. The user can download the analysis.

## Ideas to Extend

* Add DOCX resume support
* Add job description matching
* Add job-match percentage
* Generate an improved resume
* Add interview question generation
* Add user login and database
* Add resume comparison
* Add downloadable PDF reports
* Add career recommendations
* Deploy on Streamlit Community Cloud
