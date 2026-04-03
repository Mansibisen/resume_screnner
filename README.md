# Resume Screener with LangGraph

A powerful LangGraph-based system that analyzes your resume against job postings and provides an acceptance score along with actionable improvement suggestions.

## Features

✨ **Key Capabilities:**
- **Job URL Analysis**: Automatically fetches job descriptions from LinkedIn URLs
- **Resume Fit Scoring**: Calculates detailed acceptance scores (0-100) based on requirement matching
- **Skill Analysis**: Identifies matched and missing skills
- **Improvement Suggestions**: Provides 5-7 specific, actionable recommendations to improve your resume
- **Comprehensive Reports**: Generates professional evaluation reports
- **LangGraph Workflow**: Uses a state machine for reliable, step-by-step processing

## Architecture

The system uses a 5-stage LangGraph workflow:

```
START
  ↓
[1] Fetch Job Description → Scrapes LinkedIn job posting
  ↓
[2] Retrieve Resume Context → Finds relevant resume sections using vector embeddings
  ↓
[3] Calculate Fit Score → Analyzes resume against requirements
  ↓
[4] Generate Suggestions → Creates improvement recommendations
  ↓
[5] Generate Final Report → Compiles comprehensive evaluation
  ↓
END
```

## Installation

1. **Install Dependencies**:
```bash
pip install -r requirement.txt
```

Required packages:
- `langgraph`: Graph-based workflow orchestration
- `langchain`, `langchain-core`, `langchain-community`: LLM framework
- `langchain_openai`: OpenAI integration
- `langchain_chroma`: Vector database
- `langchain_text_splitters`: Document chunking
- `requests`, `bs4`: Web scraping
- `python-dotenv`: Environment variables

2. **Set Up OpenAI API**:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

3. **Prepare Your Resume**:
- Place your resume as `resume.pdf` in the project directory
- The system will automatically embed it into a ChromaDB vector store

## Usage

### Run the Resume Screener

```bash
python -m resume_screener.app
```

You'll be prompted to enter a LinkedIn job URL:
```
Enter the job URL: https://www.linkedin.com/jobs/view/1234567890
```

### Output

The system provides:

1. **Fit Score** (0-100): Overall compatibility with the job

2. **Requirement Scores**: Individual scores for each job requirement

3. **Skill Analysis**:
   - Matched skills from your resume
   - Missing skills you should add

4. **Improvement Suggestions** with:
   - Specific actions to take
   - Why each improvement matters
   - Expected impact on fit score

5. **Professional Report**: A comprehensive summary with recommendation

## Example Output

```
============================================================
🚀 Starting Resume Screening Analysis
============================================================

📄 Fetching job description from: https://www.linkedin.com/jobs/view/...
🔍 Analyzing resume for job fit...
📊 Calculating fit score...
💡 Generating improvement suggestions...
📋 Generating final report...

============================================================
📊 RESUME SCREENING RESULTS
============================================================

✅ Fit Score: 78/100

✨ Improvement Suggestions:

1. Add AWS certification: Highlight your AWS experience
   Why: Critical for this cloud infrastructure role
   Expected Impact: +8 points

2. Emphasize leadership experience: Include specific team lead examples
   Why: This role requires senior-level responsibilities
   Expected Impact: +6 points

[... more suggestions ...]

📋 Full Report:
## Resume Acceptance Score Report

**Overall Fit Score:** 78/100

**Key Findings:**
- Matched Skills: Python, AWS, Docker, Kubernetes
- Missing Skills: Terraform, Jenkins, Prometheus
...
```

## How It Works

### 1. Job Description Fetching
- Scrapes LinkedIn job posting using BeautifulSoup
- Handles multiple HTML structures for robustness
- Extracts full job description and requirements

### 2. Resume Analysis
- Loads your PDF resume using `PyPDFLoader`
- Chunks it into 500-character segments with overlap
- Converts to embeddings using OpenAI's embedding model
- Stores in ChromaDB vector database

