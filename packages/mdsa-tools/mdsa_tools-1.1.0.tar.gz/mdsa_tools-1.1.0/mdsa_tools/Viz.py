import numpy as np
import os
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import pycircos.pycircos as py 
import seaborn as sns
from matplotlib.colors import BoundaryNorm
import matplotlib.colors as mcolors
from matplotlib.cm import ScalarMappable

#Miscellaneous tools
def add_continuous_colorbar(scatter, labels, cbar_label=None, ax=None, cmap=None,
                            extend="neither", format=None):
    """
    Continuous colorbar alternative to `add_custom_colorbar`.
    Works with numeric and non-numeric labels.
    """
    if ax is None:
        ax = plt.gca()

    cmap_obj = plt.get_cmap(cmap or cm.inferno)

    # Build numeric values
    if labels is None:
        n = scatter.get_offsets().shape[0]
        vals = np.arange(n, dtype=float)
    else:
        vals = np.asarray(labels)

    if not np.issubdtype(vals.dtype, np.number):
        _, inv = np.unique(vals, return_inverse=True)
        vals = inv.astype(float)

    finite = np.isfinite(vals)
    if not finite.any():
        vmin, vmax = 0.0, 1.0
    else:
        vmin = float(np.nanmin(vals[finite]))
        vmax = float(np.nanmax(vals[finite]))
        if vmin == vmax:
            pad = 0.5 if vmin == 0 else 0.01 * abs(vmin)
            vmin, vmax = vmin - pad, vmax + pad

    norm = mcolors.Normalize(vmin=vmin, vmax=vmax)

    # Make sure the scatter is actually using this data/norm/cmap
    scatter.set_norm(norm)
    scatter.set_cmap(cmap_obj)
    scatter.set_array(vals)

    mappable = ScalarMappable(norm=norm, cmap=cmap_obj)
    mappable.set_array(vals)
    cbar = plt.colorbar(mappable, ax=ax, extend=extend, format=format)
    if cbar_label:
        cbar.set_label(cbar_label, fontsize=10)
    return cbar

def add_custom_colorbar(scatter, labels, cbar_label=None, ax=None, cmap=None):
    if ax is None:
        ax = plt.gca()

    labels = np.asarray(labels)
    uniques, label_ids = np.unique(labels, return_inverse=True)
    N = len(uniques)

    cmap = cmap if cmap is not None else cm.inferno
    bounds = np.arange(-0.5, N + 0.5, 1)  # [-0.5, 0.5], [0.5, 1.5]
    norm = BoundaryNorm(bounds, cmap.N)

    scatter.set_cmap(cmap)
    scatter.set_array(label_ids)
    scatter.set_norm(norm)

    cbar = plt.colorbar(scatter, ax=ax, boundaries=bounds,
                        ticks=np.arange(N), pad=0.02, shrink=0.8)
    cbar.set_label(cbar_label or 'Value', fontsize=10)

    if N>100:
        tick_positions = np.arange(N)[::10]         # every 10th tick
        tick_labels   = [str(u) for u in uniques][::10]
        cbar.set_ticks(tick_positions)
        cbar.set_ticklabels(tick_labels)
        return cbar

    cbar.set_ticklabels([str(u) for u in uniques])

    return cbar

def set_ticks(ax=None):
    """
    Set x and y ticks for an axis. If the axis range is greater than 100,
    ticks are placed every 10 units. Otherwise, the default tick locator
    from Matplotlib is preserved.

    Parameters
    ----------
    ax : matplotlib.axes.Axes, default=None
        Axis to apply tick settings. Defaults to current axis.

    Returns
    -------
    None
        Modifies the axis in place.
    """
    if ax is None:
        ax = plt.gca()

    xmin, xmax = ax.get_xlim()
    if xmax - xmin > 100:
        ax.set_xticks(np.arange(np.floor(xmin), np.ceil(xmax) + 1, 10))

    ymin, ymax = ax.get_ylim()
    if ymax - ymin > 100:
        ax.set_yticks(np.arange(np.floor(ymin), np.ceil(ymax) + 1, 10))

    return

