import csv
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


vol_col = []
ext_col = []

with open('data/inputex.csv', encoding="latin-1") as csvfile:

    csvreader = csv.reader(csvfile)

    for row in csvreader:

        vol_col.append(row[2])

        ext_col.append(row[3])

volstr = vol_col[0]

volume = list(map(float, vol_col[1:]))

extstr = ext_col[0]

ext_raw = ext_col[1:]

extent = [float(i) for i in ext_raw]

# Try converting to this: [float(i) for i in lst]



# --- Enter bin range:

my_range = 0.005
bin_edges = numpy.arange(0, max(extent), my_range)

# ---

idx = np.digitize(extent, bin_edges)

# for i=1:length(virtualbins)-1
#    logc = idx == i;
#    vol.binsums(i) = sum(volume(logc));
# end


sns.set()

fig = plt.figure()

ax1 = fig.add_subplot(2, 1, 1)
ax2 = fig.add_subplot(2, 1, 2)

fig.tight_layout()

ax1.hist(extent, bins=bin_edges)

ax1.set_xlabel(extstr)
ax1.set_ylabel('Counts')

plt.show()