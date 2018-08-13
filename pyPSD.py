# %% Initialization
# Austin Rhodes


import csv
import numpy as np
from termcolor import colored as color
import os
import errno
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt     
import sys
import glob
from argparse import ArgumentParser, ArgumentTypeError


try:
    os.makedirs('../output/')
    os.makedirs('../input/')
except OSError as e:
    if e.errno != errno.EEXIST:
        raise

'''Make this optional later
def color(input, nonsense, attrs='Junk'):
    return input
'''

def parseNumList(string):
    if ':' in string:
        m = [int(i)-1 for i in string.split(':')]
        return list(range(m[0],m[1]+1))
    elif ',' in string:
        return [int(i)-1 for i in string.split(',')]
    else:
        return [int(string)-1]

# %% Calculations
def sphericity(area, volume):
    c = 4.835975860 # Sphericity Constant

    CA = [c/float(a) for a in area]

    V23 = [float(v)**(2/3) for v in volume]

    sphericity_col = np.array(np.multiply(CA,V23))

    return sphericity_col

class voldist(object):
    def __init__(self, dat, strs, bin_edges, col_idces, *typ):
        self.volbinsums = []
        self.ext_col_idx = col_idces[1]
        self.vol_col_idx = col_idces[0]

        self.volstr = strs[self.vol_col_idx]
        self.volume = dat[:, self.vol_col_idx]
        self.extstr = strs[self.ext_col_idx]
        self.extent = dat[:, self.ext_col_idx]  # formats primary data and volume columns

        self.counts, self.realbins = np.histogram(self.extent, bins=bin_edges) 

        self.numavg = sum(self.extent) / len(self.extent) 

        fidx = np.searchsorted(self.realbins, self.extent, 'right')

        for i in range(1, len(self.realbins)): 
            logc = fidx == i
            self.volbinsums.append(sum(self.volume[logc]))

    #   volbinfracsums = volbinsums / sum(volume)
        self.volfrac = self.volume / sum(self.volume)  
        if typ not in locals() or typ == (0,0):
            self.volavg = sum(self.extent * self.volfrac) / sum(self.volfrac)  
        else:
            self.volavg = sum(self.extent**typ[0])/sum(extent**typ[1])
        
        self.avg = [self.numavg, self.volavg]

        self.porevol = sum(self.volume)

        self.numstd = np.std(self.extent)
        self.nummin = min(self.extent)
        self.nummax = max(self.extent)

        self.volstd = np.std(self.volume)
        self.volmin = min(self.volume)
        self.volmax = max(self.volume)
        self.extmax_fromvol = self.extent[np.argmin(self.volume)]

        self.numavgstr = 'Number average: ' + str(float('%.8f'%(self.numavg)))
        self.volavgstr = 'Volume average: ' + str(float('%.8f'%(self.volavg)))

        self.numstdstr = 'Standard Deviation (number): ' + str(float('%.8f'%(self.numstd)))
        self.numminstr = 'Minimum (number): ' + str(float('%.8f'%(self.nummin)))
        self.nummaxstr = 'Max ' + self.extstr + '(Number) ' + str(float('%.8f'%(self.nummax)))

        self.volstdstr = 'Standard Deviation (volume): ' + str(float('%.8f'%(self.volstd)))
        self.volminstr = 'Minimum (volume): ' + str(float('%.8f'%(self.volmin)))
        self.volmaxstr = 'Maximum (volume): ' + str(float('%.8f'%(self.volmax)))
    #   self.volmaxstr = 'Max ' + self.extstr + ' (Volume) ' + str(float('%.8f'%(self.extmax_fromvol)))

        self.porevolstr = 'Total Pore Volume: ' + str(float('%.8f'%(self.porevol))) #out of this section later pls

        self.binlabels = range(0, len(self.volbinsums))
        
        self.current_file_name = "".join([x if x.isalnum() else "_" for x in self.extstr])

    #   vlinenum = (self.numavg/max(self.realbins)) * (len(self.realbins)-1)
    #   vlinevol = (self.volavg/max(self.realbins)) * (len(self.realbins)-1)

    #   self.vline = [vlinenum, vlinevol] # actual location is idx-1

        return

