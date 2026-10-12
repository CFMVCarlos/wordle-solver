"""Wordle Solver Backend Engine.

Provides high-performance dictionary filtering, mathematically rigorous Wordle
constraint validation (including exact duplicate-letter handling), and
information-gain heuristics for recommending optimal guesses.
"""

from __future__ import annotations

import string
from collections import Counter
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Final

# Configuration constants
WORD_LENGTH: Final[int] = 5
MAX_RETRIES: Final[int] = 6
ERROR: Final[int] = -1
SUCCESS: Final[int] = 1
DICT_NAME: Final[str] = "CSW19.txt"

# ANSI color codes for terminal logging
COLOR_CODES: Final[dict[str, str]] = {
    "DarkGray": "\033[1;30;40m",
    "Red": "\033[1;31;40m",
    "Green": "\033[1;32;40m",
    "Yellow": "\033[1;33;40m",
    "Blue": "\033[1;34;40m",
    "Magenta": "\033[1;35;40m",
    "Cyan": "\033[1;36;40m",
    "White": "\033[1;37;40m",
    "Reset": "\033[0m",
}


class TileFeedback(StrEnum):
    """Enumeration representing the three Wordle evaluation feedback states."""

    CORRECT = "G"
    PRESENT = "Y"
    ABSENT = "B"


@dataclass(slots=True)
class SolverSnapshot:
    """Snapshot of solver state preserved for history and undo operations.

    Parameters
    ----------
    guess : str
        The 5-letter guess submitted in this turn.
    feedback : list[str]
        The 5-element feedback list corresponding to each character ('G', 'Y', 'B').
    remaining_words : list[str]
        A copy of the remaining candidate words after this turn's filtering.
    """

    guess: str
    feedback: list[str]
    remaining_words: list[str]


