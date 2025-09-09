import matplotlib.cm as cm
import os
import pandas as pd
from mdsa_tools.msm_modeler import MSM_Modeller as msm
import numpy as np
from mdsa_tools.Analysis import systems_analysis

#Pipeline setup assumed as in: Data Generation
redone_CCU_GCU_fulltraj=np.load('/Users/luis/Downloads/redone_unrestrained_CCU_GCU_Trajectory_array.npy',allow_pickle=True)
redone_CCU_CGU_fulltraj=np.load('/Users/luis/Downloads/redone_unrestrained_CCU_CGU_Trajectory_array.npy',allow_pickle=True)

from mdsa_tools.Viz import visualize_reduction
persys_frame_list=((([80] * 20) + ([160] * 10)))
persys_frame_short=([80] * 20) 
persys_frame_long= ([160] * 10) 

#For the paper we move forward with systems representations
all_systems=[redone_CCU_GCU_fulltraj,redone_CCU_CGU_fulltraj]
Systems_Analyzer = systems_analysis(systems_representations=all_systems,replicate_distribution=persys_frame_list)
Systems_Analyzer.replicates_to_featurematrix()
X_pca,_ ,_=Systems_Analyzer.reduce_systems_representations()

GCU_coordinates=X_pca[0:3200,:]
CGU_coordinates=X_pca[3200:,:]

optimal_sil_labels,optimal_elbow_labels,GCU_optimal_silcenters,optimal_elbow_centers=Systems_Analyzer.preform_clust_opt(data=GCU_coordinates,outfile_path='./klust/GCU_coordinates_')
optimal_sil_labels,optimal_elbow_labels,CGU_optimal_silcenters,optimal_elbow_centers=Systems_Analyzer.preform_clust_opt(data=CGU_coordinates,outfile_path='./klust/CGU_coordinates_')


np.save('X_PCA_both_sys',X_pca)
np.save('./klust/GCU_sil_centers',GCU_optimal_silcenters)
np.save('./klust/CGU_sil_centers',CGU_optimal_silcenters)
