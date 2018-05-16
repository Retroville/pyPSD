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
class voldist(object):
    def __init__(self, dat, strs):
        self.dat = dat
        self.strs = strs
        self.volbinsums = []
    
        my_range = input('Input the range of the x axis bins (Type \'exit:\' to quit, \'save\' to save plot data to output.csv):')
        print('Your range: ' + my_range)
    
        self.volstr = strs[vol_col_idx]
        volume = dat[:, vol_col_idx]
        self.extstr = strs[ext_col_idx]
        extent = dat[:, ext_col_idx]  # formats primary data and volume columns
    
        if my_range == 'save':
            return False
        elif my_range == 'exit':
            return None
        elif my_range:
            my_range = float(my_range)
            bin_edges = np.arange(0, max(extent), my_range)
        else:
            bin_edges = 'auto'
    
        self.counts, self.realbins = np.histogram(extent, bins=bin_edges)  # create num dist from bin edges [1]
    
        self.numavg = sum(extent) / len(extent)  # basic average of primary data        [0]
    
        idx = np.searchsorted(self.realbins, extent, 'right')
    
        for i in range(1, len(self.realbins)):  # creates binned sums of volumes per count [2]
            logc = idx == i
            self.volbinsums.append(sum(volume[logc]))
    
      # volbinfracsums = volbinsums / sum(volume)  # basic volume fraction (per bin)   [0]
        volfrac = volume / sum(volume)  # basic volume fraction                    [0]
        self.volavg = sum(extent * volfrac) / len(extent)  # what even is this?         [3]
    
        self.binlabels = range(0, len(self.volbinsums))
        
        return
    
    def vdplot(self):
        plt.figure(num=2, figsize=(8, 8))
        plt.tight_layout()
        plt.ion()
        plt.clf()
    
        plt.subplot(2, 1, 1)
        plt.bar(self.binlabels, self.counts,
                width=-1, color='green', linewidth=0.2, edgecolor='black',
                align='edge', tick_label=self.realbins[1:])
        plt.xlabel(self.extstr)
        plt.ylabel('Counts')
        plt.xticks(rotation=90)
    
        plt.subplot(2, 1, 2)
        plt.bar(self.binlabels, self.volbinsums,
                width=-1, color='green', linewidth=0.2, edgecolor='black',
                align='edge', tick_label=self.realbins[1:])
        plt.xlabel(self.volstr)
        plt.ylabel('Volume')
        plt.xticks(rotation=90)
        
        return
    
       # print('Number Average: ', numavg)
       # print('Volume Average: (Warning) ', volavg)
    
    def writeout():
        
        return
    
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
fig = plt.figure(num=1, figsize=(8, 8))
plt.suptitle(strs[ext_col_idx])
for i in range(1, len(dat[0])+1):
    # creates a grid of scatterplots, per each column pair
    plt.subplot(2, 2, i)
    plt.scatter(dat[:, i-1], dat[:, ext_col_idx], marker='.', c='black', s=1)
    plt.xlim(0, max(dat[:, i-1]))
  # plt.ylim(0, max(dat[:, ext_col_idx]))
    plt.xlabel(strs[i-1])
    plt.ylabel(strs[ext_col_idx])
fig.set_figheight(8)
fig.set_figwidth(8)
plt.show()

vdist = True
while vdist: # fix this
    vdist = voldist(dat, strs)
    if vdist == None:
        break
    vdist.vdplot()
    plt.show()