class WordleSolver:
    """Core stateful solver engine for evaluating and solving Wordle puzzles.

    Maintains the full dictionary of valid 5-letter words, filters candidate
    possibilities based on exact Wordle game rules, and ranks potential guesses
    using character frequency and positional coverage.

    Parameters
    ----------
    dict_path : str, default=DICT_NAME
        Path to the text dictionary file containing words.

    Attributes
    ----------
    dict_path : Path
        Resolved file path to the dictionary file.
    full_dictionary : list[str]
        Master list of valid 5-letter lowercase words.
    candidates : list[str]
        Currently viable remaining secret words.
    history : list[SolverSnapshot]
        Recorded snapshots of each turn for undo capabilities.
    """

    def __init__(self, dict_path: str = DICT_NAME) -> None:
        self.dict_path = Path(dict_path)
        self.full_dictionary: list[str] = []
        self.candidates: list[str] = []
        self.history: list[SolverSnapshot] = []
        self.load_dictionary()

    def load_dictionary(self, filepath: str | None = None) -> list[str]:
        """Load and parse 5-letter alphabetic words from the dictionary file.

        Parameters
        ----------
        filepath : str | None, default=None
            Optional custom file path to load from. If None, uses ``self.dict_path``.

        Returns
        -------
        list[str]
            The loaded list of 5-letter words.

        Raises
        ------
        FileNotFoundError
            If the dictionary file cannot be located on disk.
        """
        target_path = Path(filepath) if filepath else self.dict_path
        if not target_path.exists():
            # Search fallback in current file directory
            local_fallback = Path(__file__).resolve().parent / target_path.name
            if local_fallback.exists():
                target_path = local_fallback
            else:
                msg = f"Dictionary file not found at: {target_path}"
                raise FileNotFoundError(msg)

        with open(target_path, encoding="utf-8", errors="ignore") as file:
            words = [
                line.strip().lower()
                for line in file
                if len(line.strip()) == WORD_LENGTH and line.strip().isalpha()
            ]

        self.full_dictionary = words
        self.reset()
        return self.full_dictionary

    def reset(self) -> None:
        """Reset solver state back to the full dictionary and empty history."""
        self.candidates = list(self.full_dictionary)
        self.history.clear()

    @property
    def words_left(self) -> int:
        """Return the count of viable candidate words remaining.

        Returns
        -------
        int
            Number of words remaining in the candidate list.
        """
        return len(self.candidates)

    def is_valid_word(self, word: str) -> bool:
        """Check if a word is in the master dictionary.

        Parameters
        ----------
        word : str
            Candidate word to check.

        Returns
        -------
        bool
            True if the word is present in ``full_dictionary``, False otherwise.
        """
        clean_word = word.strip().lower()
        return clean_word in self.full_dictionary

    @staticmethod
    def matches_feedback(word: str, guess: str, feedback: list[str]) -> bool:
        """Check if a word satisfies all Wordle feedback constraints from a guess.

        Implements exact Wordle rules including duplicate and partial letter matching:
        - Correct ('G'): Character at index must match guess character.
        - Present ('Y'): Character at index must NOT match, but character must be present elsewhere.
        - Absent ('B'): Character at index must NOT match. If no other instance of this
          character is 'G' or 'Y', the word contains 0 instances. If other instances are
          'G' or 'Y', the word contains exactly that count.

        Parameters
        ----------
        word : str
            The candidate word being tested.
        guess : str
            The 5-letter guess that was submitted.
        feedback : list[str]
            5-element feedback list ('G', 'Y', 'B') for each letter of ``guess``.

        Returns
        -------
        bool
            True if ``word`` satisfies all constraints, False otherwise.
        """
        # 1. Positional checks
        for i in range(WORD_LENGTH):
            g_char = guess[i]
            fb = feedback[i]
            if fb == "G":
                if word[i] != g_char:
                    return False
            elif fb in ("Y", "B") and word[i] == g_char:
                return False

        # 2. Letter frequency constraints for each unique letter in the guess
        unique_chars = set(guess)
        for char in unique_chars:
            indices = [i for i, c in enumerate(guess) if c == char]
            min_count = sum(1 for i in indices if feedback[i] in ("G", "Y"))
            has_absent = any(feedback[i] == "B" for i in indices)
            word_count = word.count(char)

            if has_absent:
                if word_count != min_count:
                    return False
            elif word_count < min_count:
                return False

        return True

    def filter_candidates(self, guess: str, feedback: list[str]) -> int:
        """Filter the remaining candidates using the feedback from a guess.

        Parameters
        ----------
        guess : str
            The 5-letter guess submitted.
        feedback : list[str]
            5-element feedback list ('G', 'Y', 'B').

        Returns
        -------
        int
            Count of candidates remaining after filtering.
        """
        clean_guess = guess.lower()
        normalized_fb = [fb.upper() for fb in feedback]

        self.candidates = [
            w
            for w in self.candidates
            if self.matches_feedback(w, clean_guess, normalized_fb)
        ]

        self.history.append(
            SolverSnapshot(
                guess=clean_guess,
                feedback=normalized_fb,
                remaining_words=list(self.candidates),
            )
        )
        return len(self.candidates)

    def undo(self) -> bool:
        """Revert the most recent attempt and restore previous candidate state.

        Returns
        -------
        bool
            True if an attempt was successfully undone, False if history was empty.
        """
        if not self.history:
            return False

        self.history.pop()
        if self.history:
            self.candidates = list(self.history[-1].remaining_words)
        else:
            self.candidates = list(self.full_dictionary)
        return True

    def get_letter_frequencies(self) -> Counter[str]:
        """Compute the occurrence count of each alphabet letter across remaining candidates.

        Returns
        -------
        Counter[str]
            Frequency counter mapping each character to its total count.
        """
        joined = "".join(self.candidates)
        return Counter(joined)

    def get_best_guess(self, allow_duplicates: bool = False) -> str:
        """Calculate the optimal next word recommendation using letter frequency heuristic.

        Prioritizes words with high cumulative frequency of unique letters among
        the remaining candidate set to maximize information gain per turn.

        Parameters
        ----------
        allow_duplicates : bool, default=False
            Whether to consider words with duplicate characters when candidates > 10.

        Returns
        -------
        str
            The recommended 5-letter word, or empty string if no candidates remain.
        """
        if not self.candidates:
            return ""

        if len(self.candidates) <= 2:
            return self.candidates[0]

        char_counts = self.get_letter_frequencies()
        best_score = -1
        best_word = self.candidates[0]

        for word in self.candidates:
            if (
                not allow_duplicates
                and len(set(word)) < len(word)
                and len(self.candidates) > 10
            ):
                continue

            score = sum(char_counts[c] for c in set(word))
            if score > best_score:
                best_score = score
                best_word = word

        return best_word

    def get_top_candidates(self, limit: int = 50) -> list[str]:
        """Retrieve the top candidate words sorted by heuristic score.

        Parameters
        ----------
        limit : int, default=50
            Maximum number of candidate words to return.

        Returns
        -------
        list[str]
            List of candidate words ordered by information-gain score.
        """
        if not self.candidates:
            return []

        char_counts = self.get_letter_frequencies()
        scored = sorted(
            self.candidates,
            key=lambda w: (sum(char_counts[c] for c in set(w)), -len(set(w))),
            reverse=True,
        )
        return scored[:limit]


# ---------------------------------------------------------------------------
# Global singleton instance & legacy functional interface compatibility
# ---------------------------------------------------------------------------

_global_solver = WordleSolver()
dictionary: list[str] = _global_solver.candidates
characters: dict[str, int] = dict.fromkeys(string.ascii_lowercase, 0)


