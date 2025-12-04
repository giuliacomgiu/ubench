# • Memory intensive load: Implements read and write operations on a
# pre-allocated vector of integers with the size of m MB. The runtime
# and m are benchmark parameters;

import psutil
from time import perf_counter as pc
import random

keep_running = False
bytearray_list = []
bytearray_list_length = 0

def memory_init(size_mb, chunk_size):
    """
    Função para alocar memória
    size_mb: memória total a alocar em MB
    chunk_size: tamanho de cada chunk em bytes
    """
    global bytearray_list, bytearray_list_length

    # Calcula número de chunks necessários
    total_bytes = size_mb * 1024 * 1024  # Converte MB para bytes
    num_chunks = int(total_bytes / chunk_size)

    for _ in range(num_chunks):
        bytearray_chunk = bytearray(random.randbytes(chunk_size))  # Define todos os bytes com valor aleatório
        bytearray_list.append(bytearray_chunk)  # Aloca 1 chunk por vez

    bytearray_list_length = len(bytearray_list)
    print(f'Alocados {num_chunks} chunks de {chunk_size / (1024*1024):.2f} MB cada = {size_mb} MB total')

def memory_load(chunk_size):
    """
    Função para estressar acesso à memória
    """
    global bytearray_list, bytearray_list_length

    sub_chunk_size = chunk_size // 2
    chunk_idx = random.randint(0, bytearray_list_length - 1)
    idx = random.randint(0, chunk_size - 1 - sub_chunk_size)
    idx2 = random.randint(0, chunk_size - 1 - sub_chunk_size)

    bytearray_chunk = bytearray_list[chunk_idx]
    temp = bytearray_chunk[idx:(idx+sub_chunk_size)]
    bytearray_chunk[idx:(idx+sub_chunk_size)] = bytearray_chunk[idx2:(idx2+sub_chunk_size)]
    bytearray_chunk[idx2:(idx2+sub_chunk_size)] = temp

def memory_release():
    """
    Libera a memória alocada
    """
    global bytearray_list
    bytearray_list.clear()
    del bytearray_list

def get_system_usage():
    """
    Retorna as porcentagens atuais de uso de CPU e RAM.
    """
    cpu_usage = psutil.cpu_percent(interval=0)  # Uso de CPU não-bloqueante
    ram_usage = psutil.virtual_memory().percent  # Uso de RAM em porcentagem
    return cpu_usage, ram_usage

def time_use_mem(size_mb, chunk_size=1024 * 1024, time_limit=10, sampling_interval=1, sys_usage=True):
    """
    Executa benchmark de memória com parâmetros especificados

    Args:
        size_mb: Tamanho total da memória a alocar em MB
        chunk_size: Tamanho de cada chunk em bytes
        time_limit: Tempo total de execução em segundos
        sampling_interval: Intervalo entre amostras em segundos
        sys_usage: Se deve coletar uso do sistema
    """
    print('=== Memory Benchmark ===')
    print('Sampling interval: ', sampling_interval, 'seconds')
    print('Time limit: ', time_limit, 'seconds')
    print('Size of memory to allocate: ', size_mb, 'MB')
    print('Allocation chunk size: ', chunk_size / (1024*1024), 'MB')

    memory_init(size_mb, chunk_size)

    operation_count = 0
    last_operation_count = 0
    total_time = 0
    start_time = pc()
    last_sample_time = start_time

    # Cria arquivo de log
    log_filename = f'benchmark_mem_log_{int(start_time)}.csv'
    with open(log_filename, 'w') as log_file:
        log_file.write('timestamp,elapsed_time,throughput_instantaneous,operations_count,cpu_usage,ram_usage\n')
    print(f'Log file: {log_filename}')

    print('\nTimestamp\tElapsed(s)\tThroughput(ops/s)\tTotal Ops\tCPU(%)\tRAM(%)')
    print('-' * 80)

    while total_time < time_limit:
        total_time = pc() - start_time
        time_between_samples = total_time - (last_sample_time - start_time)

        memory_load(chunk_size)
        operation_count += 1

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

    memory_release()
    print('-' * 80)
    print('Total time: ', total_time)
    return total_time, operation_count

def main():
    """
    Função principal que executa o benchmark de memória
    """
    total_time, operation_count = time_use_mem(
        size_mb=6144,
        chunk_size=250 * 1024 * 1024,
        time_limit=20,
        sampling_interval=1,
        sys_usage=False
    )

    print('\n=== Resumo ===')
    print(f'Contagem de operações: {operation_count}')
    print(f'Throughput médio: {operation_count / total_time:.2f} ops/s')

    cpu_usage, ram_usage = get_system_usage()
    print('\n=== Uso do Sistema ===')
    print(f'Uso de CPU: {cpu_usage}%')
    print(f'Uso de RAM: {ram_usage}%')

if __name__ == '__main__':
    main()
