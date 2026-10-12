"""Wordle solver package providing core algorithms and GUI interface."""

from wordle_solver.wordleSolverBackend import (
    ERROR,
    MAX_RETRIES,
    SUCCESS,
    WORD_LENGTH,
    TileFeedback,
    WordleSolver,
    getDictionary,
    isInDictionary,
    processWordleAttempt,
    selectWord,
    validateAttempt,
    wordsLeft,
)

__all__ = [
    "ERROR",
    "MAX_RETRIES",
    "SUCCESS",
    "WORD_LENGTH",
    "TileFeedback",
    "WordleSolver",
    "getDictionary",
    "isInDictionary",
    "processWordleAttempt",
    "selectWord",
    "validateAttempt",
    "wordsLeft",
]
