from django.shortcuts import render
from schmidt import *

# Create your views here.

from django.http import HttpResponse
from django.template import loader

def index(request):
	"""
	The index page
	"""
	return render(request, 'shedcalc/index.html', {})
	

def calc(request):
	"""
	The results page (calculates the result...)
	"""

	# get which region (calibration curve) we are using
	region = int(request.POST['region'])
	
	# get which production rate was used
	prodrate = int(request.POST['prodrate'])
	
	# import the posted table of data and parse into lists
	names, lats, lngs, data = parseInputTable(request.POST['tabdata'])
	
	# get before and after values
	before = float(request.POST['before'])
	after = float(request.POST['after'])
	boulder = float(request.POST['boulder'])
	
	# calculate the drift factor and apply to cells
	df = getDriftFactor(before, after, data)
	correctedCells = applyDriftFactorToCells(df, data)

	# calibrate values against our boulder
	calibratedValues = getCalibratedValues(correctedCells, boulder)
	
	# calculate the mean for each row
	means = []
	for d in calibratedValues:
		means.append(getRowMean(d))
		
	# calculate the MAD for each row
	mads = []
	for d in calibratedValues:
		mads.append(getRowMAD(d))
 	
 	# calculate the ages and errors based upon selected region
 	if region == 0:
	 	ages, error = fitLineGB(means, prodrate)
	elif region == 1:
 		ages, error = fitLinePY(means, prodrate)
 	
 	# number of decimal places
 	sf = 3
 	
 	# prepare table for the web template
	outputs = []
	for i in range(len(names)):
		# build a dictionary (required by the template)
		o = {'name': names[i], 'lat': lats[i], 'lng': lngs[i], 'mean': round(means[i], sf), 
			'mad': round(mads[i], sf), 'age': round(ages[i], sf), 'errors': round(error[i], sf)}
		outputs.append(o)
	
	# lower precision for the chart
	ages2 = [round(i, 1) for i in ages]
	errors2 = [round(i, 1) for i in error]
	
	# prepare context to pass it to the template
	context = {'outputs': outputs, 'ages':str(ages2).replace(" ", "").replace("[", "").replace("]", ""), 'errors':str(errors2).replace(" ", "").replace("[", "").replace("]", "")}
	
	# render the template using the resulting data
	return render(request, 'shedcalc/results.html', context)
	

def chart(request):

	# one sigma (68%)
	alpha = 0.32
	twoSigma = 0.05
	
	# calibration curve data (R)
	x = np.array([39.4,49.0,47.5,39.6,36.7,39.2,41.8,42.5,42.5,26.5,30.7,27.9,31.0,41.1,41.7,40.4,45.7,41.4,41.7,45.4,43.3,39.7,35.8,38.9,28.9,34.5,35.1,35.2,39.6,36.3,36.0,59.5,63.0,58.1,63.7,60.8,47.2,46.5,42.9,45.3,46.5,44.8,27.2,30.2,29.5,25.6,28.0,30.3,28.7,29.0,28.8,33.1,38.923,37.835])
	# errors
	xu = np.array([0.9,0.9,1.2,1.3,1.0,0.8,1.3,1.2,0.8,0.9,1.6,1.2,1.1,1.0,0.6,0.7,0.8,0.6,1.1,0.8,0.7,0.8,0.5,0.7,0.5,0.6,0.7,0.6,0.8,0.8,0.6,0.7,0.7,0.5,0.6,0.6,0.5,0.5,0.6,0.5,0.5,0.5,1.1,1.1,1.4,0.9,1.3,1.2,0.5,0.7,1.1,1.3,1.3,1.2])

	# TODO: Change these based upon production rate (need to interactively update chart)
	y = np.array([15.931,13.053,13.433,14.102,13.682,15.082,13.249,14.174,12.582,22.416,19.771,20.161,22.151,15.228,14.872,15.58,11.813,12.661,12.125,12.769,13.403,17.051,19.260,16.397,20.928,15.853,14.225,16.648,16.755,15.127,16.025,2.789,1.656,5.53,0.869,2.413,11.154,11.344,12.658,11.558,11.321,12.04,21.934,21.397,21.501,23.796,21.929,22.314,22.745,22.897,20.955,18.222,15.838,16.67]) 
	yu = np.array([0.798,0.701,0.718,1.043,0.734,0.798,0.709,0.777,0.657,1.313,2.483,2.119,2.724,1.899,0.718,1.062,0.87,0.825,0.782,0.9,0.853,1.011,1.128,0.983,1.198,1.135,1.17,1.631,1.123,1.322,1.148,0.359,0.188,0.463,0.144,0.292,0.561,0.57,0.65,0.596,0.571,0.612,1.431,1.511,1.675,1.738,1.788,1.781,1.356,1.158,1.341,1.121,0.936,0.954])
	
	# select ages based on selected production rate
