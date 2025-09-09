import matplotlib.cm as cm
import os
import pandas as pd
from mdsa_tools.msm_modeler import MSM_Modeller as msm
import numpy as np
from mdsa_tools.Analysis import systems_analysis
import os
import matplotlib.pyplot as plt

##############################
#Setup as originally intended#
##############################


from mdsa_tools.Viz import visualize_reduction
persys_frame_list=((([80] * 20) + ([160] * 10)))
persys_frame_short=([80] * 20) 
persys_frame_long= ([160] * 10)

GCU_opt_labels=np.load('klust/GCU_coordinates_kluster_labels_5clust.npy')

def labels_to_frames(frame_list,labels):

    final_list=[]
    iterator=0

    for i in range(len(frame_list)):
        current_frame_length=frame_list[i]
        frame_values=labels[iterator:iterator+current_frame_length]
        final_list.append(frame_values.copy())
        iterator+=current_frame_length

    return final_list


list_of_frames = labels_to_frames(persys_frame_list,GCU_opt_labels)

import msmhelper as mh

# Implied timescales over a range of lag times
its = mh.msm.implied_timescales(list_of_frames, lagtimes=[1, 2, 5, 10, 15, 20, 25,30,35,40,45,50,55,60], ntimescales=4)
print(f"its:{its}")


lagtimes = [1, 2, 5, 10, 15, 20, 25,30,35,40,45,50,55,60]



plt.figure(figsize=(6,4))
for i in range(its.shape[1]):  
    plt.plot(lagtimes, its[:, i], 'o-', label=f"ITS {i+1}")


plt.xlabel("Lag time (frames)")
plt.ylabel("Implied timescale (frames)")
plt.title("Implied Timescales vs Lag")
plt.legend()
plt.tight_layout()
plt.show()


# CK test
#ck = mh.msm.chapman_kolmogorov_test(list_of_frames, lagtimes=[45], tmax=200)

# estimating the CK test
ck = mh.msm.ck_test(list_of_frames, lagtimes=[45], tmax=200)

ck_fig = mh.plot.plot_ck_test(ck=ck, grid=(1, 4))
ck_fig.savefig('CK plot')

print(f"ck:{ck}\n\n")

T_45, states_45 = mh.msm.estimate_markov_model(list_of_frames, lagtime=45) # to save the msm itself
T_1, states_1 = mh.msm.estimate_markov_model(list_of_frames, lagtime=1)



np.savetxt('Transition_Probability_Matrix_T_45.csv',T_45,delimiter=',')
np.savetxt('Transition_Probability_Matrix_T_1.csv',T_1,delimiter=',')

from msmhelper.msm.msm import _generate_transition_count_matrix
typed_trajs = list()
for arr in list_of_frames:  #make sure they fit the numba requirements
    typed_trajs.append(np.ascontiguousarray(arr, dtype=np.int64))

C = _generate_transition_count_matrix(typed_trajs,lagtime=1,nstates=5)
np.savetxt('Counts_Matrix_T_1.csv',C,delimiter=',')

os._exit(0)

# Stationary distribution (equilibrium populations)
pi = mh.msm.equilibrium_population(T)
print(f"shape of transition probability matrix: {T.shape}, Shape of states{states.shape}")
print(T)
print(states)