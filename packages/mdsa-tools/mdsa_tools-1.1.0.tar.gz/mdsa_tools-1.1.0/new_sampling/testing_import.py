
import numpy as np
import mdtraj as md
from mdsa_tools.Data_gen_hbond import cpptraj_hbond_import
import os


file='./GCU_HBond_Matrix.dat'
topology='/Users/luis/Desktop/workspacetwo/PDBs/5JUP_N2_GCU_nowat.prmtop'

importer_instance=cpptraj_hbond_import(file,topology)
rep=importer_instance.create_systems_rep()
np.savez_compressed(f'GCU_1_in_10_sampling',rep=rep)
