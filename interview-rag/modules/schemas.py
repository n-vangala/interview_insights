from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class UploadSchema(BaseModel):
    user_id: str = Field(..., min_length=1, description="User identifier")
    text: str = Field(..., min_length=1, description="Transcript text")

    @validator('text')
    def text_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Text cannot be empty or whitespace only')
        return v

class QuerySchema(BaseModel):
    user_id: str = Field(..., min_length=1, description="User identifier")
    question: str = Field(..., min_length=1, description="Question to ask about the transcripts")

    @validator('question')
    def question_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Question cannot be empty or whitespace only')
        return v

class TranscriptResponse(BaseModel):
    transcript_id: Optional[str] = None
    date: Optional[str] = None
    answer: Optional[str] = None
    status: str = Field(..., description="Status of the operation")

class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Error message")
    status_code: int = Field(..., description="HTTP status code")