from pydantic import BaseModel, Field
from typing import List, Optional

class Attempt(BaseModel):
    """
    Represents a single Wordle guess and its feedback.
    """
    word: str = Field(..., min_length=5, max_length=5, description="The 5-letter word guessed.")
    feedback: str = Field(..., min_length=5, max_length=5, description="The 5-letter feedback string (G=Green, Y=Yellow, B=Black).")

class SolveRequest(BaseModel):
    """
    The request payload containing all previous attempts.
    """
    attempts: List[Attempt] = Field(..., description="List of previous attempts.")

class SolveResponse(BaseModel):
    """
    The successful response payload.
    """
    status: str = Field(default="success", description="Response status.")
    message: Optional[str] = Field(default=None, description="Optional message.")
    remaining_words_count: int = Field(..., description="Number of possible words left.")
    optimal_guess: Optional[str] = Field(default=None, description="The suggested next optimal guess.")
    remaining_words: List[str] = Field(..., description="A truncated list of remaining valid words.")
