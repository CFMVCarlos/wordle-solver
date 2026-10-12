"""Automated test suite for Wordle Solver backend algorithms and constraints."""

from __future__ import annotations

import pytest

from wordle_solver.wordleSolverBackend import (
    ERROR,
    SUCCESS,
    WordleSolver,
    getDictionary,
    isInDictionary,
    processWordleAttempt,
    selectWord,
    validateAttempt,
    wordsLeft,
)


@pytest.fixture
def solver() -> WordleSolver:
    return WordleSolver("CSW19.txt")


def test_dictionary_loading(solver: WordleSolver) -> None:
    assert solver.words_left > 10000
    assert solver.is_valid_word("crane")
    assert solver.is_valid_word("soare")
    assert not solver.is_valid_word("xyz12")
    assert not solver.is_valid_word("toolongword")


def test_matches_feedback_basic(solver: WordleSolver) -> None:
    # Target: crane, Guess: slate
    # s: B, l: B, a: G, t: B, e: G
    feedback = ["B", "B", "G", "B", "G"]
    assert solver.matches_feedback("crane", "slate", feedback) is True
    assert solver.matches_feedback("brake", "slate", feedback) is True
    assert solver.matches_feedback("stare", "slate", feedback) is False  # s is present


def test_matches_feedback_duplicates(solver: WordleSolver) -> None:
    # Target: robot, Guess: boost
    # b: Y, o: G, o: Y, s: B, t: G
    assert solver.matches_feedback("robot", "boost", ["Y", "G", "Y", "B", "G"]) is True

    # Target: crest (one e), Guess: speed (two e's, first G, second B)
    # s: Y, p: B, e: G, e: B, d: B
    feedback_speed = ["Y", "B", "G", "B", "B"]
    assert solver.matches_feedback("crest", "speed", feedback_speed) is True
    # erase has 2 e's, must be rejected
    assert solver.matches_feedback("erase", "speed", feedback_speed) is False
    # fleet has 2 e's, must be rejected
    assert solver.matches_feedback("fleet", "speed", feedback_speed) is False


def test_filtering_and_undo(solver: WordleSolver) -> None:
    initial_count = solver.words_left
    assert initial_count > 10000

    # Step 1: Guess 'soare' with all absent
    rem = solver.filter_candidates("soare", ["B", "B", "B", "B", "B"])
    assert rem < initial_count
    assert "soare" not in solver.candidates

    # Step 2: Guess 'clint' with 'c' Green, 'l' Yellow
    rem_2 = solver.filter_candidates("clint", ["G", "Y", "B", "B", "B"])
    assert rem_2 < rem

    # Test Undo step 2
    assert solver.undo() is True
    assert solver.words_left == rem

    # Test Undo step 1
    assert solver.undo() is True
    assert solver.words_left == initial_count

    # Empty undo
    assert solver.undo() is False


def test_best_guess_recommendation(solver: WordleSolver) -> None:
    best = solver.get_best_guess()
    assert len(best) == 5
    assert solver.is_valid_word(best)


def test_legacy_interface_compatibility() -> None:
    getDictionary()
    count_start = wordsLeft()
    assert count_start > 10000

    valid_res, _ = validateAttempt("crane")
    assert valid_res == SUCCESS

    invalid_res, _ = validateAttempt("nonex")
    assert invalid_res == ERROR

    # Process valid attempt with annotations (! for Green, ? for Yellow)
    status, _ = processWordleAttempt("!c?r a n e")
    assert status == SUCCESS
    assert wordsLeft() < count_start

    suggested = selectWord()
    assert len(suggested) == 5
    assert isInDictionary(suggested)
