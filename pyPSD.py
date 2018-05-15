# %% Initialization
import unicodecsv as csv
import numpy as np
import matplotlib.pyplot as plt
# import tkinter as tk
# from tkinter import filedialog

vol_col = []
ext_col = []
dat = []
dat_prompt_strs = []
my_range = []
#---- initilization of variables. do I even need to do this? who knows

# %% Functions
def voldist(dat, strs):
    #Init:
    volbinsums = []

    #----
    my_range = input('Input the range of the x axis bins (Type \'exit:\' to quit):')
    print('Your range: ' + my_range)

    volstr = strs[vol_col_idx]
    volume = dat[:, vol_col_idx]
    extstr = strs[ext_col_idx]
    extent = dat[:, ext_col_idx]  # formats primary data and volume columns

    if my_range:
        my_range=float(my_range)
        bin_edges = np.arange(0, max(extent), my_range)
    elif my_range == 'exit':
        return False
    else:
        bin_edges = 'auto'

    counts, realbins = np.histogram(extent, bins=bin_edges)  # create num dist from bin edges [1]

    numavg = sum(extent) / len(extent)  # basic average of primary data        [0]

    idx = np.searchsorted(realbins, extent, 'right')

    for i in range(1, len(realbins)):  # creates binned sums of volumes per count [2]
        logc = idx == i
        volbinsums.append(sum(volume[logc]))

  # volbinfracsums = volbinsums / sum(volume)  # basic volume fraction (per bin)   [0]
    volfrac = volume / sum(volume)  # basic volume fraction                    [0]
    volavg = sum(extent * volfrac) / len(extent)  # what even is this?         [3]

    binlabels = np.arange(0, len(volbinsums))

    plt.figure(num=2, figsize=(8,8))
    plt.tight_layout()
    plt.ion()
    plt.clf()

    plt.subplot(2, 1, 1)
    plt.bar(binlabels, counts,
            width=-1, color='green', linewidth=0.2, edgecolor='black',
            align='edge', tick_label=realbins[1:])
    plt.xlabel(extstr)
    plt.ylabel('Counts')
    plt.xticks(rotation=90)

    plt.subplot(2, 1, 2)
    plt.bar(binlabels, volbinsums,
            width=-1, color='green', linewidth=0.2, edgecolor='black',
            align='edge', tick_label=realbins[1:])
    plt.xlabel(volstr)
    plt.ylabel('Volume')
    plt.xticks(rotation=90)


    print('Number Average: ', numavg)
    print('Volume Average: (Warning) ', volavg)

    return True
'''
def scattergrid(dat, str_col_idx, ext_col_idx):
    fig = plt.figure(num=1)
    plt.suptitle(strs[ext_col_idx])
    for i in range(1, len(dat[0])+1):
        # creates a grid of scatterplots, per each column pair
        plt.subplot(2, 2, i)
        plt.scatter(dat[:, i-1], dat[:, ext_col_idx], marker='.', c='black')
        plt.xlim(0, max(dat[:, i-1]))
        plt.ylim(0, max(dat[:, ext_col_idx]))
        plt.xlabel(strs[i-1])
        plt.ylabel(strs[ext_col_idx])
        fig.set_figheight(8)
        fig.set_figwidth(8)
    return '''
# %% Data Import & Prompt

# root = tk.Tk()
# root.withdraw()

# file_path = filedialog.askopenfilename()
file_path = '../data/input.csv'  # DEBUGGING - remove this later
with open(file_path, 'rb') as csvfile:
    csvreader = csv.reader(csvfile, encoding='utf-8')

    for row in csvreader:
        if 'Grand total' in row:
            break
        dat.append(row)

strs = dat[1]  # pulls column headers
dat = np.array(dat[2:])  # pulls raw numbers
strs = strs[1:]  # trims 'name' column
dat = np.delete(dat, 0, 1)  # trims name data column
dat = dat.astype(np.float)  # converts raw numbers to float(eg 2.31e7 to float)

for i in range(0, len(strs)):  # creates prompt string: choice component
    dat_prompt_strs.append(str(i + 1) + ' - ' + strs[i])

vol_col_strs = 'Select the \'volume\' column: \n' + '\n'.join(dat_prompt_strs)
vol_col_idx = int(input(vol_col_strs)) - 1
print('You chose: ', strs[vol_col_idx])

ext_col_strs = 'Select the data column:\n' + '\n'.join(dat_prompt_strs)
ext_col_idx = int(input(ext_col_strs)) - 1
print('You chose: ', strs[ext_col_idx])
# Imports data based on prompt results

# %% Main
fig = plt.figure(num=1, figsize=(8,8))
plt.suptitle(strs[ext_col_idx])
for i in range(1, len(dat[0])+1):
    # creates a grid of scatterplots, per each column pair
    plt.subplot(2, 2, i)
    plt.scatter(dat[:, i-1], dat[:, ext_col_idx], marker='.', c='black', s=1)
    plt.xlim(0, max(dat[:, i-1]))
    plt.ylim(0, max(dat[:, ext_col_idx]))
    plt.xlabel(strs[i-1])
    plt.ylabel(strs[ext_col_idx])
fig.set_figheight(8)
fig.set_figwidth(8)

stay = True
while stay:
    stay = voldist(dat, strs)
    plt.show()


