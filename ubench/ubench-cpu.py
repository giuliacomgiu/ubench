# • CPU intensive load: Implements the π calculation. A given number of
# threads calculate the π value with n decimal places. The number of
# threads, n and the execution time are configurable;
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
from threading import Thread

operation_count = 0
keep_running = False

def calculate_pi(digits):
    """
    Calculate pi to a specified number of digits
    """
    pi_value = mp.pi(dps = digits)

def get_system_usage():
    """
    Returns the current CPU and RAM usage percentages.
    """
    cpu_usage = psutil.cpu_percent(interval=1)  # CPU usage in percentage
    ram_usage = psutil.virtual_memory().percent  # RAM usage in percentage
    return cpu_usage, ram_usage

def worker_thread(digits):
    """
    Persistent worker thread that calculates pi continuously
    """
    global operation_count, keep_running
    while keep_running:
        calculate_pi(digits)
        operation_count += 1

def time_calculate_pi(digits, thread_count, time_limit, sampling_interval=1):
    global operation_count, keep_running
    total_time = 0
    start_time = pc()
    last_sample_time = start_time
    last_operation_count = 0

    # Create log file
    log_filename = f'benchmark_log_{int(start_time)}.csv'
    with open(log_filename, 'w') as log_file:
        log_file.write('timestamp,elapsed_time,throughput_instantaneous,operations_count,cpu_usage,ram_usage\n')

    print('Thread count: ', thread_count)
    print('Sampling interval: ', sampling_interval, 'seconds')
    print(f'Log file: {log_filename}')
    print('\nTimestamp\tElapsed(s)\tThroughput(ops/s)\tTotal Ops\tCPU(%)\tRAM(%)')
    print('-' * 80)

    # Create and start persistent worker threads
    keep_running = True
    threads = []
    for i in range(thread_count):
        t = Thread(target=worker_thread, args=(digits,))
        t.start()
        threads.append(t)

    while total_time < time_limit:
        total_time = pc() - start_time
        time_between_samples = total_time - (last_sample_time - start_time)

        # Check if sampling interval has passed
        if time_between_samples >= sampling_interval:
            elapsed = total_time
            ops_in_interval = operation_count - last_operation_count
            throughput_instantaneous = ops_in_interval / time_between_samples

            # Get system usage
            cpu_usage, ram_usage = get_system_usage()

            # Print to console
            print(f'{pc():.2f}\t\t{elapsed:.2f}\t\t{throughput_instantaneous:.2f}\t\t{operation_count}\t\t{cpu_usage:.1f}\t{ram_usage:.1f}')

            # Save to log file
            with open(log_filename, 'a') as log_file:
                log_file.write(f'{elapsed:.2f},{elapsed:.2f},{throughput_instantaneous:.2f},{operation_count},{cpu_usage:.1f},{ram_usage:.1f}\n')

            # Update for next sample
            last_sample_time = pc()
            last_operation_count = operation_count

    # Signal threads to stop and wait for them
    keep_running = False
    for t in threads:
        t.join()

    print('-' * 80)
    print('Total time: ', total_time)
    return total_time

total_time = time_calculate_pi(10000, 4, 6, sampling_interval=2)

print('\n=== Summary ===')
print('Operation count: ', operation_count)
print('Average throughput: ', operation_count / total_time, 'ops/s')