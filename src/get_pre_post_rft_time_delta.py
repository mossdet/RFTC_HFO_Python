import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from get_paths import *
from get_data_lists import *
from neo.io import MicromedIO


pre_files = get_pre_rftc_files()
post_files = get_post_rftc_files()

for pi in range(len(pre_files)):
    # Read EEG
    um_eeg_fn_pre = get_micromed_eeg_path() + pre_files[pi] + '.trc'
    um_eeg_fn_post = get_micromed_eeg_path() + post_files[pi] + '.trc'
    um_reader_pre = MicromedIO(um_eeg_fn_pre)
    um_reader_post = MicromedIO(um_eeg_fn_post)
    date_diff = um_reader_post.eeg_date-um_reader_pre.eeg_date
    print(pre_files[pi], date_diff.total_seconds()/3600)
