"""
Resume Screener using Local LLM (Ollama) - NO API KEYS REQUIRED!
This is a free alternative that runs completely locally on your machine
"""

from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_core.prompts import PromptTemplate
import json
from config_local import (
    OLLAMA_BASE_URL, LLM_MODEL, LLM_TEMPERATURE, 
    RESUME_FILE_PATH, EMBEDDING_MODEL, NUM_IMPROVEMENT_SUGGESTIONS,
    SAVE_RESULTS, RESULTS_OUTPUT_DIR, print_config
)
from retriever_local import initialize_resume_db_local, analyze_job_fit_local
from tools import scrape_linkedin_job
import os
from datetime import datetime

# Initialize LLM with Ollama (completely local and free!)
print(f"\n🚀 Initializing Ollama LLM: {LLM_MODEL}")
print(f"   Base URL: {OLLAMA_BASE_URL}")
print("   ⏳ First run may take a moment as the model loads...\n")

llm = ChatOllama(
    model=LLM_MODEL,
    base_url=OLLAMA_BASE_URL,
    temperature=LLM_TEMPERATURE,
)

# State schema for the graph
class JobScreeningState(TypedDict):
    job_url: str
    job_description: Optional[str]
    resume_context: Optional[str]
    fit_score: Optional[dict]
    improvement_suggestions: Optional[list]
    final_report: Optional[str]


def fetch_job_description(state: JobScreeningState) -> JobScreeningState:
    """Fetch job description from the provided URL"""
    print(f"📄 Fetching job description from: {state['job_url']}")
    
    try:
        job_description = scrape_linkedin_job(state['job_url'])
        state['job_description'] = job_description
        print(f"✅ Successfully fetched job description ({len(job_description)} chars)")
    except Exception as e:
        print(f"⚠️ Error fetching job description: {e}")
        state['job_description'] = ""
    
    print(f"   Job description preview: {state['job_description'][:200]}...")
    return state


def retrieve_resume_context(state: JobScreeningState) -> JobScreeningState:
    """Retrieve relevant resume sections based on job description"""
    print("🔍 Retrieving relevant resume sections...")
    
    # Initialize or load the resume database with local embeddings
    vectorstore = initialize_resume_db_local(RESUME_FILE_PATH)
    
    # Get relevant resume sections
    resume_context = analyze_job_fit_local(state['job_description'], vectorstore)
    state['resume_context'] = resume_context
    print(f"✅ Retrieved resume context ({len(resume_context)} chars)")

    print(f"   Resume context preview: {resume_context[:200]}...")
    
    return state


def calculate_fit_score(state: JobScreeningState) -> JobScreeningState:
    """Calculate acceptance score based on resume and job requirements"""
    print("📊 Calculating fit score...")
    
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
        job_description=state['job_description'],
        resume_context=state['resume_context']
    )
    
    try:
        response = llm.invoke(prompt)
        # Extract JSON from response
        response_text = response.content if hasattr(response, 'content') else str(response)
        
        # Try to parse JSON
        fit_score = json.loads(response_text)
        state['fit_score'] = fit_score
        print(f"✅ Overall Score: {fit_score.get('overall_score', 'N/A')}/100")
    except json.JSONDecodeError as e:
        print(f"⚠️ Error parsing JSON: {e}")
        print(f"   Response was: {response_text[:200]}")
        state['fit_score'] = {
            "overall_score": 0,
            "requirement_scores": {},
            "matched_skills": [],
            "missing_skills": [],
            "experience_fit": "Could not calculate score"
        }
    
    return state


def generate_suggestions(state: JobScreeningState) -> JobScreeningState:
    """Generate improvement suggestions"""
    print("💡 Generating improvement suggestions...")
    
    suggestions_prompt = PromptTemplate.from_template("""
Based on this resume fit analysis, provide {num_suggestions} specific, actionable suggestions to improve the resume:

OVERALL SCORE: {overall_score}/100

MATCHED SKILLS: {matched_skills}

MISSING SKILLS: {missing_skills}

JOB REQUIREMENTS: {job_description}

Provide {num_suggestions} numbered suggestions, each with:
- The action to take
- Why it matters
- Expected impact

Format as a numbered list.
""")
    
    prompt = suggestions_prompt.format(
        num_suggestions=NUM_IMPROVEMENT_SUGGESTIONS,
        overall_score=state['fit_score'].get('overall_score', 0),
        matched_skills=', '.join(state['fit_score'].get('matched_skills', [])),
        missing_skills=', '.join(state['fit_score'].get('missing_skills', [])),
        job_description=state['job_description'][:1000]
    )
    
    try:
        response = llm.invoke(prompt)
        suggestions_text = response.content if hasattr(response, 'content') else str(response)
        state['improvement_suggestions'] = suggestions_text.split('\n')
        print(f"✅ Generated {len(state['improvement_suggestions'])} suggestions")
    except Exception as e:
        print(f"⚠️ Error generating suggestions: {e}")
        state['improvement_suggestions'] = ["Could not generate suggestions"]
    
    return state


