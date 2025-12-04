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
    Retorna as porcentagens atuais de uso de CPU e RAM.
    """
    cpu_usage = psutil.cpu_percent(interval=0)  # Uso de CPU em porcentagem
    ram_usage = psutil.virtual_memory().percent  # Uso de RAM em porcentagem
    return cpu_usage, ram_usage

def create_test_files(thread_id, files_per_thread, file_size_mb):
    """
    Cria arquivos de teste para operações de I/O de disco.
    Retorna lista de caminhos dos arquivos.
    """
    file_paths = []
    file_size_bytes = file_size_mb * 1024 * 1024

    for i in range(files_per_thread):
        file_path = os.path.join(benchmark_dir, f'thread_{thread_id}_file_{i}.dat')
        file_paths.append(file_path)

        # Cria arquivo com dados aleatórios
        with open(file_path, 'wb') as f:
            # Escreve em chunks para evitar problemas de memória com arquivos grandes
            chunk_size = 1024 * 1024  # Chunks de 1MB
            remaining = file_size_bytes
            while remaining > 0:
                write_size = min(chunk_size, remaining)
                f.write(os.urandom(write_size))
                remaining -= write_size

    return file_paths

def worker_thread(thread_id, file_paths, file_size_mb, block_size, read_percentage):
    """
    Thread worker persistente que realiza operações aleatórias de I/O de disco
    """
    global operation_count, keep_running

    file_size_bytes = file_size_mb * 1024 * 1024
    max_offset = max(0, file_size_bytes - block_size)

    while keep_running:
        # Seleciona arquivo aleatório
        file_path = random.choice(file_paths)

        # Decide leitura ou escrita baseado na porcentagem
        is_read = random.randint(1, 100) <= read_percentage

        # Offset aleatório para a operação
        offset = random.randint(0, max_offset) if max_offset > 0 else 0

        if is_read:
            # Operação de leitura
            with open(file_path, 'rb') as f:
                f.seek(offset)
                f.read(block_size)
        else:
            # Operação de escrita
            with open(file_path, 'r+b') as f:
                f.seek(offset)
                f.write(os.urandom(block_size))

        with operation_lock:
            operation_count += 1

def cleanup_files():
    """
    Remove todos os arquivos de benchmark e o diretório
    """
    if os.path.exists(benchmark_dir):
        for filename in os.listdir(benchmark_dir):
            file_path = os.path.join(benchmark_dir, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f'Erro ao deletar {file_path}: {e}')
        try:
            os.rmdir(benchmark_dir)
        except Exception as e:
            print(f'Erro ao remover diretório {benchmark_dir}: {e}')

def time_disk_io(thread_count, files_per_thread, file_size_mb, block_size,
                 read_percentage, time_limit, sampling_interval=1, sys_usage=True):
    """
    Executa benchmark de I/O de disco com parâmetros especificados

    Args:
        thread_count: Número de threads a criar
        files_per_thread: Número de arquivos (n) que cada thread cria
        file_size_mb: Tamanho de cada arquivo em MB (m)
        block_size: Tamanho de cada operação de leitura/escrita em bytes
        read_percentage: Porcentagem de operações de leitura (0-100)
        time_limit: Tempo total de execução em segundos
        sampling_interval: Intervalo entre amostras em segundos
        sys_usage: Se deve coletar uso do sistema
    """
    global operation_count, keep_running

    # Limpa arquivos existentes
    cleanup_files()

    # Cria diretório de benchmark
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

    # Pré-cria todos os arquivos de teste antes de iniciar a medição
    print('\nCriando arquivos de teste...')
    thread_files = []
    for i in range(thread_count):
        file_paths = create_test_files(i, files_per_thread, file_size_mb)
        thread_files.append(file_paths)
    print(f'Criados {thread_count * files_per_thread} arquivos totalizando {thread_count * files_per_thread * file_size_mb} MB')

    operation_count = 0
    total_time = 0
    start_time = pc()
    last_sample_time = start_time
    last_operation_count = 0

    # Cria arquivo de log
    log_filename = f'benchmark_io_log_{int(start_time)}.csv'
    with open(log_filename, 'w') as log_file:
        log_file.write('timestamp,elapsed_time,throughput_instantaneous,operations_count,cpu_usage,ram_usage\n')

    print(f'Log file: {log_filename}')
    print('\nTimestamp\tElapsed(s)\tThroughput(ops/s)\tTotal Ops\tCPU(%)\tRAM(%)')
    print('-' * 80)

    # Cria e inicia threads workers persistentes
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

        # Verifica se o intervalo de amostragem passou
        if time_between_samples >= sampling_interval:
            elapsed = total_time
            ops_in_interval = operation_count - last_operation_count
            throughput_instantaneous = ops_in_interval / time_between_samples

            # Obtém uso do sistema
            cpu_usage, ram_usage = get_system_usage() if sys_usage else (-1, -1)

            # Imprime no console
            print(f'{pc():.2f}\t\t{elapsed:.2f}\t\t{throughput_instantaneous:.2f}\t\t{operation_count}\t\t{cpu_usage:.1f}\t{ram_usage:.1f}')

            # Salva no arquivo de log
            with open(log_filename, 'a') as log_file:
                log_file.write(f'{elapsed:.2f},{elapsed:.2f},{throughput_instantaneous:.2f},{operation_count},{cpu_usage:.1f},{ram_usage:.1f}\n')

            # Atualiza para próxima amostra
            last_sample_time = pc()
            last_operation_count = operation_count

    # Sinaliza threads para parar e aguarda finalização
    keep_running = False
    for t in threads:
        t.join()

    print('-' * 80)
    print(f'Tempo total: {total_time:.2f} segundos')

    # Limpa arquivos de teste
    cleanup_files()

    return total_time

def main():
    """
    Função principal que executa o benchmark de I/O de disco
    """
    global operation_count

    total_time = time_disk_io(
        thread_count=4,
        files_per_thread=2,
        file_size_mb=100,
        block_size=100 * 1024,  # Blocos de 100kB
        read_percentage=50,
        time_limit=20,
        sampling_interval=1,
        sys_usage=False
    )

    print('\n=== Resumo ===')
    print(f'Contagem de operações: {operation_count}')
    print(f'Throughput médio: {operation_count / total_time:.2f} ops/s')

if __name__ == '__main__':
    main()
