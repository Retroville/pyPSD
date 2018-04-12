#%% Initialization
import csv
import numpy as np
import matplotlib.pyplot as plt
import codecs
import tkinter as tk
from tkinter import filedialog

vol_col = []
ext_col = []
dat = []
dat_prompt_strs = []

#%% Data Import & Prompt
root = tk.Tk()
root.withdraw()

file_path = filedialog.askopenfilename()

with codecs.open(file_path, 'rb', encoding="latin-1") as csvfile:

    csvreader = csv.reader(csvfile)

    for row in csvreader:
        dat.append(row)
        # Creates list of all columns in file

dat = np.array(dat)

for i in range(0, len(dat[0])):
    dat_prompt_strs.append(str(i+1) + ' - ' + dat[0][i])

vol_col_strs = 'Select the \'volume\' column: \n' + '\n'.join(dat_prompt_strs)
vol_col_idx = int(input(vol_col_strs)) - 1
print('You chose: ', dat[0][vol_col_idx])

ext_col_strs = 'Select the data column:\n' + '\n'.join(dat[0])
ext_col_idx = int(input(ext_col_strs)) - 1
print('You chose: ', dat[0][ext_col_idx])

vol_col = dat[1:, vol_col_idx]
ext_col = dat[1:, ext_col_idx]
# Imports data based on prompt results


my_range = input('Input the range of the x axis bins: ')
print('Your range: ' + my_range)
my_range = float(my_range)

my_range = 0.005

#%% Calculations
volstr = vol_col[0]
vol_raw = vol_col[1:]
volume = np.array(sorted([float(i) for i in vol_raw]))
volbinsums = []

extstr = ext_col[0]
ext_raw = ext_col[1:]
extent = np.array(sorted([float(i) for i in ext_raw]))

bin_edges = np.arange(0, max(extent), my_range)

counts = plt.hist(extent, bins=bin_edges)[0]

numavg = sum(extent)/len(extent)

idx = np.searchsorted(bin_edges, extent, 'right')
for i in range(1, len(bin_edges)):
    logc = idx == i
    volbinsums.append(sum(volume[logc]))

volbinfracsums = volbinsums/sum(volume)
volfrac = volume/sum(volume)
volavg = sum(extent*volfrac) / len(extent)

binlabels = np.arange(0, len(volbinsums))

#%% Plotting
plt.figure(1)
#for i in range(1, len(dat[0])):
#    plt.subplot(3, 3, i)
plt.scatter(dat[1:, ext_col_idx], dat[1:, 5])

plt.show()

plt.figure(2)
plt.tight_layout()

plt.subplot(2, 1, 1)
plt.bar(binlabels, counts,
        width=-1, color='green', linewidth=0.2, edgecolor='black', align='edge',
        tick_label=bin_edges[1:])
plt.xlabel(extstr)
plt.ylabel('Counts')
plt.xticks(rotation=90)

plt.subplot(2, 1, 2)
plt.bar(binlabels, volbinsums,
        width=-1, color='green', linewidth=0.2, edgecolor='black', align='edge',
        tick_label=bin_edges[1:])
plt.xlabel(volstr)
plt.ylabel('Volume')
plt.xticks(rotation=90)

plt.show()



print('Number Average: ', numavg)
print('Volume Average: (Warning) ', volavg)