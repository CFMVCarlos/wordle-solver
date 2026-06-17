import tkinter as tk
from wordleSolverBackend import processWordleAttempt, getDictionary, wordsLeft, selectWord, printToBashCommand
from pynput import keyboard

# Constants for Wordle rules
WORD_LENGTH = 5
MAX_RETRIES = 6
ERROR = -1
NUMBER_ELEMENTS = 8

# Colors for UI
BACKGROUND_COLOR_GRAY = '#c2c2c2'
BACKGROUND_COLOR_SOFT_GRAY = '#DEDEDE'
BACKGROUND_COLOR_YELLOW = '#FCFF20'
BACKGROUND_COLOR_SOFT_YELLOW = '#FCFFA4'
BACKGROUND_COLOR_GREEN = '#4AFF20'
BACKGROUND_COLOR_SOFT_GREEN = '#B0FFA4'
ERROR_COLOR = '#FF0000'
SUCCESS_COLOR = '#00FF00'

# Global variables for state tracking
charPosition = 0  # Tracks the current position of the letter being input
attempt = 0  # Tracks the current attempt number
finishFlag = False  # Indicates if the game is finished

# Tkinter root and UI elements
root = tk.Tk()
buttons = []  # Buttons for the current attempt
previousButtons = []  # Buttons for the previous attempt
extraLabel = tk.Label()  # Label to display extra messages
messageLabel = tk.Label()  # Label for main user messages
frame = tk.LabelFrame()  # Frame for current attempt
previousFrame = tk.LabelFrame()  # Frame for previous attempt


def keyboardPress(key):
    """
    Handles keyboard inputs for gameplay.
    """
    global charPosition, finishFlag

    try:
        # Exit the program when ESC is pressed
        if key == keyboard.Key.esc:
            root.quit()

        # Handle Enter to submit the word
        if key == keyboard.Key.enter:
            if charPosition == WORD_LENGTH and not finishFlag:
                root.after(0, submit)
            return

        # Handle Backspace to delete the last letter
        if key == keyboard.Key.backspace:
            if charPosition == 0:
                return
            charPosition -= 1
            buttons[charPosition]["text"] = "  "
            buttons[charPosition]["state"] = tk.DISABLED
            buttons[charPosition]["bg"] = BACKGROUND_COLOR_GRAY
            buttons[charPosition]["activebackground"] = BACKGROUND_COLOR_SOFT_YELLOW
            return

        # Ignore input if the word is already complete
        if charPosition == WORD_LENGTH:
            return

        # Add typed letter to the current position
        if key.char.isalpha():
            buttons[charPosition]["state"] = tk.NORMAL
            buttons[charPosition]["text"] = key.char.upper()
            charPosition += 1
    except AttributeError:
        pass  # Ignore non-alphabetic keys


def showMessage(message: str, color: str):
    """
    Displays a message to the user with the specified color.
    """
    global extraLabel, attempt
    extraLabel = tk.Label(root, text=message, fg=color)
    extraLabel.grid(row=attempt + 1, column=0, columnspan=NUMBER_ELEMENTS)


def getWord():
    """
    Constructs the word from the button texts, considering color coding.
    """
    word = ''
    for button in buttons:
        if button['bg'] == BACKGROUND_COLOR_GREEN:
            word += '!' + button['text']
        elif button['bg'] == BACKGROUND_COLOR_YELLOW:
            word += '?' + button['text']
        else:
            word += button['text']
    return word


def submit():
    """
    Handles submission of the current word.
    """
    global finishFlag
    extraLabel.grid_forget()
    word = getWord().lower()
    number, message = processWordleAttempt(word)

    if number == ERROR:
        showMessage(message, ERROR_COLOR)
        return
    if number == 0:
        showMessage(message, SUCCESS_COLOR)
        finishFlag = True

    success(word)


def success(word: str):
    """
    Updates the game state on a successful submission.
    """
    global attempt, charPosition, finishFlag, previousButtons
    previousButtons = buttons.copy()

    # Disable buttons from the current attempt
    for button in buttons:
        button["state"] = tk.DISABLED
    buttons.clear()

    if finishFlag:
        wordAttempt = selectWord(True).upper(
        ) if wordsLeft() < 15 else selectWord().upper()
        messageLabel['text'] = f"You found {wordAttempt} in {attempt} attempts!"
        return

    wordAttempt = selectWord(True).upper(
    ) if wordsLeft() < 15 else selectWord().upper()
    messageLabel['text'] = f"{wordsLeft()} words left, try using {wordAttempt}"
    attempt += 1
    charPosition = 0
    createStructureAttempt(attempt)