# %% Plotting and output
    def vdplot(self):
        plt.figure(num=2, figsize=(8, 8))
        plt.ion()
        plt.clf()
        def subhistplots(num, xvals, yvals, xstr, ystr):
            plt.subplot(2, 1, num)
            plt.bar(xvals, yvals,
                    width=-1, color='white', linewidth=1, edgecolor='red',
                    hatch='////', align='edge', tick_label=np.around(self.realbins[1:],5))
            plt.xlabel(ystr)
            plt.ylabel(xstr)
        #   plt.axvline(self.vline[num-1]-1, color='k', linestyle='dashed', linewidth=1)
        #   plt.axvline(self.vline[num-1]-1 , color='k', linestyle='dashed', linewidth=1)
            plt.xticks(rotation=90)
            return
        subhistplots(1, self.binlabels, self.counts, 'Counts', self.extstr)
        subhistplots(2, self.binlabels, self.volbinsums, 'Volume', self.extstr)

        plt.subplots_adjust(bottom=0.26, top=0.98, hspace=0.40)

        plt.gcf().text(0.1,0.10,self.numavgstr)
        plt.gcf().text(0.1,0.08,self.numstdstr)
        plt.gcf().text(0.1,0.06,self.nummaxstr)

        plt.gcf().text(0.5,0.10,self.volavgstr)
        plt.gcf().text(0.5,0.08,self.volstdstr)
    #   plt.gcf().text(0.5,0.06,self.volmaxstr) Not sure what this represents

        return

    def writeout(self):
        
        binout = self.realbins[1:]
        ostr = [self.extstr, 'Counts', 'Volume']
        odat = np.column_stack([binout, self.counts, self.volbinsums])
        out = np.vstack([ostr,odat])
        with open('../output/' + self.current_file_name + '_output.csv', 'w') as csvout:
            outputwriter = csv.writer(csvout, delimiter=',')
            outputwriter.writerows(out)
            print(color("Plot saved as output.csv", 'green') + '\n')
        return
    
    def saveout(self):
        plt.figure(1)
        plt.savefig('../output/' + self.current_file_name + '_scatter')
        plt.figure(2)
        plt.savefig('../output/' + self.current_file_name + '_distribution')
        print(color("Plots saved as ", 'green') + self.current_file_name + 
                    '_scatter.png' + color(" and ", 'green') + 
                    self.current_file_name + '_distribution.png' + 
                    color(" in ", 'green') + "../output/ " + 
                    color("directory\n", 'green'))

def data_out(dat):
    with open('../output/' + 'MODIFIED_DATA.csv', 'wb') as csvout:
        outputwriter = csv.writer(csvout, delimiter=',')
        outputwriter.writerows(dat)
        print(color("filtered data saved", 'green') + '\n')

def scattergrid(dat, strs, vol_col_idx, ext_col_idx):
    gridsize = 1 + len(dat[0])//2
    scatterplots = plt.figure(num=1, figsize=(8, 8))
    plt.suptitle(strs[ext_col_idx])
    for i in range(1, len(dat[0])+1):
        # creates a grid of scatterplots, per each column pair
        plt.subplot(gridsize, 2, i)
        if not i-1 == ext_col_idx:
            plt.scatter(dat[:, i-1], dat[:, ext_col_idx], marker='.', c='black', s=1)
            plt.xlim(0, max(dat[:, i-1]))
        #   plt.ylim(0, max(dat[:, ext_col_idx-1]))
        else:
            plt.plot([0, 0, 1, 1, 0, 1, 1, 0],[0, 1, 0, 1, 0, 0, 1, 1],'r')
            plt.xticks([])
            plt.yticks([])
        plt.xlabel(strs[i-1])

    scatterplots.set_figheight(8)
    scatterplots.set_figwidth(8)
    plt.gcf().tight_layout() # rect=[0, 0.03, 1, 0.95]
    plt.subplots_adjust(top=0.95, left=0.1, right = 0.9)
    return

def clearplots():
    plt.figure(1)
    plt.clf()
    plt.figure(2)
    plt.clf()

# %% Menu                        FIX LATER: i.e. become if: elif: chain :(
def cmd_save(v):
    return v.saveout()
def cmd_csv(v):
    return v.writeout()
def cmd_next():
    clearplots()
    global idx
    global sig
    idx += 1
    sig = False
    return
def cmd_report():
    import pyPSD_report
def cmd_quit():
    sys.exit()

