"""
Demo Resume Screener - Test WITHOUT a Resume File or Job URL
Use this to test the pipeline with mock data (completely free!)
"""

from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
import json
from config_local import (
    OLLAMA_BASE_URL, LLM_MODEL, LLM_TEMPERATURE,
    NUM_IMPROVEMENT_SUGGESTIONS, print_config
)
from datetime import datetime

# Mock data for testing
MOCK_JOB_DESCRIPTION = """
Senior Python Developer

Requirements:
- 5+ years Python experience
- Django or FastAPI expertise
- PostgreSQL and Redis experience
- AWS or GCP cloud platform knowledge
- CI/CD and Docker containerization
- RESTful API design
- Unit testing and TDD
- Agile/Scrum experience

Responsibilities:
- Design and build scalable backend systems
- Optimize database performance
- Lead code reviews
- Mentor junior developers
- Collaborate with product team
"""

MOCK_RESUME = """
JOHN DOE
john.doe@email.com | GitHub: github.com/johndoe | LinkedIn: linkedin.com/in/johndoe

PROFESSIONAL SUMMARY
Experienced software engineer with 6 years building scalable web applications. 
Expertise in Python, web frameworks, and cloud technologies. Strong problem solver 
with track record of delivering high-impact projects.

EXPERIENCE

Senior Backend Engineer | TechCorp Inc. | 2022-Present
- Led development of microservices architecture serving 100K+ daily users
- Built RESTful APIs using FastAPI handling 10K+ requests/second
- Optimized PostgreSQL queries reducing response time by 60%
- Implemented Redis caching layer improving performance 3x
- Deployed containerized applications on AWS using Docker and Kubernetes
- Mentored 3 junior developers on best practices

Backend Developer | StartupXYZ | 2019-2022
- Developed Django-based e-commerce platform with 50K+ transactions/month
- Implemented comprehensive unit tests achieving 85% code coverage
- Set up CI/CD pipelines using GitHub Actions
- Worked in Agile/Scrum environment with 2-week sprints
- Optimized database performance with proper indexing strategies

Junior Python Developer | WebSolutions Ltd. | 2018-2019
- Built REST APIs for various client projects
- Wrote clean, maintainable Python code
- Participated in code reviews and pair programming

TECHNICAL SKILLS
Languages: Python, SQL, JavaScript, Bash
Frameworks: Django, FastAPI, Flask
Databases: PostgreSQL, MySQL, MongoDB, Redis
Cloud: AWS (EC2, S3, RDS, Lambda), GCP (Compute Engine)
Tools: Docker, Kubernetes, Git, GitHub Actions, Jenkins
Methodologies: TDD, Agile, Scrum, CI/CD
Other: RESTful API design, Microservices, API Gateway, Message Queues

EDUCATION
Bachelor of Science in Computer Science
University of Technology | 2018

CERTIFICATIONS
- AWS Certified Solutions Architect
- Docker Certified Associate
"""

# Initialize LLM
print(f"\n🚀 Initializing Ollama LLM: {LLM_MODEL}")
print(f"   Base URL: {OLLAMA_BASE_URL}\n")

llm = ChatOllama(
    model=LLM_MODEL,
    base_url=OLLAMA_BASE_URL,
    temperature=LLM_TEMPERATURE,
)

class JobScreeningState(TypedDict):
    job_description: Optional[str]
    resume: Optional[str]
    fit_score: Optional[dict]
    improvement_suggestions: Optional[list]
    final_report: Optional[str]


def calculate_fit_score(state: JobScreeningState) -> JobScreeningState:
    """Calculate acceptance score based on resume and job requirements"""
    print("📊 Calculating fit score...")
    
    scoring_prompt = PromptTemplate.from_template("""
You are an expert recruiter analyzing resume fit for a job position.

JOB DESCRIPTION:
{job_description}

RESUME:
{resume}

Analyze the resume against job requirements. 
Return ONLY valid JSON (no markdown) with this exact structure:
{{
    "overall_score": <0-100>,
    "requirement_scores": {{
        "Python Experience": <0-100>,
        "Django/FastAPI": <0-100>,
        "Database Skills": <0-100>,
        "Cloud Platforms": <0-100>,
        "DevOps/Docker": <0-100>
    }},
    "matched_skills": ["skill1", "skill2", "skill3"],
    "missing_skills": ["skill1", "skill2"],
    "experience_fit": "brief assessment"
}}
""")
    
    prompt = scoring_prompt.format(
        job_description=state['job_description'],
        resume=state['resume']
    )
    
    try:
        response = llm.invoke(prompt)
        response_text = response.content if hasattr(response, 'content') else str(response)
        
        # Try to extract JSON
        fit_score = json.loads(response_text)
        state['fit_score'] = fit_score
        print(f"✅ Score: {fit_score.get('overall_score', 'N/A')}/100\n")
    except json.JSONDecodeError as e:
        print(f"⚠️ JSON parse error: {e}")
        print(f"Response: {response_text[:200]}\n")
        
        # Fallback score
        state['fit_score'] = {
            "overall_score": 70,
            "requirement_scores": {
                "Python Experience": 85,
                "Django/FastAPI": 75,
                "Database Skills": 80,
                "Cloud Platforms": 70,
                "DevOps/Docker": 60
            },
            "matched_skills": ["Python", "FastAPI", "PostgreSQL", "AWS"],
            "missing_skills": ["GCP", "Advanced Kubernetes"],
            "experience_fit": "Strong candidate with relevant experience"
        }
    
    return state


