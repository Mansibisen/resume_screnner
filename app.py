from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
import json
from config import OPENAI_API_KEY,LLM_MODEL,LLM_TEMPERATURE,RESUME_FILE_PATH
from resume_screener.retriever import initialize_resume_db, analyze_job_fit
from resume_screener.tools import scrape_linkedin_job

# Initialize LLM
llm = ChatOpenAI(model=LLM_MODEL, temperature=LLM_TEMPERATURE)

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
    except Exception as e:
        print(f"⚠️ Error fetching job description: {e}")
        state['job_description'] = ""
    
    print(f"   Fetched job description (length={len(state['job_description'])} characters)")
    print(f"   Job description preview: {state['job_description'][:200]}...")
    return state


def retrieve_resume_context(state: JobScreeningState) -> JobScreeningState:
    """Retrieve relevant resume sections based on job description"""
    print("🔍 Analyzing resume for job fit...")
    
    # Initialize or load the resume database
    vectorstore = initialize_resume_db(RESUME_FILE_PATH)
    
    # Get relevant resume sections
    resume_context = analyze_job_fit(state['job_description'], vectorstore)
    state['resume_context'] = resume_context
    print(f"   Retrieved relevant resume context (length={len(resume_context)} characters)")
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

Analyze the resume against job requirements and provide a detailed scoring in JSON format.
Score each key requirement on a scale of 0-100 based on how well the resume matches.
Return ONLY a valid JSON object (no markdown, no extra text) with this structure:
{{
    "overall_score": <0-100>,
    "requirement_scores": {{
        "<requirement_name>": <0-100>,
        ...
    }},
    "matched_skills": ["skill1", "skill2", ...],
    "missing_skills": ["skill1", "skill2", ...],
    "experience_fit": "<brief description>"
}}
""")
    
    prompt = scoring_prompt.format(
        job_description=state['job_description'],
        resume_context=state['resume_context']
    )
    
    try:
        response = llm.invoke(prompt)
        fit_score = json.loads(response.content)
        state['fit_score'] = fit_score
    except json.JSONDecodeError as e:
        print(f"⚠️ Error parsing JSON response: {e}")
        state['fit_score'] = {
            "overall_score": 0,
            "requirement_scores": {},
            "matched_skills": [],
            "missing_skills": [],
            "experience_fit": "Could not calculate score"
        }
    
    return state


def generate_improvement_suggestions(state: JobScreeningState) -> JobScreeningState:
    """Generate specific suggestions to improve resume for the job"""
    print("💡 Generating improvement suggestions...")
    
    suggestions_prompt = PromptTemplate.from_template("""
You are a career coach helping a candidate improve their resume for a specific job position.

JOB DESCRIPTION:
{job_description}

CURRENT RESUME SECTIONS:
{resume_context}

CURRENT FIT ANALYSIS:
- Overall Score: {overall_score}/100
- Matched Skills: {matched_skills}
- Missing Skills: {missing_skills}
- Experience Fit: {experience_fit}

Based on this analysis, provide 5-7 specific, actionable suggestions to improve the resume.
For each suggestion, explain:
1. What to add/change
2. Why it's important for this job
3. How it will improve the fit score

Format your response as a JSON array of objects with keys: "suggestion", "why_important", "expected_impact"
Return ONLY valid JSON (no markdown, no extra text).
""")
    
    prompt = suggestions_prompt.format(
        job_description=state['job_description'],
        resume_context=state['resume_context'],
        overall_score=state['fit_score'].get('overall_score', 0),
        matched_skills=", ".join(state['fit_score'].get('matched_skills', [])),
        missing_skills=", ".join(state['fit_score'].get('missing_skills', [])),
        experience_fit=state['fit_score'].get('experience_fit', '')
    )
    
    try:
        response = llm.invoke(prompt)
        suggestions = json.loads(response.content)
        state['improvement_suggestions'] = suggestions
    except json.JSONDecodeError as e:
        print(f"⚠️ Error parsing suggestions: {e}")
        state['improvement_suggestions'] = []
    
    return state


def generate_final_report(state: JobScreeningState) -> JobScreeningState:
    """Generate a comprehensive final report"""
    print("📋 Generating final report...")
    
    report_prompt = PromptTemplate.from_template("""
You are creating a professional resume evaluation report.

Generate a comprehensive report with the following sections:

## Resume Acceptance Score Report

**Overall Fit Score:** {overall_score}/100

**Key Findings:**
- Matched Skills: {matched_skills}
- Missing Skills: {missing_skills}
- Experience Alignment: {experience_fit}

**Improvement Action Items:**
{suggestions_text}

**Recommendation:**
Based on the analysis, provide a brief recommendation on whether to apply for this position.

Keep the report professional and actionable.
""")
    
    suggestions_text = "\n".join([
        f"- {s.get('suggestion', '')}: {s.get('why_important', '')}"
        for s in state['improvement_suggestions']
    ])
    
    prompt = report_prompt.format(
        overall_score=state['fit_score'].get('overall_score', 0),
        matched_skills=", ".join(state['fit_score'].get('matched_skills', [])),
        missing_skills=", ".join(state['fit_score'].get('missing_skills', [])),
        experience_fit=state['fit_score'].get('experience_fit', ''),
        suggestions_text=suggestions_text
    )
    
    response = llm.invoke(prompt)
    state['final_report'] = response.content
    
    return state


def build_resume_screening_graph():
    """Build the LangGraph workflow for resume screening"""
    graph_builder = StateGraph(JobScreeningState)
    
    # Add nodes
    graph_builder.add_node("fetch_job", fetch_job_description)
    graph_builder.add_node("retrieve_resume", retrieve_resume_context)
    graph_builder.add_node("calculate_score", calculate_fit_score)
    graph_builder.add_node("generate_suggestions", generate_improvement_suggestions)
    graph_builder.add_node("generate_report", generate_final_report)
    
    # Add edges
    graph_builder.add_edge(START, "fetch_job")
    graph_builder.add_edge("fetch_job", "retrieve_resume")
    graph_builder.add_edge("retrieve_resume", "calculate_score")
    graph_builder.add_edge("calculate_score", "generate_suggestions")
    graph_builder.add_edge("generate_suggestions", "generate_report")
    graph_builder.add_edge("generate_report", END)
    
    return graph_builder.compile()


def screen_resume(job_url: str):
    """Main function to screen resume against a job posting"""
    graph = build_resume_screening_graph()
    
    initial_state = {
        "job_url": job_url,
        "job_description": None,
        "resume_context": None,
        "fit_score": None,
        "improvement_suggestions": None,
        "final_report": None
    }
    
    print("\n" + "="*60)
    print("🚀 Starting Resume Screening Analysis")
    print("="*60 + "\n")
    
    result = graph.invoke(initial_state)
    
    return result


# Example usage
if __name__ == "__main__":
    # Example job URL (replace with actual LinkedIn URL)
    job_url = input("Enter the job URL: ")
    result = screen_resume(job_url)
    
    print("\n" + "="*60)
    print("📊 RESUME SCREENING RESULTS")
    print("="*60)
    print(f"\n✅ Fit Score: {result['fit_score']['overall_score']}/100")
    print(f"\n✨ Improvement Suggestions:")
    for i, suggestion in enumerate(result['improvement_suggestions'], 1):
        print(f"\n{i}. {suggestion.get('suggestion', '')}")
        print(f"   Why: {suggestion.get('why_important', '')}")
    print(f"\n📋 Full Report:\n{result['final_report']}")