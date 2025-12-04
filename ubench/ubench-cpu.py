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
    Calcula pi com um número especificado de dígitos
    """
    mp.dps = digits
    pi_value = mp.pi

def get_system_usage():
    """
    Retorna as porcentagens atuais de uso de CPU e RAM.
    """
    cpu_usage = psutil.cpu_percent(interval=0)  # Uso de CPU em porcentagem
    ram_usage = psutil.virtual_memory().percent  # Uso de RAM em porcentagem
    return cpu_usage, ram_usage

def worker_process(digits, operation_count, keep_running):
    """
    Processo worker persistente que calcula pi continuamente
    """
    while keep_running.value:
        calculate_pi(digits)
        with operation_count.get_lock():
            operation_count.value += 1

def time_calculate_pi(digits, process_count, time_limit, sampling_interval=1, sys_usage=True):
    """
    Executa o benchmark de CPU com os parâmetros especificados

    Args:
        digits: Número de dígitos de pi a calcular
        process_count: Número de processos a criar
        time_limit: Tempo total de execução em segundos
        sampling_interval: Intervalo entre amostras em segundos
        sys_usage: Se deve coletar uso do sistema
    """
    # Variáveis compartilhadas entre processos
    operation_count = Value(ctypes.c_long, 0)  # Contador de operações
    keep_running = Value(ctypes.c_bool, True)  # Flag para interromper processos

    total_time = 0
    start_time = pc()
    last_sample_time = start_time
    last_operation_count = 0

    # Cria arquivo de log
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

    # Inicializa e inicia processos workers
    processes = []
    for i in range(process_count):
        p = Process(target=worker_process, args=(digits, operation_count, keep_running))
        p.start()
        processes.append(p)

    while total_time < time_limit:
        total_time = pc() - start_time
        time_between_samples = total_time - (last_sample_time - start_time)

        # Verifica se o intervalo de amostragem passou
        if time_between_samples >= sampling_interval:
            elapsed = total_time
            current_ops = operation_count.value
            ops_in_interval = current_ops - last_operation_count
            throughput_instantaneous = ops_in_interval / time_between_samples

            # Obtém uso do sistema
            cpu_usage, ram_usage = get_system_usage() if sys_usage else (-1, -1)

            # Imprime no console
            print(f'{pc():.2f}\t\t{elapsed:.2f}\t\t{throughput_instantaneous:.2f}\t\t{current_ops}\t\t{cpu_usage:.1f}\t{ram_usage:.1f}')

            # Salva no arquivo de log
            with open(log_filename, 'a') as log_file:
                log_file.write(f'{elapsed:.2f},{elapsed:.2f},{throughput_instantaneous:.2f},{current_ops},{cpu_usage:.1f},{ram_usage:.1f}\n')

            # Atualiza para próxima amostra
            last_sample_time = pc()
            last_operation_count = current_ops

    # Sinaliza processos para parar e aguarda finalização
    keep_running.value = False
    for p in processes:
        p.join()

    final_ops = operation_count.value
    print('-' * 80)
    print(f'Tempo total: {total_time:.2f} segundos')
    return total_time, final_ops

def main():
    """
    Função principal que executa o benchmark de CPU
    """
    total_time, operation_count = time_calculate_pi(
        digits=100000,
        process_count=8,
        time_limit=20,
        sampling_interval=1,
        sys_usage=False
    )

    print('\n=== Resumo ===')
    print(f'Contagem de operações: {operation_count}')
    print(f'Throughput médio: {operation_count / total_time:.2f} ops/s')

if __name__ == '__main__':
    main()
