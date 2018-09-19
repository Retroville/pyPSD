# pyPSD report mode
# Austin Rhodes, 2018
from pyPSD import *
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_pdf import PdfPages
from pylab import *
from termcolor import colored as color
from argparse import ArgumentParser, ArgumentTypeError
import re
import time

start = time.time()
savetime = 0

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

def get_file_list(frange, io):
	if type(frange) is int:
		frange = [frange]
	file_path = []
	file_name = []
	os.chdir(io[0])
	files = glob.glob('*.csv')
	files.sort()
	if frange is False:
		frange = range(len(files))
	for i in frange:
		file_path.append(io[0] + files[i])
		mfile_name = files[i]
		mfile_name = mfile_name[:-4]
		file_name.append(mfile_name)
	return file_path, file_name

'''Columns for summary:

	Sample Name
	Laser Power
	Total Volume
	Count
	Porosity
  [ Total X
	Avg. X
	STD of X
	Min X
	Max X ]

'''

parser = ArgumentParser()
parser.add_argument('-i', "--io", nargs=2, type=str) # Asks for input and output folders
parser.add_argument('-f', "--files", nargs='?', type=parseNumList, const=False)
parser.add_argument('-c', "--columns", nargs='?', type=parseNumList, const=False)
parser.add_argument('-v', "--volume", nargs='?', type=parseNumList, const=False)
parser.add_argument('-t', "--threshold", nargs=2, type=float) # filter_col filter_threshold
parser.add_argument("--list", action='store_true')
parser.add_argument("--nosphericity", action='store_true')
parser.add_argument("--nosummary", action='store_true')
parser.add_argument("--fullsummary", action='store_true')
parser.add_argument("--allcolumns", action='store_true')
parser.add_argument("--csv", action='store_true')
parser.add_argument("--init", action='store_true')
parser.add_argument("--bins", nargs=1, type=int) # This is returned as a list for god knows why
args = parser.parse_args()

if args.nosummary is True:
	is_summary = False
else:
	is_summary = True

# Assign input vars
global io

if args.io is not None:
	io = args.io
else:
	io = ['../input/','../output/']

print('Input path: ' + io[0])
print('Output path ' + io[1])

try:
	os.makedirs(io[1] + 'csv/')
	os.makedirs(io[0])
except OSError as e:
	if e.errno != errno.EEXIST:
		raise

if args.init is True:
	print('pyPSD successfully initialized!')
	quit() # This is terrible practice

if args.files is not None:
	file_path, file_name = get_file_list(args.files, io)
else:
	print(color('\n(Careful, these might not be in the order ' + 
					'you expect)','red'))
	file_path, file_name = get_file(infolder=io[0])
if type(file_path) is not list:
	file_path = [file_path]
	file_name = [file_name]

vflag = False
eflag = False

	#summary
		#	beam_diameter =input('Beam Diameter: ').rstrip()

'''
if is_summary is True:
	summ_output = []
	summ_col_strs, summ_col_idx = get_summ_cols()
	if summ_col_strs == None and summ_col_idx == None:
		args.nosumm = True
	else:
		summ_output.append(summ_col_strs)

		# Objectify this VVV
		beam_power=[]
		total_sample_volume=[]
		beam_diameter=[]
		for jdx, fp in enumerate(file_path):
			print('\nEnter the following parameters for ' + file_name[jdx] + ': ')
			if 3 in summ_col_idx or 4 in summ_col_idx:
				beam_power.append(float(input('Beam Power: ').rstrip()))
			if 2 in summ_col_idx:
				total_sample_volume.append(float(input('Total Sample Volume: ').rstrip()))
			if 4 in summ_col_idx:
				beam_diameter.append(float(input('Beam Diameter: ').rstrip()))
'''

summary2 = []

summary1 = []

tpv = []

total_sample_volume = ['Total Sample Volume']

pore_counts = ['Pore Counts']

sample_name = ['Sample Name']

total_pore_volume = ['Total Pore Volume']

beam_power = ['Laser Power']

