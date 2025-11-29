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
from threading import Thread

operation_count = 0

def runasthread(func):
    print('Running as thread')
    def wrapper(*args, **kwargs):
        thread = Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper
@runasthread

def calculate_pi(digits):
    """
    Calculate pi to a specified number of digits
    """
    # print('Calculating pi', digits)
    pi_value = mp.pi(dps = digits)
@runasthread

def get_system_usage():
    """
    Returns the current CPU and RAM usage percentages.
    """
    cpu_usage = psutil.cpu_percent(interval=1)  # CPU usage in percentage
    ram_usage = psutil.virtual_memory().percent  # RAM usage in percentage
    return cpu_usage, ram_usage

def thread_calculate_pi(digits, thread_count):
    global operation_count
    for count in range(thread_count):
        # Using `args` to pass positional arguments and `kwargs` for keyword arguments
        # t = threading.Thread(target=crawl, args=(link,), kwargs={"delay 2})
        # threads.append(t)
        calculate_pi(digits)
        operation_count += 1
    # print('Total time: ', total_time)

    # # Start each thread
    # for t in threads:
    #     t.start()

    # # Wait for all threads to finish
    # for t in threads:
    #     t.join()

def time_calculate_pi(digits, thread_count, time_limit, sampling_interval=1):
    global operation_count
    total_time = 0
    start_time = pc()
    last_sample_time = start_time
    last_operation_count = 0

    # Create log file
    log_filename = f'benchmark_log_{int(start_time)}.csv'
    with open(log_filename, 'w') as log_file:
        log_file.write('timestamp,elapsed_time,throughput_instantaneous,operations_count\n')

    print('Thread count: ', thread_count)
    print('Sampling interval: ', sampling_interval, 'seconds')
    print(f'Log file: {log_filename}')
    print('\nTimestamp\tElapsed(s)\tThroughput(ops/s)\tTotal Ops')
    print('-' * 60)

    while total_time < time_limit:
        thread_calculate_pi(digits, thread_count)
        total_time = pc() - start_time
        time_between_samples = total_time - (last_sample_time - start_time)

        # Check if sampling interval has passed
        if time_between_samples >= sampling_interval:
            elapsed = total_time
            ops_in_interval = operation_count - last_operation_count
            throughput_instantaneous = ops_in_interval / time_between_samples

            # Print to console
            print(f'{pc():.2f}\t\t{elapsed:.2f}\t\t{throughput_instantaneous:.2f}\t\t{operation_count}')

            # Save to log file
            with open(log_filename, 'a') as log_file:
                log_file.write(f'{elapsed:.2f},{elapsed:.2f},{throughput_instantaneous:.2f},{operation_count}\n')

            # Update for next sample
            last_sample_time = pc()
            last_operation_count = operation_count

    print('-' * 60)
    print('Total time: ', total_time)
    return total_time

total_time = time_calculate_pi(10000, 4, 6, sampling_interval=2)

print('\n=== Summary ===')
print('Operation count: ', operation_count)
print('Average throughput: ', operation_count / total_time, 'ops/s')