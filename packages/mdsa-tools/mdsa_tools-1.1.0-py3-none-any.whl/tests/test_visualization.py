import os
import numpy as np
import pytest

from mdsa_tools.Viz import visualize_reduction, replicatemap_from_labels


def test_visualize_reduction_continuous_saves_file(tmp_path, small_embedding):

    '''
    Nice to have, tests continous colormap of test reduction although this may break with >1000 frames from experience so not sure
    the fixture is the best possible option or maybe we should set up some kind of other fixture for large sizes or atleast
    fore-warn that for all visualizations we expect a reasonable number of bins.
    '''

    out = tmp_path / "viz_continuous.png"
    visualize_reduction(
        embedding_coordinates=small_embedding,
        color_mappings=None,      # triggers continuous colormap branch
        savepath=str(out),        # function expects a file path here
        title="Test Continuous",
        cmap=None,
        axis_one_label=None,
        axis_two_label=None,
        cbar_label=None,
        gridvisible=False
    )
    assert out.exists(), "visualize_reduction did not create the output file"
    assert out.stat().st_size > 0, "output image is empty"


def test_replicatemap_from_labels_saves_png(tmp_path, simple_labels_and_frames):
    labels, frame_list = simple_labels_and_frames
    save_dir = './tests/test_output/test_repmap'
    replicatemap_from_labels(
        labels=labels,
        frame_list=frame_list,
        savepath=save_dir,
        title="Replicate Map Test",
        xlabel="Frame",
        ylabel="Replicate",
        cmap=None,
    )

    
    return

@pytest.mark.parametrize(
    "bad_labels, frame_list",
    [
        ([0, 1], [3, 2]),            # sum(frames)=5, labels=2 -> mismatch
        ([0, 1, 2, 3, 4], [5, 1]),   # sum=6 vs len=5
    ]
)

def test_replicatemap_mismatched_lengths_raise_or_plot(tmp_path, bad_labels, frame_list):
    from mdsa_tools.Viz import replicatemap_from_labels

    labels = np.array(bad_labels, dtype=int)
    save_dir = str(tmp_path) + os.sep

    try:
        replicatemap_from_labels(labels, frame_list, savepath=save_dir)
    except Exception:
        # Raising is acceptable for mismatched inputs
        return

    out = tmp_path / "replicate_map.png"
    assert out.exists(), "Expected a plot or an error when labels length != sum(frame_list)"