def letterButtonPressed(numberOfButtonPressed: int):
    """
    Handles color cycling of letter buttons when clicked.
    """
    buttons[numberOfButtonPressed]['bg'], buttons[numberOfButtonPressed]['activebackground'] = \
        nextStage(buttons[numberOfButtonPressed]['bg'])


def nextStage(background: str):
    """
    Cycles the background color for a button.
    """
    if background == BACKGROUND_COLOR_GRAY:
        return BACKGROUND_COLOR_YELLOW, BACKGROUND_COLOR_SOFT_GREEN
    if background == BACKGROUND_COLOR_YELLOW:
        return BACKGROUND_COLOR_GREEN, BACKGROUND_COLOR_SOFT_GRAY
    return BACKGROUND_COLOR_GRAY, BACKGROUND_COLOR_SOFT_YELLOW


def undo():
    """
    Placeholder for undo functionality (not yet implemented).
    """
    pass  # TODO: Implement undo functionality


def createStructureAttempt(numberOfAttempt: int):
    """
    Creates the UI structure for a new attempt.
    """
    global frame, previousFrame
    previousFrame = frame
    frame = tk.LabelFrame(root)
    frame.grid(row=numberOfAttempt, column=0,
               columnspan=NUMBER_ELEMENTS, padx=5, pady=5)

    # Create label and buttons for the attempt
    labelAttempt = tk.Label(
        frame, text=f"Attempt {numberOfAttempt}", bd=3, relief=tk.SUNKEN)
    labelAttempt.grid(row=numberOfAttempt, column=0, padx=5, pady=5)

    for index in range(WORD_LENGTH):
        button = tk.Button(
            frame, text="  ", bd=3, bg=BACKGROUND_COLOR_GRAY, activebackground=BACKGROUND_COLOR_SOFT_YELLOW,
            padx=20, state=tk.DISABLED, cursor="hand2", command=lambda buttonNumber=index: letterButtonPressed(buttonNumber)
        )
        button.grid(row=numberOfAttempt, column=index + 1, padx=5, pady=5)
        buttons.append(button)

    # Submit and Undo buttons
    buttonSubmit = tk.Button(frame, text="Submit (Enter)", bd=6,
                             command=submit, activebackground="#bbbbbb", cursor="hand2")
    buttonSubmit.grid(row=numberOfAttempt,
                      column=WORD_LENGTH + 1, padx=5, pady=5)

    buttonUndo = tk.Button(frame, text="Undo", command=undo,
                           bg="#aaaacc", activebackground="#bbccbb", state=tk.DISABLED)
    buttonUndo.grid(row=numberOfAttempt,
                    column=NUMBER_ELEMENTS - 1, padx=5, pady=5)


def main():
    """
    Entry point for the program.
    """
    global messageLabel, attempt

    # Start keyboard listener
    keyboard.Listener(on_press=keyboardPress).start()

    # Load dictionary and display initial messages
    getDictionary()
    print("\n")
    printToBashCommand("Green", "Welcome to Wordle Solver! 😁")
    printToBashCommand("Green", "Type any 5️⃣ letter word on your keyboard!")
    printToBashCommand(
        "Green", "Afterwards press the letters according to the colors in Wordle!")
    printToBashCommand(
        "Green", "Do not worry about missclicking, you can always cycle the color of any letter! 👌")
    printToBashCommand(
        "Green", "Just ignore for now the UNDO button ↩️, it is on the TODO list ✅")
    printToBashCommand(
        "Green", "Press ESC whenever you want to leave the program! 🏃")

    # Set up main window
    root.title("Wordle Solver!")
    root.iconbitmap("ICON.ico")
    root.geometry("600x600")

    # Initial message and setup for the first attempt
    word = selectWord(True).upper() if wordsLeft(
    ) < 15 else selectWord().upper()
    messageLabel = tk.Label(
        root, text=f"{wordsLeft()} words left, try using {word}", pady=10, padx=20, bd=10, relief=tk.RAISED
    )
    messageLabel.grid(row=0, column=0, columnspan=NUMBER_ELEMENTS,
                      sticky=tk.W + tk.E, padx=5, pady=5)

    attempt += 1
    createStructureAttempt(attempt)

    root.mainloop()


if __name__ == "__main__":
    main()

# Command for creating an executable:
# pyinstaller --add-data "wordleSolverBackend.py;." --add-data "CSW19.txt;." --add-data "ICON.ico;." "wordleSolverFrontend.py"
