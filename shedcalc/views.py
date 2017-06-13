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
 	
 	# calculate the ages and errors
 	ages, error = fitLine(means)
 	
 	# number of decimal places
 	sf = 3
 	
 	# prepare table for the web template
	outputs = []
	for i in range(len(names)):
		# build a dictionary (required by the template)
		o = {'name': names[i], 'lat': lats[i], 'lng': lngs[i], 'mean': round(means[i], sf), 
			'mad': round(mads[i], sf), 'age': round(ages[i], sf), 'errors': round(error[i], sf)}
		outputs.append(o)

	
	# prepare context to pass it to the template
	context = {'outputs': outputs}
	
	# render the template using the resulting data
	return render(request, 'shedcalc/results.html', context)
	

def chart(request):

	# one sigma (68%)
	alpha = 0.32
	twoSigma = 0.05
	
	# calibration curve data
	x = np.array([39.4,49.0,47.5,39.6,36.7,39.2,41.8,42.5,42.5,26.5,30.7,27.9,31.0,41.1,41.7,40.4,45.7,41.4,41.7,45.4,43.3,39.7,35.8,38.9,28.9,34.5,35.1,35.2,39.6,36.3,36.0,59.5,63.0,58.1,63.7,60.8,47.2,46.5,42.9,45.3,46.5,44.8,27.2,30.2,29.5,25.6,28.0,30.3,28.7,29.0,28.8,33.1])
	y = np.array([15.931,13.053,13.433,14.102,13.682,15.082,13.249,14.174,12.582,22.416,19.771,20.161,22.151,15.228,14.872,15.58,11.813,12.661,12.125,12.769,13.403,17.051,19.260,16.397,20.928,15.853,14.225,16.648,16.755,15.127,16.025,2.789,1.656,5.53,0.869,2.413,11.154,11.344,12.658,11.558,11.321,12.04,21.934,21.397,21.501,23.796,21.929,22.314,22.745,22.897,20.955,18.222]) 
	
	# errors
	xu = np.array([0.798,0.701,0.718,1.043,0.734,0.798,0.709,0.777,0.657,1.313,2.483,2.119,2.724,1.899,0.718,1.062,0.87,0.825,0.782,0.9,0.853,1.011,1.128,0.983,1.198,1.135,1.17,1.631,1.123,1.322,1.148,0.359,0.188,0.463,0.144,0.292,0.561,0.57,0.65,0.596,0.571,0.612,1.431,1.511,1.675,1.738,1.788,1.781,1.356,1.158,1.341,1.121])
	yu = np.array([0.9,0.9,1.2,1.3,1.0,0.8,1.3,1.2,0.8,0.9,1.6,1.2,1.1,1.0,0.6,0.7,0.8,0.6,1.1,0.8,0.7,0.8,0.5,0.7,0.5,0.6,0.7,0.6,0.8,0.8,0.6,0.7,0.7,0.5,0.6,0.6,0.5,0.5,0.6,0.5,0.5,0.5,1.1,1.1,1.4,0.9,1.3,1.2,0.5,0.7,1.1,1.3])
	
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
	ax.plot(x, fit(x)+tval*se_predict(x), '#0076D4', dashes=[3, 1.5], label='1 Sigma Prediction limit ({0:.1f}%)'.format(limit), linewidth=0.8)
	ax.plot(x, fit(x)-tval*se_predict(x), '#0076D4', dashes=[3, 1.5], linewidth=0.8)
	
	# same for 2 sigma...
	limit = (1-twoSigma)*100
	tval2 = stats.t.isf(twoSigma / 2., df)
	ax.plot(x, fit(x)+tval2*se_predict(x), '0.5', dashes=[3, 1], label='2 Sigma Prediction Limit ({0:.1f}%)'.format(limit), linewidth=0.5)
	ax.plot(x, fit(x)-tval2*se_predict(x), '0.5', dashes=[3, 1], linewidth=0.5)

	# labels etc
	ax.set_xlabel('Mean R-Value')
	ax.set_ylabel('Age (ka)')
	ax.set_title('Linear regression and confidence limits')
	
	# configure legend
	ax.legend(bbox_to_anchor=(0.99, 0.99), borderaxespad=0., frameon=False)
	
	# add r2 text box
	textstr = '$R^2=%.2f%sp<%.2f$'%(r2, ", ", 0.01)
	ax.text(0.03, 0.03, textstr, transform=ax.transAxes, fontsize=10)

	###EXPERIMENTAL
	# encode to send to browser
	canvas=FigureCanvas(fig)
	response=http.HttpResponse(content_type='image/png')
	canvas.print_png(response)
	return response