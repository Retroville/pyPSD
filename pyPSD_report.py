# pyPSD report mode
# Austin Rhodes, 2018
from pyPSD import *
import os
import numpy as np
import matplotlib
from matplotlib.backends.backend_pdf import PdfPages
from pylab import *
from termcolor import colored as clr

try:
	os.makedirs('../output/')
	os.makedirs('../input/')
except OSError as e:
	if e.errno != errno.EEXIST:
		raise

# %% Gather Data
m_tvol = float(input('Enter total volume of sample: '))
m_pwr = float(input('Enter another parameter: '))

dat, strs, dat_prompt_strs, file_name = get_data()
vol_col_idx = get_volcol(strs, dat_prompt_strs)
ext_col_ = get_datcol(strs, dat_prompt_strs)

if type(ext_col_) is int:
	nreports = 1
else:
	nreports = len(ext_col_)

#enter filename for output:
filename = file_name + '_Report'

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
		m_pvol = v.porevol
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
		plt.figure(num=2, figsize=(8.5, 11))
		plt.clf()
		print('done')
		print('generating subplots:')
		def subhistplots(num, xvals, yvals, xstr, ystr):
			print('\tcreating subplot ' + str(num) + '...', end="")
			plt.subplot(3, 1, num)
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



		plt.subplot(3, 1, 3)
		plt.annotate('This is where metadata for an individual column might go'
			, xy=(0.25,0.5), xytext=(0.2,0.5))
		plt.annotate('Total Volume: ' + str(m_tvol)
			, xy=(0.25,0.4), xytext=(0.2,0.4))
		plt.annotate('Pore Volume: ' + str(m_pvol)
			, xy=(0.25,0.3), xytext=(0.2,0.3))
		plt.annotate('Percentage of pores per total volume: ' + str(m_pvol/m_tvol)
			, xy=(0.25,0.2), xytext=(0.2,0.2))


		print('saving page' + '...', end="")
		pdf.savefig()
		print('done')
		print('closing active page' + '...', end="")
		plt.close()
		print('done')

	#Metadata outputs
	print('formatting meta page' + '...', end="")
	plt.figure(num=3, figsize=(8.5,11))
	plt.clf()
	print('done')
	print('printing metadata:')
	print('\t' + str(m_pwr))
	print('\t' + str(2*m_pwr))
	plt.annotate('This is where metadata for an entire dataset might go'
		, xy=(0.25,0.5), xytext=(0.25,0.5))
	plt.annotate('Other parameter: ' + str(m_pwr)
		, xy=(0.25,0.45), xytext=(0.25,0.45))
	plt.annotate('Calculation from other parameter (*2): ' + str(2*m_pwr)
		, xy=(0.25,0.4), xytext=(0.25,0.4))

	print('saving page' + '...', end="")
	pdf.savefig()
	print('done')
	print('closing active page' + '...', end="")
	plt.close()
	print('done')

























