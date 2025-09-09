from mdsa_tools.Analysis import systems_analysis
import numpy as np
import matplotlib.cm as cm
import os


#umap below
#Pipeline setup assumed as in: Data Generation
redone_CCU_GCU_fulltraj=np.load('/Users/luis/Downloads/redone_unrestrained_CCU_GCU_Trajectory_array.npy',allow_pickle=True)
redone_CCU_CGU_fulltraj=np.load('/Users/luis/Downloads/redone_unrestrained_CCU_CGU_Trajectory_array.npy',allow_pickle=True)
all_systems=[redone_CCU_GCU_fulltraj,redone_CCU_CGU_fulltraj]

GCU_opt_labels=np.load('klust/GCU_coordinates_kluster_labels_5clust.npy')
CGU_opt_labels=np.load('klust/GCU_coordinates_kluster_labels_2clust.npy')
all_subdomains=np.concatenate((GCU_opt_labels, CGU_opt_labels + GCU_opt_labels.max() + 1))

#For the paper we move forward with systems representations
Systems_Analyzer = systems_analysis(all_systems)
Systems_Analyzer.replicates_to_featurematrix()
UMAP_coordinates=Systems_Analyzer.reduce_systems_representations(method='UMAP',n_components=2,n_neighbors=15,min_dist=.5) #PCA



#######################################################################################
#ALL of the examples of looking at worm behavior in same file bc of randomness of UMAP#
#######################################################################################

###############
#worm behavior#
###############

from mdsa_tools.Viz import visualize_reduction
frame_list=((([80] * 20) + ([160] * 10))*2)
per_frame_list=((([80] * 20) + ([160] * 10)))

system_labels=(([1]*3200)+[2]*3200)
per_rep_timeframe=[np.arange(0,np.max(i),1) for i in frame_list]
per_rep_timeframe=np.concatenate(per_rep_timeframe)

visualize_reduction(UMAP_coordinates,
color_mappings=system_labels,cmap=cm.magma,
savepath='./crawl/syslabels_15n_point5mindist',
title='UMAP Dimensional Reduction with per-system highlighting',
cbar_label='System',
gridvisible=True)#each system

visualize_reduction(UMAP_coordinates,
color_mappings=all_subdomains,
cmap=cm.magma_r,
savepath='./crawl/all_subdomains_',
title='UMAP Dimensional Reduction with PCA Subdomain Highlighting',
cbar_label='System',
gridvisible=True)#each system

visualize_reduction(UMAP_coordinates,color_mappings=per_rep_timeframe,cmap=cm.magma_r,
savepath='./crawl/crawlspace_15n_point5mindist_crawlspace',
title='UMAP Dimensional Reduction with per-replicate frame highlighting',cbar_label='Frame Number',
gridvisible=True)#all reps

#######################################
#PCA in same file for similar behavior#
#######################################
X_PCA,_,_=Systems_Analyzer.reduce_systems_representations(method='PCA',n_components=2,n_neighbors=15,min_dist=.5) #PCA

visualize_reduction(X_PCA[0:3200,:],
                    color_mappings=per_rep_timeframe[0:3200],
                    cmap=cm.magma_r,
                    savepath='./crawl/PCA_crawlspace',
                    title='PCA Dimensional Reduction with per-replicate frame highlighting',
                    cbar_label='Frame Number',
                    gridvisible=True)#all reps



############################################################################
#Now we can cluster UMAP since its PCA informed for better candidate states#
#actually scratch this because UMAP is too unstable                        #
############################################################################
GCU_UMAP=UMAP_coordinates[0:3200,:]
CGU_UMAP=UMAP_coordinates[3200:,:]

GCU_optimal_sil_labels,GCU_optimal_elbow_labels,GCU_optimal_silcenters,GCU_optimal_elbow_centers = Systems_Analyzer.cluster_system_level(data=GCU_UMAP,outfile_path='./UMAP_clust/GCU_coordinates_')
CGU_optimal_sil_labels,CGU_optimal_elbow_labels,CGU_optimal_silcenters,CGU_optimal_elbow_centers = Systems_Analyzer.cluster_system_level(data=CGU_UMAP,outfile_path='./UMAP_clust/CGU_coordinates_')

#For the paper we move forward with systems representations
Systems_Analyzer = systems_analysis(all_systems)
visualize_reduction(UMAP_coordinates[0:3200,:],
color_mappings=GCU_optimal_sil_labels,
cmap=cm.magma,
savepath='./substatesfigs/UMAP_GCU_substates',
title='UMAP Dimensional Reduction with umap_clustering_results',
cbar_label='System',
gridvisible=True)#each system


visualize_reduction(UMAP_coordinates[3200:,:],
color_mappings=CGU_optimal_sil_labels,
cmap=cm.magma,
savepath='./substatesfigs/UMAP_CGU',
title='UMAP Dimensional Reduction with umap_clustering_results',
cbar_label='System',
gridvisible=True)#


#at k=2 because they might be picking up on noise tbh
alt_opt_clust_labels_GCU=np.load('./UMAP_clust/GCU_coordinates_kluster_labels_2clust.npy')
alt_opt_clust_labels_CGU=np.load('./UMAP_clust/CGU_coordinates_kluster_labels_2clust.npy')
alt_all_subdomains_UMAP=np.concatenate((alt_opt_clust_labels_GCU, alt_opt_clust_labels_CGU + alt_opt_clust_labels_GCU.max() + 1))


visualize_reduction(UMAP_coordinates,
color_mappings=alt_all_subdomains_UMAP,
cmap=cm.magma,
savepath='./substatesfigs/alt_UMAP_clustering',
title='UMAP Dimensional Reduction with umap_clustering_results',
cbar_label='System',
gridvisible=True)

visualize_reduction(X_PCA,
                    color_mappings=alt_all_subdomains_UMAP,
                    cmap=cm.magma_r,
                    savepath='./substatesfigs/altUMAP_clustering_PCAspace',
                    title='PCA Dimensional Reduction with UMAP trajectory highlighting',
                    cbar_label='K =',
                    gridvisible=True)#all reps



