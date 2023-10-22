import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import mne
from get_paths import *
from get_data_lists import *
from avg_brain_plotting import plot_seeg_electrodes_3d
from read_channel_features import *
from read_channloc_table import *


pat_files = get_pre_rftc_files()
sel_pats = range(1, len(pat_files))
# sel_pats = [3, 12, 14, 16, 18, 19, 20]
all_zones = ["All", "Site", "Structure", "Lobe",
             "Hemisphere", "Func.Connected", "High EI"]

# sel_pats = [19]
# all_zones = ["Structure"]

for pi in sel_pats:
    for zi in range(len(all_zones)):
        pat_name = pat_files[pi]
        zone_name = all_zones[zi]
        # Parameters for eeg, coordinates and characterization files
        max_read_t = 60
        eeg_fn = get_eeg_path() + pat_name + '.vhdr'
        coord_fn = get_coordinates_path() + pat_name + '.csv'
        feat_table_pre_fn = get_charact_paths() + "GroupCharacterization_FlexK_Pre.xls"
        feat_table_post_fn = get_charact_paths() + "GroupCharacterization_FlexK_Post.xls"

        # Read EEG
        raw = mne.io.read_raw_brainvision(eeg_fn)

        # Read channels and their coordinates, "MNI", "T1preScannerBased"
        channloc_table = read_channloc_table(coord_fn, "T1preScannerBased")

        # Read channels and their characterization
        unip_features = read_channel_features(
            feat_table_pre_fn, pat_name, zone_name)

        if len(unip_features) == 0:
            continue

        if zone_name == "Site":
            zone_descr = unip_features['zone']
            print(zone_descr[0])
            stop = 1

        # get channels in EEG but not in MRI coordinates
        ignore_list_a = get_channels_to_ignore()
        ignore_list_b = []
        nr_ignore_channs = 0
        for eegch in raw.ch_names:
            if eegch not in channloc_table['ch'] or eegch not in unip_features['ch']:
                ignore_list_b.append(eegch)
                nr_ignore_channs += 1
        ignore_list_all = ignore_list_a + ignore_list_b
        if nr_ignore_channs == len(raw.ch_names):
            continue

        # Drop EEG channeles without coordinates
        raw.drop_channels(ignore_list_all, on_missing='warn')
        raw.set_channel_types(
            dict(zip(raw.ch_names, ['eeg']*len(raw.ch_names))))
        raw.crop(tmin=0.0, tmax=max_read_t)

        # Create Montage structure
        mtg_dict = {}
        for eci in range(len(raw.ch_names)):
            eeg_ch = raw.ch_names[eci]
            for cci in range(len(channloc_table['ch'])):
                coord_ch = channloc_table['ch'][cci]
                if eeg_ch == coord_ch:
                    mtg_dict[eeg_ch] = [channloc_table['x'][cci],
                                        channloc_table['y'][cci], channloc_table['z'][cci]]
                    stop = 1

        # 'meg', 'mri', 'mri_voxel', 'head', 'mni_tal', 'ras', 'fs_tal', 'ctf_head', 'ctf_meg', 'unknown'.
        mtg = mne.channels.make_dig_montage(mtg_dict, coord_frame='unknown')
        raw.set_montage(mtg)
        epochs = mne.make_fixed_length_epochs(
            raw, duration=max_read_t, preload=False)

        print(zone_name)
        print(epochs.ch_names)
        # continue

        plot_pat_name = [str(pi), str(zi), zone_name, pat_name]
        plot_seeg_electrodes_3d(plot_pat_name, epochs)
