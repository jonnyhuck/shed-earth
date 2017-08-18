from django.shortcuts import render
from schmidt import *

# Create your views here.

from django.http import HttpResponse
from django.template import loader
from math import ceil, log10

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
	

def chartGB(request):
	"""
	Draw the calibration curve chart
	"""

	# one sigma (68%)
	alpha = 0.32
	twoSigma = 0.05
	
	# calibration curve data (R)
	x = np.array([39.4,49.0,47.5,39.6,36.7,39.2,41.8,42.5,42.5,26.5,30.7,27.9,31.0,41.1,41.7,40.4,45.7,41.4,41.7,45.4,43.3,39.7,35.8,38.9,28.9,34.5,35.1,35.2,39.6,36.3,36.0,59.5,63.0,58.1,63.7,60.8,47.2,46.5,42.9,45.3,46.5,44.8,27.2,30.2,29.5,25.6,28.0,30.3,28.7,29.0,28.8,33.1,38.923,37.835])
	# errors
	xu = np.array([0.9,0.9,1.2,1.3,1.0,0.8,1.3,1.2,0.8,0.9,1.6,1.2,1.1,1.0,0.6,0.7,0.8,0.6,1.1,0.8,0.7,0.8,0.5,0.7,0.5,0.6,0.7,0.6,0.8,0.8,0.6,0.7,0.7,0.5,0.6,0.6,0.5,0.5,0.6,0.5,0.5,0.5,1.1,1.1,1.4,0.9,1.3,1.2,0.5,0.7,1.1,1.3,1.3,1.2])

	##TODO: Implement prod rates for charts
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


def chartPY(request):
	"""
	Pyrenees Version
	Draw the calibration curve chart
	"""

	# one sigma (68%)
	alpha = 0.32
	twoSigma = 0.05
	
	# calibration curve data
	x = np.array([54.03368396,57.60061836,61.93426224,59.23447584,51.13453623,57.80160755,49.50158588,48.60176758,47.20191692,46.60348264,46.90370451,51.63763229,55.37151306,51.90476614,53.07176254,42.90448686,42.70464598,39.97118604,39.67132362,38.90473325,52.13989717,49.50644397,53.50719023,41.95006324,23.4094335,26.47745241,25.8106217,40.5837167,45.15249304,45.81963775,45.81983488,41.58484362,40.08435908,45.48693888,40.31814028,38.45079804,45.48751973,42.91986244,46.75516721,45.95498962,48.85656394,47.22265643,51.02469707,47.79000009,48.22375316,50.09155454,48.12411378,49.2582244,47.5242191,48.83552464,59.83627399,49.60264646])
	xu = np.array([0.645869593,0.665147581,0.648418401,0.714722335,0.490293873,0.725331844,1.042209979,1.177283522,0.908976054,0.891580024,0.939696778,0.953075818,0.763677444,0.901427086,0.991038844,0.985777934,1.068574197,0.94109697,0.857469191,0.937315548,1.407951895,1.379417818,1.089255257,1.210419739,0.981734516,1.02052971,1.120091825,1.05555926,0.923392934,0.975714666,1.022411485,1.195092,1.030766439,1.215914789,1.100409312,1.148509823,1.051330926,1.444023663,1.263841747,1.339882882,1.068896815,0.682011595,1.011947715,1.09061688,1.216596025,0.817869802,1.087150282,0.761308491,1.050322726,0.824627945,0.741903071,0.870915363])

	##TODO: Implement prod rates for charts

	# according to production rate
