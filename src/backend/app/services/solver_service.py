from typing import List
import string
from app.models.schemas import Attempt
from app.repositories.dictionary_repo import DictionaryRepository

class SolverService:
    """
    Service layer containing the core business logic for solving Wordle.
    """
    
    @staticmethod
    def apply_feedback(dictionary: List[str], attempt: Attempt) -> List[str]:
        """
        Filters the dictionary based on a single attempt's feedback.
        
        Args:
            dictionary (List[str]): The current list of possible words.
            attempt (Attempt): The attempt to apply.
            
        Returns:
            List[str]: The filtered list of possible words.
        """
        word = attempt.word.lower()
        feedback = attempt.feedback.upper()
        
        filtered_dict = dictionary.copy()
        
        for i in range(5):
            char = word[i]
            fb = feedback[i]
            
            if fb == 'G':
                filtered_dict = [w for w in filtered_dict if w[i] == char]
            elif fb == 'Y':
                filtered_dict = [w for w in filtered_dict if char in w and w[i] != char]
            elif fb == 'B':
                has_green_yellow = any((word[j] == char and feedback[j] in ['G', 'Y']) for j in range(5))
                if has_green_yellow:
                    filtered_dict = [w for w in filtered_dict if w[i] != char]
                else:
                    filtered_dict = [w for w in filtered_dict if char not in w]

        return filtered_dict

    @staticmethod
    def get_optimal_guess(dictionary: List[str]) -> str:
        """
        Calculates the most statistically valuable next guess.
        
        Args:
            dictionary (List[str]): The current list of possible words.
            
        Returns:
            str: The best word to guess next.
        """
        if not dictionary:
            return ""
        
        char_counts = {char: 0 for char in string.ascii_lowercase}
        joined_dict = "".join(dictionary)
        for char in char_counts:
            char_counts[char] = joined_dict.count(char)
            
        max_val = -1
        best_word = ""
        
        for word in dictionary:
            unique_chars = set(word)
            score = sum(char_counts[char] for char in unique_chars)
            if score > max_val:
                max_val = score
                best_word = word
                
        return best_word

    @staticmethod
    def solve(attempts: List[Attempt]) -> tuple[int, str, List[str]]:
        """
        Processes a list of attempts and returns the optimal next guess and remaining words.
        
        Args:
            attempts (List[Attempt]): The history of attempts.
            
        Returns:
            tuple[int, str, List[str]]: A tuple containing the count of remaining words,
                                        the optimal next guess, and the list of remaining words.
        """
        current_dict = DictionaryRepository.get_all()
        for attempt in attempts:
            current_dict = SolverService.apply_feedback(current_dict, attempt)
            
        optimal_guess = SolverService.get_optimal_guess(current_dict)
        return len(current_dict), optimal_guess, current_dict
