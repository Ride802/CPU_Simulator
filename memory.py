class Memory:
    def __init__(self, memory_bus_size=128, bit_width=8, verbose=True):
        if not isinstance(memory_bus_size, int) or memory_bus_size <= 0:
            raise ValueError("memory_bus_size must be a positive integer")
        self.memory_bus = {}   # bus is implemented as a dictionary {Key=address: Value=value}
        self.bit_width = bit_width
        self.memory_bus_size = memory_bus_size
        self.verbose = verbose   # prints statements to the console for debugging, can be turned off by setting to false
        self.init_memory_bus() # initializes itself with the following function

    def init_memory_bus(self):
        if self.verbose:
            print("Initializing memory...")
        bit_width = max(8, (self.memory_bus_size-1).bit_length())
        for i in range(self.memory_bus_size):   
            self.memory_bus[f"{i:0{bit_width}b}"] = 0    # converts each integer in the memory size to an x digit binary string number based on the size of memory, and stores it as a key in the memory_bus dictionary  

    def search_memory_bus(self, address):
        if not isinstance(address, str) or not all(c in '01' for c in address) or len(address) != self.bit_width:
            raise ValueError(f"Invalid memory address at {address}. Ensure address is a binary string of length {self.bit_width}")  # if an invalid address is provided, return error
        if self.verbose:
            print(f"Found {self.memory_bus.get(address)} at {address}")
        return self.memory_bus.get(address)                                    
    
    def write_memory_bus(self, address, value):
        if not isinstance(address, str) or not all(c in '01' for c in address) or len(address) != self.bit_width:
            if self.verbose:
                print(f"Provided address ({address}) does not exist in memory. Please ensure address is a binary string of length {self.bit_width}")
            raise ValueError(f"Invalid memory address: {address}")
        if self.verbose:
            print(f"Writing {value} to {address}...")
        self.memory_bus[address] = value
        return True
    
    def clear_memory(self):       # function to clear memory
        self.memory_bus.clear()
        self.init_memory_bus()