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

try:
	os.makedirs('../output/csv/')
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

def get_meta_cols():
	meta_prompt_strs = []
	meta_col_base = ('Number Average',			#[0] v.numavg
				 'Volume Average',				#[1] v.volavg
				 'Porosity',					#[2] porevol/tvol
				 'Beam Power', 					#[3] --
				 'Volumetric Energy Density')	#[4] E/V (v is melt pool volume or beam dia (??))
	for i in range(0, len(meta_col_base)):
		meta_prompt_strs.append(str(i + 1) + ' - ' + meta_col_base[i])
	meta_prompt = '\nSelect any meta column(s) to be output:\n' + '\n'.join(meta_prompt_strs)
	while True:
		meta_prompt_answer = input(meta_prompt).rstrip()
		if meta_prompt_answer == "":
			return None, None
		try:    
			meta_col_idx = parseNumList(meta_prompt_answer)
		except ValueError:
			print(color("Input must be integer!\n",'red'))
		else:
			break

	meta_col_strs = ['Filename'] + [meta_col_base[i] for i in meta_col_idx]
	return meta_col_strs, meta_col_idx


parser = ArgumentParser()
parser.add_argument('-f', "--files", nargs='?', type=parseNumList, const=False)
parser.add_argument('-c', "--columns", nargs='?', type=parseNumList, const=False)
parser.add_argument('-v', "--volume", nargs='?', type=parseNumList, const=False)
parser.add_argument('-t', "--threshold", nargs=2, type=float) # filter_col filter_threshold
parser.add_argument("--list", action='store_true')
parser.add_argument("--nosphericity", action='store_true')
parser.add_argument("--nometa", action='store_true')
parser.add_argument("--allcolumns", action='store_true')
parser.add_argument("--csv", action='store_true')
args = parser.parse_args()

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

if args.nometa is not True:
	meta_output = []
	meta_col_strs, meta_col_idx = get_meta_cols()
	if meta_col_strs == None and meta_col_idx == None:
		args.nometa = True
	else:
		meta_output.append(meta_col_strs)

		# Objectify this VVV
		beam_power=[]
		total_sample_volume=[]
		beam_diameter=[]
		for jdx, fp in enumerate(file_path):
			print('\nEnter the following parameters for ' + file_name[jdx] + ': ')
			if 3 in meta_col_idx or 4 in meta_col_idx:
				beam_power.append(float(input('Beam Power: ').rstrip()))
			if 2 in meta_col_idx:
				total_sample_volume.append(float(input('Total Sample Volume: ').rstrip()))
			if 4 in meta_col_idx:
				beam_diameter.append(float(input('Beam Diameter: ').rstrip()))


for jdx, fp in enumerate(file_path):

	distribution_values = [] #reset dist values per file

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
				ext_col_ = [i for i,j in enumerate(strs) if "Voxel:" not in j]
		else:
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
				print('plotting ' + strs[i] + ' [pos' + str((i%8)+1) + ' pg' + str((i//8)+1) + ']...', end="", flush=True)

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
			distribution_values.append(dv_binlabels)
			distribution_values.append(dv_counts)
			distribution_values.append(dv_volbinsums)
			distribution_values.append('')


			plt.suptitle(supertitle, fontsize=12)
		#	plt.gcf().tight_layout(rect=[0.05, 0.2, 0.95, 0.95])
			plt.subplots_adjust(bottom=0.3, top=0.9, hspace=0.3)

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

		with open('../output/csv/' + filename + '_values.csv', 'w') as csvout:
			outputwriter = csv.writer(csvout, delimiter=',')
			outputwriter.writerows(distribution_values)
			print(color('distribution values saved as ../output/csv/' 
						+ filename + '_values.csv', 'green') + '\n')


	print(color('Report complete at ../output/' + filename + '.pdf', 'green'))

	# CSV meta outputs
	if args.nometa is not True:
		meta_row = []
		meta_row.append(file_name[jdx])
		if 0 in meta_col_idx:
			meta_row.append(v.numavg)
		if 1 in meta_col_idx:
			meta_row.append(v.volavg)
		if 2 in meta_col_idx:
			porosity = v.porevol/total_sample_volume[jdx]
			meta_row.append(porosity)
		if 3 in meta_col_idx:
			meta_row.append(beam_power[jdx])
		if 4 in meta_col_idx:
			VED = beam_power[jdx]/beam_diameter[jdx]
			meta_row.append(VED)
		print(color(meta_row, 'yellow'))

		meta_output.append(meta_row)

		print(color(meta_output, 'cyan'))

if args.nometa is not True:
	with open("../output/csv/metadata.csv", 'w') as csvout:
		outputwriter = csv.writer(csvout, delimiter=',')
		outputwriter.writerows(meta_output)
		print(color("metafile saved as ../output/csv/metadata.csv", 'green') + '\n')


end = time.time()

elapsed = end - start
print(color('Total time elapsed: ' + str(elapsed) + ' seconds' + 
			'\nOR ' + str(elapsed/60) + ' minutes.', 'cyan'))
print(color('Total time spent doing pdf.savefig(): ' + str(savetime) + ' seconds' + 
			'\nOR ' + str(savetime/60) + ' minutes.\n', 'red'))



