def generate_suggestions(state: JobScreeningState) -> JobScreeningState:
    """Generate improvement suggestions"""
    print("💡 Generating improvement suggestions...")
    
    suggestions_prompt = PromptTemplate.from_template("""
Based on this resume analysis, suggest 5 ways to improve the resume:

Overall Score: {overall_score}/100
Matched Skills: {matched_skills}
Missing Skills: {missing_skills}

Provide 5 numbered, specific suggestions (one per line, no extra formatting).
Just the number and suggestion, nothing else.
""")
    
    prompt = suggestions_prompt.format(
        overall_score=state['fit_score'].get('overall_score', 0),
        matched_skills=', '.join(state['fit_score'].get('matched_skills', [])),
        missing_skills=', '.join(state['fit_score'].get('missing_skills', []))
    )
    
    try:
        response = llm.invoke(prompt)
        suggestions_text = response.content if hasattr(response, 'content') else str(response)
        state['improvement_suggestions'] = [
            line.strip() for line in suggestions_text.split('\n') 
            if line.strip() and any(char.isdigit() for char in line[:3])
        ]
        print(f"✅ Generated {len(state['improvement_suggestions'])} suggestions\n")
    except Exception as e:
        print(f"⚠️ Error: {e}\n")
        state['improvement_suggestions'] = [
            "Add more detail about cloud platform experience",
            "Highlight Kubernetes and orchestration experience",
            "Include more metrics and impact numbers",
            "Add examples of performance optimization work",
            "Show experience with message queues and async processing"
        ]
    
    return state


def generate_final_report(state: JobScreeningState) -> JobScreeningState:
    """Generate comprehensive final report"""
    print("📋 Generating final report...\n")
    
    overall_score = state['fit_score'].get('overall_score', 0)
    
    if overall_score >= 75:
        score_assessment = "🟢 STRONG FIT - You are a competitive candidate"
    elif overall_score >= 60:
        score_assessment = "🟡 MODERATE FIT - Consider improvements below"
    else:
        score_assessment = "🔴 WEAK FIT - Significant gaps exist"
    
    report = f"""
{'='*70}
                    DEMO RESUME SCREENING REPORT
                     (Using Mock Data - No API Keys!)
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
    for skill in state['fit_score'].get('matched_skills', []):
        report += f"   • {skill}\n"
    
    report += f"""
❌ MISSING SKILLS ({len(state['fit_score'].get('missing_skills', []))})
"""
    for skill in state['fit_score'].get('missing_skills', []):
        report += f"   • {skill}\n"
    
    report += """
💡 IMPROVEMENT SUGGESTIONS
"""
    for i, suggestion in enumerate(state['improvement_suggestions'][:5], 1):
        if suggestion.strip():
            report += f"   {i}. {suggestion}\n"
    
    report += f"""
{'='*70}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Using: {LLM_MODEL} via Ollama (No API keys, completely FREE!)
{'='*70}
"""
    
    state['final_report'] = report
    return state


def create_demo_workflow():
    """Create the LangGraph workflow"""
    workflow = StateGraph(JobScreeningState)
    
    workflow.add_node("calculate_score", calculate_fit_score)
    workflow.add_node("generate_suggestions", generate_suggestions)
    workflow.add_node("generate_report", generate_final_report)
    
    workflow.add_edge(START, "calculate_score")
    workflow.add_edge("calculate_score", "generate_suggestions")
    workflow.add_edge("generate_suggestions", "generate_report")
    workflow.add_edge("generate_report", END)
    
    return workflow.compile()


def main():
    """Run demo"""
    print_config()
    
    print("🚀 Demo Resume Screener - Testing Without API Keys!")
    print("="*70)
    print("\n📝 Using mock data:")
    print("   - Job: Senior Python Developer")
    print("   - Resume: Senior Backend Engineer with 6 years experience")
    print("\n⏳ Processing...\n")
    
    # Create and run workflow
    app = create_demo_workflow()
    
    initial_state = {
        "job_description": MOCK_JOB_DESCRIPTION,
        "resume": MOCK_RESUME,
        "fit_score": None,
        "improvement_suggestions": None,
        "final_report": None
    }
    
    try:
        final_state = app.invoke(initial_state)
        print(final_state['final_report'])
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
