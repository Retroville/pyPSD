# pyPSD report mode
# Austin Rhodes, 2018
from pyPSD import *
import numpy as np
import matplotlib
from matplotlib.backends.backend_pdf import PdfPages
from pylab import *
from termcolor import colored as color
from argparse import ArgumentParser, ArgumentTypeError
import re
import time

start = time.time()
savetime = 0

try:
	os.makedirs('../output/')
	os.makedirs('../input/')
except OSError as e:
	if e.errno != errno.EEXIST:
		raise

def savepage():
	global savetime

	mtime = time.time()
	print('saving page' + '...', end="", flush=True)
	pdf.savefig()
	print('done')
	print('closing active page' + '...', end="", flush=True)
	plt.close()
	print('done')
	ntime = time.time() - mtime
	savetime = savetime + ntime

def get_file_list(frange):
	if type(frange) is int:
		frange = [frange]
	file_path = []
	file_name = []
	os.chdir('../input/')
	files = glob.glob('*.csv')
	files.sort()
	if frange is False:
		frange = range(len(files))
	for i in frange:
		file_path.append('../input/' + files[i])
		mfile_name = files[i]
		mfile_name = mfile_name[:-4]
		file_name.append(mfile_name)
	return file_path, file_name

parser = ArgumentParser()
parser.add_argument('-f', "--files", nargs='?', type=parseNumList, const=False)
parser.add_argument('-c', "--columns", type=parseNumList)
parser.add_argument('-v', "--volume", type=parseNumList)
parser.add_argument('-t', "--threshold", nargs=2, type=float)
args = parser.parse_args()
print(args.files)

if args.files is not None:
	file_path, file_name = get_file_list(args.files)
else:
	print(color('\n(Careful, these might not be in the order ' + 
					'you expect)','red'))
	file_path, file_name = get_file()
if type(file_path) is not list:
	file_path = [file_path]
	file_name = [file_name]

vflag = False
eflag = False

