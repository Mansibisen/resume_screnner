"""
Simple Flask-based frontend for Resume Screener
No additional dependencies beyond what's already in use
"""

from flask import Flask, render_template, request, jsonify
from typing import Optional
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
import json
import os
from config_local import (
    OLLAMA_BASE_URL, LLM_MODEL, LLM_TEMPERATURE, 
    EMBEDDING_MODEL, NUM_IMPROVEMENT_SUGGESTIONS
)
from retriever_local import initialize_resume_db_local, analyze_job_fit_local
from tools import scrape_linkedin_job
from datetime import datetime

# Initialize Flask app
app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')

# Initialize LLM
llm = ChatOllama(
    model=LLM_MODEL,
    base_url=OLLAMA_BASE_URL,
    temperature=LLM_TEMPERATURE,
)

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_resume():
    """API endpoint for resume analysis"""
    try:
        data = request.json
        job_url = data.get('job_url', '').strip()
        job_description = data.get('job_description', '').strip()
        
        # Validation - resume is already in RAG system
        if not job_url and not job_description:
            return jsonify({'error': 'Please provide either a job URL or description'}), 400
        
        # Step 1: Get job description
        if job_url:
            job_desc = scrape_linkedin_job(job_url)
        else:
            job_desc = job_description
        
        # Step 2: Use RAG system to retrieve resume context (resume already loaded)
        vectorstore = initialize_resume_db_local(None)  # Load from existing RAG
        resume_context = analyze_job_fit_local(job_desc, vectorstore)
        
        # Step 3: Calculate fit score
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

Provide numbered suggestions that are concrete and implementable. Format as a simple list.
""")
        
        suggestions_text = suggestions_prompt.format(
            num_suggestions=NUM_IMPROVEMENT_SUGGESTIONS,
            job_description=job_desc,
            fit_score=json.dumps(fit_score),
            matched_skills=", ".join(fit_score.get("matched_skills", [])),
            missing_skills=", ".join(fit_score.get("missing_skills", []))
        )
        
        suggestions_response = llm.invoke(suggestions_text)
        suggestions = suggestions_response.content
        
        return jsonify({
            'success': True,
            'fit_score': fit_score,
            'suggestions': suggestions,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except json.JSONDecodeError as e:
        return jsonify({'error': f'Error parsing AI response: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Analysis error: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Check if the API is running and Ollama is available"""
    try:
        # Try to ping the LLM
        test_response = llm.invoke("test")
        return jsonify({'status': 'healthy', 'model': LLM_MODEL})
    except Exception as e:
        return jsonify({
            'status': 'error', 
            'message': 'Ollama not available',
            'error': str(e)
        }), 503

if __name__ == '__main__':
    print(f"🚀 Starting Resume Screener Frontend")
    print(f"📍 Using LLM: {LLM_MODEL}")
    print(f"🔗 Ollama URL: {OLLAMA_BASE_URL}")
    print(f"🌐 Open http://localhost:5000 in your browser")
    app.run(debug=True, port=5000)
