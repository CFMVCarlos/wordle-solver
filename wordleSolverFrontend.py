"""Wordle Solver Graphical User Interface (GUI).

Provides a modern, responsive, and visually polished desktop interface featuring an
authentic 6x5 Wordle grid, interactive color-cycling tiles, a dynamic virtual keyboard,
real-time candidate filtering, and information-gain recommendations.
"""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from typing import Final

from wordleSolverBackend import (
    MAX_RETRIES,
    WORD_LENGTH,
    TileFeedback,
    WordleSolver,
)

# ---------------------------------------------------------------------------
# Visual Design Theme & Palette
# ---------------------------------------------------------------------------

BG_MAIN: Final[str] = "#121213"  # Deep matte background (official dark Wordle)
BG_CARD: Final[str] = "#18181b"  # Elevated card surface
BG_ELEVATED: Final[str] = "#27272a"  # Subtle raised container
BORDER_DEFAULT: Final[str] = "#3a3a3c"  # Inactive tile and divider border
BORDER_ACTIVE: Final[str] = "#818384"  # Active typing border

# Tile & Key feedback states
COLOR_ABSENT: Final[str] = "#3a3a3c"  # Gray / Absent
COLOR_PRESENT: Final[str] = "#b59f3b"  # Yellow / Present
COLOR_CORRECT: Final[str] = "#538d4e"  # Emerald Green / Correct
COLOR_EMPTY: Final[str] = "#121213"  # Unfilled background

TEXT_WHITE: Final[str] = "#ffffff"
TEXT_MUTED: Final[str] = "#a1a1aa"
TEXT_ACCENT: Final[str] = "#60a5fa"
COLOR_PRIMARY_BTN: Final[str] = "#538d4e"
COLOR_DANGER_BTN: Final[str] = "#ef4444"
COLOR_SECONDARY_BTN: Final[str] = "#3f3f46"

CYCLE_COLORS: Final[dict[str, str]] = {
    COLOR_ABSENT: COLOR_PRESENT,
    COLOR_PRESENT: COLOR_CORRECT,
    COLOR_CORRECT: COLOR_ABSENT,
}

CYCLE_FEEDBACK: Final[dict[str, str]] = {
    COLOR_ABSENT: TileFeedback.ABSENT.value,
    COLOR_PRESENT: TileFeedback.PRESENT.value,
    COLOR_CORRECT: TileFeedback.CORRECT.value,
}

KEYBOARD_ROWS: Final[list[list[str]]] = [
    ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
    ["A", "S", "D", "F", "G", "H", "J", "K", "L"],
    ["ENTER", "Z", "X", "C", "V", "B", "N", "M", "⌫"],
]