#Replicate maps
def replicatemap_from_labels(labels,frame_list,
                            savepath=None,
                            title=None,
                            xlabel=None, ylabel=None,
                            cbar_label=None,
                            cmap=None,
                             ) -> np.ndarray:
    '''returns an array consisting of a re-formatted list of labels through which to view a set.

    Parameters
    ----------
    labels: listlike,shape=(data,)
        A list of labels representing all of the labels from either a Kmeans or other analysis that we would like to
        use for our analysis.

    frame_list: listlike,shape=(data,)
        A list of integers representing the number of frames present in each replicate. This should be in the order
        of which the various versions of the system, and replicates where concatenated. 

    savepath:str,default=os.getcwd()
        Path to where you would like to save your plot; generally dpi=800 and default is the directory you are running from

    title : str, default = None
        Optional title for the plot.

    xlabel : str, default = None
        Optional label for the x-axis.

    ylabel : str, default = None
        Optional label for the y-axis.

    Returns
    -------
    reformatted_labels:numpy.ndarray,shape=(n_replicates,n_frames)
        A final array is returned where each row corresponds to one of our replicates in simulations.
        Each column corresponds to that particular frame in the replicate. If there are replicates of varying lengths
        we pad all to the longest trajectorys length with masked nans.

        
    Examples
    -------- 
    

    Notes
    -----
    

    '''

    cmap=cmap if cmap is not None else cm.magma_r

    savepath=savepath if savepath is not None else os.getcwd()


    iterator=0
    final_coordinates=[]



    for i in range(len(frame_list)):

        current_frame_length=frame_list[i]

        current_replicate_coordinates=np.full(shape=(current_frame_length,),fill_value=i) #make list of 11111 then 22222 for each rep
        frame_positions=np.arange(current_frame_length)
        frame_values=labels[iterator:iterator+current_frame_length]
        (frame_values.shape)
        replicate_block = np.stack([current_replicate_coordinates, frame_positions, frame_values], axis=1)
        final_coordinates.append(replicate_block)
        iterator+=current_frame_length
    
    final_coordinates = np.vstack(final_coordinates)
    
    y_spacing_factor = 1
    x_spacing_factor = 1
    
    
    scatter=plt.scatter(
                x=final_coordinates[:,1] * x_spacing_factor,
                y=final_coordinates[:,0] * y_spacing_factor,
                c=final_coordinates[:,2],
                s=1,
                marker='s',
                cmap=cmap,
                alpha=1)
    
    #cbar and cbar ticks
    if np.unique(final_coordinates).shape[0]>=1000:
        add_continuous_colorbar(scatter,final_coordinates[:,2],cbar_label,plt.gca())
    if np.unique(final_coordinates).shape[0]<1000:
        add_custom_colorbar(scatter,final_coordinates[:,2],cbar_label,plt.gca())

    #personal preferences
    plt.grid(visible=False)
    currentaax=plt.gca()
    for spine in currentaax.spines.values():
        spine.set_visible(False)

    ax=plt.gca()
    ax.invert_yaxis()
    ax.set_title('Clusters per frame', fontsize=20, weight='bold', family='monospace', style='italic')
    n_reps = int(final_coordinates[:, 0].max())
    n_frames = int(final_coordinates[:, 1].max())
    
    if title:
        plt.title(title)
    if xlabel:
        plt.xlabel(xlabel)
    if ylabel:
        plt.ylabel(ylabel)



    plt.tight_layout()
    plt.savefig(f'{savepath}replicate_map.png', dpi=800)
    plt.close()

    return 

