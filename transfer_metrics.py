#import libraries for data manipulation and visualization
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn import preprocessing


#import transport metrics
import pickle
with open('transfer_metrics.pkl', 'rb') as f:
    metrics = pickle.load(f)

#create data frame using the imported data
ds = pd.DataFrame(metrics)
#print first five rows of ds
head(ds)

var = list(ds.columns())
val = list(ds.values())

#create plots for each var
#upload rate
plt.plot(upload_rate, marker = 'o:k', mec = 'hotpink')
plt.title('Upload Rate')
plt.xlabel('Packet')
plt.ylabel('Rate (MB/s)')
plt.show()

#download rate
plt.plot(download_rate, marker = 'o:k', mec = 'hotpink')
plt.title('Download Rate')
plt.xlabel('Packet')
plt.ylabel('Rate (MB/s)')
plt.show()

#transfer time
plt.plot(file_transfer_times, marker = 'o:k', mec = 'hotpink')
plt.title('File Transfer Times')
plt.xlabel('Packet')
plt.ylabel('Total transfer/packet')
plt.show()

#response time
plt.plot(system_response_times, marker = 'o:k', mec = 'hotpink')
plt.title('System Response Times')
plt.xlabel('Packet')
plt.ylabel('System response/packet')
plt.show()


#take the mean value for each of the columns
var_means = val.mean()
print(var_means)

#average metrics for each variable
plt.barh(var, var_means, color = 'pink', width = 0.4)
plt.xticks(rotation = 45)
# add annotations
for i, v in enumerate(var_means):
    plt.annotate(str(v), xy=(i, v), ha='center', va='bottom')

plt.title('Average Metrics for Each Variable')
plt.xlabel('Variable')
plt.ylabel('Average Value')
plt.show()