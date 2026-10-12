<div align="center">

# 🟩 Wordle Solver & Game Assistant 🟨

<p align="center">
  <strong>A high-performance Wordle solver and interactive desktop assistant powered by information-theoretic heuristics and an authentic dark-mode GUI.</strong>
</p>

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![GUI](https://img.shields.io/badge/GUI-Tkinter%20(Native)-blue?style=for-the-badge&logo=python&logoColor=white)](https://docs.python.org/3/library/tkinter.html)
[![Package Manager](https://img.shields.io/badge/uv-Package%20Manager-DE5FE9?style=for-the-badge&logo=astral&logoColor=white)](https://astral.sh/uv)
[![Code Style](https://img.shields.io/badge/Code%20Style-Ruff-black?style=for-the-badge&logo=ruff&logoColor=white)](https://github.com/astral-sh/ruff)
[![Docstrings](https://img.shields.io/badge/Docstrings-NumPy%20%2F%20pydoclint-013243?style=for-the-badge&logo=numpy&logoColor=white)](https://numpydoc.readthedocs.io/)
[![Type Checker](https://img.shields.io/badge/Type%20Check-Basedpyright-2b5b84?style=for-the-badge&logo=typescript&logoColor=white)](https://github.com/DetachHead/basedpyright)
[![Tests](https://img.shields.io/badge/Tests-Pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)](https://docs.pytest.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

<br/>

<img src="WordleSolverExample.png" alt="Wordle Solver UI Preview" width="820" style="border-radius: 8px; box-shadow: 0 4px 16px rgba(0,0,0,0.4);" />

</div>

---

## 📖 Overview

**Wordle Solver & Game Assistant** is a desktop application designed to assist players with solving daily Wordle puzzles or evaluating optimal word strategies. It combines a mathematically rigorous constraint validation engine with an intuitive, modern desktop interface modeled directly after authentic Wordle gameplay.

The solver reads from the official 12,972-word Collins Scrabble wordlist (`CSW19.txt`), dynamically filters viable candidates, and computes information-gain recommendations using letter-frequency and entropy heuristics.

---

## ✨ Features

- 🧠 **Rigorous Wordle Constraint Engine:** Accurately models official Wordle game rules, including strict handling of duplicate letters, partial matches, and exact frequency limits.
- ⚡ **Information-Gain Heuristics:** Recommends the optimal next guess by analyzing unique letter frequencies and positional coverage across remaining candidate words.
- 🎨 **Modern Dark Mode Interface:** Sleek, high-contrast dark theme inspired by Wordle's official aesthetic (`#121213`), featuring large bold letter tiles and smooth color cycling.
- ⌨️ **Dual Keyboard Support:**
  - **Hardware Keyboard:** Native event bindings for typing, backspacing, and submitting without external keylogger dependencies.
  - **On-Screen Virtual Keyboard:** Dynamic keys that automatically mirror discovered letter statuses (Green, Yellow, Gray).
- 🔍 **Real-Time Possibility Explorer:**
  - Live candidate counter tracking remaining search space.
  - Scrollable candidates list displaying top matching words.
  - One-click **⚡ Use Suggestion** and candidate double-click insertion.
- ↶ **Full History & Undo Support:** Revert any attempt (<kbd>Ctrl</kbd>+<kbd>Z</kbd>) to correct misclicks or explore alternate word branches without resetting the board.
- 🪶 **Zero External Runtime Dependencies:** Runs on pure Python standard library (`tkinter`, `collections`, `pathlib`, `dataclasses`).

---

## 🎮 Interactive Controls & Shortcuts

| Action | Control / Keybinding | Description |
| :--- | :--- | :--- |
| **Type Letters** | <kbd>A</kbd> - <kbd>Z</kbd> or Virtual Keys | Enters characters into the active attempt row. |
| **Toggle Color** | **Click Tile** | Cycles tile state: ⬛ Absent ➜ 🟨 Present ➜ 🟩 Correct. |
| **Submit Guess** | <kbd>Enter</kbd> / <kbd>Return</kbd> | Evaluates feedback and filters dictionary candidates. |
| **Delete Letter** | <kbd>Backspace</kbd> / <kbd>⌫</kbd> | Deletes the last entered letter on the active row. |
| **Undo Attempt** | <kbd>Ctrl</kbd> + <kbd>Z</kbd> | Reverts the previous turn and restores prior candidates. |
| **Reset Game** | <kbd>Ctrl</kbd> + <kbd>R</kbd> or **↺ Reset** | Clears the board and reloads the full dictionary. |
| **Use Suggestion** | **⚡ Use Suggestion** | Auto-populates the recommended word into the active row. |
| **Exit** | <kbd>Esc</kbd> | Closes the solver window. |

---

## 📂 Project Architecture

```
wordle-solver/
├── CSW19.txt                 # Official Collins 5-letter Scrabble dictionary (12,972 words)
├── ICON.ico                  # Application window icon asset
├── LICENSE                   # MIT License
├── README.md                 # Project showcase and developer documentation
├── WordleSolverExample.png   # Graphical user interface preview screenshot
├── pyproject.toml            # Project metadata, tool configurations (Ruff, Pytest, Pyright)
├── requirements.txt          # Pip requirements file
├── wordleSolverBackend.py    # Core WordleSolver engine, constraints, and heuristics
├── wordleSolverFrontend.py   # Modern Tkinter dark-mode graphical desktop application
└── tests/
    └── test_solver.py        # Automated test suite (constraints, duplicates, undo)
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+** (Tested on Python 3.10, 3.11, 3.12, 3.13, 3.14)
- **Tkinter** (Bundled with standard Python on Windows/macOS; on Debian/Ubuntu install via `sudo apt install python3-tk` if using system Python)

### Installation

Clone the repository:
```bash
git clone https://github.com/CFMVCarlos/wordle-solver.git
cd wordle-solver
```

#### Option A: Using `uv` (Recommended)
Fast setup with modern Python toolchain:
```bash
# Sync environment and development tools
uv sync

# Launch the solver GUI
uv run python wordleSolverFrontend.py
```

#### Option B: Using standard Python (`pip`)
```bash
# Optional: create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Launch the solver GUI
python3 wordleSolverFrontend.py
```

---

## 🧪 Testing & Code Quality

The repository adheres to strict code quality standards, enforced through modern Astral and Python tooling:

```bash
# Run unit tests
uv run pytest

# Check formatting and linting
uv run ruff check
uv run ruff format --check

# Verify NumPy docstring compliance
uv run pydoclint .

# Run static type checking
uv run basedpyright
```

---

## 📦 Building Standalone Executable (PyInstaller)

To build a single-file executable for distribution without requiring Python:

```bash
pip install pyinstaller
pyinstaller --noconsole --onefile \
  --add-data "CSW19.txt:." \
  --add-data "ICON.ico:." \
  --icon="ICON.ico" \
  --name "WordleSolver" \
  wordleSolverFrontend.py
```
*(On Windows, use `;` as the data separator: `--add-data "CSW19.txt;."`)*

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).

Developed with ❤️ by [Carlos Valente](https://github.com/CFMVCarlos).