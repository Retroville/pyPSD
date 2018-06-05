# pyPSD report mode
# Austin Rhodes, 2018
from pyPSD import *
import numpy as np
import matplotlib
from matplotlib.backends.backend_pdf import PdfPages
from pylab import *



pdf = PdfPages('testoutput.pdf')

# %% Gather Data
dat, strs, dat_prompt_strs = get_data()
vol_col_idx = get_volcol(strs, dat_prompt_strs)
ext_col_ = get_datcol(strs, dat_prompt_strs)
if type(ext_col_) is int:
    ext_col_idx = ext_col_
else:
    ext_col_idx = ext_col_[idx]

typ = (0,0)
v = voldist(dat, strs, 20, [ext_col_idx, vol_col_idx], typ)

print(v)

pdf.close()