# Resume Screener with LangGraph & Flask

A powerful AI-driven system that analyzes your resume against job postings and provides an acceptance score along with actionable improvement suggestions. Features a modern web interface built with Flask and a RAG-based backend using LangGraph.

<figure align="center">
  <img src="docs/screenshots/01_main_dashboard.png" alt="Main Dashboard">
  <figcaption>Main Dashboard - Enter job posting details here</figcaption>
</figure>

## Features

✨ **Key Capabilities:**
- **Web-Based Interface**: Clean, intuitive UI for easy resume analysis
- **Job URL Analysis**: Automatically fetches job descriptions from LinkedIn URLs or paste custom job descriptions
- **Resume Fit Scoring**: Calculates detailed acceptance scores (0-100) based on requirement matching
- **Skill Analysis**: Identifies matched and missing skills
- **Requirement Breakdown**: Individual scores for each job requirement
- **Improvement Suggestions**: Provides specific, actionable recommendations to improve your resume
- **Export Results**: Download analysis results as formatted text files
- **RAG System**: Uses vector embeddings to find relevant resume sections
- **LangGraph Workflow**: State machine-based processing for reliable analysis

## Architecture

The system uses a Flask web server with a RAG-based backend:

```
┌─────────────────────────────────────────┐
│     Flask Web Interface (Port 5000)      │
│  • Input Panel: Job URL / Description   │
│  • Results Panel: Analysis Visualization │
└──────────┬──────────────────────────────┘
           │
           ↓
┌─────────────────────────────────────────┐
│       Backend API (/api/analyze)        │
└──────────┬──────────────────────────────┘
           │
    ┌──────┴───────┬─────────────┐
    ↓              ↓             ↓
[Job Scraper]  [RAG Retriever] [LLM Analyzer]
    │              │             │
    └──────┬───────┴─────────────┘
           ↓
┌─────────────────────────────────────────┐
│   Analysis Results & Suggestions        │
│  • Overall Fit Score (0-100)            │
│  • Matched/Missing Skills               │
│  • Requirement Scores                   │
│  • Improvement Recommendations          │
└─────────────────────────────────────────┘
```

### Workflow Steps:

1. **Job Fetching**: Scrapes LinkedIn job postings or accepts custom descriptions
2. **Resume Retrieval**: Uses vector embeddings to find relevant resume sections from ChromaDB
3. **Fit Analysis**: LLM analyzes resume against job requirements
4. **Scoring**: Calculates overall and requirement-specific scores
5. **Recommendations**: Generates actionable improvement suggestions
6. **Display**: Results rendered in the web UI with visual indicators

## Installation

### Prerequisites
- Python 3.8+
- Ollama running locally (with a model like `llama2`, `mistral`, or `neural-chat`)
- Your resume as a PDF file

### Setup Steps

1. **Clone the Repository**:
```bash
cd resume_screener
```

2. **Create a Virtual Environment**:
```bash
python3 -m venv myenv
source myenv/bin/activate  # On Windows: myenv\Scripts\activate
```

3. **Install Dependencies**:
```bash
pip install -r requirement.txt
```

Required packages:
- `flask`: Web framework
- `langchain`, `langchain-core`: LLM framework
- `langchain_ollama`: Ollama integration
- `langchain-chroma`: Vector database for RAG
- `langchain_text_splitters`: Document chunking
- `requests`, `bs4`: Web scraping
- `python-dotenv`: Environment variables
- `streamlit`: Alternative UI option

4. **Set Up Ollama**:
```bash
# Make sure Ollama is running
ollama serve

# In another terminal, pull a model
ollama pull llama2  # or mistral, neural-chat, etc.
```

5. **Configure Environment**:
Edit `config_local.py` to set:
```python
OLLAMA_BASE_URL = "http://localhost:11434"  # Ollama server URL
LLM_MODEL = "llama2"                        # Your chosen model
EMBEDDING_MODEL = "nomic-embed-text"        # For embeddings
```

6. **Prepare Your Resume**:
- Place your resume as `resume.pdf` in the `resume_screener` directory
- The system will automatically process it and create a ChromaDB vector store

## Usage

### Option 1: Web Interface (Recommended)

1. **Start the Flask Application**:
```bash
python flask_app.py
```

2. **Open the Web Interface**:
   - Navigate to `http://localhost:5000` in your browser
   - You should see the Resume Screener interface

3. **Analyze Your Resume**:
   - Your resume is already loaded and ready
   - Enter either a LinkedIn job URL or paste a job description
   - Click "Analyze Resume Against Job"
   - Wait for the analysis to complete (usually 30-60 seconds)

4. **Review Results**:
   - See your overall fit score
   - View matched and missing skills
   - Review requirement-specific scores
   - Read improvement suggestions
   - Download results as a text file