#K-means Cross-validation metrics
def plot_sillohette_scores(cluster_range, silhouette_scores, outfile_path="sillohette_method.png",
                           title=None, xlabel=None, ylabel=None):
    """
    Plot silhouette scores over k and mark the maximum.

    Parameters
    ----------
    cluster_range : array-like
        k values evaluated.

    silhouette_scores : array-like
        Silhouette score per k.

    outfile_path : str, default="sillohette_method.png"
        Path prefix where figure is saved (suffix 'sillohuette_plot' is appended).

    title, xlabel, ylabel : str or None
        Optional title/axis labels.

    Returns
    -------
    optimal_k_sil : int
        k with max silhouette score.
    """
    optimal_k_sil = cluster_range[np.argmax(silhouette_scores)]#return index 
    # Plot Silhouette Scores
    plt.figure(figsize=(8, 5))
    plt.plot(cluster_range, silhouette_scores, marker='o', linestyle='-')
    plt.axvline(optimal_k_sil, color='red', linestyle='--', linewidth=2, label=f'Optimal k = {optimal_k_sil}')

    plt.xlabel(xlabel if xlabel is not None else 'Number of Clusters (k)')
    plt.ylabel(ylabel if ylabel is not None else 'Silhouette Score')
    plt.title(title if title is not None else 'Silhouette Score for optimal K')
    plt.legend()
    plt.grid(True)
    plt.savefig(outfile_path + 'sillohuette_plot', dpi=300)
    plt.close()
    return optimal_k_sil

def plot_elbow_scores(cluster_range, inertia_scores, outfile_path="elbow_method.png",
                      title=None, xlabel=None, ylabel=None):
    """
    Plot inertia over k and mark elbow via second derivative.

    Parameters
    ----------
    cluster_range : array-like
        k values evaluated.

    inertia_scores : array-like
        KMeans inertia per k.

    outfile_path : str, default="elbow_method.png"
        Path prefix where figure is saved (suffix 'elbow_plot' is appended).

    title, xlabel, ylabel : str or None
        Optional title/axis labels.

    Returns
    -------
    optimal_k : int
        Estimated elbow k.
    """
    diff = np.diff(inertia_scores)
    diff2 = np.diff(diff)
    optimal_k = cluster_range[np.argmin(diff2) + 1]

    plt.figure(figsize=(8, 5))
    plt.plot(cluster_range, inertia_scores, marker='o', linestyle='-')
    plt.axvline(optimal_k, color='red', linestyle='--', linewidth=2, label=f'Optimal k = {optimal_k}')

    plt.xlabel(xlabel if xlabel is not None else 'Number of Clusters (k)')
    plt.ylabel(ylabel if ylabel is not None else 'Inertia (Sum of Squared Distances)')
    plt.title(title if title is not None else 'Elbow Method for Optimal k')
    plt.legend()
    plt.grid(True)
    plt.savefig(outfile_path + 'elbow_plot', dpi=300)
    plt.close()

    return optimal_k

#Circos plots
def get_Circos_coordinates(residue, gcircle):
    """helper function for creating coordinates for arc sizes in Circos graph

    Parameters
    ----------
    residue:int,default=None
        A residue index from which to create the current arc (in general you will be iterating
        through residue indexes when using this method)

    gcirlce:py.Gcircle,default=py.Gcircle(figsize=(6,6))
        A Pycircos Gcricle object. By default we use one with a figsize of (6,6).

    

    Return a 4-element tuple telling PyCircos chord_plot()
    to start in the middle of the arc with a radial anchor of 550.



    Returns
    -------
    tuple:coordinates:defualt=(residue, mid_position, mid_position, raxis_position)
        A four member tuple consisting of the positioning needed to create an arc.



    Notes
    -----




    Examples
    --------


    
    """
    arc = gcircle._garc_dict[residue]
    # The "size" is the arc length in PyCircos coordinates
    mid_position = arc.size * 0.5  # center of the arc
    # We'll anchor all chords at radial = 550
    # (this can be changed if your arcs are drawn in a different radial band)
    raxis_position = 550
    return (residue, mid_position, mid_position, raxis_position)

