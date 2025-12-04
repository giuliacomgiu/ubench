import matplotlib.pyplot as plt
import pandas as pd

cpu1 = pd.read_csv('./benchmark_cpu_log_4304.csv')
cpu2 = pd.read_csv('./benchmark_cpu_log_4386.csv')

mem1 = pd.read_csv('./benchmark_mem_log_5637.csv')
mem2 = pd.read_csv('./benchmark_mem_log_5823.csv')

io1 = pd.read_csv('./benchmark_io_log_6005.csv')
io2 = pd.read_csv('./benchmark_io_log_6168.csv')

fig, ax = plt.subplots(3, 1, figsize=(10, 15))

label_kwargs = {
    'cpu1': {'label': 'Sem pmstat', 'linestyle': '-', 'color': 'black'},
    'cpu2': {'label': 'Com pmstat', 'linestyle': '--', 'color': 'blue'},
    'mem1': {'label': 'Sem pmstat', 'linestyle': '-', 'color': 'black'},
    'mem2': {'label': 'Com pmstat', 'linestyle': '--', 'color': 'blue'},
    'io1': {'label': 'Sem pmstat', 'linestyle': '-', 'color': 'black'},
    'io2': {'label': 'Com pmstat', 'linestyle': '--', 'color': 'blue'},
}

ax[0].plot(cpu1['elapsed_time'], cpu1['throughput_instantaneous'], **label_kwargs['cpu1'])
ax[0].plot(cpu2['elapsed_time'], cpu2['throughput_instantaneous'], **label_kwargs['cpu2'])
ax[0].legend()
ax[0].set_title('Microbenchmark CPU')
ax[0].set_xlabel('Time (s)')
ax[0].set_ylabel('Throughput (ops/s)')
ax[0].grid(True)
ax[0].set_xlim(0, 20)

ax[1].plot(mem1['elapsed_time'], mem1['throughput_instantaneous'], **label_kwargs['mem1'])
ax[1].plot(mem2['elapsed_time'], mem2['throughput_instantaneous'], **label_kwargs['mem2'])
ax[1].legend()
ax[1].set_title('Microbenchmark Memória')
ax[1].set_xlabel('Time (s)')
ax[1].set_ylabel('Throughput (ops/s)')
ax[1].grid(True)
ax[1].set_xlim(0, 20)

ax[2].plot(io1['elapsed_time'], io1['throughput_instantaneous'], **label_kwargs['io1'])
ax[2].plot(io2['elapsed_time'], io2['throughput_instantaneous'], **label_kwargs['io2'])
ax[2].legend()
ax[2].set_title('Microbenchmark IO')
ax[2].set_xlabel('Time (s)')
ax[2].set_ylabel('Throughput (ops/s)')
ax[2].grid(True)
ax[2].set_xlim(0, 20)

plt.subplots_adjust(hspace=0.5)

plt.show()
