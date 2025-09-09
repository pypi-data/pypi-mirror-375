import matplotlib.cm as cm
import os
import pandas as pd
from mdsa_tools.msm_modeler import MSM_Modeller as msm
import numpy as np

frame_list=((([80] * 20) + ([160] * 10)))
colormappings=[np.arange(0,np.max(i),1) for i in frame_list]
colormappings=np.concatenate(colormappings)



#Pipeline setup assumed as in earlier analyses
X_pca=np.load('X_PCA_both_sys_embeddingspace.npy')
GCU_coordinates=X_pca[0:3200,:]
CGU_coordinates=X_pca[3200:,:]

GCU_opt_labels=np.load('klust/GCU_coordinates_kluster_labels_5clust.npy')
CGU_opt_labels=np.load('klust/GCU_coordinates_kluster_labels_2clust.npy')
GCU_sil_centers=np.load('./klust/GCU_sil_centers.npy')
CGU_sil_centers=np.load('./klust/CGU_sil_centers.npy')

from mdsa_tools.Viz import visualize_reduction
visualize_reduction(GCU_coordinates,GCU_opt_labels,colormappings=np.concatenate(colormappings),savepath="")