def DarkGray(string_val: str) -> str:
    """Format string with Dark Gray ANSI color escape code.

    Parameters
    ----------
    string_val : str
        String to format.

    Returns
    -------
    str
        Color-formatted string.
    """
    return f"{COLOR_CODES['DarkGray']}{string_val}{COLOR_CODES['Reset']}"


def Red(string_val: str) -> str:
    """Format string with Red ANSI color escape code.

    Parameters
    ----------
    string_val : str
        String to format.

    Returns
    -------
    str
        Color-formatted string.
    """
    return f"{COLOR_CODES['Red']}{string_val}{COLOR_CODES['Reset']}"


def Green(string_val: str) -> str:
    """Format string with Green ANSI color escape code.

    Parameters
    ----------
    string_val : str
        String to format.

    Returns
    -------
    str
        Color-formatted string.
    """
    return f"{COLOR_CODES['Green']}{string_val}{COLOR_CODES['Reset']}"


def Yellow(string_val: str) -> str:
    """Format string with Yellow ANSI color escape code.

    Parameters
    ----------
    string_val : str
        String to format.

    Returns
    -------
    str
        Color-formatted string.
    """
    return f"{COLOR_CODES['Yellow']}{string_val}{COLOR_CODES['Reset']}"


def Blue(string_val: str) -> str:
    """Format string with Blue ANSI color escape code.

    Parameters
    ----------
    string_val : str
        String to format.

    Returns
    -------
    str
        Color-formatted string.
    """
    return f"{COLOR_CODES['Blue']}{string_val}{COLOR_CODES['Reset']}"


def Magenta(string_val: str) -> str:
    """Format string with Magenta ANSI color escape code.

    Parameters
    ----------
    string_val : str
        String to format.

    Returns
    -------
    str
        Color-formatted string.
    """
    return f"{COLOR_CODES['Magenta']}{string_val}{COLOR_CODES['Reset']}"


def Cyan(string_val: str) -> str:
    """Format string with Cyan ANSI color escape code.

    Parameters
    ----------
    string_val : str
        String to format.

    Returns
    -------
    str
        Color-formatted string.
    """
    return f"{COLOR_CODES['Cyan']}{string_val}{COLOR_CODES['Reset']}"


def White(string_val: str) -> str:
    """Format string with White ANSI color escape code.

    Parameters
    ----------
    string_val : str
        String to format.

    Returns
    -------
    str
        Color-formatted string.
    """
    return f"{COLOR_CODES['White']}{string_val}{COLOR_CODES['Reset']}"


def removeGray(char: str, index: int, softRemove: bool = False) -> None:
    """Filter out words violating the gray (absent) feedback rule.

    Parameters
    ----------
    char : str
        Character to filter.
    index : int
        Index position of the character in the guess.
    softRemove : bool, default=False
        Flag indicating if the character appeared elsewhere in the guess as green/yellow.
    """
    global dictionary
    if softRemove:
        _global_solver.candidates = [
            w for w in _global_solver.candidates if w[index] != char
        ]
    else:
        _global_solver.candidates = [
            w for w in _global_solver.candidates if char not in w
        ]
    dictionary[:] = _global_solver.candidates


def removeYellow(char: str, index: int) -> None:
    """Filter out words violating the yellow (present) feedback rule.

    Parameters
    ----------
    char : str
        Character to filter.
    index : int
        Index position of the character in the guess.
    """
    global dictionary
    _global_solver.candidates = [
        w for w in _global_solver.candidates if char in w and w[index] != char
    ]
    dictionary[:] = _global_solver.candidates


def removeGreen(char: str, index: int) -> None:
    """Filter out words violating the green (correct) feedback rule.

    Parameters
    ----------
    char : str
        Character to filter.
    index : int
        Index position of the character in the guess.
    """
    global dictionary
    _global_solver.candidates = [
        w for w in _global_solver.candidates if w[index] == char
    ]
    dictionary[:] = _global_solver.candidates


def lookforDuplicate(word: str) -> bool:
    """Check if a word contains duplicate letters.

    Parameters
    ----------
    word : str
        Word string to check (ignoring '?' and '!').

    Returns
    -------
    bool
        True if the word has repeated characters, False otherwise.
    """
    cleaned = "".join(filter(str.isalpha, word))
    return len(set(cleaned)) < len(cleaned)


