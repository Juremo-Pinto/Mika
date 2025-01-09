from typing import Callable


class QuickCache:
        def __init__(self):
            self.cache = {}
        
        async def get_or_compute(self, key: int|str, no_value_action: Callable[[int|str], int|str]):
            if self.cache.get(key) is None:
                print("QuickCache Test Output: Compute")
                self.cache[key] = await no_value_action(key)
            else: 
                print("QuickCache Test Output: Get")
            
            return self.cache[key]