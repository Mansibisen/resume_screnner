#!/usr/bin/env python
"""
Demo Resume Screener - Test with sample data
This script demonstrates the Resume Screener system without requiring a real job URL.
"""

import json
from typing import Dict, Optional


def create_sample_result() -> Dict:
    """Create a sample screening result for demonstration"""
    return {
        "job_url": "https://www.linkedin.com/jobs/view/sample-demo",
        "job_description": """
Senior Software Engineer - Python & AI/ML

We're looking for an experienced Senior Software Engineer with expertise in:
- Python development (5+ years)
- Machine Learning/AI (TensorFlow, PyTorch)
- LLM & Prompt Engineering
- LangChain framework
- AWS (EC2, S3, Lambda)
- Docker & Kubernetes
- CI/CD pipelines (Jenkins, GitHub Actions)
- RESTful API design
- PostgreSQL and Redis
- Leadership & mentoring

Required: BS in Computer Science or equivalent
Preferred: NLP, RAG systems, vector databases (Chroma, Pinecone)
        """,
        "resume_context": """
Senior Python Developer with 6 years of experience. Proficient in:
- Python, JavaScript, Go
- TensorFlow and PyTorch for ML models
- LangChain integration and prompt engineering
- AWS (EC2, S3, RDS, Lambda)
- Docker containerization
- PostgreSQL, MongoDB
- Git, GitHub, Basic CI/CD
- Team lead for 3-person team

Recent Projects:
- Built RAG system for document analysis
- Deployed ML models on AWS
- Led migration to microservices architecture
- Mentored junior developers
        """,
        "fit_score": {
            "overall_score": 82,
            "requirement_scores": {
                "Python Development": 95,
                "Machine Learning/AI": 85,
                "LLM & Prompt Engineering": 88,
                "LangChain": 80,
                "AWS": 90,
                "Docker": 85,
                "Kubernetes": 40,
                "CI/CD": 65,
                "Leadership": 90,
                "Database Systems": 80
            },
            "matched_skills": [
                "Python (6+ years)",
                "Machine Learning (TensorFlow, PyTorch)",
                "LLM & Prompt Engineering",
                "LangChain framework",
                "AWS (EC2, S3, Lambda, RDS)",
                "Docker",
                "PostgreSQL",
                "Leadership & Mentoring",
                "REST APIs",
                "Git & GitHub"
            ],
            "missing_skills": [
                "Kubernetes",
                "Jenkins",
                "Redis",
                "NLP specialization",
                "Vector databases (Pinecone)",
                "GitHub Actions"
            ],
            "experience_fit": "Excellent match. 6 years of Python experience meets the 5+ requirement. " \
                            "Strong ML background with LangChain exposure. AWS experience covers most required services. " \
                            "Leadership experience aligns with senior role expectations."
        },
        "improvement_suggestions": [
            {
                "suggestion": "Add Kubernetes experience to your resume",
                "why_important": "Kubernetes is explicitly listed as required. Many teams use K8s for scaling ML services.",
                "expected_impact": "+8 points"
            },
            {
                "suggestion": "Highlight your RAG system development work",
                "why_important": "RAG systems are mentioned as preferred. This directly matches company tech stack.",
                "expected_impact": "+7 points"
            },
            {
                "suggestion": "Include specific LLM models you've worked with (GPT, Claude, etc.)",
                "why_important": "Demonstrates hands-on LLM experience. Show which models and frameworks.",
                "expected_impact": "+6 points"
            },
            {
                "suggestion": "Add Redis caching examples to your projects",
                "why_important": "Redis is required but not mentioned in your current resume.",
                "expected_impact": "+5 points"
            },
            {
                "suggestion": "Emphasize your GitHub Actions or CI/CD pipeline setup",
                "why_important": "Jenkins and GitHub Actions are required. Show your DevOps capabilities.",
                "expected_impact": "+6 points"
            },
            {
                "suggestion": "Include NLP-specific projects or certifications",
                "why_important": "NLP is listed as preferred. Even a small project would strengthen your profile.",
                "expected_impact": "+4 points"
            },
            {
                "suggestion": "Highlight mentorship achievements with metrics",
                "why_important": "Leadership role needs quantifiable impact. Show growth of team members.",
                "expected_impact": "+5 points"
            }
        ],
        "final_report": """
## Resume Acceptance Score Report

**Overall Fit Score:** 82/100

### Key Findings

**Matched Skills:**
Your resume strongly aligns with most requirements:
- Python (6 years) exceeds the 5+ year requirement
- ML/AI background (TensorFlow, PyTorch) is excellent
- LangChain and LLM experience is relevant and current
- AWS expertise covers required services
- Leadership experience demonstrates seniority

**Missing Skills:**
Several important areas need attention:
- Kubernetes: Important for modern deployment strategies
- Redis: Mentioned but not in your current resume
- CI/CD Tools: Only partial coverage (GitHub, not Jenkins)
- Specialized NLP: General ML is good, but NLP focus would help

**Experience Alignment:**
Your 6 years of senior Python development aligns well with the senior engineer role. 
Leadership of a 3-person team matches expectations for mentoring responsibilities.

### Recommendations

**🟢 STRONG CANDIDATE - Highly Recommended to Apply!**

With an 82/100 score, you're a strong match for this position. Your core skills 
(Python, ML, LangChain, AWS) are exactly what they need. The gaps are learnable 
and not dealbreakers.

### Action Items for Improvement

**High Priority (Do before applying):**
1. Add a line about Kubernetes or container orchestration
2. Mention specific RAG projects prominently
3. Highlight one LLM project with results

**Medium Priority (Mention in cover letter if not on resume):**
4. Redis experience (if you have any)
5. Any GitHub Actions or CI/CD setup you've done

**Nice to Have:**
6. NLP certifications or projects
7. Metrics on mentorship success

### Estimated Improvement
If you implement the top 3 suggestions, your score could reach 93/100, making you 
an exceptional candidate. Even implementing 1-2 would push you to 88-90.

### Interview Talking Points
1. Your RAG system: Discuss challenges and solutions
2. LangChain integration: Show understanding of prompt engineering
3. ML deployment: Talk about moving models to production
4. Leadership: Mention specific examples of mentoring
5. AWS architecture: Explain a complex deployment

### Conclusion
You're a great fit for this role. Your background in Python, ML, and AWS, combined 
with leadership experience, makes you competitive. The missing Kubernetes experience 
is not a dealbreaker, especially if you show eagerness to learn.

**Recommendation:** ✅ APPLY - Your 82/100 score indicates you'll likely get an interview."""
    }