def menu_cmd(v):
    OPTIONS = {"bins":dict( desc = "Change bins of currently active distribution plot", func = None),
               "save":dict( desc = "Save currently active plots as images", func = cmd_save),
               "csv":dict( desc = "Export currently active plots to csv file", func = cmd_csv),
               "next":dict( desc = "Select next data column (retains volume column selection)", func = cmd_next),
               "report":dict( desc = "Runs pyPSD_report.py to generate a report of the data", func = cmd_report),
               "quit":dict( desc = "Exits the program", func = cmd_quit)}

    while sig == True:
        print("\nPlease choose an option:")
        for key in OPTIONS.keys():
            print("\t" + key + "\t" + OPTIONS[key]["desc"])
        cmd = input('Selection: ').rstrip()
        if not cmd in OPTIONS.keys():
            print(color("Invalid selection", 'red') + '\n')
        elif cmd == 'bins':
            return
        elif (cmd == 'save') or (cmd == 'csv'):
            OPTIONS[cmd]["func"](v)
        else:
            OPTIONS[cmd]["func"]()
    return

# %% Data Import & Prompt
def track_parameter():
    pass

def filter_data(dat, filter_col, threshold):
    m = [row for row in dat if row[filter_col] >= threshold]
    return m

def get_file(nolists=False, noparse=False):
    fn_prompt_strs = []
    os.chdir('../input/')
    files = glob.glob('*.csv')
    files.sort()
    for i in range(0, len(files)):  # creates prompt string: choice component
        fn_prompt_strs.append(str(i + 1) + ' - ' + files[i])
    if noparse == False:
        fn_strs = 'Select the file to analyze:\n' + '\n'.join(fn_prompt_strs)
    elif noparse == True:
        print('All files in input directory:\n' + '\n'.join(fn_prompt_strs))
        return
    while True:
        try:
            file_path_idx = parseNumList(input(fn_strs).rstrip())
            if (nolists == True) and (type(file_path_idx) is list):
                if len(file_path_idx) != 1:
                    print(color('Lists are not permitted in this mode, defaulting to first list item','red'))
                file_path_idx = file_path_idx[0]

            break
        except ValueError:
            print(color("Input must be integer!\n",'red'))
    if type(file_path_idx) is not int:
        print(color('You chose: ', 'green') + 'multiple files' + '\n')
        file_path = []
        file_name = []
        for i in file_path_idx:
            file_path.append('../input/' + files[i])
            mfile_name = files[i]
            mfile_name = mfile_name[:-4]
            file_name.append(mfile_name)
    else:
        print(color('You chose: ', 'green') + files[file_path_idx] + '\n')
        file_path = '../input/' + files[file_path_idx]
        file_name_ = files[file_path_idx]
        file_name = file_name_[:-4]
    return file_path, file_name


def get_data(file_path):
    dat = []
    dat_prompt_strs = []

    with open(file_path, 'rU') as csvfile:
        csvreader = csv.reader(csvfile)

        for row in csvreader:
            if 'Grand total' in row:
                break
            row = [ x for x in row if "" != x ]
            dat.append(row)

    strs = dat[1]  # pulls column headers
    dat = np.array(dat[2:])  # pulls raw numbers
    strs = strs[1:]  # trims 'name' column
    dat = np.delete(dat, 0, 1)  # trims name data column
    dat = dat.astype(np.float)  # converts raw numbers to float(eg 2.31e7 to float)

    for i in range(0, len(strs)):  # creates prompt string: choice component
        dat_prompt_strs.append(str(i + 1) + ' - ' + strs[i])

    return dat, strs, dat_prompt_strs

def get_bins(dat, ext_col_idx):
    while True:
        my_range = input('Input the range of the x axis histogram bins: \n'
                 '(Leave blank to bin automatically)').rstrip()
        print(color('You Chose: ', 'green') + my_range + '\n')
        try:
            if my_range:
                my_range = float(my_range)
                bin_edges = np.arange(0, max(dat[:, ext_col_idx]), my_range)
            else:
                bin_edges = 20
        except ValueError:
            print(color("Input must be number or null (empty)!\n",'red'))
        else:
            break
    return bin_edges


