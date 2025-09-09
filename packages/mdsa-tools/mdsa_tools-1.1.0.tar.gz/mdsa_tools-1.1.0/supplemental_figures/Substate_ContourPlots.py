import numpy as np
from matplotlib import cm

X_pca=np.load('X_PCA_both_sys_embeddingspace.npy')
GCU_coordinates=X_pca[0:3200,:]
CGU_coordinates=X_pca[3200:,:]

from mdsa_tools.Viz import contour_embedding_space

contour_embedding_space(outfile_path='./contourmaps/GCU_',embeddingspace_coordinates=GCU_coordinates,
title='Contour of Frames in System (GCU)')
contour_embedding_space(outfile_path='./contourmaps/CGU_',embeddingspace_coordinates=CGU_coordinates,
title='Contour of Frames in System (CGU)')
contour_embedding_space(outfile_path='./contourmaps/Global_candidate_states',embeddingspace_coordinates=X_pca,title='Global candidate states')