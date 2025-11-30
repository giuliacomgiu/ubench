# • CPU intensive load: Implements the π calculation. A given number of
# threads calculate the π value with n decimal places. The number of
# threads, n and the execution time are configurable;
# • Memory intensive load: Implements read and write operations on a
# pre-allocated vector of integers with the size of m MB. The runtime
# and m are benchmark parameters;
# • Disk intensive load: Implements random read and write operations in
# the stable storage. For each thread, n files are created with the size of
# m MB. The number of threads, size of the block, percentage of readings
# and writes, and runtime are configurable, along with n and m.
# The implemented benchmarks generate log files with the throughput of
# operations measured throughout the execution. These data are made
# available in time series, with an adjustable sampling interval.

from mpmath import mp
import psutil
import os
from time import perf_counter as pc
from time import sleep
from threading import Thread
import random

# operation_count = 0
keep_running = False
bytearray_list = []

def memory_init(size_mb, chunk_size):
    """
    Function to allocate memory
    """
    global bytearray_list
    for _ in range(size_mb):
        bytearray_chunk = bytearray(random.randbytes(chunk_size))  # Set all bytes in the array to a random value
        bytearray_list.append(bytearray_chunk)  # Allocate 1 MB at a time

def memory_load(chunk_size):
    """
    Function to stress memory access
    """
    global bytearray_list
    for bytearray_chunk in bytearray_list:
        idx = random.randint(0, chunk_size - 1)
        idx2 = random.randint(0, chunk_size - 1)
        temp = bytearray_chunk[idx]
        bytearray_chunk[idx] = bytearray_chunk[idx2]
        bytearray_chunk[idx2] = temp

def memory_release():
    global bytearray_list
    bytearray_list.clear()
    del bytearray_list

def get_system_usage():
    """
    Returns the current CPU and RAM usage percentages.
    """
    cpu_usage = psutil.cpu_percent(interval=1)  # CPU usage in percentage
    ram_usage = psutil.virtual_memory().percent  # RAM usage in percentage
    return cpu_usage, ram_usage

def time_use_mem(size_mb, chunk_size=1024 * 1024, time_limit=10, sampling_interval=1):
    memory_init(size_mb, chunk_size)

    operation_count = 0
    last_operation_count = 0
    total_time = 0
    start_time = pc()
    last_sample_time = start_time


    # Create log file
    # log_filename = f'benchmark_log_{int(start_time)}.csv'
    # with open(log_filename, 'w') as log_file:
    #     log_file.write('timestamp,elapsed_time,throughput_instantaneous,operations_count,cpu_usage,ram_usage\n')
    # print(f'Log file: {log_filename}')

    print('Sampling interval: ', sampling_interval, 'seconds')
    print('\nTimestamp\tElapsed(s)\tThroughput(ops/s)\tTotal Ops\tCPU(%)\tRAM(%)')
    print('-' * 80)

    # Create and start persistent worker threads
    while total_time < time_limit:
        total_time = pc() - start_time
        time_between_samples = total_time - (last_sample_time - start_time)
        # print('time_between_samples: ', time_between_samples)

        memory_load(chunk_size)
        operation_count += 1
        # sleep(sampling_interval)

        # # Check if sampling interval has passed
        if time_between_samples >= sampling_interval:
            elapsed = total_time
            ops_in_interval = operation_count - last_operation_count
            throughput_instantaneous = ops_in_interval / time_between_samples

            # Get system usage
            cpu_usage, ram_usage = get_system_usage()

            # Print to console
            print(f'{pc():.2f}\t\t{elapsed:.2f}\t\t{throughput_instantaneous:.2f}\t\t{operation_count}\t\t{cpu_usage:.1f}\t{ram_usage:.1f}')

            # Save to log file
            # with open(log_filename, 'a') as log_file:
            #     log_file.write(f'{elapsed:.2f},{elapsed:.2f},{throughput_instantaneous:.2f},{operation_count},{cpu_usage:.1f},{ram_usage:.1f}\n')

            # Update for next sample
            last_sample_time = pc()
            last_operation_count = operation_count

    memory_release()
    print('-' * 80)
    print('Total time: ', total_time)
    return total_time, operation_count

total_time, operation_count = time_use_mem(size_mb=1024, chunk_size=1024 * 1024, time_limit=10, sampling_interval=2)

print('\n=== Summary ===')
print('Operation count: ', operation_count)
print('Average throughput: ', operation_count / total_time, 'ops/s')