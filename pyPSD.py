import csv
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

vol_col = []
ext_col = []

with open('../data/inputex.csv', encoding="latin-1") as csvfile:

    csvreader = csv.reader(csvfile)

    for row in csvreader:
        vol_col.append(row[2])
        ext_col.append(row[3])

volstr = vol_col[0]
vol_raw = vol_col[1:]
volume = np.array([float(i) for i in vol_raw])
volbinsums = []

extstr = ext_col[0]
ext_raw = ext_col[1:]
extent = np.array([float(i) for i in ext_raw])

# Enter bin range

my_range = 0.005
bin_edges = np.arange(0, max(extent), my_range)

# ---

counts = plt.hist(extent, bins=bin_edges)[0]

idx = np.digitize(extent, bin_edges)
for i in range(1, len(bin_edges)):
    logc = idx == i
    volbinsums.append(sum(volume[logc]))

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