def make_MDCircos_object(residue_indexes):
    """Returns a PyCircos Gcircle scaled arcs

    Returns a PyCircos Gcircle object whose arcs are automatically scaled
    based on how many arcs (residues) there are. Also scales line widths,
    so that very few arcs don't produce huge lines and many arcs don't
    produce lines too thin to see.

    Parameters
    ----------
    residue_indexes : list
        List of residue indices you want as arcs.

    Returns
    -------
    circle : py.Gcircle
        A PyCircos object containing arcs scaled by the number of residues.
    """

    if len(residue_indexes) <= 50:
        circle = py.Gcircle(figsize=(6, 6))
        plt.subplots_adjust(left=0.01, right=0.99, bottom=0.01, top=0.99)

        # Add each arc
        for index in residue_indexes:
            circle.add_garc(
                py.Garc(
                    arc_id=str(index),
                    facecolor='#FFFFFF',   
                    edgecolor='#000000',   
                    label=str(index),
                    label_visible=True,
                    labelposition=40,
                    labelsize=6,
                    size=10,        
                    interspace=0,          
                    linewidth=.1          
                )
            )

        circle.set_garcs()


    if len(residue_indexes) >50:
        circle = py.Gcircle(figsize=(10, 10))
        plt.subplots_adjust(left=0.01, right=0.99, bottom=0.01, top=0.99)

        # Add each arc
        for index in residue_indexes:
            circle.add_garc(
                py.Garc(
                    arc_id=str(index),
                    facecolor='#FFFFFF',   # White arcs
                    edgecolor='#000000',   # Black outline
                    label=str(index),
                    label_visible=True,
                    labelposition=30,
                    labelsize=2,
                    size=100,         # scaled by number of arcs
                    interspace=4,          # small gap
                    linewidth=.1           # scaled line thickness
                )
            )

    circle.set_garcs()
    return circle

def mdcircos_graph(empty_circle, residue_dict, savepath=os.getcwd()+'mdcircos_graph', scale_factor=5,colormap=cm.magma_r):
    ''' creates and saves a mdcircos graph to a desired output directory

    Parameters
    ----------
    Residue_indexes:list, shape=(n_residues)
        A list of residue indexes pertaining to the residues you would like to use as parts of the circle

    Residue_dict:dict,format:dict['residue']=float(value)
        A dictionary where keys are residue indexes (as strings) and values are floats representing the corresponding 
        edge weights in the adjacency matrix (or another method) used for mapping.

    savepath:str(),default=os.getcwd()+'mdcircos_graph'
        Absolute path to the location and name of the file you would like to save the file. Default is mdcircos_graph in the 
        working directory

    Residue_dict:dict,dict['residue']=float(value)
        A dictionary containing mappings from specific residue indexes *as strings* to their respective edge weights in whatever adjacency matrix
        (or other method) is being used as the basis for mapping.
    
    scale_values:bool,default=False
        A boolean argument meant to give the user the option of using a gradient color map in order to visualize stronger interactions

    Returns
    -------
    None
        Strictly a graphing function the methods can be called individually if youd like to tamper with the
        Circos object further


    Notes
    -----
    This is built as basically a wrapper for another python package so it is a little finicky in its implementation. In theory it should work fine
    with the other two functions and really only needs to be specific in the way that its taking the inputs for.
    
    An important note is that the scale is saved as a seperate colorbar and the values are normalized by min max because it takes
    generally as input the weightings which happen to be too small to really visualize well typically.

    
    Examples
    --------

    '''
   
    import matplotlib.pyplot as plt
    from matplotlib import cm
    from matplotlib.colors import Normalize
    import numpy as np


    # Normalize the colors based on the values provided 
    vals = list(residue_dict.values())
    vmin, vmax = min(vals), max(vals)
    color_norm = Normalize(vmin=vmin, vmax=vmax)
    cmap = colormap if colormap is not None else cm.plasma
    hex_color_map = {k: cmap(color_norm(v)) for k, v in residue_dict.items()}

    # Width normalization on the absolute values via min–max (makes plot aesthetically closer to raw
    # values it is still suggested to use outputted tables for any actual raw analysis of values)
    abs_vals = [abs(v) for v in vals if v != 0]
    min_abs, max_abs = min(abs_vals), max(abs_vals)

    # avoid division by zero if all values are the same magnitude
    denom = max_abs - min_abs if max_abs != min_abs else 1.0

    width_norm = {
        k: (abs(v) - min_abs) / denom
        for k, v in residue_dict.items()
    }

    # 3) Plot chords
    for key, value in residue_dict.items():
        if value == 0:
            continue
        
        res1, res2 = key.split('-')
        arc1 = get_Circos_coordinates(res1, empty_circle)
        arc2 = get_Circos_coordinates(res2, empty_circle)
        color = hex_color_map[key]

        lw = width_norm[key] * scale_factor
        empty_circle.chord_plot(arc1, arc2,
                                linewidth=lw,
                                facecolor=color,
                                edgecolor=color)

    empty_circle.figure.savefig(savepath + ".png",
                                dpi=300, bbox_inches="tight")

    # 4) Separate colorbar (using the original signed range)
    fig_cb, ax_cb = plt.subplots(figsize=(1.5, 4))
    sm = cm.ScalarMappable(cmap=cmap, norm=color_norm)
    sm.set_array([])

    cbar = plt.colorbar(sm, cax=ax_cb)
    ticks = np.linspace(vmin, vmax, num=6)
    cbar.set_ticks(ticks)
    cbar.set_ticklabels([f"{t:.2f}" for t in ticks])
    cbar.set_label("Directional Difference")

    fig_cb.savefig(savepath + "_colorbar.png",
                dpi=300, bbox_inches="tight")
    
    plt.close(fig_cb)

