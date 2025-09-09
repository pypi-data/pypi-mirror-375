import numpy as np

GCU_opt_labels=np.load('klust/GCU_coordinates_kluster_labels_5clust.npy')
CGU_opt_labels=np.load('klust/CGU_coordinates_kluster_labels_2clust.npy')

from mdsa_tools.Viz import replicatemap_from_labels

persys_frame_distributions = ((([80] * 20) + ([160] * 10)))

replicatemap_from_labels(GCU_opt_labels,persys_frame_distributions,
title='GCU Substate transitions replicatemap',
cbar_label='State',
savepath='./replicate_maps/GCU',
)

replicatemap_from_labels(CGU_opt_labels,persys_frame_distributions,
title='CGU Substate transitions replicatemap',
cbar_label='State',
savepath='./replicate_maps/CGU',
)