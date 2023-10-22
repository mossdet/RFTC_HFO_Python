
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def read_channel_features(feat_table_fn, pat_name, zone_name):

    charact_table = pd.read_excel(feat_table_fn, sheet_name="HFO")

    # Select Patient
    sel_vec = charact_table['patName'] == pat_name
    charact_table = charact_table[sel_vec]

    bp_feat_table = {}
    bp_feat_table['idx'] = np.array(range(len(charact_table['patName'])))
    bp_feat_table['pat'] = np.array(charact_table['patName'])
    bp_feat_table['ch'] = np.array(charact_table['chName'])
    bp_feat_table['zone'] = np.array(charact_table['zone'])
    bp_feat_table['site'] = np.array(charact_table['rftcSite'] > 0)
    bp_feat_table['struct'] = np.array(charact_table['rftcStruct'] > 0)
    bp_feat_table['lobe'] = np.array(charact_table['rftcLobe'] > 0)
    bp_feat_table['hemis'] = np.array(charact_table['rftcHemis'] > 0)
    bp_feat_table['fconn'] = np.array(charact_table['rftcConn'] > 0)
    bp_feat_table['ei'] = np.array(charact_table['highEI'] > 0)

    # Copy numpy arrays with feature values
    unip_table_a = {}
    for key in bp_feat_table.keys():
        unip_table_a[key] = bp_feat_table[key].copy()

    # Assign only first channel to channel array
    for chi in range(len(bp_feat_table['ch'])):
        bip_name = bp_feat_table['ch'][chi]
        labels = bip_name.split("-")
        label = labels[0].replace(" ", "")
        unip_table_a['ch'][chi] = label

    # Copy numpy arrays with feature values
    unip_table_b = {}
    for key in bp_feat_table.keys():
        unip_table_b[key] = bp_feat_table[key].copy()

    # Assign only second channel to channel array
    for chi in range(len(bp_feat_table['ch'])):
        bip_name = bp_feat_table['ch'][chi]
        labels = bip_name.split("-")
        label = labels[1].replace(" ", "")
        unip_table_b['ch'][chi] = label
    # Increase index array by 0.5 to be able to sort it correctly later
    unip_table_b['idx'] = unip_table_b['idx']+0.5

    # Append both dictionaries to form the big table
    unip_table = {}
    for key in bp_feat_table.keys():
        unip_table[key] = np.append(unip_table_a[key], unip_table_b[key])

    # Sort the arrays
    # sort_idx = np.argsort(unip_table['idx'])
    # for key in bp_feat_table.keys():
    #    unip_table[key] = unip_table[key][sort_idx]

    # del unip_table['idx']

    # assign zone if it was ever a 1
    ch_labels = np.unique(unip_table['ch'])
    zone_names = ["site", "struct", "lobe", "hemis", "fconn", "ei"]
    for label in ch_labels:
        chsel = unip_table['ch'] == label

        for zn in zone_names:
            if sum(chsel) > 1 and sum(unip_table[zn][chsel]) > 0 and sum(unip_table[zn][chsel]) < sum(chsel):
                stop = 1
            val = sum(unip_table[zn][chsel]) > 0
            unip_table[zn][chsel] = val
    #
    #
    # Select table entries within Zone
    print(zone_name)
    zone_sel = []
    sitesel = unip_table['site'] > 0
    structsel = unip_table['struct'] > 0
    lobesel = unip_table['lobe'] > 0
    hemisel = unip_table['hemis'] > 0
    connsel = unip_table['fconn'] > 0
    eisel = unip_table['ei'] == 1

    if zone_name == 'All':
        zone_sel = np.full(len(unip_table['ch']), True)
    if zone_name == 'Site':
        zone_sel = sitesel
    elif zone_name == 'Structure':
        zone_sel = np.logical_and(structsel, np.logical_not(sitesel))
    elif zone_name == 'Lobe':
        zone_sel = np.logical_and(lobesel, np.logical_not(structsel))
        zone_sel = np.logical_and(zone_sel, np.logical_not(sitesel))
    elif zone_name == 'Hemisphere':
        zone_sel = np.logical_and(hemisel, np.logical_not(lobesel))
        zone_sel = np.logical_and(zone_sel, np.logical_not(structsel))
        zone_sel = np.logical_and(zone_sel, np.logical_not(sitesel))
    elif zone_name == 'Func.Connected':
        zone_sel = np.logical_and(connsel, np.logical_not(sitesel))
    elif zone_name == 'High EI':
        zone_sel = np.logical_and(eisel, np.logical_not(sitesel))

    if sum(zone_sel) == 0:
        return []

    for key in unip_table.keys():
        unip_table[key] = unip_table[key][zone_sel]

    print(f"Patient: {pat_name}")
    print(f"Zone: {zone_name}")
    print(f"Nr. Total Channels: {len(zone_sel)}")
    print(f"Nr. Zone Channels: {len(unip_table['ch'])}")

    return unip_table