def extract_properties_from_weightsdf(pca_table):

    comps = pca_table['Comparisons'].astype(str)

    # split stack and clean
    sides = comps.str.split('-', n=1, expand=True)
    residues = (sides.stack()
                      .str.strip()
                      .dropna()
                      .unique())

    # arc ids are strings
    residues = [str(x) for x in residues]

    PC1_weight_dict = pca_table.set_index('Comparisons')['PC1_magnitude'].to_dict()
    PC2_weight_dict = pca_table.set_index('Comparisons')['PC2_magnitude'].to_dict()
    return residues, PC1_weight_dict, PC2_weight_dict

def create_MDcircos_from_weightsdf(PCA_ranked_weights, outfilepath=None):
    '''Processes Weights table to create MDcircos plots visualizing weightings

    Parameters
    ----------
    PCA_ranked_weights:Pandas.DataFrame,default=None
      A table containing the ranked weights we created as a part of the analysis Systems Analysis
      module. It is expected that it wold contain columns with the headers:

    Returns
    -------
    None

    Notes
    -----
    Mdcircos plots where arcs are residue indexes and line thickness and darkness are eigenvector coefficient magnituses. 



    Examples
    --------



    Notes
    -----


    '''
    outfilepath = outfilepath if outfilepath is not None else os.getcwd()

    res_indexes,PC1_magnitude_dict,PC2_magnitude_dict = extract_properties_from_weightsdf(PCA_ranked_weights)
    pc1_circos_object=make_MDCircos_object(res_indexes)
    pc2_circos_object=make_MDCircos_object(res_indexes)
    mdcircos_graph(pc1_circos_object,PC1_magnitude_dict,outfilepath+'PC1_magnitudeviz')
    mdcircos_graph(pc2_circos_object,PC2_magnitude_dict,outfilepath+'PC2_magnitudeviz') 

