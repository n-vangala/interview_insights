from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from modules.storage import init_db, add_transcript, get_all_transcripts, delete_transcript
from modules.vectorstore import load_or_init, add_transcript_chunks, delete_transcript_vectors
from modules.schemas import UploadSchema, QuerySchema, TranscriptResponse, ErrorResponse
import os
from typing import List

# Initialize FastAPI app and middleware
app = FastAPI(
    title="Interview RAG API",
    description="API for storing and querying interview transcripts using RAG",
    version="1.0.0"
)

# Configure CORS for production
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)

# Initialize persistence layers
db_conn = init_db()
vectordb = load_or_init()

@app.post("/upload", response_model=TranscriptResponse, responses={400: {"model": ErrorResponse}})
async def upload(data: UploadSchema):
    try:
        if len(data.text.strip()) == 0:
            raise HTTPException(status_code=400, detail="Transcript text cannot be empty")
        
        # Store transcript and update FAISS index
        tid = add_transcript(db_conn, data.user_id, data.text)
        add_transcript_chunks(vectordb, tid, data.text)
        return {"transcript_id": tid, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query", response_model=TranscriptResponse, responses={400: {"model": ErrorResponse}})
async def query(data: QuerySchema):
    try:
        if len(data.question.strip()) == 0:
            raise HTTPException(status_code=400, detail="Question cannot be empty")
            
        # Retrieve relevant chunks and run RAG
        retriever = vectordb.as_retriever(search_kwargs={"k": 5})
        docs = retriever.get_relevant_documents(data.question)
        
        # Assemble prompt and call LLM
        from modules.vectorstore import run_llm_chain
        answer = run_llm_chain(docs, data.question)
        return {"answer": answer, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/transcripts", response_model=List[TranscriptResponse])
async def list_transcripts(user_id: str):
    try:
        items = get_all_transcripts(db_conn, user_id)
        return [{"id": tid, "date": date, "status": "success"} for tid, date in items]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/transcripts/{transcript_id}", response_model=TranscriptResponse)
async def delete_transcript_endpoint(transcript_id: str, user_id: str):
    try:
        delete_transcript(db_conn, transcript_id, user_id)
        delete_transcript_vectors(vectordb, transcript_id)
        return {"transcript_id": transcript_id, "status": "deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))