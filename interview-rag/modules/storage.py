import sqlite3
from sqlite3 import Connection, Error
import os
from datetime import datetime
from typing import List, Tuple, Optional

DB_PATH = os.path.join("data", "transcripts.db")

def init_db() -> Connection:
    """Initialize the database connection and create tables if they don't exist."""
    try:
        os.makedirs("data", exist_ok=True)
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        c = conn.cursor()
        
        # Create transcripts table with indexes
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS transcripts (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                date TEXT NOT NULL,
                text TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """
        )
        
        # Create indexes for better query performance
        c.execute("CREATE INDEX IF NOT EXISTS idx_user_id ON transcripts(user_id)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_date ON transcripts(date)")
        
        conn.commit()
        return conn
    except Error as e:
        raise Exception(f"Database initialization failed: {str(e)}")

def add_transcript(conn: Connection, user_id: str, text: str) -> str:
    """Add a new transcript to the database."""
    try:
        tid = f"{user_id}_{int(datetime.utcnow().timestamp())}"
        date = datetime.utcnow().isoformat()
        c = conn.cursor()
        c.execute(
            "INSERT INTO transcripts (id, user_id, date, text) VALUES (?, ?, ?, ?)",
            (tid, user_id, date, text)
        )
        conn.commit()
        return tid
    except Error as e:
        conn.rollback()
        raise Exception(f"Failed to add transcript: {str(e)}")

def get_all_transcripts(conn: Connection, user_id: str) -> List[Tuple[str, str]]:
    """Get all transcripts for a user."""
    try:
        c = conn.cursor()
        c.execute(
            "SELECT id, date FROM transcripts WHERE user_id = ? ORDER BY date DESC",
            (user_id,)
        )
        return c.fetchall()
    except Error as e:
        raise Exception(f"Failed to get transcripts: {str(e)}")

def delete_transcript(conn: Connection, transcript_id: str, user_id: str) -> None:
    """Delete a transcript from the database."""
    try:
        c = conn.cursor()
        # Verify ownership before deleting
        c.execute(
            "SELECT 1 FROM transcripts WHERE id = ? AND user_id = ?",
            (transcript_id, user_id)
        )
        if not c.fetchone():
            raise Exception("Transcript not found or unauthorized")
            
        c.execute("DELETE FROM transcripts WHERE id = ?", (transcript_id,))
        conn.commit()
    except Error as e:
        conn.rollback()
        raise Exception(f"Failed to delete transcript: {str(e)}")

def get_transcript(conn: Connection, transcript_id: str, user_id: str) -> Optional[Tuple[str, str, str]]:
    """Get a specific transcript by ID."""
    try:
        c = conn.cursor()
        c.execute(
            "SELECT id, date, text FROM transcripts WHERE id = ? AND user_id = ?",
            (transcript_id, user_id)
        )
        return c.fetchone()
    except Error as e:
        raise Exception(f"Failed to get transcript: {str(e)}")