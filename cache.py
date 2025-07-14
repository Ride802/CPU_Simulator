from collections import OrderedDict

class Cache:
    def __init__(self, cache_size=16, verbose=True, eviction_policy='LFU', write_policy='write-through'):
        self.cache = OrderedDict() if eviction_policy == 'LRU' else {}           # inits empty dict to represent cache
        self.access_counts = {} if eviction_policy == 'LFU'else None  # inits empty dict to track freq for LFU eviction policy
        self.cache_size = cache_size
        self.verbose = verbose   # prints statements to the console for debugging, can be turned off by setting to false
        self.eviction_policy = eviction_policy
        self.write_policy = write_policy
        self.dirty_bits = {} if write_policy == 'write-back' else None
        self.flush_cache()

    def flush_cache(self):
        if self.verbose:    # if debugging is left on:
            print("Flushing cache...")
        self.cache.clear()
        if self.access_counts is not None:
            self.access_counts.clear()  # clears cache and LFU counter
        if self.dirty_bits is not None:
            self.dirty_bits.clear()   
        for i in range(self.cache_size):
            empty_address = f"empty_{i:04d}"   # creates unique empty address keys
            self.cache[empty_address] = ""      # associates the values at those addresses as empty strings
            if self.access_counts is not None:
                self.access_counts[empty_address] = 0   # initializes count for LFU tracking
            if self.dirty_bits is not None:
                self.dirty_bits[empty_address] = False      # clears bit count for write back tracking 
    
    def search_cache(self, address):
        if address not in self.cache:
            if self.verbose:
                print(f"Provided address ({address}) does not exist in cache.")
            return None
        if self.eviction_policy == 'LFU':
            self.access_counts[address] += 1   # increment counter for LFU
        elif self.eviction_policy == 'LRU':
            self.cache.move_to_end(address)
        if self.verbose:
            print(f"Found {self.cache[address]} at {address}")
        return self.cache[address]
    
    def write_cache(self, address, value):
        if len(self.cache) >= self.cache_size and address not in self.cache:    # if cache is full
            if self.eviction_policy == 'LFU':
                min_access_address = min(self.access_counts, key=self.access_counts.get)   # find the least accessed address
                if self.verbose:
                    print(f"Deleting {self.cache[min_access_address]} from {min_access_address}")
                    del self.cache[min_access_address]            # removes item from cache
                    del self.access_counts[min_access_address]    # resets access counter
                if self.dirty_bits is not None:
                    del self.dirty_bits[min_access_address]
            elif self.eviction_policy == 'LRU':
                min_access_address, _ = self.cache.popitem(last=False)
                if self.verbose:
                    print(f'Deleting {self.cache[min_access_address]} from {min_access_address}')
                if self.dirty_bits is not None:
                    del self.dirty_bits[min_access_address]
        if self.verbose:
            print(f"Writing {value} to {address}")   
        self.cache[address] = value   # writes value to address in cache
        if self.eviction_policy == 'LFU':
            self.access_counts[address] = self.access_counts.get(address, 0) + 1   # adds to LFU counter
        elif self.eviction_policy == 'LRU':
            self.cache.move_to_end(address)
        if self.write_policy == 'write-back':
            self.dirty_bits[address] = True