"""
Local Resume Retriever using Ollama Embeddings (NO API KEYS!)
Uses free local embeddings instead of OpenAI
"""

import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from config_local import (
    CHUNK_SIZE, CHUNK_OVERLAP, CHROMA_PERSIST_DIR, 
    CHROMA_COLLECTION_NAME, TOP_K_RESULTS, EMBEDDING_MODEL, OLLAMA_BASE_URL
)


def initialize_resume_db_local(file_path, persist_directory=CHROMA_PERSIST_DIR):
    """
    Initialize resume database with FREE local embeddings using Ollama
    No API keys required, runs entirely locally!
    """
    print(f"📖 Loading resume from: {file_path}")
    
    # Check if database already exists
    if os.path.exists(persist_directory):
        print(f"✅ Found existing database at {persist_directory}")
        print(f"   Loading embeddings with {EMBEDDING_MODEL}...")
        
        embeddings = OllamaEmbeddings(
            model=EMBEDDING_MODEL,
            base_url=OLLAMA_BASE_URL
        )
        
        vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=embeddings,
            collection_name=CHROMA_COLLECTION_NAME
        )
        return vectorstore
    
    # Create new database
    print("Creating new resume database...")
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    print(f"   Loaded {len(documents)} pages")
    
    # Split resume into chunks
    print(f"   Splitting into chunks (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    chunks = text_splitter.split_documents(documents)
    print(f"   Created {len(chunks)} chunks")
    
    # Create embeddings with local Ollama model (FREE!)
    print(f"   Generating embeddings with {EMBEDDING_MODEL}...")
    embeddings = OllamaEmbeddings(
        model=EMBEDDING_MODEL,
        base_url=OLLAMA_BASE_URL
    )
    
    # Create ChromaDB with local embeddings
    print(f"   Storing in ChromaDB...")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_directory,
        collection_name=CHROMA_COLLECTION_NAME
    )
    
    print(f"✅ Database created successfully at {persist_directory}")
    return vectorstore


def analyze_job_fit_local(job_description, vectorstore, k=TOP_K_RESULTS):
    """
    Retrieve relevant resume sections using local semantic search
    """
    print(f"🔍 Searching for relevant resume sections (top {k} results)...")
    
    # Simple semantic search (no need for compression with local embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    relevant_docs = retriever.invoke(job_description)
    
    print(f"   Found {len(relevant_docs)} relevant sections")
    
    # Combine the retrieved text
    context = "\n\n---\n\n".join([
        f"[Section {i+1}]\n{doc.page_content}"
        for i, doc in enumerate(relevant_docs)
    ])
    
    return context
