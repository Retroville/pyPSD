# %% Initialization
import unicodecsv as csv
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from termcolor import colored as color
import os
import errno
from textwrap import wrap
# import tkinter as tk
# from tkinter import filedialog

try:
    os.makedirs('../output/')
except OSError as e:
    if e.errno != errno.EEXIST:
        raise

vol_col = []
ext_col = []
dat = []
dat_prompt_strs = []
my_range = []
#---- initilization of variables. do I even need to do this? who knows

# %% Calculations
class voldist(object):
    def __init__(self, dat, strs, bin_edges):
        self.dat = dat
        self.strs = strs
        self.volbinsums = []


        self.volstr = strs[vol_col_idx]
        volume = dat[:, vol_col_idx]
        self.extstr = strs[ext_col_idx]
        extent = dat[:, ext_col_idx]  # formats primary data and volume columns

        self.counts, self.realbins = np.histogram(extent, bins=bin_edges) # [1]
        plt.show

        self.numavg = sum(extent) / len(extent)  #                          [0]

        fidx = np.searchsorted(self.realbins, extent, 'right')

        for i in range(1, len(self.realbins)):  #                           [2]
            logc = fidx == i
            self.volbinsums.append(sum(volume[logc]))

      # volbinfracsums = volbinsums / sum(volume)  #                        [0]
        volfrac = volume / sum(volume)  #                                   [0]
        if typ == (0,0):
            self.volavg = sum(extent * volfrac) / sum(volfrac)  #            [3] Weighted
        else:
            self.volavg = sum(extent**typ[0])/sum(extent**typ[1])
        
        
        self.navgstr = 'Number average: ' + str(float('%.8f'%(self.numavg)))
        self.vavgstr = 'Volume average: ' + str(float('%.8f'%(self.volavg)))

        self.binlabels = range(0, len(self.volbinsums))
        
        self.current_file_name = "".join([x if x.isalnum() else "_" for x in self.extstr])
        return

# %% Plotting and output
    def vdplot(self):

        plt.figure(num=2, figsize=(8, 8))
        plt.ion()
        plt.clf()

        def subhistplots(num, xvals, yvals, xstr, ystr):
            plt.subplot(2, 1, num)
            plt.bar(xvals, yvals,
                    width=--1, color='white', linewidth=1, edgecolor='red',
                    hatch='////', align='edge', tick_label=np.around(self.realbins[1:],5))
            plt.xlabel(ystr)
            plt.ylabel(xstr)
            plt.xticks(rotation=90)
            plt.annotate(self.navgstr, xy=(0.55, 0.9), xytext=(0.55, 0.9), 
                         textcoords='axes fraction')
            plt.annotate(self.vavgstr, xy=(0.55, 0.8), xytext=(0.55, 0.8),
                         textcoords='axes fraction')
            return
        subhistplots(1, self.binlabels, self.counts, 'Counts', self.extstr)
        subhistplots(2, self.binlabels, self.volbinsums, 'Volume', self.extstr)
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        
        print(color('Plot created...', 'green'))
        return

    def writeout(self):
        binout = self.realbins[1:]
        ostr = [self.extstr, 'Counts', 'Volume']
        odat = np.column_stack([binout, self.counts, self.volbinsums])
        out = np.vstack([ostr,odat])
        with open('../output/' + self.current_file_name + '_output.csv', 'wb') as csvout:
            outputwriter = csv.writer(csvout, delimiter=',')
            outputwriter.writerows(out)
            print(color("\n\nPlot saved as output.csv", 'green') + '\n')
        return
    
    def saveout(self):
        plt.figure(1)
        plt.savefig('../output/' + self.current_file_name + '_scatter', bbox_inches='tight')
        plt.figure(2)
        plt.savefig('../output/' + self.current_file_name + '_distribution', bbox_inches='tight')
        print(color("Plots saved as ", 'green') + self.current_file_name + 
                    '_scatter.png' + color(" and ", 'green') + 
                    self.current_file_name + '_distribution.png' + 
                    color("directory", 'green'))
        