for jdx, fp in enumerate(file_path):

	dv_all = [] # New distribution values per each file

	summ_row_2_strs = []

	summ_row_2 = []

	dat, strs, dat_prompt_strs = get_data(file_path[jdx])

	print(args.list)
	if args.list is True: # Breaks if '-l' arg is parsed
		print('\n')
		get_file(noparse=True)
		print('\n')
		list_cols(strs, dat_prompt_strs)
		print('\n')
		sys.exit()

	if args.volume is not None:
		if type(args.volume) is list:
			print(color('Volume column must be single integer, not list', 'red'))
			args.volume = False
		if args.volume is False:
			vol_col_idx = [i for i,j in enumerate(strs) if "Voxel:Volume" in j][0]
	elif vflag == False:
		vol_col_idx = get_volcol(strs, dat_prompt_strs)
		vflag = True

	sur_col_idx = [i for i,x in enumerate(strs) if 'Voxel:Surface area' in x]
	# Detect Surface Area column and calculate sphericity

	if (len(sur_col_idx) > 0) and (args.nosphericity is False):
		print(color('Surface Area column detected! ',
			'green',attrs=['bold']), end="", flush=True)

		sphericity_col = sphericity(dat[:, sur_col_idx], dat[:, vol_col_idx])
		dat = np.concatenate((dat,sphericity_col[:,None]), axis=1)
		# Add sphericity data to 'dat' variable
		
		strs.append('Sphericity')
		dat_prompt_strs.append(str(len(strs)) + ' - ' + strs[len(strs)-1])

		print(color('Sphericity has been added as a a data option.',
			'green',attrs=['bold']))
	elif (len(sur_col_idx) > 0) and (args.nosphericity is True):
		print(color('Surface Area column detected, but suppressed. Ignoring. . .',
			'red',attrs=['bold']))

	if args.columns is not None:
		if args.columns is False:
			if args.allcolumns is True:
				ext_col_ = [i for i,j in enumerate(strs)]
			else:
				ext_col_ = [i for i,j in enumerate(strs) if "Count" not in j]
		else:
			ext_col_ = args.columns
	elif eflag == False:
		ext_col_ = get_datcol(strs, dat_prompt_strs)
		eflag = True
	
	if args.bins is not None:
		binz = args.bins[0]
	else:
		binz = 25
	
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
		cleaned_filepath = io[1] + '/csv/' + file_name[jdx] + '_CLEANED_FILTERED.csv'
	else:
		FILTERED = False
		filename = file_name[jdx] + '_Report'
		cleaned_filepath = io[1] + '/csv/' + file_name[jdx] + '_CLEANED.csv'


	if type(ext_col_) is int:
		nreports = 1
	else:
		nreports = len(ext_col_)

	
	#outputs cleaned csv data files
	cleaned_output = []
	cleaned_output.append(strs)
	for i in range(0,len(dat)):
		cleaned_output.append(dat[i])


	print(cleaned_output)
	with open(cleaned_filepath, 'w') as csvout:
		outputwriter = csv.writer(csvout, delimiter=',')
		outputwriter.writerows(cleaned_output)
		print(color('cleaned output saved as ' + cleaned_filepath, 'green') + '\n')

	#---

	numofpages = len(dat[0])//8
	if not len(dat[0])%8 == 0:
		numofpages += 1

	print('creating empty pdf file at ' + io[1]+ filename + '.pdf:\n\t')
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

	


	with PdfPages(io[1] + filename + '.pdf') as pdf:



		for idx in range(0, nreports):

			if type(ext_col_) is int:
				ext_col_idx = ext_col_
			else:
				ext_col_idx = ext_col_[idx]

			if FILTERED:
				filterstr = ', Filtered\n'
			else:
				filterstr = '\n'
			supertitle = (file_name[jdx] + filterstr + strs[ext_col_idx] + '\n')

			typ = (0,0)
			v = voldist(dat, strs, 25, [ext_col_idx, vol_col_idx], typ)
			m_pvol = v.porevol
			for i in range(0, len(dat[0])):
				# creates a grid of scatterplots, per each column pair
				plt.figure(currentpage)
				plt.subplot(4, 2, (i%8)+1)

				print('creating scatterplot ' + str(i+1) + ' of ' + str(len(dat[0])))
				print('plotting ' + strs[i] + ' [pos' + str((i%8)+1) + ' pg' + 
					str((i//8)+1) + ']...', end="", flush=True)

				if not i == ext_col_idx:
					plt.scatter(dat[:, i], dat[:, ext_col_idx], marker='|', c='black', s=1, rasterized=True)
					plt.xlim(0, max(dat[:, i]))
				#   plt.ylim(0, max(dat[:, ext_col_idx-1]))
				else:
					plt.plot([0, 0, 1, 1, 0, 1, 1, 0],[0, 1, 0, 1, 0, 0, 1, 1],'r')
					plt.xticks([])
					plt.yticks([])
				plt.xlabel(strs[i])
			#	plt.ylabel(strs[ext_col_idx])

				print('done')

				if ((((i+1)%8) == 0) and (i != 0)) or (i+1 == len(dat[0])):
					print('formatting plot' + '...', end="", flush=True)
					plt.figure(currentpage).set_figheight(11)
					plt.figure(currentpage).set_figwidth(8.5)
					plt.suptitle(supertitle, fontsize=12)
					plt.gcf().tight_layout() # rect=[0, 0.03, 1, 0.95]
					plt.subplots_adjust(top=0.9, left=0.1, right = 0.9, wspace=0.35)
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
			v = voldist(dat, strs, binz, [vol_col_idx, ext_col_idx])
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
					tick_label=np.around(v.realbins[1:],5), rasterized=False)
				plt.xlabel(ystr)
				plt.ylabel(xstr)
				plt.xticks(rotation=90)
				print('done')
				return
			subhistplots(1, v.binlabels, v.counts, 'Counts', v.extstr)
			subhistplots(2, v.binlabels, v.volbinsums, 'Volume', v.extstr)

			# Append histogram data to this file's csv output

			dv_binlabels = ['Bin Max (' + v.extstr + ')'] + v.realbins[1:].tolist()
			dv_counts = ['Counts'] + v.counts.tolist()
			dv_volbinsums = ['Volume'] + v.volbinsums

			dv_all.append(dv_binlabels)
			dv_all.append(dv_counts)
			dv_all.append(dv_volbinsums)

			plt.suptitle(supertitle, fontsize=12)
			plt.subplots_adjust(bottom=0.3, top=0.9, hspace=0.3)

			plt.gcf().text(0.1,0.20,v.numavgstr)
			plt.gcf().text(0.1,0.185,v.numstdstr)
			plt.gcf().text(0.1,0.17,v.nummaxstr)

			plt.gcf().text(0.1,0.155,v.volavgstr)
			plt.gcf().text(0.1,0.14,v.volstdstr)
			plt.gcf().text(0.1,0.125,v.volmaxstr)

			'''
			plt.subplot(3, 1, 3)
			plt.annotate('This is where summdata for an individual column might go'
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

			# APPENDING TO SUMMARY EXPORT
		#	summ_row_2
		#	summ_row_2_strs
			summ_col_str = strs[ext_col_idx]
			summ_dat = dat[:, ext_col_idx]
			print('Performing calculations for column ' + summ_col_str + '...')
			summ_row_2_strs.append('Total ' + strs[ext_col_idx])
			summ_row_2.append(v.numtot)
			summ_row_2_strs.append('Avg. ' + strs[ext_col_idx])
			summ_row_2.append(v.numavg)
			summ_row_2_strs.append('STD of ' + strs[ext_col_idx])
			summ_row_2.append(v.numstd)
			summ_row_2_strs.append('Minimum ' + strs[ext_col_idx])
			summ_row_2.append(v.nummin)
			summ_row_2_strs.append('Maximum ' + strs[ext_col_idx])
			summ_row_2.append(v.nummax)


		#Format distribution table to prep for export
		distribution_values = []
		for i in range(0,len(dv_all[0])):
			distrow = [item[i] for item in dv_all]
			distribution_values.append(distrow)

		#Export distribution table to csv row by row
		with open(io[1] + '/csv/' + filename + '_values.csv', 'w') as csvout:
			outputwriter = csv.writer(csvout, delimiter=',')
			outputwriter.writerows(distribution_values)
			print(color('distribution values saved as ' + io[1] + '/csv/' 
						+ filename + '_values.csv', 'green') + '\n')

	#Append that files summary2 row to the main summary2
	summary2.append(summ_row_2)
	print(summary2)


	print(color('Report complete at ' + io[1] + filename + '.pdf', 'green'))

	pore_counts.append(v.porecount)
	sample_name.append(file_name[0])
	tpv.append(float(v.porevol))

tsv = []

	# CSV summ outputs
if is_summary is True:
	for jdx, fp in enumerate(file_path):
		print('\nEnter the following parameters for ' + file_name[jdx])
			#': \n(leave blank if not applicable) ')
		beam_power.append(float(input('Laser Power: '))) # dont use float here, use it later IF exists
		tsv.append(float(input('Total Sample Volume: ')))

	if tsv:
		total_sample_volume.append(tsv)
		total_pore_volume.append(tpv)
		porosity = ['Porosity'] + [tpv/tsv for tpv,tsv in zip(tpv,tsv)]

	# At this point the following variables exist: (? - optional, ! - special)
	#	beam_power
	# ? total_sample_volume
	# ? porosity
	#	pore_counts
	#	sample_name
	#	total_pore_volume
	# ! summary2
	summary1.append(sample_name)
	summary1.append(beam_power)
	summary1.append(pore_counts)
	summary1.append(total_pore_volume[0])
	if total_sample_volume:
		summary1.append(total_sample_volume[0])
		summary1.append(porosity)

	summary2 = [summ_row_2_strs] + summary2

	midsummary1 = []
	for i in range(0,len(summary1[0])):
		midsummary1.append([item[i] for item in summary1])

	summary1 = midsummary1

	summary = []

	print(summary1)
	print('\n\n')
	print(summary2)
	for i in range(0,(len(summary1))):
		fullrow = summary1[i] + summary2[i]
		summary.append(fullrow)

	with open(io[1] + '/csv/summary.csv', 'w') as csvout:
		outputwriter = csv.writer(csvout, delimiter=',')
		outputwriter.writerows(summary)
		print(color('summfile saved as ' + io[1] + 'csv/summary.csv', 'green') + '\n')


end = time.time()

elapsed = end - start
print(color('Total time elapsed: ' + str(elapsed) + ' seconds' + 
			'\nOR ' + str(elapsed/60) + ' minutes.', 'cyan'))
print(color('Total time spent doing pdf.savefig(): ' + str(savetime) + ' seconds' + 
			'\nOR ' + str(savetime/60) + ' minutes.\n', 'red'))

#.933652 mm^3
#140 WATT











