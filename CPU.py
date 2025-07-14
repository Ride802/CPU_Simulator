from memory import Memory
from cache import Cache


# Helper function to convert register string to index. I.e. register labelled 'R2' should correspond to int index 2
def convert_register_to_index(value):
    if not value.startswith('R') or not value[1:].isdigit():
        raise ValueError(f"Invalid register name: {value}")
    return int(value[1:])


# CPU class to implement the bulk of CPU Simulator requirements. Member properties include:
# CPU Counter - Int representing the number of the instruction being parsed
# Registers - List used to represent internal registers used by the CPU
# Cache Flag - boolean representing whether or not the cache is to be used
# Cache - instance of Cache object instantiated for CPU
# Memory Bus - instance of Memory Bus object instantiated for CPU

class CPU:

    def __init__(self, cpu_counter=0, num_registers=9, verbose = True, cache_size=16, eviction_policy='LFU', write_policy='write-through'):
        if not isinstance(num_registers, int) or num_registers <= 0:
            raise ValueError("num_registers must be a positive integer")
        if not isinstance(cpu_counter, int) or cpu_counter < 0:
            raise ValueError("cpu_counter must be a non-negative integer")
        self.cpu_counter = cpu_counter
        self.registers = [0] * num_registers
        self.cache_flag = False
        self.cache = Cache(cache_size=cache_size, verbose=verbose, eviction_policy=eviction_policy, write_policy=write_policy)
        self.memory_bus = Memory()
        self.verbose = verbose
        self.stats = {'cache_hits': 0, 'cache_misses': 0, 'instructions': 0}

    def increment_cpu_counter(self):
        self.cpu_counter += 1

    def reset_cpu_counter(self):
        self.cpu_counter = 0

    def set_cpu_counter(self, value):
        self.cpu_counter = value

    def get_cpu_counter(self):
        return self.cpu_counter

    def reset_registers(self):
        for i in range(len(self.registers)):
            self.registers[i] = 0

    def set_cache_flag(self, value):
        self.cache_flag = value

    def print_stats(self):
        print(f"Instructions executed: {self.stats['instructions']}")
        print(f"Cache hits: {self.stats['cache_hits']}")
        print(f"Cache misses: {self.stats['cache_misses']}")

    # --- These methods are copies of methods in the Cache and Memory classes and could be considered redundant        

    def flush_cache(self):
        self.cache.flush_cache()
    def search_cache(self, address):
        return self.cache.search_cache(address)
    def write_cache(self, address, value):
        self.cache.write_cache(address, value)
    def search_memory_bus(self, address):
        return self.memory_bus.search_memory_bus(address)
    def write_memory_bus(self, address, value):
        self.memory_bus.write_memory_bus(address, value)

    # --- Sample implementations for an ISA that can handle MIPS instructions 

    def jump_instruction(self, target):
        if self.verbose:
            print("Setting cpu counter to {}".format(target))
        self.cpu_counter = int(target)


    def add_instruction(self, destination, source, target):
        destination_idx = convert_register_to_index(destination)
        source_idx = convert_register_to_index(source)
        target_idx = convert_register_to_index(target)

        if self.verbose:
            print("Adding {} to {} and storing result {} at {}".format(self.registers[target_idx], self.registers[source_idx], (self.registers[source_idx] + self.registers[target_idx]), self.registers[destination_idx]))
        self.registers[destination_idx] = self.registers[source_idx] + self.registers[target_idx]


    def add_i_instruction(self, destination, source, immediate):
        destination_idx = convert_register_to_index(destination)
        source_idx = convert_register_to_index(source)
        immediate = int(immediate)
        if self.verbose:
            print("Adding {} to {} and storing result {} at {}".format(immediate, self.registers[source_idx], (self.registers[source_idx] + immediate), self.registers[destination_idx]))
        self.registers[destination_idx] = self.registers[source_idx] + int(immediate)
    
    
    def sub_instruction(self, destination, source, target):   # subtraction source - target
        destination_idx = convert_register_to_index(destination)
        source_idx = convert_register_to_index(source)
        target_idx =  convert_register_to_index(target)

        if self.verbose:
            print("Subtracting {} from {} and storing result {} at {}".format(self.registers[target_idx], self.registers[source_idx], (self.registers[source_idx] - self.registers[target_idx]), self.registers[destination_idx]))
        self.registers[destination_idx] = self.registers[source_idx] - self.registers[target_idx]


    def slt_instruction(self, destination, source, target):   # if s < t, d = 1; else d = 0
        destination_idx = convert_register_to_index(destination)
        source_idx = convert_register_to_index(source)
        target_idx =  convert_register_to_index(target)
        value = 1 if self.registers[source_idx] < self.registers[target_idx] else 0
        
        if self.verbose:
            print('Setting register {} to {}'.format(destination_idx, value))
        self.registers[destination_idx] = value


    def bne_instruction(self, source, target, offset):   # if s != t, counter = (counter + 4) + 4 * offset
        source_idx = convert_register_to_index(source)
        target_idx =  convert_register_to_index(target)

        if self.registers[source_idx] != self.registers[target_idx]:
            if self.verbose:
                print("Increasing counter by offset")
            self.cpu_counter = self.cpu_counter + 4 + 4 * int(offset)


    def j_instruction(self, target):   # counter = 4 * target
        if self.verbose:
            print("Increasing counter by target")
        self.cpu_counter = 4 * int(target)


    def jal_instruction(self, target):   # r7 = counter + 4, counter = 4 * target
        self.registers[7] = self.cpu_counter + 4
        self.cpu_counter = 4 * int(target)


    # --- Method to implement cache instruction. 0 = OFF, 1 = ON, 2 = Flush Cache
    def cache_instruction(self, value):
        value = int(value)
        if value == 0:
            if self.verbose:
                print('No cache flag')
            self.set_cache_flag(False)
        if value == 1:
            if self.verbose:
                print('CACHE FLAG RISEN')
            self.set_cache_flag(True)
        if value == 2:
            if self.verbose:
                print('Flushing cache...')
            self.flush_cache()


    # --- For these methods, we will need to convert (register + offset) to a binary string since Memory uses binary string addresses, while Cache uses arbitrary strings
    def lw_instruction(self, source, target, offset):   # target = MEM[source + offset]
        source_idx = convert_register_to_index(source)
        target_idx = convert_register_to_index(target)
        address_int = self.registers[source_idx] + int(offset)
        address = f"{address_int:0{self.memory_bus.bit_width}b}"  # this is the conversion to a binary string

        if self.cache_flag:                         # to decide whether to access cache or memory directly
            value = self.search_cache(address)      
            if value is None:
                self.stats['cache_misses'] += 1
                value = self.memory_bus.search_memory_bus(address)
                if value is not None:
                    self.cache.write_cache(address, value)
            else:
                self.stats['cache_hits'] += 1
        else:
            value = self.memory_bus.search_memory_bus(address)
        if value is None:
            raise ValueError(f"Invalid memory address: {address}")
        self.registers[target_idx] = value


    def sw_instruction(self, source, target, offset):   # MEM[source + offset] = target
        source_idx = convert_register_to_index(source)
        target_idx = convert_register_to_index(target)
        address_int = self.registers[source_idx] + int(offset)
        address = f"{address_int:0{self.memory_bus.bit_width}b}"
        value = self.registers[target_idx]
        if self.cache_flag:
            self.cache.write_cache(address, value)
        self.memory_bus.write_memory_bus(address, value)


    def halt_instruction(self):   # terminate execution
        if self.verbose:
            print("Termininating...")
        return False

    # Main parser method used to interpret instructions from input file.
    # Check value of operator and call subsequent helper function
    def parse_instruction(self, instruction):
        try:
            instruction = instruction.strip()
            if not instruction:
                raise ValueError("Empty instruction")
            instruction_parsed = instruction.split(",")
            if self.verbose:
                print(f"Reading instruction: {instruction}")
            self.increment_cpu_counter()
            op = instruction_parsed[0].upper()
            handlers = {
                "ADD": (4, self.add_instruction),
                "ADDI": (4, self.add_i_instruction),
                "SUB": (4, self.sub_instruction),
                "SLT": (4, self.slt_instruction),
                "BNE": (4, self.bne_instruction),
                "J": (2, self.j_instruction),
                "JAL": (2, self.jal_instruction),
                "LW": (4, self.lw_instruction),
                "SW": (4, self.sw_instruction),
                "CACHE": (2, lambda x: self.cache_instruction(int(x))),
                "HALT": (1, self.halt_instruction)
            }
            if op not in handlers:
                raise ValueError(f"Unknown instruction: {op}")
            expected_args, handler = handlers[op]
            if len(instruction_parsed) != expected_args:
                raise ValueError(f"Instruction {op} expects {expected_args - 1} arguments, got {len(instruction_parsed)-1}")
            self.stats['instructions'] += 1
            self.increment_cpu_counter()
            return handler(*instruction_parsed[1:])
        except (IndexError, ValueError) as e:
            if self.verbose:
                print(f"Invalid instruction: {instruction} ({str(e)})")
            return None
        
    # --- add a method to run the program until HALT
    def run_program(self, instructions):
        self.reset_cpu_counter()
        while self.cpu_counter < len(instructions):
            result = self.parse_instruction(instructions[self.cpu_counter])
            if result is False:
                break