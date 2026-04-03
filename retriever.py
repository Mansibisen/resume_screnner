import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_classic.retrievers.contextual_compression import ContextualCompressionRetriever
from langchain_classic.retrievers.document_compressors import EmbeddingsFilter
from config import CHUNK_SIZE, CHUNK_OVERLAP, CHROMA_PERSIST_DIR, CHROMA_COLLECTION_NAME, TOP_K_RESULTS

# 1. Load and Split Resume
def initialize_resume_db(file_path, persist_directory=CHROMA_PERSIST_DIR):
    """Initialize resume database with semantic embeddings using OpenAI embeddings"""
    loader = PyPDFLoader(file_path)
    data = loader.load()

    # Split resume into chunks so the AI can find specific sections
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    chunks = text_splitter.split_documents(data)

    # 2. Create Persistent ChromaDB with Semantic Embeddings (OpenAI)
    # OpenAI embeddings use transformer models that understand semantic meaning
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_directory,
        collection_name=CHROMA_COLLECTION_NAME
    )
    return vectorstore

def analyze_job_fit(job_description, vectorstore):
    """
    Retrieve relevant resume sections using semantic embeddings with compression.
    This uses semantic similarity to find the most relevant resume sections.
    """
    # Get base retriever with semantic search
    base_retriever = vectorstore.as_retriever(
        search_kwargs={"k": TOP_K_RESULTS * 2}  # Get more candidates for filtering
    )
    
    # Add embeddings-based compression for semantic relevance filtering
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    compressor = EmbeddingsFilter(embeddings=embeddings, similarity_threshold=0.76)
    
    # Create a semantic compression retriever
    semantic_retriever = ContextualCompressionRetriever(
        base_compressor=compressor,
        base_retriever=base_retriever
    )
    
    # Retrieve semantically similar resume sections
    relevant_resume_parts = semantic_retriever.invoke(job_description)
    
    # Combine the retrieved text for the LLM
    context = "\n".join([doc.page_content for doc in relevant_resume_parts])
    
    return context