#Embeddingspace visualizations
def create_2d_color_mappings(labels=([80]*20)+([160]*10), 
                             colors_list=['purple', 'orange', 'green', 'yellow', 'blue', 'red', 'pink', 'cyan', 'grey', 'brown'], 
                             clustering=True):
    ''' 
    Parameters
    ----------
    labels: list, shape (n_samples), default=([80]*20)+([160]*10)
        A list of integers that help describe how you want to label each sample once they have been reduced to 2 dimensions.

    colors_list: list-like, default=['purple', 'orange', 'green', 'yellow', 'blue', 'red', 'pink', 'cyan', 'grey', 'brown']
        A list of colors that we can use to visualize all of our clusters.

    clustering: bool, default=True
        Whether to assign discrete colors for clusters (True) or use a heatmap-based visualization (False).
    '''

    if clustering == True:
        # Create a dictionary mapping each label to a color
        label_dict = {}
        i = 0
        for label in labels:
            if label not in label_dict:
                label_dict[label] = colors_list[i % len(colors_list)]  # Ensure cycling through colors if necessary
                i += 1
        sample_color_mappings = [label_dict[i] for i in labels]
        return sample_color_mappings

def visualize_reduction(embedding_coordinates, 
                        color_mappings=None, 
                        savepath=os.getcwd(), 
                        title=None, 
                        cmap=None,
                        axis_one_label=None,
                        axis_two_label=None,
                        cbar_label=None,
                        gridvisible=False):

    axis_one_label=None if axis_one_label is not None else 'Embedding Space Axis 1'
    axis_two_label=None if axis_two_label is not None else 'Embedding Space Axis 2'
    title=title if title is not None else "Dimensional Reduction of Systems"
    cbar_label=cbar_label if cbar_label is not None else "Value"
    cmap = cmap if cmap is not None else cm.magma_r

    labels_font_dict = {
        'family': 'monospace',
        'size': 20,
        'weight': 'bold',
        'style': 'italic',
        'color': 'black',
    }

    fig = plt.figure(figsize=(16, 12), dpi=300)
    ax = plt.gca()


    if color_mappings is not None and len(color_mappings) > 0:
        scatter=ax.scatter(embedding_coordinates[:, 0], embedding_coordinates[:, 1],
                            c=color_mappings, cmap=cmap, alpha=0.6)
        add_custom_colorbar(scatter, color_mappings, cbar_label, plt.gca(), cmap=cmap)
 
    if color_mappings is None or len(color_mappings) == 0:
        color_mappings = np.arange(embedding_coordinates.shape[0])
        print("No color_mappings provided — defaulting to sample index gradient.")
        scatter=ax.scatter(embedding_coordinates[:, 0], embedding_coordinates[:, 1],
                            c=color_mappings, cmap=cmap, alpha=0.6)
        add_continuous_colorbar(scatter, color_mappings, cbar_label, plt.gca(), cmap=cmap)


    # Final touches
    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.grid(visible=gridvisible)
    set_ticks(ax=plt.gca())
    ax.set_title(title, fontdict=labels_font_dict)
    ax.set_xlabel(axis_one_label, fontdict=labels_font_dict)
    ax.set_ylabel(axis_two_label, fontdict=labels_font_dict)
    ax.tick_params(axis='x', colors='black')  
    ax.tick_params(axis='y', colors='black')

    plt.tight_layout()
    plt.savefig(savepath, dpi=500)
    plt.close()

    return