# 	if prodrate = 0:	# Loch Lomond
# 		y = np.array([15.931,13.053,13.433,14.102,13.682,15.082,13.249,14.174,12.582,22.416,19.771,20.161,22.151,15.228,14.872,15.58,11.813,12.661,12.125,12.769,13.403,17.051,19.260,16.397,20.928,15.853,14.225,16.648,16.755,15.127,16.025,2.789,1.656,5.53,0.869,2.413,11.154,11.344,12.658,11.558,11.321,12.04,21.934,21.397,21.501,23.796,21.929,22.314,22.745,22.897,20.955,18.222,15.838,16.67]) 
# 		yu = np.array([0.798,0.701,0.718,1.043,0.734,0.798,0.709,0.777,0.657,1.313,2.483,2.119,2.724,1.899,0.718,1.062,0.87,0.825,0.782,0.9,0.853,1.011,1.128,0.983,1.198,1.135,1.17,1.631,1.123,1.322,1.148,0.359,0.188,0.463,0.144,0.292,0.561,0.57,0.65,0.596,0.571,0.612,1.431,1.511,1.675,1.738,1.788,1.781,1.356,1.158,1.341,1.121,0.936,0.954])
# 	elif prodrate = 1:	# Glen Roy
# 		y = np.array([14.864,12.178,12.532,13.156,12.764,14.071,12.361,13.224,11.737,20.914,18.448,18.811,20.668,14.212,13.879,14.539,11.027,11.818,11.318,11.918,12.51,15.913,18.96821516,15.302,19.528,14.793,13.273,15.535,15.634,14.115,14.955,2.602,1.545,5.16,0.811,2.252,10.409,10.586,11.812,10.786,10.565,11.235,20.467,19.966,20.063,22.204,20.462,20.822,21.223,21.366,19.555,17.005,14.781,15.557]) 
# 		yu = np.array([0.818,0.71,0.728,1.018,0.744,0.811,0.719,0.785,0.668,1.314,2.354,2.022,2.584,1.801,0.741,1.045,0.85,0.816,0.774,0.883,0.845,1.01,1.135,0.981,1.203,1.112,1.132,1.563,1.106,1.274,1.124,0.34,0.179,0.448,0.136,0.277,0.575,0.584,0.663,0.608,0.584,0.625,1.415,1.482,1.628,1.699,1.732,1.728,1.354,1.185,1.328,1.116,0.936,0.958])
# 	elif prodrate = 2:	# CRONUS-calc default
# 		y = np.array([16.040,13.143,13.525,14.199,13.776,15.186,13.341,14.272,12.668,22.570,19.907,20.299,22.303,15.333,14.973,15.687,11.894,12.748,12.208,12.856,13.495,17.168,20.156,16.510,21.072,15.961,14.322,16.762,16.869,15.231,16.135,2.808,1.667,5.568,0.875,2.430,11.230,11.422,12.745,11.638,11.398,12.122,22.084,21.544,21.648,23.959,22.079,22.467,22.902,23.054,21.099,18.347,15.946,16.784]) 
# 		yu = np.array([1.539,1.286,1.322,1.566,1.348,1.480,1.304,1.406,1.229,2.274,2.985,2.705,3.296,2.287,1.423,1.671,1.309,1.333,1.271,1.388,1.398,1.735,2.004,1.675,2.107,1.736,1.661,2.140,1.785,1.823,1.755,0.428,0.233,0.651,0.162,0.354,1.078,1.096,1.231,1.125,1.095,1.167,2.314,2.331,2.448,2.632,2.553,2.571,2.322,2.221,2.194,1.880,1.610,1.676])
	
	# number of samples
	n = len(x)				   
	
	# intermediate values used later (sum(x^2) - sum(x)^2 / n)
	Sxx = np.sum(x**2) - np.sum(x)**2 / n
	Sxy = np.sum(x*y) - np.sum(x) * np.sum(y) / n	 
	
	# r squared value
	r2 = ((n * np.sum(x*y) - np.sum(x) * np.sum(y))**2) / ((n * np.sum(x**2) - np.sum(x)**2) * (n * np.sum(y**2) - np.sum(y)**2))
	
	# mean for each array
	mean_x = np.mean(x)
	mean_y = np.mean(y)

	# line fit
	b = Sxy / Sxx
	a = mean_y - b * mean_x
	
	# fit function
	fit = lambda xx: a + b * xx 
	
	# residuals
	residuals = y - fit(x)
	
	# variation of the residuals
	var_res = np.sum(residuals**2)/(n - 2)
	
	# standard deviation of the residuals
	sd_res = np.sqrt(var_res)
	
	# standard errors for the line fit
	se_b = sd_res / np.sqrt(Sxx)
	se_a = sd_res * np.sqrt(np.sum(x**2) / (n*Sxx))
	
	# degrees of freedom
	df = n - 2
	
	# appropriate t value						
	tval = stats.t.isf(alpha / 2., df)	
	
	# confidence intervals
	ci_a = a + tval * se_a * np.array([-1,1])
	ci_b = b + tval * se_b * np.array([-1,1])
	
	# standard error functions
	se_fit	   = lambda x: sd_res * np.sqrt(	1. / n + (x-mean_x)**2 / Sxx)
	se_predict = lambda x: sd_res * np.sqrt(1 + 1. / n + (x-mean_x)**2 / Sxx)
	
	# create a figure to draw on and add a subplot
	fig = Figure()
	ax = fig.add_subplot(1,1,1)
	
	# set axis limit to stop y axis going to -5...
	ax.set_ylim(0, 25)
	
	# regression line
	npts = 100
	px = np.linspace(np.min(x),np.max(x),num=npts)
	ax.plot(px, fit(px),'#EC472F', label='OLS Regression line')
	
	# points and error bars
	ax.plot(x,y,'k.', label='Age Control Points', markersize=3.5)
	ax.errorbar(x, y, ecolor='k', xerr=xu, yerr=yu, fmt=" ", linewidth=0.5, capsize=0)
	
	# prediction limit lines
	x.sort()
	limit = (1-alpha)*100
	ax.plot(x, fit(x)+tval*se_predict(x), '#0076D4', dashes=[9, 4.5], label='1 Sigma Prediction limit ({0:.1f}%)'.format(limit), linewidth=0.8)
	ax.plot(x, fit(x)-tval*se_predict(x), '#0076D4', dashes=[9, 4.5], linewidth=0.8)
	
	# same for 2 sigma...
	limit = (1-twoSigma)*100
	tval2 = stats.t.isf(twoSigma / 2., df)
	ax.plot(x, fit(x)+tval2*se_predict(x), '0.5', dashes=[9, 3], label='2 Sigma Prediction Limit ({0:.1f}%)'.format(limit), linewidth=0.5)
	ax.plot(x, fit(x)-tval2*se_predict(x), '0.5', dashes=[9, 3], linewidth=0.5)

	# labels etc
	ax.set_xlabel('Mean R-Value')
	ax.set_ylabel('Age (ka)')
	ax.set_title('Linear regression and confidence limits')
	
	# configure legend
	ax.legend(bbox_to_anchor=(0.99, 0.99), borderaxespad=0., frameon=False)
	
	# add r2 text box
	textstr = '$R^2=%.2f%sp<%.2f$'%(r2, ", ", 0.01)
	ax.text(0.03, 0.03, textstr, transform=ax.transAxes, fontsize=10)

	# encode to send to browser
	canvas=FigureCanvas(fig)
	response=http.HttpResponse(content_type='image/png')
	canvas.print_png(response)
	return response
	

def samples_chart(request):
	
	# get sample numbers
	ages = [float(x) for x in request.GET['a'].split(",")]
	errors = [float(x) for x in request.GET['e'].split(",")]
	x = range(1, len(ages)+1)

 	# create a figure to draw on and add a subplot
	fig = Figure()
	ax = fig.add_subplot(1,1,1)
	
	# set axis limit to stop y axis going to -5...
	ax.set_ylim(0, 25)
	
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