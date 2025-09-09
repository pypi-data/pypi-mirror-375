import numpy as np
import os
import pandas as pd

class MSM_Modeller():

    def __init__(self,labels,centers,reduced_coordinates,frame_scale):
        '''A module for evaluating and modelling the candidate states and subsequent MSM of an emebddingspace.

        
        Parameters
        ----------


        Returns
        -------


        Notes
        -----


        Examples
        --------

        '''

        self.labels=labels if labels is not None else None 
        self.centers=centers if centers is not None else None 
        self.frame_scale=frame_scale if frame_scale is not None else None 
        self.reduced_coordinates=reduced_coordinates if reduced_coordinates is not None else None

    #Candidate State Evaluation
    def rmsd_from_centers(self, X, labels, centers):
        results = []
        for k in np.unique(labels):
            m = (labels == k)  # mask frames belonging to cluster k
            d = np.linalg.norm(X[m] - centers[int(k)], axis=1)
            rmsd = float(np.sqrt(np.mean(d**2)))
            results.append((int(k), rmsd))
        results=np.array(results)
        return results

    def evaluate_cohesion_slidingwindow(self,labels=None,centers=None,reduced_coordinates=None,frame_scale=None,step_size=None):
        '''evaluate whether trajectories are temporally settling into the candidate states
        
        Paramters
        ---------
        candidatestates=arraylike,default=mdsa_tools.Analysis.cluster_embeddingspace(),shape=(number_of_systems_)
            A list of arrays holding, each array in every system contains the cluster assignments and labels returned
            from the system analysis module's preform_clust_opt() operation.
        
        reduced coordinates =arraylike,shape=(n_samples,2)
            The results of either Principal Components Analysis or UMAP reduction to 2 new dimensions.
        
        frame_scale:list of int, optional
            A list holding integer counts of the number of frames in each replicate. 
            Default is (([80] * 20) + ([160] * 10)) * 2.
        
        
            
        
        Returns
        -------



        Notes
        -----




        Examples
        --------



        
        '''
        reduced_coordinates=reduced_coordinates if reduced_coordinates is not None else self.reduced_coordinates
        frame_scale=frame_scale if frame_scale is not None else self.frame_scale
        step_size = step_size if step_size is not None else 10
        labels = labels if labels is not None else self.labels        
        centers = centers if centers is not None else self.centers


        slidingwindow=0
        window_df_all=[]
        for j in range(1,(np.max(frame_scale)//step_size)+1):
            print(f"shrink: {j}")

            mask=[]

            #iterate through reps and make mask
            for rep_length in frame_scale:
                
                if slidingwindow>rep_length:
                    replicate_bools = np.full(rep_length,False)
                    mask.append(replicate_bools)
                    continue

                replicate_bools = np.full(rep_length,False)
                replicate_bools[slidingwindow:slidingwindow+step_size]=True
                mask.append(replicate_bools)
            

            slidingwindow+=step_size#increase creep

            #apply mask save current window as a pd 
            window_mask=np.concatenate(mask)
            window_labels=labels[window_mask]
            window_coordinates=reduced_coordinates[window_mask,:]

            rmsd_results = self.rmsd_from_centers(window_coordinates,window_labels,centers)
            windowdf=pd.DataFrame(rmsd_results,columns=('cluster','rmsd'))
            windowdf['window'] = j
            
            window_df_all.append(windowdf)

                
        #concatenate pd and return
        window_df_all=pd.concat(window_df_all)
        

        
        return window_df_all

    def evaluate_cohesion_shrinkingwindow(self,labels=None,centers=None,reduced_coordinates=None,frame_scale=None,step_size=None):
        '''shrinking window version of slidingwindow
        '''
        reduced_coordinates=reduced_coordinates if reduced_coordinates is not None else self.reduced_coordinates
        frame_scale=frame_scale if frame_scale is not None else self.frame_scale
        step_size = step_size if step_size is not None else 10

        labels = labels if labels is not None else self.labels        
        centers = centers if centers is not None else self.centers

        creepingstart=0
        window_df_all=[]
        for j in range(1,(np.max(frame_scale)//step_size)+1):
            print(f"shrink: {j}")

            mask=[]

            #iterate through reps and make mask
            for rep_length in frame_scale:
                if creepingstart>rep_length:
                    replicate_bools = np.full(rep_length,False)
                    mask.append(replicate_bools)
                    continue
                
                replicate_bools = np.full(rep_length,True)
                replicate_bools[0:creepingstart]=False
                mask.append(replicate_bools)


            #apply mask save currenti window as a pd 
            window_mask=np.concatenate(mask)

            window_labels=labels[window_mask]
            window_coordinates=reduced_coordinates[window_mask,:]

            rmsd_results = self.rmsd_from_centers(window_coordinates,window_labels,centers)
            windowdf=pd.DataFrame(rmsd_results,columns=('cluster','rmsd'))
            windowdf['window'] = j
            
            creepingstart+=step_size#oincrease creep

            window_df_all.append(windowdf)

            
        #concatenate pd and return
        window_df_all=pd.concat(window_df_all)
        print(window_df_all)
   
        return window_df_all

    def compute_implied_timescales(self, lags, labels=None, frame_list=None, n_timescales=10):
        """
        Compute implied timescales as a function of lag time.
        
        Parameters
        ----------
        lags : list of int
            Lag times to evaluate.
        labels : array-like
            State labels.
        frame_list : list-like
            Frame counts per trajectory.
        n_timescales : int
            Number of slowest timescales to return.

        Returns
        -------
        dict of lag -> timescales
        """

        results = {}

        for lag in lags:
            T = self.create_transition_probability_matrix(
                labels=labels, frame_list=frame_list, lag=lag
            )[1:,1:]  # strip index row/col

            eigvals, _ = np.linalg.eig(T.T) #transpose bc row normalized
            eigvals = np.real(eigvals)

            # sort by magnitude, ignore the trivial 1
            eigvals = np.sort(np.abs(eigvals))[::-1][1:n_timescales+1]

            timescales = -lag / np.log(eigvals)
            results[lag] = timescales

        return results

    def chapman_kolmogorov_test(self, labels=None, frame_list=None, lag=None, steps=4):
        """
        Compare predicted vs. direct transition matrices at multiples of lag.
        
        Parameters
        ----------
        lag : int
            Base lag time.
        steps : int
            How many multiples of lag to test (e.g. 2τ, 3τ, 4τ).
        """
        labels=labels if labels is not None else self.labels
        lag=lag if lag is not None else 30
        frame_list=frame_list if frame_list is not None else self.frame_scale
        # Transition matrix at lag τ
        T_tau = self.create_transition_probability_matrix(labels, frame_list, lag=lag)[1:,1:]

        results = {}
        for k in range(1, steps+1):
            # Predicted transition matrix
            T_pred = np.linalg.matrix_power(T_tau, k)

            # Directly estimated from data
            T_direct = self.create_transition_probability_matrix(labels, frame_list, lag=lag*k)[1:,1:]

            results[k] = (T_pred, T_direct)

        return results

    #Creation of Transition Probability Matrix
    def create_transition_probability_matrix(self,labels=None,frame_list=None,lag=None):
        '''Create probability matrix from input data (returns, and updates class attribute)

        Parameters
        ----------
        labels:arraylike,shape=(n_labels,)
            A list of labels pertaining to frames of molecular dynamics trajectories assigned particular substates

        frame_list: listlike,shape=(data,)
            A list of integers representing the number of frames present in each replicate. This should be in the order
            of which the various versions of the system, and replicates where concatenated. 

        
        Returns
        -------
        transition_probability_matrix:arraylike;shape=(n_states+1,n_states+1)
            A transition probability matrix created from the list of labels. Diagonals indicate
            if it is likely to stay in the same state and off diagonals mark probabilities of transitions



        
        Notes
        -----
        Much in the spirit of our original matrices the first row and column of theese matrices contain
        indexes mainly for ease of use and manipulation. Yes, in theory pandas dataframes could streamline this process
        but, numpy arrays are just that much more efficient in most use cases,



        Examples
        --------

        

        '''


        labels=labels if labels is not None else self.labels
        frame_list=frame_list if frame_list is not None else self.frame_scale
        lag=lag if lag is not None else 1

        #extract unique states and initiate transiiton probability matrix
        unique_states=np.unique(labels)
        number_of_states=len(unique_states)
        transtion_prob_matrix=np.zeros(shape=(number_of_states,number_of_states))
        
        iterator=0
        for trajectory_length in frame_list: # iterate through 

            current_trajectory=labels[iterator:iterator+trajectory_length]
            iterator=iterator+trajectory_length #update this 

            if lag>=trajectory_length:#so we only use the long data
                continue

            for i in range(current_trajectory.shape[0]-lag):
                current_state=current_trajectory[i]
                next_state = current_trajectory[i+lag]
                transtion_prob_matrix[current_state, next_state] += 1

        row_sums = transtion_prob_matrix.sum(axis=1, keepdims=True)

        print(f"matrix counts before rownorm:\n{transtion_prob_matrix}")

        transition_probs = np.divide(
                    transtion_prob_matrix, row_sums,
                    out=np.zeros_like(transtion_prob_matrix), #because we dont want to divide by zero!
                    where=row_sums>0
                )

        final_transition_prob_matrix=np.zeros(shape=(number_of_states+1,number_of_states+1))
        final_transition_prob_matrix[1:,1:]=transition_probs
        final_transition_prob_matrix[0,1:],final_transition_prob_matrix[1:,0]=unique_states,unique_states

        self.transition_probability_matrix=final_transition_prob_matrix

        return final_transition_prob_matrix
    
    def extract_stationary_states(self,final_transition_prob_matrix=None):
        '''grab eigenvalues and eigenvectors of the transition matrix
        
        '''

        if final_transition_prob_matrix is None:
            final_transition_prob_matrix=self.create_transition_probability_matrix()

        # Get the "core" transition matrix without labels
        T = final_transition_prob_matrix[1:, 1:]

        # Compute eigenvalues and eigenvectors of the transpose
        eigvals, eigvecs = np.linalg.eig(T.T)

        print(f"eigenvals:{eigvals},eigvecs:{eigvecs}")

        # Find the eigenvector for eigenvalue closest to 1
        idx = np.argmin(np.abs(eigvals - 1))
        stationary = np.real(eigvecs[:, idx])
        print(f"idx:{idx},stationary:{stationary}")

        # Normalize to sum to 1
        stationary = stationary / stationary.sum()
        print(f"stationary:{stationary}")

        print("Eigenvalues:", eigvals)
        print("Stationary distribution:", stationary)


        return stationary
   
    def evaluate_Chapman_Kolmogorov(self,transition_probability_matrix=None,n=None,labels=None,original_lag=None):
        '''evaluate if the chapman kolmogorov test evaluates to true

        Parameters
        ----------
        n:int,default=4
            The original number of lags we used to compute the transition probability matrix
        
        transition_proability_matrix:arraylike,shape=(n_states+1,n_states+1),

        n:int,default=4
            The time lag we are using to compute our labels

        labels:arraylike,default=self.labels
            The list of labels we are using for the labeling of data from trajectories. 
        
        original_lag:int:default=1


        Notes
        -----

        
        Returns
        -------



        Examples
        --------
        
        
        '''

        transition_probability_matrix=transition_probability_matrix if transition_probability_matrix is not None else self.create_transition_probability_matrix()
        original_lag=original_lag if original_lag is not None else 1
        n = n if n is not None else 4
        labels=labels if labels is not None else self.labels

        transition_prob_data=transition_probability_matrix[1:,1:]
        post_timestep_data=np.linalg.matrix_power(transition_prob_data,n)
        transition_probability_matrix[1:,1:]=post_timestep_data

        total_lag=original_lag*n
        matrix_from_total_lag = self.create_transition_probability_matrix(lag=total_lag)
        diff=matrix_from_total_lag[1:,1:]-transition_probability_matrix[1:,1:]
        frob = np.linalg.norm(diff, ord='fro')

        return frob
    

    if __name__=="__main__":
    
        from mdsa_tools.Analysis import systems_analysis
        import numpy as np
        import matplotlib.cm as cm
        import os
        import pandas as pd
        from mdsa_tools.msm_modeler import MSM_Modeller as msm

        #Pipeline setup assumed as in: Data Generation
        redone_CCU_GCU_fulltraj=np.load('/Users/luis/Downloads/redone_unrestrained_CCU_GCU_Trajectory_array.npy',allow_pickle=True)
        redone_CCU_CGU_fulltraj=np.load('/Users/luis/Downloads/redone_unrestrained_CCU_CGU_Trajectory_array.npy',allow_pickle=True)

        from mdsa_tools.Viz import visualize_reduction
        persys_frame_list=((([80] * 20) + ([160] * 10)))
        persys_frame_short=([80] * 20) 
        persys_frame_long= ([160] * 10)

        #Just out of curiosity try just gcu
        all_systems=[redone_CCU_GCU_fulltraj]
        Systems_Analyzer = systems_analysis(systems_representations=all_systems,replicate_distribution=persys_frame_list)
        Systems_Analyzer.replicates_to_featurematrix()
        X_pca,_ ,_=Systems_Analyzer.reduce_systems_representations()
        cluster_labels,cluster_centers=Systems_Analyzer.cluster_system_level(data=X_pca,k=6,outfile_path='../manuscript_explorations/GCU_solo/GCU_pcaspace_clustersolo')#because we define k so no sets

        visualize_reduction(X_pca,color_mappings=cluster_labels,savepath='../manuscript_explorations/GCU_solo/GCU_pcaspace_clustersolo',cmap=cm.inferno_r)


        #################################################
        #building replicate maps to visualize transition#
        #################################################
        from mdsa_tools.Viz import replicatemap_from_labels
    
        GCU_with_filler=np.concatenate((cluster_labels,np.full(shape=(3200,),fill_value=np.max(cluster_labels)+1)))
        replicatemap_from_labels(GCU_with_filler,persys_frame_list*2,savepath='../manuscript_explorations/replicate_maps/6klust_replicate_map',title='6klust_replicate_map')
        fourk_modeller=msm(cluster_labels,cluster_centers,X_pca,frame_scale=persys_frame_list)
        GCU_transition_prob_matrix = fourk_modeller.create_transition_probability_matrix()
        stationarystates = fourk_modeller.extract_stationary_states()

        np.savetxt('../manuscript_explorations/GCU_solo/GCUsolo_transition_prob_matrix.csv',GCU_transition_prob_matrix,delimiter=',')
        os._exit(0)

        coordinates=[X_pca[0:3200,:],X_pca[3200:,:]]
