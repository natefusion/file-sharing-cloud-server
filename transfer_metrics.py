import numpy as np
import matplotlib.pyplot as plt

# put path for metrics here
fname = ''

import pickle
with open(fname, 'rb') as f:
    metrics = pickle.load(f)

upload_rate = metrics['upload_rate']
download_rate = metrics['download_rate']
file_transfer_times = metrics['file_transfer_times']
system_response_times = [x[1] for x in metrics['system_response_times']]

cp_response = []
ls_response = []
rm_response = []
mkdir_response = []
for x in metrics['system_response_times']:
    if x[0] == 'cp':
        cp_response.append(x[1])
    elif x[0] == 'ls':
        ls_response.append(x[1])
    elif x[0] == 'rm':
        rm_response.append(x[1])
    elif x[0] == 'mkdir':
        mkdir_response.append(x[1])


rate_labels = ['Upload rate', 'Download rate']
rate_avgs = [np.mean(upload_rate), np.mean(download_rate)]
plt.bar(rate_labels, rate_avgs)
plt.xlabel('Averages')
plt.ylabel('Rate (MB/s)')
plt.show()

plt.boxplot((upload_rate, download_rate), labels=rate_labels, showfliers=False)
plt.ylabel('Rate (MB/s)')
plt.show()

response_labels = ['cp', 'rm', 'ls', 'mkdir', 'All']
response_avgs = [np.mean(cp_response), np.mean(rm_response), np.mean(ls_response), np.mean(mkdir_response), np.mean(system_response_times)]
plt.bar(response_labels, response_avgs)
plt.xlabel('Averages')
plt.ylabel('Response Time (s)')
plt.show()

times_run = [len(cp_response), len(ls_response), len(rm_response), len(mkdir_response)]
plt.pie(times_run, labels=response_labels[0:4], autopct='%1.1f%%')
plt.title('Times run')
plt.show()

plt.boxplot((cp_response, rm_response, ls_response, mkdir_response, system_response_times), showfliers=False, labels=response_labels)
plt.ylabel('Response Time (s)')
plt.show()