#RMSD lineplots
def rmsd_lineplots(pandasdf=None,title='RMSD plot',
                xgroupvar='window',
                ygroupvar='rmsd',
                xlab="window",
                ylab="rmsd",
                groupingvar='cluster',
                cmap=cm.inferno_r,
                legendtitle='Cluster',
                outfilepath=os.getcwd()):
    '''
    Creates a line plot of RMSD values across a specified grouping variable.

    Parameters
    ----------
    pandasdf : pandas.DataFrame, default=None
        A DataFrame containing the values to be plotted. It should contain at least 
        the columns specified by `xgroupvar`, `ygroupvar`, and `groupingvar`.

    title : str, default='RMSD plot'
        Title for the plot.

    xgroupvar : str, default='window'
        Column name in `pandasdf` to be used as the x-axis variable.

    ygroupvar : str, default='rmsd'
        Column name in `pandasdf` to be used as the y-axis variable.

    xlab : str, default='window'
        Label for the x-axis.

    ylab : str, default='rmsd'
        Label for the y-axis.

    groupingvar : str, default='cluster'
        Column name in `pandasdf` used to group lines (e.g., clusters or categories) and
        Column name used by seaborn to color lines by category.

    palette : colormap or palette, default=cm.magma_r
        Color mapping for different groups. Accepts matplotlib colormap or seaborn palette.

    legendtitle : str, default='Cluster'
        Title for the legend.

    outfilepath : str, default=os.getcwd()
        Path prefix where the figure will be saved. The function appends '_rmsdlineplot' to this path.

    Returns
    -------
    None
        Saves the line plot to disk and displays it.

    Notes
    -----
    This function uses seaborn's lineplot for grouped visualization of RMSD trajectories 
    or similar metrics. It assumes the input DataFrame has one row per observation.

    Examples
    --------
    '''

    plt.figure(figsize=(10, 8))
    sns.lineplot(
        data=pandasdf,
        x=xgroupvar,
        y=ygroupvar,
        hue=groupingvar,   # automatically treats as categorical
        palette=cmap  # choose color palette
    )
    ax=plt.gca()

    for spine in ax.spines.values():
        spine.set_visible(False)

    plt.legend(title=legendtitle, bbox_to_anchor=(1.0, 1), loc="upper left")    
    plt.xlabel(xlab)
    plt.ylabel(ylab)
    plt.savefig(outfilepath+'_rmsdlineplot',dpi=800)
    
    plt.close()
    return


#Contour plots 
def contour_embedding_space(outfile_path, embeddingspace_coordinates, levels=10, thresh=0, bw_adjust=.5,
                             title=None, xlabel=None, ylabel=None,gridvisible=False):
    '''Plots a contour map of embedding space coordinates.

    Parameters
    ----------
    outfile_path : str or None
        Path to save the output plot. If None, defaults to the current working directory.

    embeddingspace_coordinates : array-like, shape = (n_samples, 2)
        The coordinates of your samples in the embedding space created by either UMAP or PCA.
        This function assumes a two-dimensional representation for visualization purposes.
        A Gaussian KDE (via Seaborn) is used to estimate the density.

    levels : int, default = 10
        Number of contour levels to draw.

    thresh : float, default = 0
        Only plot density regions where the estimated value is greater than this threshold.

    bw_adjust : float, default = 0.5
        Bandwidth adjustment factor for the KDE. Lower values give finer detail, higher values
        give smoother estimates.

    title : str, default = None
        Optional title for the plot.

    xlabel : str, default = None
        Optional label for the x-axis.

    ylabel : str, default = None
        Optional label for the y-axis.

    Returns
    -------
    None
        Saves the contour plot to the specified path.

    Notes
    -----
    This function wraps `sns.kdeplot` for quick integration into analysis workflows.
    For more customized control over contour appearance, call `sns.kdeplot` directly
    on the reduced coordinates.

    Examples
    --------
    contour_embedding_space("embedding_contour.png", X_pca, title="Embedding Space",
                            xlabel="PC1", ylabel="PC2")
    '''

    outfile_path = outfile_path if outfile_path is not None else os.getcwd()
    gridvisible = gridvisible if gridvisible is not None else False

    sns.kdeplot(
        x=embeddingspace_coordinates[:, 0],
        y=embeddingspace_coordinates[:, 1],
        fill=True,
        cmap="cividis",
        levels=levels,
        thresh=thresh,
        bw_adjust=bw_adjust,
        cbar=True
    )

    ax = plt.gca()
    
    for spine in ax.spines.values():
        spine.set_visible(False)

    if title:
        plt.title(title)
    if xlabel:
        plt.xlabel(xlabel)
    if ylabel:
        plt.ylabel(ylabel)

    plt.grid(visible=gridvisible)
    plt.savefig(outfile_path, dpi=800)
    plt.close()

    return


if __name__ == "__main__":
    frame_list=((([80] * 20) + ([160] * 10)) * 2)
    print('running just the visualization module')
    fake_labels=[1]*3200+[2]*3200
    print(fake_labels)
    replicatemap_from_labels(fake_labels,frame_list)