# Resume Screener - System Architecture

## 🏗️ LangGraph Workflow Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INPUT                               │
│                    LinkedIn Job URL                             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
         ┌───────────────────────────────┐
         │   1. FETCH JOB DESCRIPTION    │
         │   (fetch_job_description)     │
         │                               │
         │ • Scrapes LinkedIn URL        │
         │ • Extracts job posting        │
         │ • Handles errors gracefully   │
         └───────────┬───────────────────┘
                     │
                     ▼
         ┌───────────────────────────────┐
         │  2. RETRIEVE RESUME CONTEXT   │
         │  (retrieve_resume_context)    │
         │                               │
         │ • Loads PDF resume            │
         │ • Chunks text (500 chars)     │
         │ • Creates embeddings          │
         │ • Queries ChromaDB for match  │
         │ • Returns top 4 sections      │
         └───────────┬───────────────────┘
                     │
                     ▼
         ┌───────────────────────────────┐
         │  3. CALCULATE FIT SCORE       │
         │  (calculate_fit_score)        │
         │                               │
         │ • Analyzes skill matches      │
         │ • Scores requirements 0-100   │
         │ • Lists matched skills        │
         │ • Lists missing skills        │
         │ • Evaluates experience fit    │
         └───────────┬───────────────────┘
                     │
                     ▼
         ┌───────────────────────────────┐
         │ 4. GENERATE IMPROVEMENTS      │
         │ (generate_improvement_...     │
         │                               │
         │ • Analyzes gaps               │
         │ • Creates 5-7 suggestions     │
         │ • Explains why each matters   │
         │ • Estimates score impact      │
         └───────────┬───────────────────┘
                     │
                     ▼
         ┌───────────────────────────────┐
         │  5. GENERATE FINAL REPORT     │
         │  (generate_final_report)      │
         │                               │
         │ • Compiles findings           │
         │ • Creates professional report │
         │ • Provides recommendation     │
         └───────────┬───────────────────┘
                     │
                     ▼
        ┌──────────────────────────────────┐
        │      STRUCTURED RESULTS          │
        │  TypedDict: JobScreeningState    │
        │                                  │
        │ ├─ job_url                       │
        │ ├─ job_description               │
        │ ├─ resume_context                │
        │ ├─ fit_score (dict)              │
        │ ├─ improvement_suggestions       │
        │ └─ final_report                  │
        └──────────────────────────────────┘
                     │
                     ▼
        ┌──────────────────────────────────┐
        │        USER OUTPUT               │
        │  • Fit Score: X/100              │
        │  • Skills Analysis               │
        │  • Suggestions with Impact       │
        │  • Professional Report           │
        │  • Recommendation                │
        └──────────────────────────────────┘
```

## 📦 Component Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    LANGGRAPH CORE                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  StateGraph + START/END Nodes                        │  │
│  │  • Defines JobScreeningState (TypedDict)            │  │
│  │  • Creates workflow edges                           │  │
│  │  • Manages state transitions                        │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
  │   LLM LAYER  │ │ VECTOR STORE │ │ SCRAPER TOOL │
  │              │ │              │ │              │
  │ ChatOpenAI   │ │ ChromaDB     │ │ BeautifulSoup│
  │ (gpt-4o-mini)│ │ (Local)      │ │ (Scraping)   │
  │              │ │              │ │              │
  │ • Scoring    │ │ • Embedding  │ │ • Fetch Job  │
  │ • Suggestions│ │ • Retrieval  │ │ • Parse HTML │
  │ • Reports    │ │ • Storage    │ │ • Extract    │
  └──────────────┘ └──────────────┘ └──────────────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
  │ DOCUMENT     │ │ TEXT         │ │ FILE         │
  │ LOADERS      │ │ SPLITTERS    │ │ UTILITIES    │
  │              │ │              │ │              │
  │ PyPDFLoader  │ │ Recursive    │ │ Config       │
  │              │ │ CharTextSplit│ │ Export/Save  │
  │ • Load PDF   │ │              │ │              │
  │ • Process    │ │ • Chunk 500  │ │ • JSON       │
  │ • Extract    │ │ • Overlap 50 │ │ • Markdown   │
  └──────────────┘ └──────────────┘ └──────────────┘
```

## 🔄 Data Flow Diagram

```
                    INPUT: LinkedIn URL
                            │
                            ▼
        ┌─────────────────────────────────┐
        │   scrape_linkedin_job(url)      │  [tools.py]
        │   Extract job description       │
        └──────────────┬──────────────────┘
                       │
                       ▼
        ┌─────────────────────────────────┐
        │   resume.pdf                    │  
        │   Local Document                │
        └──────────────┬──────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
        ▼                             ▼
    PyPDFLoader            RecursiveCharTextSplit
    Load PDF                Split into 500 char chunks
        │                             │
        └──────────────┬──────────────┘
                       │
                       ▼
        ┌─────────────────────────────────┐
        │   OpenAI Embeddings             │
        │   Convert chunks to vectors     │
        └──────────────┬──────────────────┘
                       │
                       ▼
        ┌─────────────────────────────────┐
        │   ChromaDB Vector Store         │
        │   Persist embeddings locally    │
        └──────────────┬──────────────────┘
                       │
        ┌──────────────┴──────────────────────┐
        │                                     │
        ▼                                     ▼
    Job Description              Resume Embeddings
    Similarity Search            Vector Matching
        │                                │
        └──────────────┬─────────────────┘
                       │
                       ▼
        ┌─────────────────────────────────┐
        │   Relevant Resume Context       │
        │   (Top 4 matching sections)     │
        └──────────────┬──────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
        ▼                             ▼
    GPT-4o-mini              GPT-4o-mini
    Fit Score Analysis       Suggestions
    JSON Response            JSON Response
        │                             │
        └──────────────┬──────────────┘
                       │
                       ▼
        ┌─────────────────────────────────┐
        │   GPT-4o-mini                   │
        │   Generate Professional Report  │
        └──────────────┬──────────────────┘
                       │
                       ▼
        ┌─────────────────────────────────┐
        │   Compiled Results              │
        │   JobScreeningState with all    │
        │   fit_score, suggestions, etc   │
        └──────────────┬──────────────────┘
                       │
                       ▼
                    OUTPUT
        ┌─────────────────────────────────┐
        │   Display/Save Results          │
        │ • Console Output                │
        │ • JSON File                     │
        │ • Markdown Report               │
        │ • Action Plan                   │
        └─────────────────────────────────┘
```

## 🔗 File Structure & Dependencies

```
resume_screener/
│
├── app.py                          [MAIN APPLICATION]
│   ├── Imports: langgraph, langchain_openai, retriever, tools
│   ├── Functions:
│   │   ├── fetch_job_description()
│   │   ├── retrieve_resume_context()
│   │   ├── calculate_fit_score()
│   │   ├── generate_improvement_suggestions()
│   │   ├── generate_final_report()
│   │   ├── build_resume_screening_graph()
│   │   └── screen_resume()
│   └── Main entry point
│
├── retriever.py                    [VECTOR DB & RETRIEVAL]
│   ├── Imports: langchain_community, langchain_chroma
│   ├── Functions:
│   │   ├── initialize_resume_db(file_path)
│   │   └── analyze_job_fit(job_description, vectorstore)
│   └── Manages ChromaDB embeddings
│
├── tools.py                        [WEB SCRAPING]
│   ├── Imports: requests, BeautifulSoup
│   ├── Functions:
│   │   └── scrape_linkedin_job(url)
│   └── Extracts job posting HTML
│
├── utilities.py                    [HELPER FUNCTIONS]
│   ├── Classes:
│   │   └── ScreeningResults (save, export, analyze)
│   ├── Functions:
│   │   ├── compare_screenings()
│   │   ├── calculate_improvement_potential()
│   │   ├── create_action_plan()
│   │   └── export_all_formats()
│   └── Advanced analysis features
│
├── config.py                       [CONFIGURATION]
│   ├── Environment variables
│   ├── System prompts
│   ├── validate_config()
│   └── print_config()
│
├── example_usage.py                [EXAMPLE SCRIPT]
│   ├── Interactive user interface
│   ├── Result display formatting
│   ├── Multi-job analysis
│   └── Result saving
│
└── Supporting files
    ├── README.md                   [Full documentation]
    ├── QUICKSTART.md               [Quick start guide]
    ├── requirement.txt             [Dependencies]
    ├── .env.example                [Configuration template]
    └── resume.pdf                  [Your resume]
```

## 🔐 Security & Privacy

```
┌─────────────────────────────────────────────────────────────┐
│                     DATA FLOW SECURITY                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Your Machine (PRIVATE)          Remote Services (EXTERNAL) │
│ ┌─────────────────────┐          ┌──────────────────────┐ │
│ │ • resume.pdf        │          │ • OpenAI API         │ │
│ │ • chroma_db/        │          │ • LinkedIn Jobs      │ │
│ │ • embeddings        │◄────────►│ • Scraping           │ │
│ │ • analysis results  │          │                      │ │
│ └─────────────────────┘          └──────────────────────┘ │
│                                                             │
│ Security Considerations:                                    │
│ ✅ Resume never leaves your machine (ChromaDB is local)    │
│ ✅ Only job descriptions fetched from LinkedIn             │
│ ✅ API calls use your own OpenAI credentials               │
│ ✅ Results stored locally unless explicitly exported       │
│ ⚠️  Review OpenAI's privacy policy                         │
│ ⚠️  Your resume content is sent to OpenAI for analysis     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## ⚡ Performance Considerations

```
Process                          Time        Cost
─────────────────────────────────────────────────
Fetch LinkedIn Job               1-2s        Free
Load & Embed Resume              2-3s        ~$0.01
Retrieve Context                 <1s         Free
Calculate Fit Score              3-5s        ~$0.05
Generate Suggestions             3-5s        ~$0.05
Generate Report                  2-3s        ~$0.02
─────────────────────────────────────────────────
TOTAL                           12-19s       ~$0.13
```

## 🎯 Key Design Patterns

1. **LangGraph StateGraph**
   - Ensures reliable state management
   - Clear workflow visualization
   - Easy debugging and monitoring

2. **Vector Embeddings (ChromaDB)**
   - Semantic search vs keyword matching
   - Finds contextually relevant resume sections
   - Handles complex job requirements

3. **Structured Output (TypedDict)**
   - Type-safe state management
   - Better IDE support and validation
   - Clear data contracts between nodes

4. **Error Handling**
   - Graceful degradation on failures
   - Informative error messages
   - Continues processing when possible

5. **Modular Design**
   - Separate concerns (scraping, retrieval, analysis)
   - Easy to test and extend
   - Reusable components