def generate_final_report(state: JobScreeningState) -> JobScreeningState:
    """Generate comprehensive final report"""
    print("📋 Generating final report...")
    
    overall_score = state['fit_score'].get('overall_score', 0)
    
    if overall_score >= 75:
        score_assessment = "🟢 STRONG FIT - You are a competitive candidate for this role"
    elif overall_score >= 60:
        score_assessment = "🟡 MODERATE FIT - You have relevant skills but consider improvements"
    else:
        score_assessment = "🔴 WEAK FIT - Significant skill gaps exist for this role"
    
    report = f"""
{'='*70}
                    RESUME SCREENING ANALYSIS REPORT
{'='*70}

📊 OVERALL FIT SCORE: {overall_score}/100
   {score_assessment}

🎯 REQUIREMENT BREAKDOWN:
"""
    
    for req, score in state['fit_score'].get('requirement_scores', {}).items():
        bar_length = int(score / 10)
        bar = '█' * bar_length + '░' * (10 - bar_length)
        report += f"   {req}: [{bar}] {score}/100\n"
    
    report += f"""
✅ MATCHED SKILLS ({len(state['fit_score'].get('matched_skills', []))})
"""
    for skill in state['fit_score'].get('matched_skills', [])[:10]:
        report += f"   • {skill}\n"
    
    report += f"""
❌ MISSING SKILLS ({len(state['fit_score'].get('missing_skills', []))})
"""
    for skill in state['fit_score'].get('missing_skills', [])[:10]:
        report += f"   • {skill}\n"
    
    report += """
💡 IMPROVEMENT SUGGESTIONS
"""
    for i, suggestion in enumerate(state['improvement_suggestions'][:NUM_IMPROVEMENT_SUGGESTIONS], 1):
        if suggestion.strip():
            report += f"   {i}. {suggestion}\n"
    
    report += f"""
{'='*70}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*70}
"""
    
    state['final_report'] = report
    print("✅ Final report generated")
    
    return state


def save_report(state: JobScreeningState) -> JobScreeningState:
    """Save the report to a file"""
    if SAVE_RESULTS and state['final_report']:
        os.makedirs(RESULTS_OUTPUT_DIR, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{RESULTS_OUTPUT_DIR}/resume_screening_{timestamp}.txt"
        
        with open(filename, 'w') as f:
            f.write(state['final_report'])
        
        print(f"💾 Report saved to: {filename}")
    
    return state


def create_screening_workflow():
    """Create the LangGraph workflow for resume screening"""
    workflow = StateGraph(JobScreeningState)
    
    # Add nodes
    workflow.add_node("fetch_job", fetch_job_description)
    workflow.add_node("retrieve_resume", retrieve_resume_context)
    workflow.add_node("calculate_score", calculate_fit_score)
    workflow.add_node("generate_suggestions", generate_suggestions)
    workflow.add_node("generate_report", generate_final_report)
    workflow.add_node("save_report", save_report)
    
    # Add edges
    workflow.add_edge(START, "fetch_job")
    workflow.add_edge("fetch_job", "retrieve_resume")
    workflow.add_edge("retrieve_resume", "calculate_score")
    workflow.add_edge("calculate_score", "generate_suggestions")
    workflow.add_edge("generate_suggestions", "generate_report")
    workflow.add_edge("generate_report", "save_report")
    workflow.add_edge("save_report", END)
    
    return workflow.compile()


def main():
    """Main entry point"""
    print_config()
    
    print("🚀 Starting Resume Screening Analysis")
    print("="*70)
    
    # Get job URL from user
    job_url = input("\n🔗 Enter the job URL (LinkedIn, Indeed, etc.): ").strip()
    
    if not job_url:
        print("❌ URL cannot be empty!")
        return
    
    # Create and run workflow
    app = create_screening_workflow()
    
    print("\n⏳ Processing... This may take a moment.\n")
    
    initial_state = {
        "job_url": job_url,
        "job_description": None,
        "resume_context": None,
        "fit_score": None,
        "improvement_suggestions": None,
        "final_report": None
    }
    
    try:
        final_state = app.invoke(initial_state)
        
        # Print final report
        print("\n" + final_state['final_report'])
        
    except Exception as e:
        print(f"\n❌ Error during screening: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