for jdx, fp in enumerate(file_path):

	dat, strs, dat_prompt_strs = get_data(file_path[jdx])

	if args.volume is not None:
		vol_col_idx = args.volume
		if type(vol_col_idx) is list:
			vol_col_idx = vol_col_idx[0]
			print(color('Volume column must be single integer, not list', 'red'))
	elif vflag == False:
		vol_col_idx = get_volcol(strs, dat_prompt_strs)
		vflag = True

	if args.columns is not None:
		ext_col_ = args.columns
	elif eflag == False:
		ext_col_ = get_datcol(strs, dat_prompt_strs)
		eflag = True

	if args.threshold is not None:
		prefilt = len(dat)

		print(color(dat,'red'))
		print(color('\t\t\t>>[Filtering]>>','yellow',attrs=['blink','bold']))
		dat = np.array(filter_data(dat, int(args.threshold[0])-1, args.threshold[1]))
		print(color(dat,'blue'))

		postfilt = len(dat)

		print(color(str(prefilt) + '-->' + str(postfilt), 'yellow'))

		FILTERED = True
		filename = file_name[jdx] + '_Report_FILTERED'
	#	data_out(dat)
	else:
		FILTERED = False
		filename = file_name[jdx] + '_Report'


	if type(ext_col_) is int:
		nreports = 1
	else:
		nreports = len(ext_col_)

	#enter filename for output:
	

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

		for idx in range(0, nreports):

			if type(ext_col_) is int:
				ext_col_idx = ext_col_
			else:
				ext_col_idx = ext_col_[idx]

			supertitle = (file_name[jdx] + '         ' + strs[ext_col_idx] + 
				'          Filtered: ' + str(FILTERED))

			typ = (0,0)
			v = voldist(dat, strs, 25, [ext_col_idx, vol_col_idx], typ)
			m_pvol = v.porevol
			for i in range(0, len(dat[0])):
				# creates a grid of scatterplots, per each column pair
				plt.figure(currentpage)
				plt.subplot(4, 2, (i%8)+1)

				print('creating scatterplot ' + str(i+1) + ' of ' + str(len(dat[0])))
				print('plotting ' + strs[i] + ' [pos' + str((i%8)+1) + ' pg' + str((i//8)+1) + ']...', end="", flush=True)

				if not i == ext_col_idx:
					plt.scatter(dat[:, i], dat[:, ext_col_idx], marker='.', c='black', s=2)
					plt.xlim(0, max(dat[:, i]))
				  # plt.ylim(0, max(dat[:, ext_col_idx-1]))
				else:
					plt.plot([0, 0, 1, 1, 0, 1, 1, 0],[0, 1, 0, 1, 0, 0, 1, 1],'r')
					plt.xticks([])
					plt.yticks([])
				plt.xlabel(strs[i])
				plt.ylabel(strs[ext_col_idx])

				print('done')

				if ((((i+1)%8) == 0) and (i != 0)) or (i+1 == len(dat[0])):
					print('formatting plot' + '...', end="", flush=True)
					plt.figure(currentpage).set_figheight(11)
					plt.figure(currentpage).set_figwidth(8.5)
					plt.suptitle(supertitle)
					plt.gcf().tight_layout() # rect=[0, 0.03, 1, 0.95]
					plt.subplots_adjust(top=0.95, left=0.1, right = 0.9, wspace=0.35)
					print('done')

					savepage()
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
			print('performing volume distribution calculations' + '...', end="", flush=True)
			v = voldist(dat, strs, 25, [vol_col_idx, ext_col_idx])
			print('done')
			print('formatting histogram page' + '...', end="", flush=True)
			plt.figure(num=2, figsize=(8.5, 11))
			plt.clf()
			print('done')
			print('generating subplots:')
			def subhistplots(num, xvals, yvals, xstr, ystr):
				print('\tcreating subplot ' + str(num) + '...', end="", flush=True)
				plt.subplot(2, 1, num)
				plt.subplots_adjust(bottom=0.5)
				plt.bar(xvals, yvals, width=-1, color='white', linewidth=1, 
					edgecolor='red', hatch='////', align='edge', 
					tick_label=np.around(v.realbins[1:],5))
				plt.xlabel(ystr)
				plt.ylabel(xstr)
				plt.xticks(rotation=90)
				print('done')
				return
			subhistplots(1, v.binlabels, v.counts, 'Counts', v.extstr)
			subhistplots(2, v.binlabels, v.volbinsums, 'Volume', v.extstr)
			plt.suptitle(supertitle)
		#	plt.gcf().tight_layout(rect=[0.05, 0.2, 0.95, 0.95])
			plt.subplots_adjust(bottom=0.3, top=0.95, hspace=0.3)

			plt.gcf().text(0.1,0.18,v.numavgstr)
			plt.gcf().text(0.1,0.15,v.numstdstr)
			plt.gcf().text(0.1,0.12,v.nummaxstr)

			plt.gcf().text(0.5,0.18,v.volavgstr)
			plt.gcf().text(0.5,0.15,v.volstdstr)
			plt.gcf().text(0.5,0.12,v.volmaxstr)

			'''
			plt.subplot(3, 1, 3)
			plt.annotate('This is where metadata for an individual column might go'
				, xy=(0.25,0.5), xytext=(0.2,0.5))
			plt.annotate('Total Volume: ' + str(m_tvol)
				, xy=(0.25,0.4), xytext=(0.2,0.4))
			plt.annotate('Pore Volume: ' + str(m_pvol)
				, xy=(0.25,0.3), xytext=(0.2,0.3))
			plt.annotate('Percentage of pores per total volume: ' + str(m_pvol/m_tvol)
				, xy=(0.25,0.2), xytext=(0.2,0.2))
			'''

			savepage()

			print(color('distributions complete', 'green'))

		#Metadata outputs
		print(color('all plots complete', 'green'))
		print('formatting meta page' + '...', end="", flush=True)
		plt.figure(num=3, figsize=(8.5,11))
		plt.clf()
		print('done')

		savepage()
	print(color('Report complete at ../output/' + filename + '.pdf', 'green'))

end = time.time()

elapsed = end - start
print(color('Total time elapsed: ' + str(elapsed) + ' seconds' + 
			'\nOR ' + str(elapsed/60) + ' minutes.', 'cyan'))
print(color('Total time spent doing pdf.savefig(): ' + str(savetime) + ' seconds' + 
			'\nOR ' + str(savetime/60) + ' minutes.\n', 'red'))




