def get_datcol(strs, pstrs, noparse=False):
    dstrs = [ x for x in pstrs if "Count" not in x ]
    ext_col_strs = 'Select the data column(s):\n' + '\n'.join(dstrs)
    while True:
        try:    
            ext_col_idx = parseNumList(input(ext_col_strs).rstrip())
        except ValueError:
            print(color("Input must be integer!\n",'red'))
        else:
            if type(ext_col_idx) is list:
                print(color('You chose: ', 'green') + 'Multiple Columns')
            else:
                print(color('You chose: ', 'green') + str(pstrs[ext_col_idx]) + '\n')
            break
    return ext_col_idx

def get_volcol(strs, pstrs, noparse=False):
    vstrs = [ x for x in pstrs if "Voxel:" in x ] # Not sure if centroid needed
    vol_col_strs = 'Select the \'volume\' column: \n' + '\n'.join(vstrs)
    if len(vstrs) > 1:
        while True: 
            vol_col_idx = input(vol_col_strs).rstrip()
            try:
                vol_col_idx = int(vol_col_idx) - 1
            except ValueError:
                print(color("Input must be integer!\n",'red'))
            else:
                break
    elif len(vstrs) == 1:
        vol_col_idx = vstrs[0]
    else:
        print(color('No volume columns identified: Exiting', 'red'))
        sys.exit()
    print(color('You chose: ', 'green') + strs[vol_col_idx] + '\n')   
    return vol_col_idx

def list_cols(strs, pstrs):
    print('All columns in data: \n' + '\n'.join(pstrs))

# %% Main Loop
def main():
    global idx
    global sig
    global endx
    idx = 0
    typ = (0,0) 
        # Specifiy method of determining volume average:
        # (Leave blank to calculate weighted average)
        # Fill in according to D[x,y] parameter
        # e.g.: De Brouckere mean dia. = (4,3),  Sauter mean dia. = (3,2)
    dat, strs, dat_prompt_strs = get_data(get_file(nolists=True)[0])
    vol_col_idx = get_volcol(strs, dat_prompt_strs)
    sur_col_idx = [i for i,x in enumerate(strs) if 'Voxel:Surface area' in x]

    if len(sur_col_idx) > 0:
    #   print(color('Surface Area column detected! ',
    #       'green',attrs=['bold']), end="", flush=True)

        sphericity_col = sphericity(dat[:, sur_col_idx], dat[:, vol_col_idx])
        dat = np.concatenate((dat,sphericity_col[:,None]), axis=1)
        
        strs.append('Sphericity')
        dat_prompt_strs.append(str(len(strs)) + ' - ' + strs[len(strs)-1])

    #   print(color('Sphericity has been added as a a data option.',
    #       'green',attrs=['bold']))
        
        
    ext_col_ = get_datcol(strs, dat_prompt_strs)

    filter_legality = input('Filter data? [Y/N]').rstrip()
    if filter_legality in ('Y', 'y'):
        while True:
            try:    
                fil_col_idx = int(input('Select the filter column:\n' + '\n'.join(dat_prompt_strs)).rstrip())
            except ValueError:
                print(color("Input must be integer!\n",'red'))
            else:
                print(color('You chose: ', 'green') + str(fil_col_idx) + '\n')
                pass
            try:    
                filter_threshold = float(input('Enter filter threshold in mm: ').rstrip())
            except ValueError:
                print(color("Input must be number!\n",'red'))
            else:
                print(color('You chose: ', 'green') + str(filter_threshold) + '\n')
                break

        dat = np.array(filter_data(dat, fil_col_idx, filter_threshold))

    while True:
        if type(ext_col_) is int:
            if idx != 0:
                print(color('End of file reached\n', 'blue') + 
                      color('Closing Program . . .', 'red'))
                break
            ext_col_idx = ext_col_

        else:
            try:
                ext_col_idx = ext_col_[idx]
            except IndexError:
                print(color('End of file reached\n', 'blue') + 
                      color('Closing Program . . .', 'red'))
                break
        fig1 = scattergrid(dat, strs, vol_col_idx, ext_col_idx)
        plt.show(block=False)
        sig = True
        while sig == True:
            v = voldist(dat, strs, get_bins(dat, ext_col_idx), 
                        [vol_col_idx, ext_col_idx])
            fig2 = v.vdplot()
            plt.show()
            menu_cmd(v)
    return

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--init", action='store_true')
    args = parser.parse_args()

    if args.init is not None:
        print(color('pyPSD successfully initialized!', 'green'))
        print('Closing...')
        quit()
    main()










# END, FIN, QED, ETC