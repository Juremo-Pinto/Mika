import asyncio
import os
from typing import Callable, List, Tuple, Union
import warnings
import time
import json

class QuickCache:
    def __init__(self, filter_keys: Tuple[str, ...] | None = None, max_cache_size: int = None):
        # Initialize the cache manager with optional filter keys
        self.filter_keys = filter_keys
        self.max_size = max_cache_size
        
        self.are_filter_keys_enabled = self.filter_keys is not None
        self.is_size_capped = self.max_size is not None and self.max_size != 0
        
        self.cache = {}
    
    
    async def _get_filter_index(self, number):
        # Retrieve the index of the filter key
        return self.filter_keys[number]
    
    async def _set_filter_parameters(self, key, result_from_callback):
        # Set the filter parameters for the specified key in the cache
        if not self.are_filter_keys_enabled:
            return
        
        self.cache[key].setdefault('filter_parameters', {})
        
        for filter_key in enumerate(self.filter_keys):
            self.cache[key]['filter_parameters'][filter_key[1]] = result_from_callback[filter_key[0] + 1]
    
    
    async def _evaluate_ttl(self):
        now = time.time()
        
        for key in self.cache:
            if 'time' in self.cache[key] and now > self.cache[key]['time']['expiration_date']:
                del self.cache[key]
    
    async def _set_ttl(self, key, ttl_secs):
        # Set the time to live (TTL) for a new item created
        self._evaluate_ttl()
        
        if ttl_secs == 0:
            return
        
        now = time.time()
        
        self.cache[key].setdefault('time', {})
        self.cache[key]['time']['expiration_date'] = now + ttl_secs
    
    
    async def _cache_size_monitor(self):
        if not self.is_size_capped:
            return
        
        if len(self.cache) > self.max_size:
            item_to_remove = next(iter(self.cache))
            self.cache.pop(item_to_remove)
    
    
    async def _compute_multiple(self, result_from_callback):
        for key in result_from_callback:
            self.cache[key] = result_from_callback[key]
    
    async def _compute(self, key, result_from_callback, multiple_compute):
        if multiple_compute:
            await self._compute_multiple(result_from_callback) # Multi Compute
            return
        
        self.cache.setdefault(key, {})
        self.cache[key]['value'] = result_from_callback[0] if self.are_filter_keys_enabled else result_from_callback # Single Compute
    
    
    async def get_or_compute(
                        self,
                        key: int|str,
                        calculate_on_miss: Callable[[any], Union[any, Tuple[any, ...]]], # Callback to compute value if not in cache, must output a dict with "key: value" in case multi_compute is enabled
                        *,
                        cache_ttl: int = 0,
                        multiple_compute: bool = False, # If True, separates dict output into cache
                        metric_callback_on_miss: Callable[[None], None] = None # Optional metric callback
                        ):
        
        if self.cache.get(key) is None:
            print("CacheManager: Compute")
            result_from_callback = await calculate_on_miss(key)
            
            await self._compute(key, result_from_callback, multiple_compute) # compute
            
            await self._set_filter_parameters(key, result_from_callback) # Filtering
            await self._set_ttl(key, cache_ttl) # TTl
            await self._cache_size_monitor() # Size cap
            
            if metric_callback_on_miss is not None:
                await metric_callback_on_miss() # Call metric function if provided
        else: 
            print("CacheManager: Get")
        
        return self.cache[key]['value']
    
    
    
    async def get_all_cached(self, filter_keys: List[str] = None, match_all = True):
        # Retrieve all cached values, optionally filtered by keys
        await self._evaluate_ttl()
        
        if not filter_keys:
            return self.cache
        elif not self.are_filter_keys_enabled:
            warnings.warn("Filter keys will only work if filter_keys is enabled.")
            return self.cache
        
        return await self._filter_cache_results(filter_keys=filter_keys, match_all=match_all)
    
    
    async def _filter_cache_results(self, filter_keys, match_all):
        # Filter cache results based on provided keys and matching criteria
        operator = all if match_all else any
        
        return_list = (
            (lambda number: [filter_keys[self._get_filter_index(number)], None])
            if match_all else
            (lambda number: [filter_keys[self._get_filter_index(number)]])
        )
        
        return [
            item['value']
            for item in self.cache
            if operator(
                item['filter_parameters'][self._get_filter_index(number)] in return_list(number)
                for number in range(len(filter_keys))
            )
        ]
    
    
    async def reset(self):
        # Reset the cache
        self.cache = {}



class JsonCache:
    def __init__(self, cache_file_path: str, size_limit = None):
        self.cache_file_path = cache_file_path
        
        self.cache_keys = {}
        
        self.size_limit = size_limit
        self.is_size_capped = size_limit is not None
        
        if not os.path.exists(cache_file_path):
            os.makedirs(os.path.dirname(cache_file_path), exist_ok=True)
            with open(cache_file_path, 'w') as f:
                json.dump({}, f)
    
    def _evaluate_size(self, cache: dict):
        if self.is_size_capped:
            while len(cache) > self.size_limit:
                item_to_remove = next(iter(cache))
                cache.pop(item_to_remove)
        
        return cache
    
    def _dump(self, cache, file):
        file.seek(0)
        json.dump(cache, file)
        file.truncate()
        return file
    
    def modify(self, key, value):
            with open(self.cache_file_path, 'r+') as file:
                cache = json.load(file)
                
                if value:
                    cache[key] = value
                else:
                    del cache[key]
                
                cache = self._evaluate_size(cache)
                self._dump(cache, file)
    
    def get(self, key, bump_to_top = False):
            with open(self.cache_file_path, 'r' if not bump_to_top else 'r+') as file:
                cache = json.load(file)
                cache = self._evaluate_size(cache)
                
                value = cache.get(key)
                
                if value and bump_to_top:
                    cache[key] = cache.pop(key)
                    self._dump(cache, file)
                
                return value
    
    def has(self, key):
        if not self.cache_keys:
            with open(self.cache_file_path, 'r') as file:
                cache = json.load(file)
                self.cache_keys = list(cache.keys())
        
        return key in self.cache_keys
    
    def reset_keys(self):
        self.cache_keys = {}



async def test():
    jogn = {}
    i = 0
    while True:
        jogn[i] = i
        
        if len(jogn) > 10:
            b = next(iter(jogn))
            real = jogn.pop(b)
        
        await asyncio.sleep(1)
        
        print(jogn)
        
        i+=1


if __name__ == "__main__":
    asyncio.run(test())
