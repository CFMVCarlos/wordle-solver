import os
from typing import List

class DictionaryRepository:
    """
    Repository pattern for managing the word dictionary data.
    """
    _dictionary: List[str] = []
    
    @classmethod
    def load(cls) -> None:
        """
        Loads the dictionary file into memory if not already loaded.
        
        Raises:
            RuntimeError: If the dictionary file is not found.
        """
        if not cls._dictionary:
            dict_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "CSW19.txt")
            try:
                with open(dict_path, 'r') as file:
                    cls._dictionary = [line.strip().lower() for line in file if len(line.strip()) == 5 and line.strip().isalpha()]
            except FileNotFoundError:
                raise RuntimeError(f"Dictionary file not found at {dict_path}.")

    @classmethod
    def get_all(cls) -> List[str]:
        """
        Returns a copy of the entire dictionary.
        
        Returns:
            List[str]: A list of all valid words.
        """
        if not cls._dictionary:
            cls.load()
        return cls._dictionary.copy()
