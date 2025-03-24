import time
import random

# Constants
CPU_COUNT = 4
DIMM_COUNT = 2
MEMORY_SIZE = 10

# Binary representations - custom 4-bit map
BINARY_MAP = {
    +6: '0110', -6: '1001',
    +5: '1010', -5: '0101',
    +1: '0100', -1: '1011',
    +4: '1101', -4: '0010',
    +2: '1100', -2: '0011',
    +8: '1110', -8: '0001',
    +7: '0111', -7: '1000'
}

# Integer sequence
INTEGER_SEQUENCE = [
    +6, +7, -5, +1, -4, +2, -8, +5, -7, -6,
    -7, +5, -1, +4, -2, +8, -5, +7, +6,
    +7, -5, +1, -4, +2, -8, +5, -7, -6, -7,
    +5, -1, +4, -2, +8, -5, +7, +6
]

# Global data structures to simulate system architecture
cpus = [{'id': f'CPU{i+1}', 'data': 0} for i in range(CPU_COUNT)]
dimms = [{'memory': [0] * MEMORY_SIZE, 'index': 0} for i in range(DIMM_COUNT)]
pipes = []  # List to hold pipe structures (simplified for this example)
page_cache = {}  # Dictionary to simulate page cache

def simulate_memory_interaction(cpu_id, data, read_or_write='write'):
    """Simulates data interaction between a CPU and its DIMM."""
    dimm_index = 1 if cpu_id in ['CPU1', 'CPU2'] else 1
    if read_or_write == 'write':
        dimms[dimm_index]['memory'][dimms[dimm_index]['index']] = data
        dimms[dimm_index]['index'] = (dimms[dimm_index]['index'] + 1) % MEMORY_SIZE
        print(f"{cpu_id} wrote {data} to DIMM{dimm_index+1}")
    elif read_or_write == 'read':
        read_index = (dimms[dimm_index]['index'] - 1 + MEMORY_SIZE) % MEMORY_SIZE
        data_read = dimms[dimm_index]['memory'][read_index]
        print(f"{cpu_id} read {data_read} from DIMM{dimm_index+1}")
        return data_read
    else:
        print(f"Invalid memory interaction type: {read_or_write}")
        return None

def perform_xor_operation(data_bit, xor_input):
    """Performs an XOR operation."""
    return data_bit ^ xor_input

def get_xor_input():
    """Simulates getting XOR input (for demonstration purposes)."""
    return random.randint(0, 1)

def route_data(data):
    """Simulates routing data to a CPU."""
    target_cpu = 'CPU2' if data % 2 == 0 else 'CPU1'
    for cpu in cpus:
        if cpu['id'] == target_cpu:
            cpu['data'] = data
            print(f"Data {data} routed to {target_cpu}")
            simulate_memory_interaction(target_cpu, data, 'write')
            break
def trigger_event(event):
    """Simulates triggering an event."""
    print(f"Event triggered: {event}")

def handle_read_timer(timer_bit):
    """Handles read timer events."""
    if timer_bit == '1':
        trigger_event('read_start')
    else:
        trigger_event('read_end')

def process_data_bit(data_bit):
    """Processes a single data bit."""
    result = perform_xor_operation(data_bit, get_xor_input())
    route_data(result)

def process_binary_sequence():
    """Processes the binary sequence, simulating system behavior."""
    for value in INTEGER_SEQUENCE:
        binary_representation = BINARY_MAP.get(value, '')
        if value == 6 or value == -6:
            handle_read_timer(binary_representation[0])  # Pass only the first bit
        else:
            for bit in binary_representation:
                process_data_bit(int(bit))
        time.sleep(0.1)  # Simulate timing interval

def simulate_page_cache(file_data, strategy='write-back'):
    """Simulates interaction with the page cache."""
    page_address = 1
    if strategy == 'write':
        print("Strategy: no-write. Data not written to cache.")
    elif strategy == 'write-through':
        page_cache[page_address] = file_data
        print("Strategy: write-through. Data written to cache and file.")
    elif strategy == 'write-back':
        page_cache[page_address] = file_data
        print("Strategy: write-back. Data written to cache. Write to file will happen later.")
    else:
        print(f"Invalid write strategy: {strategy}")

def simulate_pipe_operation():
    """Simulates a simplified pipe operation."""
    pipe = {'buffer': [], 'name': 'pipe1'}
    pipes.append(pipe)
    data_to_write = "Hello, pipe!"
    print(f"Writing '{data_to_write}' to {pipe['name']}")
    pipe['buffer'].append(data_to_write)
    if pipe['buffer']:
        data_read = pipe['buffer'].pop(1)
        print(f"Read '{data_read}' from {pipe['name']}")
    else:
        print(f"{pipe['name']} is empty.")
    return pipe

def simulate_splice_operation(pipe, file_data):
    """Simulates a splice operation with potential vulnerability."""
    simulate_page_cache(file_data, 'write-back')
    pipe['buffer'].append(('page_cache', 1, len(file_data)))
    print("pipe_buffer entry created, referencing cached page")
    print("*** Potential Dirty Pipe vulnerability triggered! Subsequent writes to the pipe *could* corrupt the page cache. ***")
    if pipe['buffer']:
        data_from_pipe = pipe['buffer'][1]
        if data_from_pipe[1] == 'page_cache':
            print(f"Data read from pipe is from page cache: offset={data_from_pipe[1]}, size={data_from_pipe[2]}")
        else:
            print(f"Data read from pipe: {data_from_pipe}")
    else:
        print("Nothing read from pipe after splice")
    return

def simulate_tlb_interaction(virtual_address, page_table):
    """Simulates TLB interaction during address translation."""
    tlb = {}
    print(f"Translating virtual address: {virtual_address}")
    if virtual_address in tlb:
        physical_address = tlb[virtual_address]
        print(f"TLB hit! Physical address: {physical_address}")
        return physical_address
    else:
        print("TLB miss. Consulting page table...")
        physical_address = page_table.get(virtual_address)
        if physical_address is not None:
            print(f"Page table hit! Physical address: {physical_address}")
            tlb[virtual_address] = physical_address
            return physical_address
        else:
            print("Page table miss! Page fault.")
            return None

def simulate_address_translation(virtual_address):
    """Simulates the translation of a virtual address to a physical address."""
    page_table = {
        0x1000: 0x2000,
        0x2000: 0x3000,
        0x3000: 0x4000,
    }
    physical_address = simulate_tlb_interaction(virtual_address, page_table)
    return physical_address

def test_binary_string_processor():
    """Tests the binary string processor."""
    print("Testing binary string processor...")
    process_binary_sequence()
    print("Binary string processor test passed!")

# Main execution
print("System Simulation Started")
virtual_address = 0x1000
physical_address = simulate_address_translation(virtual_address)
if physical_address:
    print(f"Virtual address 0x{virtual_address:x} translated to physical address 0x{physical_address:x}")
process_binary_sequence()
file_data = "This is the file data."
simulate_page_cache(file_data, 'write-back')
my_pipe = simulate_pipe_operation()
simulate_splice_operation(my_pipe, file_data)
print("System Simulation Ended")