class WordleSolverApp:
    """Main graphical interface controller for Wordle Solver.

    Coordinates the Wordle 6x5 interactive grid, feedback tile states,
    hardware and virtual keyboard inputs, statistical heuristic panels,
    and undo/reset operations.

    Parameters
    ----------
    root : tk.Tk
        The Tkinter root window instance.
    dict_path : str
        Path to the 5-letter dictionary file.

    Attributes
    ----------
    root : tk.Tk
        The master Tkinter application window.
    solver : WordleSolver
        Underlying Wordle solver engine managing candidate word lists.
    current_row : int
        Zero-indexed index of the current active attempt (0 to 5).
    current_col : int
        Zero-indexed letter position in the current attempt (0 to 5).
    grid_letters : list[list[str]]
        2D matrix (6x5) storing the character typed into each tile.
    grid_states : list[list[str]]
        2D matrix (6x5) storing the background color of each tile.
    tile_labels : list[list[tk.Label]]
        2D matrix of Tkinter Label widgets representing the board grid.
    key_buttons : dict[str, tk.Button]
        Mapping of alphabet and action keys to virtual keyboard Button widgets.
    """

    def __init__(self, root: tk.Tk, dict_path: str = "CSW19.txt") -> None:
        self.root = root
        self.root.title("Wordle Solver & Assistant")
        self.root.configure(bg=BG_MAIN)
        self.root.geometry("980x760")
        self.root.minsize(860, 680)

        # Set taskbar / window icon if present
        self._setup_window_icon()

        # Initialize solver engine
        self.solver = WordleSolver(dict_path)

        # Game board state
        self.current_row: int = 0
        self.current_col: int = 0
        self.grid_letters: list[list[str]] = [
            ["" for _ in range(WORD_LENGTH)] for _ in range(MAX_RETRIES)
        ]
        self.grid_states: list[list[str]] = [
            [COLOR_ABSENT for _ in range(WORD_LENGTH)] for _ in range(MAX_RETRIES)
        ]
        self.tile_labels: list[list[tk.Label]] = []
        self.key_buttons: dict[str, tk.Button] = {}

        # Construct UI hierarchy
        self._build_ui()

        # Setup keyboard event bindings
        self._bind_events()

        # Initial UI refresh
        self._refresh_intelligence_panel()
        self._set_status(
            "Type letters on your keyboard, click tiles to toggle colors, then press Submit.",
            "info",
        )

    def _setup_window_icon(self) -> None:
        """Attempt to set the application window icon if available."""
        icon_path = Path(__file__).resolve().parent / "ICON.ico"
        if icon_path.exists():
            try:
                self.root.iconbitmap(str(icon_path))
            except tk.TclError:
                pass  # Ignore on X11 platforms without native ICO support

    def _build_ui(self) -> None:
        """Construct the primary UI layout frames, grid, sidebar, and controls."""
        # Top Header Bar
        header_frame = tk.Frame(self.root, bg=BG_MAIN, pady=10)
        header_frame.pack(fill=tk.X, padx=24)

        title_label = tk.Label(
            header_frame,
            text="WORDLE SOLVER",
            font=("Helvetica", 20, "bold"),
            fg=TEXT_WHITE,
            bg=BG_MAIN,
        )
        title_label.pack(side=tk.LEFT)

        subtitle_label = tk.Label(
            header_frame,
            text="  •  Interactive Assistant & Heuristic Engine",
            font=("Helvetica", 11),
            fg=TEXT_MUTED,
            bg=BG_MAIN,
        )
        subtitle_label.pack(side=tk.LEFT, pady=(4, 0))

        # Status notification banner
        self.status_banner = tk.Label(
            self.root,
            text="",
            font=("Helvetica", 10, "bold"),
            fg=TEXT_WHITE,
            bg=BG_CARD,
            pady=6,
            padx=16,
            relief=tk.FLAT,
        )
        self.status_banner.pack(fill=tk.X, padx=24, pady=(0, 10))

        # Main 2-column container
        main_container = tk.Frame(self.root, bg=BG_MAIN)
        main_container.pack(fill=tk.BOTH, expand=True, padx=24, pady=(0, 16))

        # Left Column: Board Grid & Virtual Keyboard
        left_col = tk.Frame(main_container, bg=BG_MAIN)
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 16))

        self._build_grid(left_col)
        self._build_keyboard(left_col)

        # Right Column: Intelligence & Heuristics Panel
        right_col = tk.Frame(main_container, bg=BG_MAIN, width=320)
        right_col.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(16, 0))
        right_col.pack_propagate(False)

        self._build_sidebar(right_col)

    def _build_grid(self, parent: tk.Frame) -> None:
        """Build the 6x5 Wordle letter grid.

        Parameters
        ----------
        parent : tk.Frame
            The parent container frame for the grid.
        """
        grid_frame = tk.Frame(parent, bg=BG_MAIN)
        grid_frame.pack(pady=(0, 10))

        self.tile_labels = []
        for r in range(MAX_RETRIES):
            row_labels: list[tk.Label] = []
            row_frame = tk.Frame(grid_frame, bg=BG_MAIN)
            row_frame.pack(pady=3)

            for c in range(WORD_LENGTH):
                tile = tk.Label(
                    row_frame,
                    text="",
                    font=("Helvetica", 20, "bold"),
                    width=3,
                    height=1,
                    fg=TEXT_WHITE,
                    bg=COLOR_EMPTY,
                    relief=tk.SOLID,
                    bd=2,
                    highlightthickness=0,
                    cursor="hand2",
                )
                tile.pack(side=tk.LEFT, padx=3)
                tile.bind("<Button-1>", lambda event, row=r, col=c: self._on_tile_clicked(row, col))
                row_labels.append(tile)

            self.tile_labels.append(row_labels)

        # Tile legend hint
        legend_frame = tk.Frame(parent, bg=BG_MAIN)
        legend_frame.pack(pady=(2, 10))

        legend_hint = tk.Label(
            legend_frame,
            text="Click letters on active attempt to cycle colors:  "
            "⬛ Absent  ➜  🟨 Present  ➜  🟩 Correct",
            font=("Helvetica", 9),
            fg=TEXT_MUTED,
            bg=BG_MAIN,
        )
        legend_hint.pack()

    def _build_keyboard(self, parent: tk.Frame) -> None:
        """Construct the on-screen virtual keyboard with dynamic feedback colors.

        Parameters
        ----------
        parent : tk.Frame
            Parent frame container.
        """
        kbd_frame = tk.Frame(parent, bg=BG_MAIN)
        kbd_frame.pack(fill=tk.X, pady=(4, 0))

        for _row_idx, row_keys in enumerate(KEYBOARD_ROWS):
            row_frame = tk.Frame(kbd_frame, bg=BG_MAIN)
            row_frame.pack(pady=2)

            for key in row_keys:
                width = 5 if key in ("ENTER", "⌫") else 3
                btn = tk.Button(
                    row_frame,
                    text=key,
                    font=("Helvetica", 9, "bold"),
                    width=width,
                    height=2,
                    fg=TEXT_WHITE,
                    bg=COLOR_SECONDARY_BTN,
                    activebackground=BORDER_ACTIVE,
                    activeforeground=TEXT_WHITE,
                    relief=tk.FLAT,
                    bd=0,
                    cursor="hand2",
                    command=lambda k=key: self._on_virtual_key_pressed(k),
                )
                btn.pack(side=tk.LEFT, padx=2)
                self.key_buttons[key] = btn

    def _build_sidebar(self, parent: tk.Frame) -> None:
        """Construct the intelligence sidebar cards and action controls.

        Parameters
        ----------
        parent : tk.Frame
            Parent sidebar container frame.
        """
        # Card 1: Words Remaining
        stats_card = tk.LabelFrame(
            parent,
            text="  POSSIBILITIES  ",
            font=("Helvetica", 9, "bold"),
            fg=TEXT_MUTED,
            bg=BG_CARD,
            bd=1,
            relief=tk.SOLID,
            padx=14,
            pady=10,
        )
        stats_card.pack(fill=tk.X, pady=(0, 10))

        self.words_left_label = tk.Label(
            stats_card,
            text=f"{self.solver.words_left:,}",
            font=("Helvetica", 24, "bold"),
            fg=TEXT_WHITE,
            bg=BG_CARD,
        )
        self.words_left_label.pack(anchor=tk.W)

        self.filter_ratio_label = tk.Label(
            stats_card,
            text="Initial master dictionary loaded",
            font=("Helvetica", 9),
            fg=TEXT_MUTED,
            bg=BG_CARD,
        )
        self.filter_ratio_label.pack(anchor=tk.W, pady=(2, 0))

        # Card 2: Recommended Best Guess
        rec_card = tk.LabelFrame(
            parent,
            text="  OPTIMAL SUGGESTION  ",
            font=("Helvetica", 9, "bold"),
            fg=TEXT_ACCENT,
            bg=BG_CARD,
            bd=1,
            relief=tk.SOLID,
            padx=14,
            pady=10,
        )
        rec_card.pack(fill=tk.X, pady=(0, 10))

        self.rec_word_label = tk.Label(
            rec_card,
            text="---",
            font=("Helvetica", 20, "bold"),
            fg=TEXT_WHITE,
            bg=BG_CARD,
        )
        self.rec_word_label.pack(anchor=tk.W)

        self.rec_desc_label = tk.Label(
            rec_card,
            text="Entropy & coverage analysis",
            font=("Helvetica", 8),
            fg=TEXT_MUTED,
            bg=BG_CARD,
        )
        self.rec_desc_label.pack(anchor=tk.W, pady=(2, 6))

        use_btn = tk.Button(
            rec_card,
            text="⚡ Use Suggestion",
            font=("Helvetica", 9, "bold"),
            fg=TEXT_WHITE,
            bg=COLOR_SECONDARY_BTN,
            activebackground=COLOR_CORRECT,
            activeforeground=TEXT_WHITE,
            relief=tk.FLAT,
            cursor="hand2",
            pady=4,
            command=self._use_suggestion,
        )
        use_btn.pack(fill=tk.X)

        # Card 3: Remaining Candidates Preview List
        candidates_card = tk.LabelFrame(
            parent,
            text="  MATCHING CANDIDATES  ",
            font=("Helvetica", 9, "bold"),
            fg=TEXT_MUTED,
            bg=BG_CARD,
            bd=1,
            relief=tk.SOLID,
            padx=10,
            pady=8,
        )
        candidates_card.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        list_frame = tk.Frame(candidates_card, bg=BG_CARD)
        list_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL)
        self.candidates_listbox = tk.Listbox(
            list_frame,
            font=("Courier", 10, "bold"),
            fg=TEXT_WHITE,
            bg=BG_MAIN,
            selectbackground=COLOR_CORRECT,
            selectforeground=TEXT_WHITE,
            relief=tk.FLAT,
            yscrollcommand=scrollbar.set,
            highlightthickness=0,
            cursor="hand2",
        )
        scrollbar.config(command=self.candidates_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.candidates_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.candidates_listbox.bind("<Double-Button-1>", self._on_candidate_double_click)

        # Action Buttons Area
        btn_frame = tk.Frame(parent, bg=BG_MAIN)
        btn_frame.pack(fill=tk.X)

        submit_btn = tk.Button(
            btn_frame,
            text="Submit Guess (Enter)",
            font=("Helvetica", 10, "bold"),
            fg=TEXT_WHITE,
            bg=COLOR_PRIMARY_BTN,
            activebackground="#457840",
            activeforeground=TEXT_WHITE,
            relief=tk.FLAT,
            pady=8,
            cursor="hand2",
            command=self.submit_attempt,
        )
        submit_btn.pack(fill=tk.X, pady=(0, 6))

        action_row = tk.Frame(btn_frame, bg=BG_MAIN)
        action_row.pack(fill=tk.X)

        undo_btn = tk.Button(
            action_row,
            text="↶ Undo (Ctrl+Z)",
            font=("Helvetica", 9, "bold"),
            fg=TEXT_WHITE,
            bg=COLOR_SECONDARY_BTN,
            activebackground=BORDER_ACTIVE,
            activeforeground=TEXT_WHITE,
            relief=tk.FLAT,
            pady=6,
            cursor="hand2",
            command=self.undo_attempt,
        )
        undo_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))

        reset_btn = tk.Button(
            action_row,
            text="↺ Reset",
            font=("Helvetica", 9, "bold"),
            fg=TEXT_WHITE,
            bg=COLOR_DANGER_BTN,
            activebackground="#dc2626",
            activeforeground=TEXT_WHITE,
            relief=tk.FLAT,
            pady=6,
            cursor="hand2",
            command=self.reset_game,
        )
        reset_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(4, 0))

    def _bind_events(self) -> None:
        """Bind hardware keyboard keystroke events to the main Tkinter window."""
        self.root.bind("<Key>", self._on_hardware_key_press)
        self.root.bind("<Control-z>", lambda e: self.undo_attempt())
        self.root.bind("<Control-r>", lambda e: self.reset_game())
        self.root.bind("<Escape>", lambda e: self.root.quit())

    def _on_hardware_key_press(self, event: tk.Event) -> None:
        """Handle hardware keyboard inputs directly via Tk event listeners.

        Parameters
        ----------
        event : tk.Event
            Tkinter event object containing the pressed keysym.
        """
        keysym = event.keysym.upper()
        if keysym == "RETURN":
            self.submit_attempt()
        elif keysym in ("BACKSPACE", "DELETE"):
            self._handle_backspace()
        elif len(keysym) == 1 and keysym.isalpha():
            self._handle_char_input(keysym)

    def _on_virtual_key_pressed(self, key: str) -> None:
        """Handle inputs originating from virtual on-screen keyboard clicks.

        Parameters
        ----------
        key : str
            The key string value clicked (e.g. 'A', 'ENTER', '⌫').
        """
        if key == "ENTER":
            self.submit_attempt()
        elif key == "⌫":
            self._handle_backspace()
        elif key.isalpha() and len(key) == 1:
            self._handle_char_input(key)

    def _handle_char_input(self, char: str) -> None:
        """Insert a typed letter into the active row.

        Parameters
        ----------
        char : str
            Uppercase character to insert.
        """
        if self.current_row >= MAX_RETRIES:
            return

        if self.current_col < WORD_LENGTH:
            self.grid_letters[self.current_row][self.current_col] = char
            # Default new typed letters to absent color (gray)
            if self.grid_states[self.current_row][self.current_col] == COLOR_EMPTY:
                self.grid_states[self.current_row][self.current_col] = COLOR_ABSENT

            self._update_tile_widget(self.current_row, self.current_col)
            self.current_col += 1

    def _handle_backspace(self) -> None:
        """Remove the most recently entered character from the active row."""
        if self.current_row >= MAX_RETRIES:
            return

        if self.current_col > 0:
            self.current_col -= 1
            self.grid_letters[self.current_row][self.current_col] = ""
            self.grid_states[self.current_row][self.current_col] = COLOR_EMPTY
            self._update_tile_widget(self.current_row, self.current_col)

    def _on_tile_clicked(self, row: int, col: int) -> None:
        """Cycle tile color when clicked by user on the active row.

        Parameters
        ----------
        row : int
            Row index of clicked tile.
        col : int
            Column index of clicked tile.
        """
        if row != self.current_row:
            return

        if not self.grid_letters[row][col]:
            return

        current_color = self.grid_states[row][col]
        next_color = CYCLE_COLORS.get(current_color, COLOR_ABSENT)
        self.grid_states[row][col] = next_color
        self._update_tile_widget(row, col)

    def _update_tile_widget(self, row: int, col: int) -> None:
        """Synchronize the graphical Label tile with its internal letter and state.

        Parameters
        ----------
        row : int
            Row index of tile.
        col : int
            Column index of tile.
        """
        tile = self.tile_labels[row][col]
        char = self.grid_letters[row][col]
        color = self.grid_states[row][col]

        tile.config(text=char)
        if char:
            tile.config(bg=color, fg=TEXT_WHITE)
            if color == COLOR_EMPTY:
                tile.config(bg=BG_MAIN, relief=tk.SOLID, bd=2)
            else:
                tile.config(relief=tk.FLAT, bd=0)
        else:
            tile.config(bg=COLOR_EMPTY, relief=tk.SOLID, bd=2)

    def _use_suggestion(self) -> None:
        """Auto-populate the current active row with the recommended suggestion."""
        if self.current_row >= MAX_RETRIES:
            return

        suggested = self.solver.get_best_guess()
        if not suggested:
            return

        # Clear current row letters
        for c in range(WORD_LENGTH):
            self.grid_letters[self.current_row][c] = ""
            self.grid_states[self.current_row][c] = COLOR_ABSENT

        # Fill suggested word
        for c, char in enumerate(suggested.upper()):
            self.grid_letters[self.current_row][c] = char
            self.grid_states[self.current_row][c] = COLOR_ABSENT
            self._update_tile_widget(self.current_row, c)

        self.current_col = WORD_LENGTH
        self._set_status(
            f"Populated '{suggested.upper()}'. Click tiles to adjust colors, then press Submit.",
            "info",
        )

    def _on_candidate_double_click(self, event: tk.Event) -> None:
        """Insert double-clicked word from candidate list into current row."""
        selection = self.candidates_listbox.curselection()
        if not selection or self.current_row >= MAX_RETRIES:
            return

        selected_word = self.candidates_listbox.get(selection[0]).strip().upper()
        if len(selected_word) == WORD_LENGTH:
            for c, char in enumerate(selected_word):
                self.grid_letters[self.current_row][c] = char
                self.grid_states[self.current_row][c] = COLOR_ABSENT
                self._update_tile_widget(self.current_row, c)
            self.current_col = WORD_LENGTH

    def submit_attempt(self) -> None:
        """Validate and evaluate the current attempt row against the solver engine."""
        if self.current_row >= MAX_RETRIES:
            self._set_status("Game finished. Click Reset to start a new puzzle.", "warning")
            return

        if self.current_col < WORD_LENGTH:
            self._set_status(
                f"Please enter all {WORD_LENGTH} letters before submitting.", "warning"
            )
            return

        guess = "".join(self.grid_letters[self.current_row]).lower()
        if not self.solver.is_valid_word(guess):
            self._set_status(f"'{guess.upper()}' is not in the dictionary!", "error")
            return

        # Extract feedback list ('G', 'Y', 'B')
        feedback: list[str] = []
        for col in range(WORD_LENGTH):
            color = self.grid_states[self.current_row][col]
            fb_code = CYCLE_FEEDBACK.get(color, TileFeedback.ABSENT.value)
            feedback.append(fb_code)

        # Check if solved (all Green)
        all_green = all(fb == TileFeedback.CORRECT.value for fb in feedback)

        # Execute candidate filtering
        remaining = self.solver.filter_candidates(guess, feedback)

        # Update keyboard key colors based on revealed feedback
        self._update_keyboard_colors(guess, feedback)

        if all_green or (remaining == 1 and self.solver.candidates[0] == guess):
            self._set_status(
                f"🎉 Solved! The target word is '{guess.upper()}' in {self.current_row + 1} attempts!",
                "success",
            )
            self._refresh_intelligence_panel()
            self.current_row = MAX_RETRIES
            return

        if remaining == 0:
            self._set_status(
                "⚠️ No dictionary words match this feedback pattern. Check for tile color mistakes.",
                "error",
            )
            return

        # Advance to next attempt
        self.current_row += 1
        self.current_col = 0
        self._refresh_intelligence_panel()

        best_next = self.solver.get_best_guess()
        self._set_status(
            f"Filtered to {remaining:,} words. Recommended next guess: '{best_next.upper()}'.",
            "success",
        )

    def undo_attempt(self) -> None:
        """Revert the previous attempt row and restore prior candidates state."""
        if self.current_row == 0:
            self._set_status("Cannot undo: board is at initial attempt.", "warning")
            return

        if not self.solver.undo():
            return

        # If game was solved or finished at attempt 6, step back
        target_row = min(self.current_row - 1, MAX_RETRIES - 1)

        # Clear target row tiles
        for c in range(WORD_LENGTH):
            self.grid_letters[target_row][c] = ""
            self.grid_states[target_row][c] = COLOR_EMPTY
            self._update_tile_widget(target_row, c)

        self.current_row = target_row
        self.current_col = 0

        # Recalculate keyboard colors across remaining history
        self._rebuild_keyboard_colors()
        self._refresh_intelligence_panel()
        self._set_status(
            f"Undid attempt {self.current_row + 1}. Restored {self.solver.words_left:,} candidates.",
            "info",
        )

    def reset_game(self) -> None:
        """Reset the solver board, history, keyboard, and candidate state."""
        self.solver.reset()
        self.current_row = 0
        self.current_col = 0

        for r in range(MAX_RETRIES):
            for c in range(WORD_LENGTH):
                self.grid_letters[r][c] = ""
                self.grid_states[r][c] = COLOR_EMPTY
                self._update_tile_widget(r, c)

        for btn in self.key_buttons.values():
            btn.config(bg=COLOR_SECONDARY_BTN)

        self._refresh_intelligence_panel()
        self._set_status(
            "Board reset. Type your initial guess (e.g. AEROS, SOARE, or CRANE).", "info"
        )

    def _update_keyboard_colors(self, guess: str, feedback: list[str]) -> None:
        """Update virtual keyboard key background colors according to feedback priority.

        Parameters
        ----------
        guess : str
            The 5-letter guess word.
        feedback : list[str]
            Feedback codes ('G', 'Y', 'B') for each position.
        """
        for i, char in enumerate(guess.upper()):
            btn = self.key_buttons.get(char)
            if not btn:
                continue

            fb = feedback[i]
            current_bg = btn.cget("bg")

            # Green overrides Yellow and Gray; Yellow overrides Gray
            if fb == TileFeedback.CORRECT.value:
                btn.config(bg=COLOR_CORRECT)
            elif fb == TileFeedback.PRESENT.value and current_bg != COLOR_CORRECT:
                btn.config(bg=COLOR_PRESENT)
            elif fb == TileFeedback.ABSENT.value and current_bg not in (
                COLOR_CORRECT,
                COLOR_PRESENT,
            ):
                btn.config(bg=COLOR_ABSENT)

    def _rebuild_keyboard_colors(self) -> None:
        """Recompute keyboard colors across all active history snapshots."""
        for btn in self.key_buttons.values():
            btn.config(bg=COLOR_SECONDARY_BTN)

        for snapshot in self.solver.history:
            self._update_keyboard_colors(snapshot.guess, snapshot.feedback)

    def _refresh_intelligence_panel(self) -> None:
        """Update candidate counts, best guess recommendation, and candidate preview."""
        rem_count = self.solver.words_left
        initial_count = len(self.solver.full_dictionary)

        self.words_left_label.config(text=f"{rem_count:,}")

        if rem_count < initial_count and initial_count > 0:
            filtered_pct = ((initial_count - rem_count) / initial_count) * 100
            self.filter_ratio_label.config(text=f"Filtered {filtered_pct:.1f}% of search space")
        else:
            self.filter_ratio_label.config(text="Master dictionary loaded")

        best_word = self.solver.get_best_guess()
        if best_word:
            self.rec_word_label.config(text=best_word.upper())
            self.rec_desc_label.config(text="Highest information gain heuristic")
        else:
            self.rec_word_label.config(text="NONE")
            self.rec_desc_label.config(text="No valid words remaining")

        # Update candidate listbox
        self.candidates_listbox.delete(0, tk.END)
        top_words = self.solver.get_top_candidates(limit=100)
        for w in top_words:
            self.candidates_listbox.insert(tk.END, f"  {w.upper()}")

    def _set_status(self, message: str, level: str = "info") -> None:
        """Display an informational status banner message.

        Parameters
        ----------
        message : str
            Message text to display.
        level : str
            Severity level ('info', 'success', 'warning', 'error').
        """
        color_map = {
            "info": "#3b82f6",
            "success": "#10b981",
            "warning": "#f59e0b",
            "error": "#ef4444",
        }
        self.status_banner.config(text=message, bg=color_map.get(level, BG_CARD))


def main() -> None:
    """Launch the Wordle Solver graphical desktop application."""
    root = tk.Tk()
    _ = WordleSolverApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
