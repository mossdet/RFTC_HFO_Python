

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def read_channloc_table(coord_fn, loc_type):

    coord_jj_fn = coord_fn[0:-4]+"_JJ.xls"
    channloc_table = pd.read_excel(coord_jj_fn)
    coord_table = {}
    coord_table['ch'] = np.array(channloc_table['contact'].str.lower())
    coord_table['ch'] = correct_channel_labels(coord_table['ch'])
    nr_channs = len(coord_table['ch'])

    if loc_type == "MNI":
        coord_str_vec = channloc_table['MNI']
    elif loc_type == "T1preScannerBased":
        coord_str_vec = channloc_table['T1preScannerBased']

    xvec = []
    yvec = []
    zvec = []
    coord_table['hemisphere'] = np.array(np.array(["Right"]*nr_channs))
    for chi in range(nr_channs):
        coord_str = coord_str_vec[chi]
        coord_str = coord_str.replace('[', '')
        coord_str = coord_str.replace(']', '')
        coord_str = coord_str.split(',')
        xvec.append(float(coord_str[0]))
        yvec.append(float(coord_str[1]))
        zvec.append(float(coord_str[2]))

        # Get hemisphere also
        ch_label = coord_table['ch'][chi]
        if "\'" in ch_label:
            coord_table['hemisphere'][chi] = "Left"

    coord_table['x'] = np.array(xvec)/1000
    coord_table['y'] = np.array(yvec)/1000
    coord_table['z'] = np.array(zvec)/1000

    """ 
    channloc_table = pd.read_csv(coord_fn)
    coord_table = {}
    coord_table['ch'] = np.array(channloc_table['ChName'])
    coord_table['x'] = np.array(channloc_table['XPos'])/1000
    coord_table['y'] = np.array(channloc_table['YPos'])/1000
    coord_table['z'] = np.array(channloc_table['ZPos'])/1000 
    """

    # Get estimated Brain Lobe
    estimated_struct = np.array(channloc_table['BrainRegion_JJ'])
    coord_table['lobe'] = np.array(np.array(["NaN"]*nr_channs))

    region_codes = np.unique(estimated_struct)
    for code in region_codes:
        sel_vec = estimated_struct == code

        lobeName = "NaN"
        if code == 1:
            parcelenameJJ = "hippocampus"
            lobeName = "Mesiotemporal"
        elif code == 2:
            parcelenameJJ = "amygdala"
            lobeName = "Mesiotemporal"
        elif code == 3:
            parcelenameJJ = "Parahippocampus"
            lobeName = "Mesiotemporal"
        elif code == 4:
            parcelenameJJ = "Temporal neocortical"
            lobeName = "Temporal"
        elif code == 5:
            parcelenameJJ = "Frontal"
            lobeName = "Frontal"
        elif code == 6:
            parcelenameJJ = "Parietal"
            lobeName = "Parietal"
        elif code == 7:
            parcelenameJJ = "Occipital"
            lobeName = "Occipital"
        elif code == 8:
            parcelenameJJ = "Insula"
            lobeName = "Insula"

        coord_table['lobe'][sel_vec] = lobeName

    # Get Brain Structure estimation
    coord_table['sructure'] = np.array(np.array(["NaN"]*nr_channs))

    if 'AICHA' in channloc_table.keys():
        coord_table['sructure'] = channloc_table['AICHA']
    elif 'Freesurfer' in channloc_table.keys():
        coord_table['sructure'] = channloc_table['Freesurfer']
    elif 'MNI_DKT' in channloc_table.keys():
        coord_table['sructure'] = channloc_table['MNI_DKT']
    elif 'MNI_Destrieux' in channloc_table.keys():
        coord_table['sructure'] = channloc_table['MNI_Destrieux']
    elif 'Hammers' in channloc_table.keys():
        coord_table['sructure'] = channloc_table['Hammers']
    elif 'AAL' in channloc_table.keys():
        coord_table['sructure'] = channloc_table['AAL']

    # Get Hemisphere
    right_hemis = coord_table['ch']

    del_sel = np.logical_or(
        coord_table['lobe'] == "NaN", coord_table['sructure'] == "NaN")

    for key in coord_table.keys():
        # print(len(coord_table[key]))
        coord_table[key] = np.delete(coord_table[key], del_sel)

    return coord_table


def correct_channel_labels(labels_array):
    corr_labels = labels_array.copy()
    for chi in range(len(labels_array)):
        ch_name = labels_array[chi].lower()
        ch_name = ch_name.replace(' ', '')

        if len(ch_name) > 0:
            if "-" in ch_name:
                bip_labels = ch_name.split("-")
                chA = bip_labels[0]
                chB = bip_labels[1]
                correct_ch_name = get_correct_ch_number(
                    chA) + '-' + get_correct_ch_number(chB)
            else:
                correct_ch_name = get_correct_ch_number(ch_name)
        corr_labels[chi] = correct_ch_name
    return corr_labels


def get_correct_ch_number(chName):

    numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    foundNrIndices = []
    for digit in numbers:
        strIdx = chName.find(digit)
        if strIdx != -1:
            foundNrIndices.append(strIdx)

    firstNumIdx = min(foundNrIndices)
    lastNumIdx = max(foundNrIndices)
    contactNr = int(chName[firstNumIdx:lastNumIdx+1])
    electrodeName = chName[0:firstNumIdx]

    if "p" in electrodeName:
        if len(electrodeName) > 1:
            if "'" not in electrodeName:
                electrodeName = electrodeName.replace('p', '\'')
        else:
            stop = 1
            # print(chName)

    correct_ch_name = electrodeName + str(contactNr)

    return correct_ch_name