def display_sample_results():
    """Display sample screening results"""
    result = create_sample_result()
    
    print("\n" + "="*70)
    print("  🎓 SAMPLE RESUME SCREENING RESULTS")
    print("="*70)
    
    print("\n📌 Job Role: Senior Software Engineer - Python & AI/ML")
    print(f"📍 Fit Score: {result['fit_score']['overall_score']}/100")
    
    print("\n✅ MATCHED SKILLS:")
    for skill in result['fit_score']['matched_skills'][:5]:
        print(f"   • {skill}")
    print(f"   ... and {len(result['fit_score']['matched_skills'])-5} more")
    
    print("\n❌ MISSING SKILLS:")
    for skill in result['fit_score']['missing_skills'][:3]:
        print(f"   • {skill}")
    
    print("\n💡 TOP SUGGESTIONS:")
    for i, sugg in enumerate(result['improvement_suggestions'][:3], 1):
        print(f"\n   {i}. {sugg['suggestion']}")
        print(f"      Impact: {sugg['expected_impact']}")
    
    print("\n" + "="*70)
    print("  📊 FULL REPORT")
    print("="*70)
    print(result['final_report'])
    
    return result


def export_sample_results():
    """Export sample results to files"""
    result = create_sample_result()
    
    # Save as JSON
    with open('sample_screening_result.json', 'w') as f:
        json.dump(result, f, indent=2)
    print("✅ Saved: sample_screening_result.json")
    
    # Save as Markdown
    md_content = f"""# Sample Resume Screening Report

**Fit Score:** {result['fit_score']['overall_score']}/100

## Matched Skills
{chr(10).join(f"- {s}" for s in result['fit_score']['matched_skills'])}

## Missing Skills
{chr(10).join(f"- {s}" for s in result['fit_score']['missing_skills'])}

## Improvement Suggestions

{chr(10).join(f"**{i}. {s['suggestion']}**{chr(10)}{s['why_important']}{chr(10)}Expected Impact: {s['expected_impact']}{chr(10)}" for i, s in enumerate(result['improvement_suggestions'], 1))}

## Full Report

{result['final_report']}
"""
    
    with open('sample_screening_report.md', 'w') as f:
        f.write(md_content)
    print("✅ Saved: sample_screening_report.md")


def main():
    """Main entry point"""
    print("\n" + "="*70)
    print("  🎯 RESUME SCREENER - SAMPLE DEMONSTRATION")
    print("="*70)
    print("""
This demo shows what a real resume screening analysis looks like.

Features demonstrated:
✓ Fit Score (82/100)
✓ Skill matching and gaps
✓ Actionable improvement suggestions
✓ Professional comprehensive report
✓ Career guidance

The actual system will:
1. Accept a LinkedIn job URL
2. Scrape the job description
3. Analyze your real resume (resume.pdf)
4. Generate similar results
5. Provide personalized suggestions
    """)
    
    input("Press Enter to see sample results...")
    
    result = display_sample_results()
    
    print("\n\nWould you like to:")
    print("1. Export results to files (JSON + Markdown)")
    print("2. See configuration options")
    print("3. Learn how to run with a real job URL")
    print("0. Exit")
    
    choice = input("\nEnter your choice (0-3): ").strip()
    
    if choice == "1":
        export_sample_results()
        print("\n✅ Sample results exported!")
        print("   • sample_screening_result.json")
        print("   • sample_screening_report.md")
    
    elif choice == "2":
        print("\n" + "="*70)
        print("Configuration options available in config.py:")
        print("="*70)
        print("""
        • LLM_MODEL: Which OpenAI model to use
        • CHUNK_SIZE: Size of resume sections for analysis
        • TOP_K_RESULTS: Number of resume sections to retrieve
        • Scoring thresholds and other parameters
        
        Copy .env.example to .env and customize as needed.
        """)
    
    elif choice == "3":
        print("\n" + "="*70)
        print("To run with a real LinkedIn job URL:")
        print("="*70)
        print("""
        1. Ensure you have resume.pdf in the current directory
        2. Set your OpenAI API key:
           export OPENAI_API_KEY="sk-..."
        
        3. Run the interactive screener:
           python example_usage.py
        
        4. Or use directly:
           python -c "from app import screen_resume; \\
                      result = screen_resume('https://...')"
        """)
    
    print("\nThank you for checking out Resume Screener! 👋\n")


if __name__ == "__main__":
    main()