def scattergrid(ext_col_idx):
    gridsize = 1 + len(dat[0])//2
    scatterplots = plt.figure(num=1, figsize=(11, 8.5))
    plt.suptitle(strs[ext_col_idx])
    for i in range(1, len(dat[0])+1):
        # creates a grid of scatterplots, per each column pair
        plt.subplot(gridsize, 2, i)
        if not i-1 == ext_col_idx:
            plt.scatter(dat[:, i-1], dat[:, ext_col_idx], marker='.', c='black', s=1)
            plt.xlim(0, max(dat[:, i-1]))
          # plt.ylim(0, max(dat[:, ext_col_idx-1]))
        else:
            plt.plot([0, 0, 1, 1, 0, 1, 1, 0],[0, 1, 0, 1, 0, 0, 1, 1],'r')
            plt.xticks([])
            plt.yticks([])
        plt.xlabel('\n'.join(wrap(strs[i-1],30)), fontsize=8)
        plt.xticks(fontsize=8)
        plt.yticks(fontsize=8)
    scatterplots.set_figheight(8.5)
    scatterplots.set_figwidth(11)
    plt.gcf().tight_layout() # rect=[0, 0.03, 1, 0.95]
    plt.show(block=False)
    return

def clearplots():
    plt.figure(1)
    plt.clf()
    plt.figure(2)
    plt.clf()
    
# %% Menu
def cmd_save():
    return v.saveout()
def cmd_csv():
    return v.writeout()
def cmd_next():
    clearplots()
    global idx
    global sig
    idx += 1
    sig = False
    return
def cmd_quit():
    return quit()

def menu_cmd():
    OPTIONS = {"bins":dict( desc = "Change bins of currently active distribution plot", func = None), # wew lad
               "save":dict( desc = "Save currently active plots as images", func = cmd_save),
               "csv":dict( desc = "Export currently active plots to csv file", func = cmd_csv),
               "next":dict( desc = "Select next data column (retains volume column selection)", func = cmd_next),
               "quit":dict( desc = "Exits the program", func = cmd_quit)}

    while sig == True:
        print("\nPlease choose an option:")
        for key in OPTIONS.keys():
            print("\t" + key + "\t" + OPTIONS[key]["desc"])
        cmd = input('Selection: ')
        if not cmd in OPTIONS.keys():
            print(color("\n\nInvalid selection", 'red') + '\n')
        elif cmd == 'bins':
            return
        else:
            OPTIONS[cmd]["func"]()
    return

# %% Data Import & Prompt
def report_prompt():
    report_prompt_ans = input('Enter report mode? (Y/N)')
    print(report_prompt_ans)
    if any(c in report_prompt_ans for c in ('y', 'Y')):
        return True
    else:
        return False

def get_bins():
    my_range = input('Input the range of the x axis histogram bins: \n'
                     '(Leave blank to bin automatically)')
    print(color('\n\nYou Chose: ', 'green') + my_range + '\n')
    if my_range:
        my_range = float(my_range)
        bin_edges = np.arange(0, max(dat[:, ext_col_idx]), my_range)
    else:
        bin_edges = 20
    return bin_edges


def promptdatcol():
    ext_col_strs = 'Select the data column(s):\n' + '\n'.join(dat_prompt_strs)
    ext_col_idx = input(ext_col_strs)
    if ',' in ext_col_idx:
        ext_col_idx = [int(i)-1 for i in ext_col_idx.split(',')]
        print(color('\n\nYou chose: ', 'green') + 'Multiple input columns' + '\n')
    elif ':' in ext_col_idx:
        minmax = [int(i)-1 for i in ext_col_idx.split(':')]
        ext_col_idx = range(minmax[0],minmax[1]+1)
    else:
        ext_col_idx = int(ext_col_idx)-1
        print(color('\n\nYou chose: ', 'green') + strs[ext_col_idx] + '\n')
    return ext_col_idx
    # Imports data based on prompt results    


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
print(color('\n\nYou chose: ', 'green') + strs[vol_col_idx] + '\n')

# %% Main Loop

idx = 0
typ = (3,2) 
    # Specifiy method of determining volume average:
    # (Leave blank to calculate weighted average)
    # Fill in according to D[x,y] parameter
    # e.g.: De Brouckere mean dia. = (4,3),  Sauter mean dia. = (3,2)

ext_col_ = promptdatcol()
reportmode = report_prompt()
if reportmode is True:
    matplotlib.use('Agg')

while True:
    if type(ext_col_) is int:
        ext_col_idx = ext_col_
        fig1 = scattergrid(ext_col_)
    else:
        ext_col_idx = ext_col_[idx]
        fig1 = scattergrid(ext_col_[idx])
    sig = True
    while sig == True:
        v = voldist(dat, strs, get_bins())
        fig2 = v.vdplot()
        plt.show()
        menu_cmd()