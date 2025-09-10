import pathlib
from dewan_h5 import DewanH5

broken_file = '/mnt/r2d2/5_Projects/1_Sniffing/3_benzaldehyde/Raw_Data_8-26-2025/215/mouse215_sess1_D2025_9_8T15_24_40.h5'
broken_file = pathlib.Path(broken_file)

h5obj = DewanH5(broken_file, drop_early_lick_trials=False, drop_cheating_trials=True)
with h5obj as h5:
    print(h5)