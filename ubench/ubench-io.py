# • Disk intensive load: Implements random read and write operations in
# the stable storage. For each thread, n files are created with the size of
# m MB. The number of threads, size of the block, percentage of readings
# and writes, and runtime are configurable, along with n and m.
# The implemented benchmarks generate log files with the throughput of
# operations measured throughout the execution. These data are made
# available in time series, with an adjustable sampling interval.

import psutil
import os
import random
from time import perf_counter as pc
from threading import Thread, Lock

operation_count = 0
keep_running = False
operation_lock = Lock()
benchmark_dir = 'benchmark_files'

def get_system_usage():
    """
    Returns the current CPU and RAM usage percentages.
    """
    cpu_usage = psutil.cpu_percent(interval=0)  # CPU usage in percentage
    ram_usage = psutil.virtual_memory().percent  # RAM usage in percentage
    return cpu_usage, ram_usage

def create_test_files(thread_id, files_per_thread, file_size_mb):
    """
    Create test files for disk I/O operations
    Returns list of file paths
    """
    file_paths = []
    file_size_bytes = file_size_mb * 1024 * 1024

    for i in range(files_per_thread):
        file_path = os.path.join(benchmark_dir, f'thread_{thread_id}_file_{i}.dat')
        file_paths.append(file_path)

        # Create file with random data
        with open(file_path, 'wb') as f:
            # Write in chunks to avoid memory issues with large files
            chunk_size = 1024 * 1024  # 1MB chunks
            remaining = file_size_bytes
            while remaining > 0:
                write_size = min(chunk_size, remaining)
                f.write(os.urandom(write_size))
                remaining -= write_size

    return file_paths

def worker_thread(thread_id, file_paths, file_size_mb, block_size, read_percentage):
    """
    Persistent worker thread that performs random disk I/O operations
    """
    global operation_count, keep_running

    file_size_bytes = file_size_mb * 1024 * 1024
    max_offset = max(0, file_size_bytes - block_size)

    while keep_running:
        # Select random file
        file_path = random.choice(file_paths)

        # Decide read or write based on percentage
        is_read = random.randint(1, 100) <= read_percentage

        # Random offset for the operation
        offset = random.randint(0, max_offset) if max_offset > 0 else 0

        try:
            if is_read:
                # Read operation
                with open(file_path, 'rb') as f:
                    f.seek(offset)
                    f.read(block_size)
            else:
                # Write operation
                with open(file_path, 'r+b') as f:
                    f.seek(offset)
                    f.write(os.urandom(block_size))

            with operation_lock:
                operation_count += 1
        except Exception as e:
            print(f'Error in thread {thread_id}: {e}')
            break

def cleanup_files():
    """
    Remove all benchmark files and directory
    """
    if os.path.exists(benchmark_dir):
        for filename in os.listdir(benchmark_dir):
            file_path = os.path.join(benchmark_dir, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f'Error deleting {file_path}: {e}')
        try:
            os.rmdir(benchmark_dir)
        except Exception as e:
            print(f'Error removing directory {benchmark_dir}: {e}')

def time_disk_io(thread_count, files_per_thread, file_size_mb, block_size,
                 read_percentage, time_limit, sampling_interval=1):
    """
    Run disk I/O benchmark with specified parameters

    Args:
        thread_count: Number of threads to spawn
        files_per_thread: Number of files (n) each thread creates
        file_size_mb: Size of each file in MB (m)
        block_size: Size of each read/write operation in bytes
        read_percentage: Percentage of read operations (0-100)
        time_limit: Total execution time in seconds
        sampling_interval: Interval between samples in seconds
    """
    global operation_count, keep_running

    # Clean up any existing files
    cleanup_files()

    # Create benchmark directory
    os.makedirs(benchmark_dir, exist_ok=True)

    print('=== Disk I/O Benchmark ===')
    print(f'Thread count: {thread_count}')
    print(f'Files per thread: {files_per_thread}')
    print(f'File size: {file_size_mb} MB')
    print(f'Block size: {block_size} bytes')
    print(f'Read percentage: {read_percentage}%')
    print(f'Write percentage: {100 - read_percentage}%')
    print(f'Time limit: {time_limit} seconds')
    print(f'Sampling interval: {sampling_interval} seconds')

    # Pre-create all test files before timing starts
    print('\nCreating test files...')
    thread_files = []
    for i in range(thread_count):
        file_paths = create_test_files(i, files_per_thread, file_size_mb)
        thread_files.append(file_paths)
    print(f'Created {thread_count * files_per_thread} files totaling {thread_count * files_per_thread * file_size_mb} MB')

    operation_count = 0
    total_time = 0
    start_time = pc()
    last_sample_time = start_time
    last_operation_count = 0

    # Create log file
    log_filename = f'benchmark_io_log_{int(start_time)}.csv'
    with open(log_filename, 'w') as log_file:
        log_file.write('timestamp,elapsed_time,throughput_instantaneous,operations_count,cpu_usage,ram_usage\n')

    print(f'Log file: {log_filename}')
    print('\nTimestamp\tElapsed(s)\tThroughput(ops/s)\tTotal Ops\tCPU(%)\tRAM(%)')
    print('-' * 80)

    # Create and start persistent worker threads
    keep_running = True
    threads = []
    for i in range(thread_count):
        t = Thread(target=worker_thread, args=(i, thread_files[i], file_size_mb,
                                                block_size, read_percentage))
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
            cpu_usage, ram_usage = -1, -1 # get_system_usage()

            # Print to console
            # print(f'{pc():.2f}\t\t{elapsed:.2f}\t\t{throughput_instantaneous:.2f}\t\t{operation_count}\t\t{cpu_usage:.1f}\t{ram_usage:.1f}')

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
    print(f'Total time: {total_time:.2f} seconds')

    # Clean up test files
    cleanup_files()

    return total_time

# Run benchmark with default parameters
total_time = time_disk_io(
    thread_count=4,
    files_per_thread=2,
    file_size_mb=100,
    block_size=100 * 1024,  # 100kB blocks
    read_percentage=50,
    time_limit=20,
    sampling_interval=1
)

print('\n=== Summary ===')
print(f'Operation count: {operation_count}')
print(f'Average throughput: {operation_count / total_time:.2f} ops/s')