### Option 2: Command Line (CLI)

```bash
python app.py
```

Then follow the prompts to enter a job URL or description.

### Option 3: Streamlit Interface

```bash
streamlit run streamlit_app.py
```

A Streamlit-based alternative UI with the same functionality.

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

## Screenshots & Demo

### Web Interface Overview

#### 1. Main Dashboard

The main dashboard shows:
- **Header**: "Resume Screener" title with description
- **Left Panel**: Resume status indicator and job posting input area
  - Shows "Your resume is already loaded in the system"
  - Job URL input field with LinkedIn placeholder
  - OR divider
  - Job description textarea for custom input
  - "Analyze Resume Against Job" button (disabled until input provided)
- **Right Panel**: Results panel (empty until analysis runs)

<div align="center">
  <img src="static/01_main_dashboard%20PM.png" alt="Main Dashboard" width="800">
  <p><em>Main Dashboard - Job score </em></p>
</div>

<div align="center">
  <img src="static/02_analysis_loading%20PM.png" alt="Analysis Loading" width="800">
  <p><em>Resume report </em></p>
</div>

<div align="center">
  <img src="static/03_analysis_results%20PM.png" alt="Analysis Results" width="800">
  <p><em>Complete analysis results with all suggestions</em></p>
</div>

---

#### 2. Analysis in Progress

Shows:
- Loading overlay with spinner
- Message: "Analyzing your resume against the job posting..."
- Analyze button disabled during processing


---

#### 3. Results Display

Displays comprehensive analysis results:
- **Score Card Section**:
  - Overall Fit Score (0-100%) with color-coded status
  - Matched Skills count
  - Missing Skills count
- **Skills Section**:
  - ✅ Matched Skills (green tags)
  - ❌ Missing Skills (red tags)
- **Experience Fit**: Summary of experience alignment
- **Requirement Scores**: Individual requirement breakdowns with progress bars
- **Improvement Suggestions**: Numbered list of actionable recommendations

---

#### 4. Downloaded Report

Example of downloaded text file showing:
- Timestamp and analysis parameters
- Overall fit score
- Matched and missing skills list
- Experience fit assessment
- Requirement scores table
- Improvement suggestions

---

### Color Scheme & Visual Design

