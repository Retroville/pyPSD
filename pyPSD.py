# %% Initialization
import unicodecsv as csv
import numpy as np
from termcolor import colored as color
import os
import errno
import matplotlib.pyplot as plt     
import sys
from pyfiglet import figlet_format
# import tkinter as tk
# from tkinter import filedialog

try:
	os.makedirs('../output/')
except OSError as e:
	if e.errno != errno.EEXIST:
		raise

# %% Calculations
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
		plt.show

		self.numavg = sum(self.extent) / len(self.extent) 

		fidx = np.searchsorted(self.realbins, self.extent, 'right')

		for i in range(1, len(self.realbins)): 
			logc = fidx == i
			self.volbinsums.append(sum(self.volume[logc]))

	  # volbinfracsums = volbinsums / sum(volume)
		self.volfrac = self.volume / sum(self.volume)  
		if typ not in locals() or typ == (0,0):
			self.volavg = sum(self.extent * self.volfrac) / sum(self.volfrac)  
		else:
			self.volavg = sum(self.extent**typ[0])/sum(extent**typ[1])
		
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
					width=-1, color='white', linewidth=1, edgecolor='red',
					hatch='////', align='edge', tick_label=np.around(self.realbins[1:],5))
			plt.xlabel(ystr)
			plt.ylabel(xstr)
			plt.xticks(rotation=90)
			return
		subhistplots(1, self.binlabels, self.counts, 'Counts', self.extstr)
		subhistplots(2, self.binlabels, self.volbinsums, 'Volume', self.extstr)
		plt.tight_layout(rect=[0, 0.03, 1, 0.95])
		plt.annotate(self.navgstr, xy=(0.55, 0.9), xytext=(0.55, 0.9), 
						 textcoords='axes fraction')
		plt.annotate(self.vavgstr, xy=(0.55, 0.8), xytext=(0.55, 0.8),
						 textcoords='axes fraction') 
		return

	def writeout(self):
		binout = self.realbins[1:]
		ostr = [self.extstr, 'Counts', 'Volume']
		odat = np.column_stack([binout, self.counts, self.volbinsums])
		out = np.vstack([ostr,odat])
		with open('../output/' + self.current_file_name + '_output.csv', 'wb') as csvout:
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
		  # plt.ylim(0, max(dat[:, ext_col_idx-1]))
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
def cmd_quit():
	sys.exit()
def cmd_help():
	print(figlet_format('pyPSD', font='big'))
	print('Python Pore Size Analyzer')
	print('Austin Rhodes (C) 2018\n')
	egg = input()
	if egg == 'about':
		print('This software fulfulls the specific needs of Dr. Choo\'s research group at ' +
			  'The University of Tennessee, Knoxville. The primary function is to take in ' +
			  'pore/particle size data from ScanIP (csv) and generate plots/reports to quickly ' +
			  'gauge correlations and general usefulness of the data. Originally developed ' +
			  'in MATLAB as a ' +
			  'way to plot basic pore size distribution histograms, the project was later ' + 
			  'recreated in python and heavily expanded upon to add features such as ' +
			  'scatterplots, outputting to image/csv, interactive plotting, a pdf report mode, ' +
			  'and eventually inputs of multiple scanIP files.')
	else:
		return

def menu_cmd(v):
	OPTIONS = {"bins":dict( desc = "Change bins of currently active distribution plot", func = None), # wew lad
			   "save":dict( desc = "Save currently active plots as images", func = cmd_save),
			   "csv":dict( desc = "Export currently active plots to csv file", func = cmd_csv),
			   "next":dict( desc = "Select next data column (retains volume column selection)", func = cmd_next),
			   "about":dict( desc = "Displays helpful information", func = cmd_help),
			   "quit":dict( desc = "Exits the program", func = cmd_quit)}

	while sig == True:
		print("\nPlease choose an option:")
		for key in OPTIONS.keys():
			print("\t" + key + "\t" + OPTIONS[key]["desc"])
		cmd = input('Selection: ')
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
def get_data():
	dat = []
	dat_prompt_strs = []

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
	return dat, strs, dat_prompt_strs

def get_bins(dat, ext_col_idx):
	while True:
		my_range = input('Input the range of the x axis histogram bins: \n'
				 '(Leave blank to bin automatically)')
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


def get_datcol(strs, pstrs):
	ext_col_strs = 'Select the data column(s):\n' + '\n'.join(pstrs)
	while True:
		ext_col_idx = input(ext_col_strs)
		try:    
			if ',' in ext_col_idx:
				ext_col_idx = [int(i)-1 for i in ext_col_idx.split(',')]
				print(color('You chose: ', 'green') + 'Multiple input columns' + '\n')
			elif ':' in ext_col_idx:
				minmax = [int(i)-1 for i in ext_col_idx.split(':')]
				ext_col_idx = range(minmax[0],minmax[1]+1)
				print(color('You chose: ', 'green') + 'Range of input columns' + '\n')
			else:
				ext_col_idx = int(ext_col_idx)-1
				print(color('You chose: ', 'green') + strs[ext_col_idx] + '\n')
		except ValueError:
			print(color("Input must be integer!\n",'red'))
		else:
			break
	return ext_col_idx

def get_volcol(strs, pstrs):
	vol_col_strs = 'Select the \'volume\' column: \n' + '\n'.join(pstrs)
	while True: 
		vol_col_idx = input(vol_col_strs)
		try:
			vol_col_idx = int(vol_col_idx) - 1
		except ValueError:
			print(color("Input must be integer!\n",'red'))
		else:
			break
	print(color('You chose: ', 'green') + strs[vol_col_idx] + '\n')   
	return vol_col_idx

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
	dat, strs, dat_prompt_strs = get_data()
	vol_col_idx = get_volcol(strs, dat_prompt_strs)
	ext_col_ = get_datcol(strs, dat_prompt_strs)

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
	main()

# END, FIN, QED, ETC

