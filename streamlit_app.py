"""
Resume Screener Frontend - Streamlit Web Interface
A simple, intuitive frontend for analyzing resume fit against job postings
"""

import streamlit as st
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
import json
import os
from datetime import datetime
from config_local import (
    OLLAMA_BASE_URL, LLM_MODEL, LLM_TEMPERATURE, 
    RESUME_FILE_PATH, EMBEDDING_MODEL, NUM_IMPROVEMENT_SUGGESTIONS,
    SAVE_RESULTS, RESULTS_OUTPUT_DIR
)
from retriever_local import initialize_resume_db_local, analyze_job_fit_local
from tools import scrape_linkedin_job
import tempfile

# Page configuration
st.set_page_config(
    page_title="Resume Screener",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .score-high {
        color: #28a745;
        font-weight: bold;
    }
    .score-medium {
        color: #ffc107;
        font-weight: bold;
    }
    .score-low {
        color: #dc3545;
        font-weight: bold;
    }
    .skill-matched {
        background-color: #d4edda;
        color: #155724;
        padding: 5px 10px;
        border-radius: 5px;
        margin: 3px;
        display: inline-block;
    }
    .skill-missing {
        background-color: #f8d7da;
        color: #721c24;
        padding: 5px 10px;
        border-radius: 5px;
        margin: 3px;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'resume_text' not in st.session_state:
    st.session_state.resume_text = ""
if 'results' not in st.session_state:
    st.session_state.results = None
if 'analyzing' not in st.session_state:
    st.session_state.analyzing = False

# Header
st.title("📄 Resume Screener")
st.markdown("Analyze how well your resume matches job postings using AI-powered evaluation")

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    st.info(f"Using model: **{LLM_MODEL}** via Ollama")
    st.info(f"Ollama URL: `{OLLAMA_BASE_URL}`")
    
    with st.expander("About This Tool", expanded=True):
        st.markdown("""
        This resume screener:
        - 📊 Calculates a fit score (0-100)
        - 🎯 Identifies matched and missing skills
        - 💡 Provides actionable improvement suggestions
        - 📈 Analyzes experience fit
        
        Powered by LangGraph and Ollama
        """)

# Main content
# Main content
col1, col2 = st.columns([1, 1])

with col1:
    st.header("✅ Resume Status")
    st.success("📄 Your resume is already loaded in the system")
    st.info("The RAG system has access to your complete resume. Just provide a job posting below to start the analysis.")
    st.divider()
    
    st.header("🔗 Job Posting")
    
    # Job input options
    job_input_method = st.radio(
        "Choose how to provide the job posting:",
        ["Paste URL", "Paste Description"],
        label_visibility="collapsed"
    )
    
    if job_input_method == "Paste URL":
        job_url = st.text_input(
            "Enter job posting URL (LinkedIn):",
            placeholder="https://www.linkedin.com/jobs/view/..."
        )
        job_description = ""
    else:
        job_url = ""
        job_description = st.text_area(
            "Job description text:",
            height=300,
            placeholder="Paste the job description here..."
        )

# Analysis section
st.divider()
st.header("🚀 Analysis")

col1, col2, col3 = st.columns(3)
with col1:
    analyze_button = st.button(
        "🔍 Analyze Resume",
        use_container_width=True,
        type="primary"
    )
with col2:
    st.empty()
with col3:
    st.empty()

# Analysis logic
if analyze_button:
    if not job_url and not job_description:
        st.error("❌ Please provide either a job posting URL or description!")
    else:
        # Initialize LLM
        llm = ChatOllama(
            model=LLM_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=LLM_TEMPERATURE,
        )
        
        with st.spinner("⏳ Analyzing your resume..."):
            try:
                # Step 1: Get job description
                if job_url:
                    with st.spinner("📄 Fetching job description..."):
                        job_desc = scrape_linkedin_job(job_url)
                else:
                    job_desc = job_description
                
                # Step 2: Retrieve resume context (resume already in RAG)
                with st.spinner("🔍 Analyzing resume..."):
                    vectorstore = initialize_resume_db_local(None)
                    resume_context = analyze_job_fit_local(job_desc, vectorstore)
                
                # Step 3: Calculate fit score
                with st.spinner("📊 Calculating fit score..."):
                    scoring_prompt = PromptTemplate.from_template("""
You are an expert recruiter analyzing resume fit for a job position.

JOB DESCRIPTION:
{job_description}

RELEVANT RESUME SECTIONS:
{resume_context}

Analyze the resume against job requirements and provide scoring.
Return ONLY a valid JSON object with this structure:
{{
    "overall_score": <0-100>,
    "requirement_scores": {{
        "<requirement_name>": <0-100>
    }},
    "matched_skills": ["skill1", "skill2"],
    "missing_skills": ["skill1", "skill2"],
    "experience_fit": "brief description"
}}
""")
                    
                    prompt = scoring_prompt.format(
                        job_description=job_desc,
                        resume_context=resume_context
                    )
                    
                    response = llm.invoke(prompt)
                    fit_score = json.loads(response.content)
                
                # Step 4: Generate improvement suggestions
                with st.spinner("💡 Generating improvement suggestions..."):
                    suggestions_prompt = PromptTemplate.from_template("""
Based on this job description and resume analysis, provide {num_suggestions} specific, actionable improvements to make the resume more attractive for this role.

JOB DESCRIPTION:
{job_description}

FIT SCORE ANALYSIS:
{fit_score}

MATCHED SKILLS:
{matched_skills}

MISSING SKILLS:
{missing_skills}

Provide numbered suggestions that are concrete and implementable.
""")
                    
                    suggestions_prompt_text = suggestions_prompt.format(
                        num_suggestions=NUM_IMPROVEMENT_SUGGESTIONS,
                        job_description=job_desc,
                        fit_score=json.dumps(fit_score),
                        matched_skills=", ".join(fit_score.get("matched_skills", [])),
                        missing_skills=", ".join(fit_score.get("missing_skills", []))
                    )
                    
                    suggestions_response = llm.invoke(suggestions_prompt_text)
                    suggestions_text = suggestions_response.content
                
                st.session_state.results = {
                    "fit_score": fit_score,
                    "suggestions": suggestions_text,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.success("✅ Analysis complete!")
                
            except Exception as e:
                st.error(f"❌ Error during analysis: {str(e)}")
                st.info("Make sure Ollama is running and the model is available.")

# Display results
if st.session_state.results:
    st.divider()
    st.header("📊 Results")
    
    results = st.session_state.results
    fit_score = results["fit_score"]
    overall_score = fit_score.get("overall_score", 0)
    
    # Score display
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Overall score with color coding
        if overall_score >= 75:
            score_class = "score-high"
            status = "🟢 Excellent Match"
        elif overall_score >= 50:
            score_class = "score-medium"
            status = "🟡 Good Match"
        else:
            score_class = "score-low"
            status = "🔴 Fair Match"
        
        st.markdown(f"""
        <div class="metric-card">
            <h3>Overall Fit Score</h3>
            <h1 class="{score_class}">{overall_score}%</h1>
            <p>{status}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        matched_skills = fit_score.get("matched_skills", [])
        st.markdown(f"""
        <div class="metric-card">
            <h3>Matched Skills</h3>
            <h1 style="color: #28a745;">{len(matched_skills)}</h1>
            <p>Skills you have</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        missing_skills = fit_score.get("missing_skills", [])
        st.markdown(f"""
        <div class="metric-card">
            <h3>Missing Skills</h3>
            <h1 style="color: #dc3545;">{len(missing_skills)}</h1>
            <p>Skills to acquire</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Detailed breakdown
    st.subheader("✅ Matched Skills")
    matched_html = " ".join([f'<span class="skill-matched">{skill}</span>' for skill in matched_skills])
    st.markdown(matched_html, unsafe_allow_html=True)
    
    st.subheader("❌ Missing Skills")
    missing_html = " ".join([f'<span class="skill-missing">{skill}</span>' for skill in missing_skills])
    st.markdown(missing_html, unsafe_allow_html=True)
    
    # Experience fit
    st.subheader("📈 Experience Fit")
    st.info(fit_score.get("experience_fit", "No data available"))
    
    # Requirement scores
    if fit_score.get("requirement_scores"):
        st.subheader("🎯 Requirement Scores")
        requirement_scores = fit_score["requirement_scores"]
        
        for requirement, score in requirement_scores.items():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{requirement}**")
            with col2:
                if score >= 75:
                    st.success(f"{score}%")
                elif score >= 50:
                    st.warning(f"{score}%")
                else:
                    st.error(f"{score}%")
            
            progress_color = "green" if score >= 75 else ("orange" if score >= 50 else "red")
            st.progress(score / 100, text=f"{score}%")
    
    # Improvement suggestions
    st.subheader("💡 Improvement Suggestions")
    st.markdown(results["suggestions"])
    
    # Download results
    st.divider()
    results_text = f"""
RESUME SCREENING RESULTS
Generated: {results['timestamp']}

OVERALL FIT SCORE: {overall_score}%

MATCHED SKILLS:
{', '.join(matched_skills)}

MISSING SKILLS:
{', '.join(missing_skills)}

EXPERIENCE FIT:
{fit_score.get('experience_fit', 'N/A')}

IMPROVEMENT SUGGESTIONS:
{results['suggestions']}
"""
    
    st.download_button(
        label="📥 Download Results",
        data=results_text,
        file_name=f"resume_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain"
    )

# Footer
st.divider()
st.markdown("""
---
**Resume Screener** | Powered by LangGraph & Ollama | Built with Streamlit
""")