# 	if prodrate == 0:	# Loch Lomond
# 		y = np.array([13.577,12.203,4.106,5.171,11.351,8.179,13.634,13.446,14.645,15.582,15.945,11.856,8.319,11.99,11.488,21.303,21.115,22.541,23.171,24.058,10.778,11.891,11.866,21.446,50.732,43.619,42.31,20.697,17.277,17.464,17.496,21.226,23.656,19.104,22.389,25.521,18.254,19.775,18.493,18.999,16.908,16.614,15.27,16.963,17.077,16.762,16.714,15.438,17.633,17.458,8.738,18.125]) 
# 		yu = np.array([0.773,0.663,0.228,0.303,0.619,0.562,0.844,1.37,1.18,1.17,1.056,0.838,0.62,1.217,0.988,3.752,3.118,3.087,3.697,3.067,1.824,1.56,2.734,4.476,2.634,2.266,2.195,1.111,0.914,0.948,0.965,1.127,1.251,1,1.854,1.329,0.959,1.032,0.965,0.993,0.889,0.877,0.802,0.895,0.887,2.547,2.437,2.59,2.127,2.59,1.841,4.685])
# 	elif prodrate == 1:	# Glen Roy
# 		y = np.array([12.666,11.37,3.842,4.828,10.583,7.617,12.72,12.543,13.675,14.56,14.902,11.052,7.75,11.175,10.713,19.907,19.729,21.075,21.669,22.502,10.05,11.083,11.058,20.041,47.188,40.813,39.605,19.339,16.151,16.325,16.354,19.836,22.131,17.85,20.936,23.863,17.061,18.477,17.283,17.753,15.807,15.531,14.267,15.859,15.966,15.669,15.624,14.425,16.482,16.316,8.142,16.939]) 
# 		yu = np.array([0.776,0.669,0.231,0.303,0.625,0.552,0.839,1.309,1.145,1.142,1.043,0.821,0.604,1.162,0.952,3.535,2.947,2.925,3.492,2.913,1.716,1.476,2.56,4.207,2.678,2.317,2.245,1.127,0.93,0.961,0.976,1.146,1.274,1.019,1.798,1.356,0.977,1.052,0.984,1.012,0.905,0.893,0.817,0.911,0.906,2.407,2.305,2.442,2.023,2.448,1.725,4.395])
# 	elif prodrate == 2:	# CRONUS-calc default
	y = np.array([13.67,12.288,4.134,5.205,11.43,8.236,13.727,13.538,14.744,15.687,16.052,11.94,8.377,12.074,11.568,21.445,21.256,22.691,23.324,24.219,10.852,11.974,11.95,21.589,51.107,43.909,42.589,20.836,17.393,17.581,17.613,21.368,23.812,19.232,22.536,25.692,18.377,19.908,18.617,19.127,17.021,16.724,15.372,17.077,17.191,16.874,16.826,15.542,17.752,17.575,8.8,18.247]) 
	yu = np.array([1.362,1.206,0.408,0.523,1.123,0.879,1.408,1.769,1.693,1.742,1.69,1.291,0.927,1.573,1.372,4.166,3.59,3.622,4.185,3.672,2.039,1.852,2.922,4.842,4.985,4.278,4.147,2.041,1.696,1.727,1.739,2.087,2.324,1.869,2.626,2.497,1.788,1.934,1.808,1.859,1.656,1.629,1.495,1.663,1.667,2.912,2.814,2.901,2.588,2.978,1.988,4.948])
	
	# log the R values
	x2 = x
	x = np.array([log10(i) for i in x])
	
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
	
	# calculate y limit
	ymax =  int((5 * ceil((max(y) + max(yu))/5)))
	
	# set axis limit to stop y axis going to -5...
	ax.set_ylim(0, ymax)
	
	### regression line ###
	
	# 100 points evenly spaced between the min and max LOGGED x values 
	npts = 100
	px = np.linspace(np.min(x),np.max(x),num=npts) # get 100 points along the line
	
	# plot y calculated from px against de-logged x
	ax.plot(10**px, fit(px),'#EC472F', label='OLS Regression line')
	
	### sigma lines line ###
	
	# 1 sigma
	x.sort()
	limit = (1-alpha)*100
	ax.plot(10**px, fit(px)+tval*se_predict(px), '#0076D4', dashes=[9, 4.5], label='1 Sigma Prediction limit ({0:.1f}%)'.format(limit), linewidth=0.8)
	ax.plot(10**px, fit(px)-tval*se_predict(px), '#0076D4', dashes=[9, 4.5], linewidth=0.8)
	
	# same for 2 sigma...
	limit = (1-twoSigma)*100
	tval2 = stats.t.isf(twoSigma / 2., df)
	ax.plot(10**px, fit(px)+tval2*se_predict(px), '0.5', dashes=[9, 3], label='2 Sigma Prediction Limit ({0:.1f}%)'.format(limit), linewidth=0.5)
	ax.plot(10**px, fit(px)-tval2*se_predict(px), '0.5', dashes=[9, 3], linewidth=0.5)

	### points ###
	
	# points and error bars
	ax.plot(x2,y,'k.', label='Age Control Points', markersize=3.5)
	ax.errorbar(x2, y, ecolor='k', xerr=xu, yerr=yu, fmt=" ", linewidth=0.5, capsize=0)

	### decorations ###

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