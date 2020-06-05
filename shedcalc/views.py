from schmidt import *
from math import ceil
from numpy import array
from coefficients import ShedInfo
from django.template import loader
from django.shortcuts import render
from django.http import HttpResponse


def index(request):
	"""
	Render the index page
	"""
	return render(request, 'shedcalc/index.html', {})


def calc(request):
	"""
	Render the results page (calculates the result...)
	"""

	# retrieve data from the request object
	region = int(request.POST['region'])		# region
	prodrate = int(request.POST['prodrate'])	# production rate
	before = float(request.POST['before'])		# R before sampling
	after = float(request.POST['after'])		# R after sampling
	boulderR = float(request.POST['boulder_r'])	# mean R for boulder
	boulderU = float(request.POST['boulder_u'])	# R uncertainty for boulder
	boulderV = float(request.POST['boulder_v'])	# calibration R for boulder

	# import the posted table of data and parse into lists
	names, lats, lngs, data = parseInputTable(request.POST['tabdata'])

	# if the difference between value and reference is >uncertainty then calibrate values
	if abs(boulderV - boulderR) > boulderU:
		data = getCalibratedValues(applyDriftFactorToCells(getDriftFactor(before,
			after, data), data), boulderV, boulderR)

	# calculate the mean and MAD for each row
	means = array([ getRowMean(d) for d in data ])
	mads = [ getRowMAD(d) for d in data ]

 	# calculate the ages and errors based upon selected region
	regions = ['britain', 'pyrenees']
	prodrates = ['balco_age', 'cronus_age', 'lochlomond_age', 'rannoch_age', 'glenroy_age']
	ages, error = getAges(ShedInfo.coefficients[regions[region]][prodrates[prodrate]], means)

 	# number of decimal places for results display
 	sf = 2

 	# prepare table for the web template
	outputs = []
	for i in range(len(names)):
		outputs.append({
			'name': names[i],
			'lat': lats[i],
			'lng': lngs[i],
			'mean': round(means[i], sf),
			'mad': round(mads[i], sf),
			'age': round(ages[i], sf),
			'errors': round(error[i], sf)
			})

	# lower precision for the chart
	ages2 = [ round(i, 1) for i in ages ]
	errors2 = [ round(i, 1) for i in error ]

	# render the template using the resulting data
	return render(request, 'shedcalc/results.html', {
		'outputs': outputs,
		'ages':str(ages2).replace(" ", "").replace("[", "").replace("]", ""),
		'errors':str(errors2).replace(" ", "").replace("[", "").replace("]", "")
		})


def samples_chart(request):
	"""
	Draw the results page samples chart
	"""

	# get sample numbers
	ages = [float(x) for x in request.GET['a'].split(",")]
	errors = [float(x) for x in request.GET['e'].split(",")]
	x = range(1, len(ages)+1)

	# max limit of y axis
	ymax =  int((5 * ceil((max(ages) + max(errors))/5)))

 	# create a figure to draw on and add a subplot
	fig = Figure()
	ax = fig.add_subplot(1,1,1)

	# set axis limit to stop y axis going to -5...
	ax.set_ylim(0, ymax)

	# points and error bars
	ax.plot(x,ages,'k.', label='Sample Age Points', markersize=3.5)
	ax.errorbar(x, ages, ecolor='k', yerr=errors, fmt=" ", linewidth=0.5, capsize=0)

	# labels etc
	ax.set_xlabel('Sample Order')
	ax.set_ylabel('Age (ka)')
	ax.set_title('Estimated Sample Ages')

	# encode to send to browser
	canvas=FigureCanvas(fig)
	response=http.HttpResponse(content_type='image/png')
	canvas.print_png(response)
	return response
