import numpy as np

data = np.load('GCU_1_in_10_sampling.npz')


print(data.files)   

rep = data['rep']

print(type(rep), rep.shape)
print(rep)