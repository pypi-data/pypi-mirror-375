import numpy as np 
import matplotlib.cm as cm

frame_list=((([80] * 20) + ([160] * 10))*2)
system_labels=(([1]*22000)+[2]*22000)
colormappings=[np.arange(0,np.max(i),1) for i in frame_list]
colormappings=np.concatenate(colormappings)

full_sampling_GCU = np.load('/Users/luis/Downloads/full_sampling_CGU.npy')
full_sampling_CGU = np.load('/Users/luis/Downloads/full_sampling_GCU.npy')


#lets try to run through everything
from mdsa_tools.Analysis import systems_analysis

#For the paper we move forward with systems representations
all_systems=[full_sampling_GCU,full_sampling_CGU]
Systems_Analyzer = systems_analysis(all_systems)
Systems_Analyzer.replicates_to_featurematrix()

#system level kmeans first
#optimal_k_silhouette_labels,optimal_k_elbow_labels,centers_sillohuette,centers_elbow = Systems_Analyzer.cluster_system_level()
opt_labels=np.load('/Users/luis/Desktop/workspacetwo/new_samplingkluster_labels_2clust.npy')

from mdsa_tools.Viz import visualize_reduction
#reduce and visualize
X_pca,_,_=Systems_Analyzer.reduce_systems_representations(method='PCA',n_components=2) #PCA
np.save('reduced_coordinates_1_in_10',X_pca)
visualize_reduction(X_pca,color_mappings=system_labels,cmap=cm.magma_r,savepath='systemlabels_1_in_10_PCA')#each system
visualize_reduction(X_pca,color_mappings=opt_labels,cmap=cm.magma_r,savepath='klusterlabels_1_in_10_PCA')#each system

