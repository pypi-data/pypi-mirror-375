from mdsa_tools.Analysis import systems_analysis
import numpy as np
import matplotlib.cm as cm


N, take = 3200, 10       # total number, threshold
b = np.arange(N) % 3200  # position within each 3200-frame block


########################################################################

#Pipeline setup assumed as in: Data Generation
redone_CCU_GCU_fulltraj=np.load('/Users/luis/Downloads/redone_unrestrained_CCU_GCU_Trajectory_array.npy',allow_pickle=True)
redone_CCU_CGU_fulltraj=np.load('/Users/luis/Downloads/redone_unrestrained_CCU_CGU_Trajectory_array.npy',allow_pickle=True)

from mdsa_tools.Viz import visualize_reduction
persys_frame_list=((([80] * 20) + ([160] * 10))*2)

#For the paper we move forward with systems representations
all_systems=[redone_CCU_GCU_fulltraj,redone_CCU_CGU_fulltraj]
Systems_Analyzer = systems_analysis(systems_representations=all_systems,replicate_distribution=persys_frame_list)
Systems_Analyzer.replicates_to_featurematrix()
X_pca,_ ,_=Systems_Analyzer.reduce_systems_representations()

np.set_printoptions(threshold=np.inf, linewidth=200)

########################
########long only#######
########################

start_mask = ((b >= 1600) & (((b - 1600) % 160) < 20)).astype(int)
end_mask = ((b >= 1600) & (((b - 1600) % 160) >= 140)).astype(int)

visualize_reduction(X_pca[0:3200,:],color_mappings=start_mask,title='long only GCU first20ns of every trajectory',
savepath='./PCA_cohesion_visuals/long_only_GCUfirst20ns_10frame',
cmap=cm.magma_r,
gridvisible=True)

visualize_reduction(X_pca[3200:,:],color_mappings=start_mask,title='long only CGU first 20ns of every trajectory',
savepath='./PCA_cohesion_visuals/long_only_CGUfirst20ns_10frame',
cmap=cm.magma_r,
gridvisible=True)

visualize_reduction(X_pca[0:3200,:],color_mappings=end_mask,title='long only GCU last 20ns of every trajectory',
savepath='./PCA_cohesion_visuals/long_only_GCUlast20ns_10frame',
cmap=cm.magma_r,
gridvisible=True)

visualize_reduction(X_pca[3200:,:],color_mappings=end_mask,title='long only CGU last 20ns of every trajectory',
savepath='./PCA_cohesion_visuals/long_only_CGUlast20ns_10frame',
cmap=cm.magma_r,
gridvisible=True)

np.set_printoptions(threshold=np.inf, linewidth=200)

########################
#short only#############
########################

start_mask = ((b < 1600)  & ((b % 80)  < 10)).astype(int)
end_mask = ((b < 1600)  & ((b % 80)  >= 70)).astype(int)

print(start_mask[start_mask==1].shape)
print(end_mask[end_mask==1].shape)

visualize_reduction(X_pca[0:3200,:],color_mappings=start_mask,title='short only GCU first20ns of every trajectory',
savepath='./PCA_cohesion_visuals/short_only_GCUfirst20ns_10frame',
cmap=cm.magma_r,gridvisible=True)

visualize_reduction(X_pca[3200:,:],color_mappings=start_mask,title='short only CGU first 20ns of every trajectory',
savepath='./PCA_cohesion_visuals/short_only_CGUfirst20ns_10frame',
cmap=cm.magma_r,gridvisible=True)

visualize_reduction(X_pca[0:3200,:],color_mappings=end_mask,title='short only GCU last 20ns of every trajectory',
savepath='./PCA_cohesion_visuals/short_only_GCUlast20ns_10frame',
cmap=cm.magma_r,gridvisible=True)

visualize_reduction(X_pca[3200:,:],color_mappings=end_mask,title='short only CGU last 20ns of every trajectory',
savepath='./PCA_cohesion_visuals/short_only_CGUlast20ns_10frame',
cmap=cm.magma_r,gridvisible=True)

np.set_printoptions(threshold=np.inf, linewidth=200)