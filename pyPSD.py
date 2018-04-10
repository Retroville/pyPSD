# Initialization
import csv
import numpy as np
import matplotlib.pyplot as plt

vol_col = []
ext_col = []
dat = []

# Data Import & Prompt
with open('../data/inputex.csv', encoding="latin-1") as csvfile:

    csvreader = csv.reader(csvfile)

    for row in csvreader:
        dat.append(row)

dat = np.array(dat)
vol_col_strs = 'Select the \'volume\' column: ' + ', '.join(dat[0])
vol_col_idx = int(input(vol_col_strs)) - 1
print('You chose: ', dat[0][vol_col_idx])

ext_col_strs = 'Select the data column: ' + ', '.join(dat[0])
ext_col_idx = int(input(ext_col_strs)) - 1
print('You chose: ', dat[0][ext_col_idx])

with open('../data/inputex.csv', encoding="latin-1") as csvfile:        # Clean this later

    csvreader = csv.reader(csvfile)

    for row in csvreader:
        vol_col.append(row[vol_col_idx])
        ext_col.append(row[ext_col_idx])


#my_range = input('Input the range of the x axis bins: ')
#print('Your range: ' + my_range)
#my_range = float(my_range)

#add 6 mins

my_range = 0.005

# Calculations
volstr = vol_col[0]
vol_raw = vol_col[1:]
volume = np.array(sorted([float(i) for i in vol_raw]))
volbinsums = []

extstr = ext_col[0]
ext_raw = ext_col[1:]
extent = np.array(sorted([float(i) for i in ext_raw]))

bin_edges = np.arange(0, max(extent), my_range)

counts = plt.hist(extent, bins=bin_edges)[0]

idx = np.searchsorted(bin_edges, extent, 'right')
for i in range(1, len(bin_edges)):
    logc = idx == i
    volbinsums.append(sum(volume[logc]))

# Plotting
fig = plt.figure()

ax1 = fig.add_subplot(2, 1, 1)
ax2 = fig.add_subplot(2, 1, 2)

fig.tight_layout()

ax1.bar(np.arange(0, len(volbinsums)), counts,
        width=-1, color='green', linewidth=0.2, edgecolor='black', align='edge',
        tick_label=bin_edges[1:])
ax1.set_xlabel(extstr)
ax1.set_ylabel('Counts')
plt.setp(ax1.get_xticklabels(), rotation=90)

ax2.bar(np.arange(0, len(volbinsums)), volbinsums,
        width=-1, color='green', linewidth=0.2, edgecolor='black', align='edge',
        tick_label=bin_edges[1:])
ax2.set_xlabel(volstr)
ax2.set_ylabel('Volume')
plt.setp(ax2.get_xticklabels(), rotation=90)

plt.show()