### 3. Relevance Retrieval
- Queries the vector database with the job description
- Retrieves the 4 most relevant resume sections
- Combines them for analysis

### 4. Fit Scoring
- Uses GPT-4o-mini to analyze resume vs. requirements
- Scores each requirement on a 0-100 scale
- Identifies matched and missing skills
- Evaluates overall experience fit

### 5. Improvement Suggestions
- Analyzes gaps between resume and job requirements
- Generates 5-7 specific, actionable recommendations
- Explains why each suggestion matters
- Estimates impact on overall fit score

### 6. Final Report
- Compiles all findings into a professional report
- Provides clear recommendation on whether to apply
- Actionable insights for resume improvement

## State Management

The system uses a `JobScreeningState` TypedDict to maintain state throughout the workflow:

```python
class JobScreeningState(TypedDict):
    job_url: str                           # Input: LinkedIn job URL
    job_description: Optional[str]         # Scraped job posting
    resume_context: Optional[str]          # Relevant resume sections
    fit_score: Optional[dict]              # Scoring analysis
    improvement_suggestions: Optional[list] # Recommendations
    final_report: Optional[str]            # Compiled report
```

## Configuration

### Customize Chunk Size
Edit `retriever.py`:
```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,  # Adjust as needed
    chunk_overlap=50
)
```

### Adjust Retrieval Results
Edit `retriever.py`:
```python
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})  # Top 4 results
```

### Change LLM Model
Edit `app.py`:
```python
llm = ChatOpenAI(model="gpt-4", temperature=0)  # Use gpt-4 instead
```

## Advanced Usage

### Programmatic Usage

```python
from resume_screener.app import screen_resume

# Screen resume for a job
result = screen_resume("https://www.linkedin.com/jobs/view/1234567890")

# Access results
print(f"Fit Score: {result['fit_score']['overall_score']}/100")
print(f"Suggestions: {result['improvement_suggestions']}")
print(f"Report: {result['final_report']}")
```

### Custom Analysis

```python
from resume_screener.retriever import initialize_resume_db, analyze_job_fit
from resume_screener.tools import scrape_linkedin_job

# Load resume
vectorstore = initialize_resume_db("resume.pdf")

# Get job description
job_desc = scrape_linkedin_job(job_url)

# Get relevant resume sections
context = analyze_job_fit(job_desc, vectorstore)
```

## Troubleshooting

**Issue**: "Could not retrieve job description"
- **Solution**: Ensure LinkedIn URL is correct and publicly accessible
- Try viewing the job in your browser first
- Some jobs may require authentication

**Issue**: "ChromaDB connection error"
- **Solution**: Delete the `chroma_db` folder and reinitialize:
  ```bash
  rm -rf chroma_db
  python -m resume_screener.app
  ```

**Issue**: "OpenAI API key not found"
- **Solution**: Set your API key:
  ```bash
  export OPENAI_API_KEY="sk-..."
  ```

**Issue**: "Embedding model error"
- **Solution**: Ensure you have credits on your OpenAI account
- Check API key permissions

## Best Practices

1. **Update Your Resume**: Keep your resume PDF current before running analyses

2. **Multiple Jobs**: Run the screener for multiple similar jobs to see common gaps

3. **Track Improvements**: Note suggestions across jobs to identify priority improvements

4. **Tailor Context**: Add more detail to your resume for roles you're most interested in

5. **Review Suggestions**: Not all AI suggestions may be valid - use professional judgment

## Future Enhancements

- 📧 Email integration to analyze job postings directly
- 🔄 Batch processing multiple jobs
- 📊 Dashboard for tracking scores over time
- 🤖 Resume auto-improvement using AI
- 💾 Save/compare multiple job analyses
- 🌐 Support for other job boards (Indeed, Glassdoor, etc.)

## Support

For issues or questions:
1. Check the troubleshooting section
2. Verify all dependencies are installed: `pip install -r requirement.txt`
3. Ensure your OpenAI API key is valid
4. Check that your resume PDF exists in the project directory

## License

This project is part of the RAG Agent suite for resume optimization and career matching.
