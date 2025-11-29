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
        # t = threading.Thread(target=crawl, args=(link,), kwargs={"delay": 2})
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

def time_calculate_pi(digits, thread_count, time_limit):
    total_time = 0
    start_time = pc()
    print('Thread count: ', thread_count)
    while total_time < time_limit:
        thread_calculate_pi(digits, thread_count)
        total_time = pc() - start_time
    print('Total time: ', total_time)
    return total_time

total_time = time_calculate_pi(10000, 4, 6)

print('Operation count: ', operation_count)
print('Operation per second: ', operation_count / total_time)

