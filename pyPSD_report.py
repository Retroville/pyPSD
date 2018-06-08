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
idx = 0

dat, strs, dat_prompt_strs = get_data()
vol_col_idx = get_volcol(strs, dat_prompt_strs)
ext_col_ = get_datcol(strs, dat_prompt_strs)
if type(ext_col_) is int:
	ext_col_idx = ext_col_
else:
	ext_col_idx = ext_col_[idx]

typ = (0,0)
v = voldist(dat, strs, 25, [ext_col_idx, vol_col_idx], typ)


'''
pdf = PdfPages('../output/testoutput.pdf')

scatterplots = plt.figure(num=1, figsize=(8.5, 11))
plt.suptitle(strs[ext_col_idx])
for i in range(0, len(dat[0])):
	plt.subplot(4, 2, (i%8)+1)
	if not i == ext_col_idx:
		plt.scatter(dat[:, (i%8)], dat[:, ext_col_idx], marker='.', c='black', s=2)
		plt.xlim(0, max(dat[:, (i%8)]))
	  # plt.ylim(0, max(dat[:, ext_col_idx-1]))
	else:
		plt.plot([0, 0, 1, 1, 0, 1, 1, 0],[0, 1, 0, 1, 0, 0, 1, 1],'r')
		plt.xticks([])
		plt.yticks([])
	if (i%8 == 0) and (i != 0):
		pdf.savefig(scatterplots)
		scatterplots = plt.figure(num=1, figsize=(8.5, 11))
		plt.suptitle(strs[ext_col_idx])


'''
numofpages = len(dat[0])//8
if not len(dat[0])%8 == 0:
	numofpages += 1
pages = [plt.figure(num=n+1, figsize=(8.5, 11)) for n in range(len(dat[0])//8)]

print('total colimns: ' + clr(str(len(dat[0])), 'magenta'))
print('expected pages: ' + clr(numofpages, 'magenta'))
print('current active figures: ' + clr(len(pages),'magenta'))
print('figure pointers: ' + clr(pages,'magenta'))

print('\nbeginning page creation loop...\n')
with PdfPages('../output/testpdfreg.pdf') as pdf:
	for i in range(0, len(dat[0])):
		# creates a grid of scatterplots, per each column pair
		
		plt.subplot(4, 2, (i%8)+1)
		if not i == ext_col_idx:
			plt.scatter(dat[:, i], dat[:, ext_col_idx], marker='.', c='black', s=2)
			plt.xlim(0, max(dat[:, i]))
		  # plt.ylim(0, max(dat[:, ext_col_idx-1]))
		else:
			plt.plot([0, 0, 1, 1, 0, 1, 1, 0],[0, 1, 0, 1, 0, 0, 1, 1],'r')
			plt.xticks([])
			plt.yticks([])
		plt.xlabel(strs[i])

		print('Figure ' + clr(i, 'cyan') + ', ' + clr(strs[i],'magenta') +
			  'in position ' + clr((i%8)+1, 'magenta') + 'on page ' + 
			  clr((i//8)+1, 'magenta'))
		test = (i%8)+1
		testcase = test == 0
		print(str(test) + str(testcase))
		if ((i%8) == 0) and (i != 0):
			print('formatting plot...')
			scatterplots.set_figheight(11)
			scatterplots.set_figwidth(8.5)
			plt.suptitle(strs[ext_col_idx])
			plt.gcf().tight_layout() # rect=[0, 0.03, 1, 0.95]
			plt.subplots_adjust(top=0.95, left=0.1, right = 0.9)

			print('\nsaving page...')
			pdf.savefig()
			print('page saving complete!')
			print('closing active page...')
			plt.close()
			print('active page closed!')






























	# 420