from mdsa_tools.Analysis import systems_analysis
import numpy as np
import matplotlib.cm as cm
import os
import pandas as pd
from mdsa_tools.msm_modeler import MSM_Modeller as msm
from mdsa_tools.Viz import replicatemap_from_labels

frame_list=(([600]*20 + [1000]*10) * 2)
system_labels=(([1]*22000)+[2]*22000)
colormappings=[np.arange(0,np.max(i),1) for i in frame_list]
timeseries=np.concatenate(colormappings)

full_sampling_GCU = np.load('/Users/luis/Downloads/full_sampling_CGU.npy')
full_sampling_CGU = np.load('/Users/luis/Downloads/full_sampling_GCU.npy')
print(full_sampling_GCU.shape,full_sampling_CGU.shape)

#Just out of curiosity try just gcu
all_systems=[full_sampling_GCU,full_sampling_CGU]
Systems_Analyzer = systems_analysis(systems_representations=all_systems,replicate_distribution=frame_list)
Systems_Analyzer.replicates_to_featurematrix()
X_pca,_ ,_=Systems_Analyzer.reduce_systems_representations()
cluster_solodf=Systems_Analyzer.create_PCA_ranked_weights(outfile_path="./1_in_10_total_df")

PC1_magnitude_table=cluster_solodf.sort_values('PC1_magnitude',ascending=False)
PC2_magnitude_table=cluster_solodf.sort_values('PC2_magnitude',ascending=False)

PC1_magnitude_table.to_csv('./1_in_10_total_df_PC1_orderdf.csv')
PC2_magnitude_table.to_csv('./1_in_10_total_df_PC2_orderdf.csv')

optimal_k_silhouette_labels_GCU,optimal_k_elbow_labels_GCU,centers_sillohuette_GCU,centers_elbow_GCU=Systems_Analyzer.cluster_system_level(data=X_pca[0:22000,:],outfile_path='./embeddingspace/klust/GCU_')
optimal_k_silhouette_labels_CGU,optimal_k_elbow_labels_CGU,centers_sillohuette_CGU,centers_elbow_CGU=Systems_Analyzer.cluster_system_level(data=X_pca[22000:,:],outfile_path='./embeddingspace/klust/CGU_')

from mdsa_tools.Viz import visualize_reduction

visualize_reduction(X_pca[0:22000,:],color_mappings=optimal_k_silhouette_labels_GCU,savepath='./embeddingspace/GCU_i_in_10_embeddingspace')
visualize_reduction(X_pca[22000:,:],color_mappings=optimal_k_silhouette_labels_CGU,savepath='./embeddingspace/CGU_i_in_10_embeddingspace')

full_labels = np.concatenate((optimal_k_silhouette_labels_GCU,optimal_k_silhouette_labels_CGU+np.max(optimal_k_silhouette_labels_GCU)+1))
visualize_reduction(X_pca,color_mappings=full_labels,savepath='./embeddingspace/all_i_in_10_embeddingspace')

#note this is every hundred frames for less bins
visualize_reduction(X_pca[::10],color_mappings=timeseries[::10],savepath='./embeddingspace/allframes_i_in_10_timeseries',cmap=cm.magma_r)

os._exit(0)
#################################################
#building replicate maps to visualize transition#
#################################################
from mdsa_tools.Viz import replicatemap_from_labels
import matplotlib.pyplot as plt

GCU_with_filler=np.concatenate((cluster_labels,np.full(shape=(3200,),fill_value=np.max(cluster_labels)+1)))
replicatemap_from_labels(GCU_with_filler,persys_frame_list*2,savepath='./replicate_maps/6klust_replicate_map',title='6klust_replicate_map')

modeller = msm(cluster_labels, cluster_centers, X_pca, frame_scale=persys_frame_list)

# Transition matrix + stationary states
Tmat = modeller.create_transition_probability_matrix()[1:,1:]
print(Tmat.shape)
np.savetxt('./replicate_maps/Tmat.csv',Tmat,delimiter=',')

os._exit(0)
stat = modeller.extract_stationary_states()

# Implied timescales
lags=[10,20,30,40,50,60]
its = modeller.compute_implied_timescales(lags=[10,20,30,40,50,60])
for i in range(len(next(iter(its.values())))):
    plt.plot(lags, [its[lag][i] for lag in lags], marker='o')

plt.xlabel("Lag time")
plt.ylabel("Implied timescale")
plt.yscale("log")
plt.title(f"ITS plot: ")
plt.show()

# CK test
results = modeller.chapman_kolmogorov_test(cluster_labels, persys_frame_list, lag=1, steps=10)

def plot_ck_overlay(results, state_i=3, state_j=2):
    ks = sorted(results.keys())
    pred_vals = [results[k][0][state_i, state_j] for k in ks]
    direct_vals = [results[k][1][state_i, state_j] for k in ks]

    plt.plot(ks, pred_vals, "o-", label="Predicted")
    plt.plot(ks, direct_vals, "s--", label="Direct")
    plt.xlabel("k (multiple of τ)")
    plt.ylabel(f"P({state_i}→{state_j})")
    plt.title(f"CK Overlay: {state_i}→{state_j}")
    plt.legend()
    plt.show()
    return 

plot_ck_overlay(results,state_i=3,state_j=2)


# ====================================================
# Run for shorts and longs
# ====================================================

os._exit(0)

