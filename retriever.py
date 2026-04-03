import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from config import CHUNK_SIZE,CHUNK_OVERLAP,CHROMA_PERSIST_DIR, CHROMA_COLLECTION_NAME, TOP_K_RESULTS

# 1. Load and Split Resume
def initialize_resume_db(file_path, persist_directory=CHROMA_PERSIST_DIR):
    loader = PyPDFLoader(file_path)
    data = loader.load()

    # Split resume into chunks so the AI can find specific sections
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    chunks = text_splitter.split_documents(data)

    # 2. Create Persistent ChromaDB
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_directory,
        collection_name=CHROMA_COLLECTION_NAME
    )
    return vectorstore

def analyze_job_fit(job_description, vectorstore):
    # This finds the top 4 most relevant parts of your resume for this specific job
    retriever = vectorstore.as_retriever(search_kwargs={"k": TOP_K_RESULTS})
    relevant_resume_parts = retriever.invoke(job_description)
    
    # Combine the retrieved text for the LLM
    context = "\n".join([doc.page_content for doc in relevant_resume_parts])
    
    return context