The interface uses:
- **Primary Colors**: Purple gradient (#667eea to #764ba2)
- **Success**: Green (#28a745) for matched items
- **Warning**: Yellow (#ffc107) for moderate scores
- **Danger**: Red (#dc3545) for missing items
- **Score Ratings**:
  - 🟢 Excellent Match: 75%+
  - 🟡 Good Match: 50-74%
  - 🔴 Fair Match: Below 50%

---

##  Screenshots

### Prerequisites
- Flask app running on `http://localhost:5000`
- Resume already loaded in the system

### Steps
1. **Main Dashboard**: 
   - Open the app, don't enter any job info
   - Take full-page screenshot

2. **Analysis Loading**:
   - Paste a job description
   - Click analyze and immediately screenshot before loading completes

3. **Results Display**:
   - Wait for analysis to complete
   - Scroll to show all results sections
   - Take full-page screenshot

4. **Download Report**:
   - Click "Download Results" button
   - Open the generated `.txt` file
   - Screenshot showing the report format

### Screenshot Storage
Create a `docs/screenshots/` directory and save images as:
- `01_main_dashboard.png`
- `02_analysis_loading.png`
- `03_analysis_results.png`
- `04_download_report.png`

Update the image paths in this README after adding screenshots.
## How It Works

### 1. Web Request Flow
- User enters job URL or description in the Flask web interface
- Frontend sends API request to `/api/analyze` endpoint
- Flask backend processes the request

### 2. Job Description Fetching
- If URL is provided: System scrapes LinkedIn job posting using BeautifulSoup
- If description is provided: Uses the custom text directly
- Extracts full job description and requirements

### 3. Resume Context Retrieval (RAG)
- Your pre-loaded resume is stored in ChromaDB vector database
- System converts job description to embeddings
- Performs semantic search to find 4 most relevant resume sections
- Combines relevant sections for analysis

### 4. LLM-Based Analysis
- Ollama LLM analyzes resume context against job requirements
- Scores each requirement on a 0-100 scale using structured prompts
- Identifies matched and missing skills
- Evaluates overall experience fit
- Generates JSON response with structured data

### 5. Improvement Suggestions
- LLM generates specific, actionable recommendations
- Based on gaps between resume and job requirements
- Provides concrete steps to improve candidacy
- Returns suggestions as formatted text

### 6. Results Rendering
- Flask API returns JSON with fit score and suggestions
- Frontend JavaScript displays results dynamically
- Shows visualizations: score cards, skill tags, progress bars
- User can download analysis as text file

## Configuration

### Ollama Settings
Edit `config_local.py`:
```python
# Ollama Server Configuration
OLLAMA_BASE_URL = "http://localhost:11434"

# Model Selection (common options)
LLM_MODEL = "llama2"            # Good general model
# LLM_MODEL = "mistral"         # Faster and more accurate
# LLM_MODEL = "neural-chat"     # Optimized for chat

# Embedding Model
EMBEDDING_MODEL = "nomic-embed-text"  # For semantic search

# LLM Parameters
LLM_TEMPERATURE = 0.3  # Lower = more consistent; Higher = more creative

# Suggestion Count
NUM_IMPROVEMENT_SUGGESTIONS = 5
```

### Vector Database
- **Type**: ChromaDB (persistent local storage)
- **Location**: `chroma_db/` directory
- **Persistence**: Automatically saved on disk
- **Refresh**: Delete `chroma_db/` to force re-index

## Advanced Usage

### Programmatic API Usage

```python
import requests

# Call the API directly
response = requests.post('http://localhost:5000/api/analyze', json={
    'job_url': 'https://www.linkedin.com/jobs/view/...',
    # OR use job_description instead:
    # 'job_description': 'Senior Python Developer...'
})

result = response.json()
print(f"Fit Score: {result['fit_score']['overall_score']}/100")
print(f"Suggestions: {result['suggestions']}")
```

### Custom Resume Loading

```python
from retriever_local import initialize_resume_db_local

# Load a specific resume PDF
vectorstore = initialize_resume_db_local('path/to/your/resume.pdf')
```

## Troubleshooting

**Issue**: "Network error" or "Ollama not available"
- **Solution**: Ensure Ollama is running:
  ```bash
  # Terminal 1: Start Ollama
  ollama serve
  
  # Terminal 2: Verify it's running
  curl http://localhost:11434/api/tags
  ```

**Issue**: Model not found
- **Solution**: Pull the required model:
  ```bash
  ollama pull llama2
  ollama pull mistral
  ollama pull neural-chat
  ```

**Issue**: "ChromaDB connection error"
- **Solution**: Reinitialize the database:
  ```bash
  rm -rf chroma_db/
  python flask_app.py  # Will recreate on first run
  ```

**Issue**: Slow analysis (>2 minutes)
- **Solution**: Try a faster model:
  ```bash
  ollama pull mistral  # Generally faster than llama2
  # Update config_local.py: LLM_MODEL = "mistral"
  ```

**Issue**: Analysis results don't match resume
- **Solution**: Verify resume is properly indexed:
  1. Delete `chroma_db/` folder
  2. Ensure `resume.pdf` is in the correct location
  3. Restart Flask app
  4. Check console for embedding messages

## Best Practices

1. **Keep Resume Updated**: Your PDF should be current before analyses

2. **Use Specific Job Descriptions**: More detail = more accurate analysis

3. **Try Multiple Models**: Different models may provide different insights:
   - `llama2`: Best accuracy
   - `mistral`: Faster, good balance
   - `neural-chat`: Optimized for conversation

4. **Review Suggestions**: AI suggestions are helpful but require professional judgment

5. **Track Patterns**: Run multiple analyses to identify common skill gaps

6. **Batch Processing**: Analyze multiple similar roles to prioritize improvements

## Future Enhancements

- 📧 Email integration for direct job posting analysis
- 🔄 Batch processing for multiple job postings
- 📊 Dashboard showing score trends over time
- 💾 Save/compare multiple analyses
- 🌐 Support for Indeed, Glassdoor, and other job boards
- 🎯 Resume optimization suggestions with AI rewrites
- 📈 Skills gap tracking and learning path recommendations

## Project Structure

```
resume_screener/
├── flask_app.py              # Main Flask web server
├── app.py                    # CLI version
├── streamlit_app.py          # Streamlit UI version
├── config_local.py           # Local configuration
├── retriever_local.py        # RAG system (ChromaDB + embeddings)
├── tools.py                  # Utility functions (LinkedIn scraper)
├── templates/
│   └── index.html           # Web UI HTML
├── static/
│   ├── app.js               # Frontend JavaScript
│   └── style.css            # Styling
├── chroma_db/               # Vector database (auto-created)
├── myenv/                   # Python virtual environment
└── README.md                # This file
```

## Support

For issues:
1. Check Ollama is running: `curl http://localhost:11434/api/tags`
2. Verify dependencies: `pip list | grep -E "langchain|chromadb|flask"`
3. Check logs in Flask console for detailed error messages
4. Try a different model if results are inconsistent
5. Delete `chroma_db/` and restart if database issues persist

## License

This project is part of the RAG Agent suite for resume optimization and career matching.
