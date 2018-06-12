# pyPSD report mode
# Austin Rhodes, 2018
from pyPSD import *
import numpy as np
import matplotlib
from matplotlib.backends.backend_pdf import PdfPages
from pylab import *
from termcolor import colored as clr

try:
	os.makedirs('../output/')
except OSError as e:
	if e.errno != errno.EEXIST:
		raise

# %% Gather Data
dat, strs, dat_prompt_strs = get_data()
vol_col_idx = get_volcol(strs, dat_prompt_strs)
ext_col_ = get_datcol(strs, dat_prompt_strs)

if type(ext_col_) is int:
	nreports = 1
else:
	nreports = len(ext_col_)

#enter filename for output:
filename = 'testoutputTRU'

numofpages = len(dat[0])//8
if not len(dat[0])%8 == 0:
	numofpages += 1

print('creating empty pdf file at ' + '../output/' + filename + '.pdf:\n\t')
pages = [plt.figure(num=n+1, figsize=(8.5, 11)) for n in range(numofpages)]
print(str(numofpages) + ' empty pages\n\t' + str(len(pages)) + 
		' active empty figures')
print(pages)

print('creating ' + str(len(dat[0])) + ' empty scatterplots')
# void
print('done: \n\t' + str(len(dat[0])) + ' empty scatterplots')

print('\nbeginning page creation loop...\n')
print('setting current page to 1...')
currentpage = 1
with PdfPages('../output/' + filename + '.pdf') as pdf:
	#for idx in range(0, nreports)
	for idx in range(0, nreports):	#was lst working on this

		if type(ext_col_) is int:
			ext_col_idx = ext_col_
		else:
			ext_col_idx = ext_col_[idx]

		typ = (0,0)
		v = voldist(dat, strs, 25, [ext_col_idx, vol_col_idx], typ)

		for i in range(0, len(dat[0])):
			# creates a grid of scatterplots, per each column pair
			plt.figure(currentpage)
			plt.subplot(4, 2, (i%8)+1)

			print('creating scatterplot ' + str(i+1) + ' of ' + str(len(dat[0])))
			print('plotting ' + strs[i] + ' [pos' + str((i%8)+1) + ' pg' + str((i//8)+1) + ']...', end="")

			if not i == ext_col_idx:
				plt.scatter(dat[:, i], dat[:, ext_col_idx], marker='.', c='black', s=2)
				plt.xlim(0, max(dat[:, i]))
			  # plt.ylim(0, max(dat[:, ext_col_idx-1]))
			else:
				plt.plot([0, 0, 1, 1, 0, 1, 1, 0],[0, 1, 0, 1, 0, 0, 1, 1],'r')
				plt.xticks([])
				plt.yticks([])
			plt.xlabel(strs[i])

			print('done')

			if ((((i+1)%8) == 0) and (i != 0)) or (i+1 == len(dat[0])):
				print('formatting plot' + '...', end="")
				plt.figure(currentpage).set_figheight(11)
				plt.figure(currentpage).set_figwidth(8.5)
				plt.suptitle(strs[ext_col_idx])
				plt.gcf().tight_layout() # rect=[0, 0.03, 1, 0.95]
				plt.subplots_adjust(top=0.95, left=0.1, right = 0.9)
				print('done')

				print('saving page' + '...', end="")
				pdf.savefig()
				print('done')
				print('closing active page' + '...', end="")
				plt.close()
				print('done')
				if not i+1 == len(dat[0]):
					print('incrementing currentpage from ' + str(currentpage) + 
						  ' to ' + str(currentpage+1) + '...')
					currentpage += 1
					print('beginning page creation loop...')
				else:
					print('no more plots, closing...')
					print(color('scatterplot pages complete, ' +
								'switching to histogram mode', 'green'))


		#Distribution plots
		print('performing volume distribution calculations' + '...', end="")
		v = voldist(dat, strs, 25, [vol_col_idx, ext_col_idx])
		print('done')
		print('formatting histogram page' + '...', end="")
		plt.figure(num=2, figsize=(8, 11))
		plt.ion()
		plt.clf()
		print('done')
		print('generating subplots:')
		def subhistplots(num, xvals, yvals, xstr, ystr):
			print('\tcreating subplot ' + str(num) + '...', end="")
			plt.subplot(2, 1, num)
			plt.bar(xvals, yvals, width=--1, color='white', linewidth=1, 
				edgecolor='red', hatch='////', align='edge', 
				tick_label=np.around(v.realbins[1:],5))
			plt.xlabel(ystr)
			plt.ylabel(xstr)
			plt.xticks(rotation=90)
			print('done')
			return
		subhistplots(1, v.binlabels, v.counts, 'Counts', v.extstr)
		subhistplots(2, v.binlabels, v.volbinsums, 'Volume', v.extstr)
		plt.suptitle(strs[ext_col_idx])
		plt.tight_layout(rect=[0, 0.03, 1, 0.95])
		plt.annotate(v.navgstr, xy=(0.55, 0.9), xytext=(0.55, 0.9), 
						 textcoords='axes fraction')
		plt.annotate(v.vavgstr, xy=(0.55, 0.8), xytext=(0.55, 0.8),
						 textcoords='axes fraction') 

		print('saving page' + '...', end="")
		pdf.savefig()
		print('done')
		print('closing active page' + '...', end="")
		plt.close()
		print('done')

		#if r = 
		#Metadata outputs go here
		






























	# 420