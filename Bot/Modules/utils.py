import os, sys, resources_path
from typing import Any, Callable, Iterable, List, Optional, Sized, TypeVar
import zc.lockfile # type: ignore

from unidecode import unidecode

class Utils:
    @staticmethod
    def is_duplicate(lock_name: str) -> Optional[Any]:
        try:
            lock: Any = zc.lockfile.LockFile(lock_name) 
            return lock 
        except zc.lockfile.LockError:  
            return None
    
    @staticmethod
    def has_terminal():
        return sys.stdout is not None
    
    @staticmethod
    async def get_the_forbidden_list() -> List[str]:
        path = os.path.join(resources_path.TEXTS, 'the_big_forbidden_list_of_bad_words.txt')
        with open(path, 'r') as file:
            forbidden_list = file.read().split(',')
            forbidden_list = IterTools.for_each_item(forbidden_list, StringTools.clean)
            
            return forbidden_list



class StringTools:
    @staticmethod
    def split_all(iter: Iterable[str], sep: str):
        return [string.split(sep) for string in iter]
    
    @staticmethod
    def clean_all(iter: Iterable[str]) -> List[str]:
        """Performs StringTools.clean in a Iterable of strings

        Args:
            iter (Iterable[str]): Strings to be cleaned

        Returns:
            List[str]: List of cleaned strings
        """
        return [StringTools.clean(msg) for msg in iter]
    
    @staticmethod
    def clean(msg: str):
        """
        Cleans a string by removing cursed characters and normalizing it for comparison.

        This method performs the following operations on the input string:
        - Converts to lowercase
        - Strips leading and trailing whitespace
        - Transliterates Unicode characters to their closest ASCII equivalents (e.g., 'é' → 'e')

        Parameters:
            msg (str): The input string to be cleaned.

        Returns:
            str: The cleaned, lowercase, ASCII-only version of the input string.
        """
        return unidecode(msg.lower().strip())



S = TypeVar("S")
class IterTools:
    @staticmethod
    def for_each_item(item_list: Iterable[S], *actions: Callable[[S], S]) -> List[S]:
        end_list: List[S] = []
        
        for item in item_list:
            new_item = item
            
            for action in actions:
                new_item = action(new_item)
                
            end_list.append(new_item)
        
        return end_list
    
    @staticmethod
    def get_smallest_size(iter_of_iters: Iterable[Sized]) :
        size = float('inf')
        for iter in iter_of_iters:
            if len(iter) < size:
                size = len(iter)
        return size