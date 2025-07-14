from CPU import CPU

INSTRUCTION_INPUT_FILE = "instruction_input.txt"
DATA_INPUT_FILE = "data_input.txt"


# Generate list of instructions from input file, use lambda function to strip off '\n' character from each line
def fetch_instructions():
    try:
        with open(INSTRUCTION_INPUT_FILE, 'r') as instruction_file:
            instructions = [s.strip() for s in instruction_file.readlines() if s.strip()]
            return instructions
    except FileNotFoundError:
        print(f'Error: {INSTRUCTION_INPUT_FILE} not found')
        return []
    except Exception as e:
        print(f'Error reading {INSTRUCTION_INPUT_FILE}: {str(e)}')
    return []


# Generate list of data inputs to initialize the memory bus from.
def fetch_data():
    try:
        with open(DATA_INPUT_FILE, 'r') as data_file:
            data = [s.strip() for s in data_file.readlines() if s.strip()]
            return data
    except FileNotFoundError:
        print(f'Error: {DATA_INPUT_FILE} not found')
        return []
    except Exception as e:
        print(f'Error reading {DATA_INPUT_FILE}: {str(e)}')
        return []

# Method to write each value from data_input file to CPU's memory bus
def initialize_memory_bus(cpu):
    data_loaded = fetch_data()
    for data in data_loaded:
        try:
            data_parsed = data.split(",")
            if len(data_parsed) != 2:
                raise ValueError(f'Invalid data format: {data}')
            cpu.memory_bus.write_memory_bus(data_parsed[0], int(data_parsed[1]))
        except ValueError as e:
            print(f'Error initializing memory: {str(e)}')

# Method to send instructions line-by-line to CPU object
def send_instructions_to_cpu(cpu):
    instructions_loaded = fetch_instructions()
    if instructions_loaded:
        cpu.run_program(instructions_loaded)


# Start of Python script to run the CPU simulator
my_cpu = CPU()
print("---------------------------------------------------")
print("Welcome to the Python CPU Simulator!")
print("---------------------------------------------------")
print("Initializing Memory Bus from data input file...")
initialize_memory_bus(my_cpu)
print("Memory Bus successfully initialized")
print("---------------------------------------------------")
print("Sending instructions to CPU...")
send_instructions_to_cpu(my_cpu)
print("---------------------------------------------------")
print("Terminating CPU Processing...")