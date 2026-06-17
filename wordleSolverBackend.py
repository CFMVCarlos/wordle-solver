import string
import os

# Configuration constants
WORD_LENGTH = 5        # Length of the word used in the game
MAX_RETRIES = 6        # Maximum number of attempts allowed
ERROR = -1             # Error code
SUCCESS = 1            # Success code
DICT_NAME = "CSW19.txt"  # Name of the dictionary file

# Initialize dictionary and character frequency map
dictionary = []
characters = {}

# Utility functions to apply color formatting for terminal output


def DarkGray(
    string: str) -> str: return "\033[1;30;40m" + string + "\033[0;37;40m"


def Red(string: str) -> str: return "\033[1;31;40m" + string + "\033[0;37;40m"


def Green(
    string: str) -> str: return "\033[1;32;40m" + string + "\033[0;37;40m"
def Yellow(
    string: str) -> str: return "\033[1;33;40m" + string + "\033[0;37;40m"


def Blue(string: str) -> str: return "\033[1;34;40m" + string + "\033[0;37;40m"
def Magenta(
    string: str) -> str: return "\033[1;35;40m" + string + "\033[0;37;40m"


def Cyan(string: str) -> str: return "\033[1;36;40m" + string + "\033[0;37;40m"


def White(
    string: str) -> str: return "\033[1;37;40m" + string + "\033[0;37;40m"

# Filters out words based on "gray" rule: removes words containing a specific character


def removeGray(char: str, index: int, softRemove: bool = False):
    # Optimize O(N^2) list.pop() to O(N) slice assignment with list comprehension
    dictionary[:] = [word for word in dictionary if not ((softRemove and word[index] != char) or (char in word))]

# Filters out words based on "yellow" rule: removes words missing the character at any index


def removeYellow(char: str, index: int):
    # Optimize O(N^2) list.pop() to O(N) slice assignment with list comprehension
    dictionary[:] = [word for word in dictionary if char in word and word[index] != char]

# Filters out words based on "green" rule: removes words that don't have the character at the exact index


def removeGreen(char: str, index: int):
    # Optimize O(N^2) list.pop() to O(N) slice assignment with list comprehension
    dictionary[:] = [word for word in dictionary if char in word and word[index] == char]

# Checks for duplicate characters in a word


def lookforDuplicate(word: str) -> bool:
    word = word.replace("?", "")  # Exclude placeholder characters
    return len(set(word)) < len(word)

# Evaluates the guessed word and filters the dictionary


def evaluateAttempt(word: str):
    previous = False
    char_index = 0
    for index, char in enumerate(word):
        if previous:  # Skip processing for placeholders
            previous = False
            continue
        softRemove = False
        if char == "?":
            removeYellow(word[index + 1], char_index)
            previous = True
        elif char == "!":
            removeGreen(word[index + 1], char_index)
            previous = True
        else:
            if lookforDuplicate(word):
                softRemove = True
            removeGray(char, char_index, softRemove)
        char_index += 1

# Checks if the guessed word exists in the dictionary


def isInDictionary(word: str) -> bool:
    return word in dictionary

# Validates the input word and ensures it follows the game's rules


def validateAttempt(word: str = "") -> tuple[int, str]:
    letterWord = "".join(filter(str.isalpha, word))
    if len(letterWord) != WORD_LENGTH:
        return ERROR, printToBashCommand("Red", f"\nWord must be {WORD_LENGTH} letters long")

    if not isInDictionary(letterWord):
        return ERROR, printToBashCommand("Red", f"\nWord \"{letterWord.upper()}\" does not belong to dictionary!")

    for i in range(len(word) - 1):
        if word[i] in "?!" and not word[i + 1].isalpha():
            return ERROR, printToBashCommand("Red", f"\nInvalid placement of \"{word[i]}\"")

    return SUCCESS, word

# Resets the character frequency map


def resetCharacters():
    global characters
    characters = dict.fromkeys(string.ascii_lowercase, 0)

# Counts the occurrences of each character in the dictionary


def countCharacters():
    for word in dictionary:
        for char in word:
            characters[char] += 1

# Selects the "most valuable" word based on character frequency


def selectWord(look_duplicate=False) -> str:
    resetCharacters()
    countCharacters()
    maxValuableWord = ""
    maxCount = 0
    for word in dictionary:
        if not look_duplicate and lookforDuplicate(word):
            continue
        count = sum(characters[char] for char in word)
        if count > maxCount:
            maxCount = count
            maxValuableWord = word
    return maxValuableWord

# Loads the dictionary from a file


def getDictionary():
    global dictionary
    with open(DICT_NAME, 'r') as file:
        dictionary = [line.strip().lower() for line in file if len(
            line.strip()) == WORD_LENGTH and line.strip().isalpha()]

# Returns the number of words remaining in the dictionary


def wordsLeft() -> int:
    return len(dictionary)

# Main backend function for Wordle logic


def processWordleAttempt(string: str = "") -> tuple[int, str]:
    try:
        errorNumber, attempt = validateAttempt(string)
        if errorNumber == ERROR:
            return errorNumber, attempt

        evaluateAttempt(attempt)

        with open('words.txt', 'w') as wordFile:
            wordFile.write("\n".join(dictionary))

        if len(dictionary) == 1:
            return 0, printToBashCommand("Red", f"\nCongratulations! Today's word was {dictionary[0].upper()}.")

        return SUCCESS, attempt
    except IndexError:
        return ERROR, printToBashCommand("Red", "\nNo words available!")
    except KeyboardInterrupt:
        return ERROR, printToBashCommand("Red", "\nProgram terminated by force")

# Prints messages to Bash with colored output


def printToBashCommand(color: str, string: str) -> str:
    bashCommand = f"powershell write-host -fore {color} {string}"
    os.system(bashCommand)
    return string


# Entry point
if __name__ == "__main__":
    getDictionary()
    processWordleAttempt()
