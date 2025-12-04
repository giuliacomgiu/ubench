# • CPU intensive load: Implements the π calculation. A given number of
# processes calculate the π value with n decimal places. The number of
# processes, n and the execution time are configurable;
# The implemented benchmarks generate log files with the throughput of
# operations measured throughout the execution. These data are made
# available in time series, with an adjustable sampling interval.

from mpmath import mp
import psutil
from time import perf_counter as pc
from multiprocessing import Process, Value
import ctypes

def calculate_pi(digits):
    """
    Calculate pi to a specified number of digits
    """
    mp.dps = digits
    pi_value = mp.pi

def get_system_usage():
    """
    Returns the current CPU and RAM usage percentages.
    """
    cpu_usage = psutil.cpu_percent(interval=0)  # CPU usage in percentage
    ram_usage = psutil.virtual_memory().percent  # RAM usage in percentage
    return cpu_usage, ram_usage

def worker_process(digits, operation_count, keep_running):
    """
    Persistent worker process that calculates pi continuously
    """
    while keep_running.value:
        calculate_pi(digits)
        with operation_count.get_lock():
            operation_count.value += 1

def time_calculate_pi(digits, process_count, time_limit, sampling_interval=1, sys_usage=True):
    # Shared variables between processes
    operation_count = Value(ctypes.c_long, 0)
    keep_running = Value(ctypes.c_bool, True)

    total_time = 0
    start_time = pc()
    last_sample_time = start_time
    last_operation_count = 0

    # Create log file
    log_filename = f'benchmark_cpu_log_{int(start_time)}.csv'
    with open(log_filename, 'w') as log_file:
        log_file.write('timestamp,elapsed_time,throughput_instantaneous,operations_count,cpu_usage,ram_usage\n')

    print('=== CPU Benchmark ===')
    print(f'Process count: {process_count}')
    print(f'Sampling interval: {sampling_interval} seconds')
    print(f'Time limit: {time_limit} seconds')
    print(f'Pi digits: {digits}')
    print(f'Log file: {log_filename}')
    print('\nTimestamp\tElapsed(s)\tThroughput(ops/s)\tTotal Ops\tCPU(%)\tRAM(%)')
    print('-' * 80)

    # Create and start persistent worker processes
    processes = []
    for i in range(process_count):
        p = Process(target=worker_process, args=(digits, operation_count, keep_running))
        p.start()
        processes.append(p)

    while total_time < time_limit:
        total_time = pc() - start_time
        time_between_samples = total_time - (last_sample_time - start_time)

        # Check if sampling interval has passed
        if time_between_samples >= sampling_interval:
            elapsed = total_time
            current_ops = operation_count.value
            ops_in_interval = current_ops - last_operation_count
            throughput_instantaneous = ops_in_interval / time_between_samples

            # Get system usage
            cpu_usage, ram_usage = get_system_usage() if sys_usage else -1, -1

            # Print to console
            # print(f'{pc():.2f}\t\t{elapsed:.2f}\t\t{throughput_instantaneous:.2f}\t\t{current_ops}\t\t{cpu_usage:.1f}\t{ram_usage:.1f}')

            # Save to log file
            with open(log_filename, 'a') as log_file:
                log_file.write(f'{elapsed:.2f},{elapsed:.2f},{throughput_instantaneous:.2f},{current_ops},{cpu_usage:.1f},{ram_usage:.1f}\n')

            # Update for next sample
            last_sample_time = pc()
            last_operation_count = current_ops

    # Signal processes to stop and wait for them
    keep_running.value = False
    for p in processes:
        p.join()

    final_ops = operation_count.value
    print('-' * 80)
    print(f'Total time: {total_time:.2f} seconds')
    return total_time, final_ops

if __name__ == '__main__':
    total_time, operation_count = time_calculate_pi(100000, 1, 20, sampling_interval=1, sys_usage=False)

    print('\n=== Summary ===')
    print(f'Operation count: {operation_count}')
    print(f'Average throughput: {operation_count / total_time:.2f} ops/s')
