"""
Configuration file for Resume Screener LangGraph application.
Customize parameters here to adjust the behavior of the system.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# LLM CONFIGURATION
# ============================================================================

# OpenAI Model to use
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")

# Temperature for LLM responses (0 = deterministic, 1 = creative)
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0"))

# API Key (loaded from environment)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ============================================================================
# RESUME PROCESSING CONFIGURATION
# ============================================================================

# Path to your resume PDF file
RESUME_FILE_PATH = os.getenv("RESUME_FILE_PATH", "resume.pdf")

# ChromaDB configuration
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "my_resume")

# Text splitting configuration
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))

# Retrieval configuration
TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "4"))  # Number of resume chunks to retrieve

# ============================================================================
# SCORING CONFIGURATION
# ============================================================================

# Minimum score thresholds
MIN_SCORE_STRONG_CANDIDATE = int(os.getenv("MIN_SCORE_STRONG", "75"))
MIN_SCORE_MODERATE_CANDIDATE = int(os.getenv("MIN_SCORE_MODERATE", "60"))

# Number of improvement suggestions to generate
NUM_IMPROVEMENT_SUGGESTIONS = int(os.getenv("NUM_SUGGESTIONS", "7"))

# ============================================================================
# JOB SCRAPING CONFIGURATION
# ============================================================================

# Request timeout for web scraping (in seconds)
SCRAPING_TIMEOUT = int(os.getenv("SCRAPING_TIMEOUT", "10"))

# User agent for requests
USER_AGENT = os.getenv("USER_AGENT", 
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

# ============================================================================
# OUTPUT CONFIGURATION
# ============================================================================

# Save results to JSON
SAVE_RESULTS = os.getenv("SAVE_RESULTS", "false").lower() == "true"
RESULTS_OUTPUT_DIR = os.getenv("RESULTS_OUTPUT_DIR", "./screening_results")

# Verbosity level: 'debug', 'info', 'warning'
LOG_LEVEL = os.getenv("LOG_LEVEL", "info")

# ============================================================================
# ADVANCED CONFIGURATION
# ============================================================================

# Enable caching for API calls
ENABLE_CACHING = os.getenv("ENABLE_CACHING", "false").lower() == "true"

# Maximum retries for API calls
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

# ============================================================================
# PROMPT TEMPLATES
# ============================================================================

SCORING_SYSTEM_PROMPT = """
You are an expert recruiter and resume analyst. Your task is to carefully analyze 
how well a candidate's resume matches job requirements. Be objective and thorough 
in your analysis. Consider both hard skills and soft skills, experience level, 
and overall fit for the position.
"""

SUGGESTIONS_SYSTEM_PROMPT = """
You are a professional career coach specializing in resume optimization. Your goal 
is to provide specific, actionable, and realistic suggestions to improve a candidate's 
resume for a particular job position. Focus on practical changes that will have the 
most impact on the candidate's chances of getting an interview.
"""

REPORT_SYSTEM_PROMPT = """
You are a professional report writer. Compile the resume screening analysis into 
a clear, professional, and actionable report. Include specific findings, recommendations, 
and next steps. Make it suitable for sharing with the candidate.
"""


# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def validate_config():
    """Validate that all required configuration is present"""
    errors = []
    
    if not OPENAI_API_KEY:
        errors.append("OPENAI_API_KEY environment variable not set")
    
    if not os.path.exists(RESUME_FILE_PATH):
        errors.append(f"Resume file not found at {RESUME_FILE_PATH}")
    
    if CHUNK_SIZE <= 0:
        errors.append("CHUNK_SIZE must be positive")
    
    if TOP_K_RESULTS <= 0:
        errors.append("TOP_K_RESULTS must be positive")
    
    return errors


def print_config():
    """Print current configuration"""
    print("\n" + "="*60)
    print("📋 RESUME SCREENER CONFIGURATION")
    print("="*60)
    print(f"\n🤖 LLM Settings:")
    print(f"   Model: {LLM_MODEL}")
    print(f"   Temperature: {LLM_TEMPERATURE}")
    
    print(f"\n📄 Resume Processing:")
    print(f"   Resume File: {RESUME_FILE_PATH}")
    print(f"   Chunk Size: {CHUNK_SIZE}")
    print(f"   Top K Results: {TOP_K_RESULTS}")
    print(f"   ChromaDB Dir: {CHROMA_PERSIST_DIR}")
    
    print(f"\n🎯 Scoring:")
    print(f"   Strong Threshold: {MIN_SCORE_STRONG_CANDIDATE}/100")
    print(f"   Moderate Threshold: {MIN_SCORE_MODERATE_CANDIDATE}/100")
    print(f"   Suggestions Count: {NUM_IMPROVEMENT_SUGGESTIONS}")
    
    print(f"\n🌐 Web Scraping:")
    print(f"   Timeout: {SCRAPING_TIMEOUT}s")
    
    print(f"\n💾 Output:")
    print(f"   Save Results: {SAVE_RESULTS}")
    print(f"   Output Dir: {RESULTS_OUTPUT_DIR}")
    print(f"   Log Level: {LOG_LEVEL}")
    print("="*60 + "\n")


if __name__ == "__main__":
    # Test configuration
    errors = validate_config()
    if errors:
        print("❌ Configuration Errors:")
        for error in errors:
            print(f"   • {error}")
    else:
        print("✅ Configuration is valid!")
    
    print_config()
