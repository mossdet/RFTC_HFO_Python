import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mne
import os

from mne.datasets import fetch_fsaverage
from get_paths import *


def plot_seeg_electrodes_3d(pat_name, epochs):
    # paths to mne datasets - sample sEEG and FreeSurfer's fsaverage subject
    # which is in MNI space
    misc_path = mne.datasets.misc.data_path()
    sample_path = mne.datasets.sample.data_path()
    subjects_dir = sample_path / "subjects"

    # Plot sensors and brain
    plot_title_str = "_".join(pat_name)
    views_str = ['rostral', 'axial', 'coronal']
    for view_str in views_str:
        view_kwargs = dict(view=view_str)
        brain3d = mne.viz.Brain(
            "fsaverage",
            hemi='both',  # both split
            title=plot_title_str+"_"+view_str,
            subjects_dir=subjects_dir,
            cortex="low_contrast",  # 'bone' 'classic', 'high_contrast', 'low_contrast', or 'bone'
            alpha=0.1,
            background="white",
        )
        brain3d.add_sensors(epochs.info, trans='fsaverage')
        # brain3d.add_head(alpha=0.1, color="tan")
        brain3d.show_view(distance=400, **view_kwargs)

        pat_path = get_images_path() + pat_name[0]+'_'+pat_name[3]+os.path.sep
        os.makedirs(pat_path, exist_ok=True)

        new_name = pat_name[0]+'_' + view_str + '_' + \
            pat_name[1]+'_'+pat_name[3]+'_'+pat_name[2]
        brain3d_fn = pat_path + new_name + '.png'
        brain3d.save_image(filename=brain3d_fn)
        brain3d.close()


def plot_seeg_electrodes_3d_transform(pat_name, epochs):
    # paths to mne datasets - sample sEEG and FreeSurfer's fsaverage subject
    # which is in MNI space
    misc_path = mne.datasets.misc.data_path()
    sample_path = mne.datasets.sample.data_path()
    subjects_dir = sample_path / "subjects"

    # use mne-python's fsaverage data, downloads if needed
    fetch_fsaverage(subjects_dir=subjects_dir, verbose=True)

    montage = epochs.get_montage()

    # Transform coordinates to plot in freesurfer averag brain

    # first we need a head to mri transform since the data is stored in "head"
    # coordinates, let's load the mri to head transform and invert it
    this_subject_dir = misc_path / "seeg"
    head_mri_t = mne.coreg.estimate_head_mri_t("sample_seeg", this_subject_dir)
    # apply the transform to our montage
    ####################################
    montage.apply_trans(head_mri_t)

    # now let's load our Talairach transform and apply it
    mri_mni_t = mne.read_talxfm("sample_seeg", misc_path / "seeg")
    ####################################
    montage.apply_trans(mri_mni_t)  # mri to mni_tal (MNI Taliarach)

    # for fsaverage, "mri" and "mni_tal" are equivalent and, since
    # we want to plot in fsaverage "mri" space, we need use an identity
    # transform to equate these coordinate frames
    ####################################
    montage.apply_trans(mne.transforms.Transform(
        fro="mni_tal", to="mri", trans=np.eye(4)))

    epochs.set_montage(montage)

    ####################################
    trans = mne.channels.compute_native_head_t(montage)
    trans = 'fsaverage'

    # 4.Plot sensors and brain
    view_kwargs = dict(view='lateral', roll=-10, azimuth=150,
                       elevation=100, focalpoint=(0, 0, 0))
    brain3d = mne.viz.Brain(
        "fsaverage",
        hemi='both',
        title=pat_name,
        subjects_dir=subjects_dir,
        cortex="low_contrast",  # 'bone' 'classic', 'high_contrast', 'low_contrast', or 'bone'
        alpha=0.25,
        background="white",
    )
    brain3d.add_sensors(epochs.info, trans=trans)
    brain3d.add_head(alpha=0.1, color="tan")
    brain3d.show_view(distance=500, **view_kwargs)

    """     
    # Now, let's project onto the inflated brain surface for visualization.
    brain2d = mne.viz.Brain(
        "fsaverage", subjects_dir=subjects_dir, surf="inflated", background="black"
    )
    brain2d.add_annotation("aparc.a2009s")
    brain2d.add_sensors(epochs.info, trans='fsaverage')
    brain2d.show_view(distance=500, **view_kwargs)
    brain2d.close() 
    """

    brain3d_fn = get_images_path() + pat_name + ".png"
    brain3d.save_image(filename=brain3d_fn)
    brain3d.close()


def plot_seeg_electrodes_3d_old(epochs):
    # paths to mne datasets - sample sEEG and FreeSurfer's fsaverage subject
    # which is in MNI space
    # misc_path = mne.datasets.misc.data_path()
    sample_path = mne.datasets.sample.data_path()
    subjects_dir = sample_path / "subjects"

    # use mne-python's fsaverage data, downloads if needed
    fetch_fsaverage(subjects_dir=subjects_dir, verbose=True)

    montage = epochs.get_montage()

    trans = mne.channels.compute_native_head_t(montage)
    trans = 'fsaverage'

    # 4.Plot sensors and brain
    view_kwargs = dict(azimuth=105, elevation=100, focalpoint=(0, 0, -15))
    brain3d = mne.viz.Brain(
        "fsaverage",
        subjects_dir=subjects_dir,
        cortex="low_contrast",
        alpha=0.25,
        background="white",
    )
    brain3d.add_sensors(epochs.info, trans=trans)
    brain3d.add_head(alpha=0.25, color="tan")
    brain3d.show_view(distance=400, **view_kwargs)

    # Now, let's project onto the inflated brain surface for visualization.
    # This video may be helpful for understanding the how the annotations on
    # the pial surface translate to the inflated brain and flat map:
    #
    # .. youtube:: OOy7t1yq8IM
    brain2d = mne.viz.Brain(
        "fsaverage", subjects_dir=subjects_dir, surf="inflated", background="black"
    )
    brain2d.add_annotation("aparc.a2009s")
    brain2d.add_sensors(epochs.info, trans='fsaverage')
    brain2d.show_view(distance=500, **view_kwargs)

    brain3d.close()
    brain2d.close()
