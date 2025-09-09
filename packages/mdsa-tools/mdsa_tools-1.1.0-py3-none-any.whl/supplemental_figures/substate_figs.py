import matplotlib.cm as cm
import os
import pandas as pd
from mdsa_tools.msm_modeler import MSM_Modeller as msm
import numpy as np
from mdsa_tools.Analysis import systems_analysis

#Pipeline setup assumed as in earlier analyses
X_pca=np.load('X_PCA_both_sys_embeddingspace.npy')
GCU_coordinates=X_pca[0:3200,:]
CGU_coordinates=X_pca[3200:,:]
GCU_opt_labels=np.load('klust/GCU_coordinates_kluster_labels_5clust.npy')
CGU_opt_labels=np.load('klust/CGU_coordinates_kluster_labels_2clust.npy')


from mdsa_tools.Viz import visualize_reduction

visualize_reduction(GCU_coordinates,color_mappings=GCU_opt_labels,title='GCU candidate states',cmap=cm.inferno,cbar_label='K=',
savepath='./substatesfigs/GCU_candidate_states',
gridvisible=True)

visualize_reduction(CGU_coordinates,color_mappings=CGU_opt_labels,title='CGU candidate states',cmap=cm.inferno,cbar_label='K=',
savepath='./substatesfigs/CGU_candidate_states',
gridvisible=True)

#global cuz why not
visualize_reduction(X_pca,color_mappings=np.concatenate((GCU_opt_labels, CGU_opt_labels + GCU_opt_labels.max() + 1)),title='global candidate states',cmap=cm.inferno,cbar_label='K=',
savepath='./substatesfigs/Global_candidate_states',
gridvisible=True)