def evaluateAttempt(word: str) -> None:
    """Evaluate an annotated attempt string and filter the dictionary.

    Interprets '!' as Green (correct position), '?' as Yellow (present),
    and unmarked letters as Gray (absent).

    Parameters
    ----------
    word : str
        Formatted attempt string with prefix markers.
    """
    global dictionary
    # Parse into guess and feedback
    clean_chars: list[str] = []
    feedback: list[str] = []

    i = 0
    while i < len(word):
        ch = word[i]
        if ch == "!":
            i += 1
            if i < len(word):
                clean_chars.append(word[i])
                feedback.append("G")
        elif ch == "?":
            i += 1
            if i < len(word):
                clean_chars.append(word[i])
                feedback.append("Y")
        elif ch.isalpha():
            clean_chars.append(ch)
            feedback.append("B")
        i += 1

    if len(clean_chars) == WORD_LENGTH and len(feedback) == WORD_LENGTH:
        guess_str = "".join(clean_chars).lower()
        _global_solver.filter_candidates(guess_str, feedback)
        dictionary[:] = _global_solver.candidates


def isInDictionary(word: str) -> bool:
    """Check if the word exists in the dictionary.

    Parameters
    ----------
    word : str
        Word to test.

    Returns
    -------
    bool
        True if present in dictionary, False otherwise.
    """
    return _global_solver.is_valid_word(word)


def validateAttempt(word: str = "") -> tuple[int, str]:
    """Validate a submitted attempt string against game constraints.

    Parameters
    ----------
    word : str, default=""
        Attempt string to validate.

    Returns
    -------
    tuple[int, str]
        Status code (SUCCESS or ERROR) and formatted status message.
    """
    letter_word = "".join(filter(str.isalpha, word)).lower()
    if len(letter_word) != WORD_LENGTH:
        return ERROR, printToBashCommand(
            "Red", f"\nWord must be {WORD_LENGTH} letters long"
        )

    if not isInDictionary(letter_word):
        return ERROR, printToBashCommand(
            "Red", f'\nWord "{letter_word.upper()}" does not belong to dictionary!'
        )

    for i in range(len(word) - 1):
        if word[i] in "?!" and not word[i + 1].isalpha():
            return ERROR, printToBashCommand(
                "Red", f'\nInvalid placement of "{word[i]}"'
            )

    return SUCCESS, word


def resetCharacters() -> None:
    """Reset the legacy global character frequency dictionary."""
    global characters
    characters = dict.fromkeys(string.ascii_lowercase, 0)


def countCharacters() -> None:
    """Populate the legacy character count dictionary using remaining candidates."""
    counts = _global_solver.get_letter_frequencies()
    for char in characters:
        characters[char] = counts.get(char, 0)


def selectWord(look_duplicate: bool = False) -> str:
    """Select the most valuable next word suggestion based on letter coverage.

    Parameters
    ----------
    look_duplicate : bool, default=False
        Whether to allow words with duplicate letters.

    Returns
    -------
    str
        The recommended word.
    """
    return _global_solver.get_best_guess(allow_duplicates=look_duplicate)


def getDictionary() -> None:
    """Reload the global dictionary from disk."""
    global dictionary
    _global_solver.load_dictionary()
    dictionary[:] = _global_solver.candidates


def wordsLeft() -> int:
    """Return the number of remaining candidate words in the solver.

    Returns
    -------
    int
        Count of viable candidate words.
    """
    return _global_solver.words_left


def processWordleAttempt(string_val: str = "") -> tuple[int, str]:
    """Process an attempt string, filter candidates, and write word list snapshot.

    Parameters
    ----------
    string_val : str, default=""
        Attempt string to process.

    Returns
    -------
    tuple[int, str]
        Result code and message string.
    """
    try:
        error_number, attempt = validateAttempt(string_val)
        if error_number == ERROR:
            return error_number, attempt

        evaluateAttempt(attempt)

        try:
            Path("words.txt").write_text(
                "\n".join(_global_solver.candidates), encoding="utf-8"
            )
        except OSError:
            pass

        if len(_global_solver.candidates) == 1:
            return (
                0,
                printToBashCommand(
                    "Green",
                    f"\nCongratulations! Today's word was {_global_solver.candidates[0].upper()}.",
                ),
            )

        return SUCCESS, attempt
    except IndexError:
        return ERROR, printToBashCommand("Red", "\nNo words available!")
    except KeyboardInterrupt:
        return ERROR, printToBashCommand("Red", "\nProgram terminated by force")


def printToBashCommand(color: str, string_val: str) -> str:
    """Print a colored message to standard output using ANSI escape codes.

    Parameters
    ----------
    color : str
        Target color name from COLOR_CODES (e.g. 'Red', 'Green', 'Yellow').
    string_val : str
        Message string to print.

    Returns
    -------
    str
        The original message string.
    """
    code = COLOR_CODES.get(color, "")
    reset = COLOR_CODES["Reset"]
    print(f"{code}{string_val}{reset}")
    return string_val


if __name__ == "__main__":
    getDictionary()
    printToBashCommand("Green", f"Loaded {wordsLeft()} words into solver engine.")
