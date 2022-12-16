# -*- coding: utf-8 -*-

# from django import http
from scipy.stats import t
# import matplotlib.pyplot as plt
# from matplotlib.figure import Figure
from numpy import zeros, ones, sqrt, log10
# from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

'''
# If it whinges about matplotlib, do this:
# Create a file ~/.matplotlib/matplotlibrc there and add the following line:
	backend: TkAgg

# if the file exists already, it might be that you need to remove it...
'''

def parseInputTable(input):
	"""
	read table of tab-delimited data into lists (one per column)
	"""

	# init lists
	names = []
	lats = []
	lngs = []
	rValues = []

	# split into lines and loop through them
	for line in input.splitlines():

		# extract the tab separated data
		data = line.strip().split("\t")

		# clip off the first three cols
		names.append(data.pop(0))
		lats.append(float(data.pop(0)))
		lngs.append(float(data.pop(0)))

		# convert the rest to floats
		rValues.append([float(d) for d in data])

	# make list of lists and return
	return names, lats, lngs, rValues


def getNumberCells(textAreaData):
	"""
	for incoming data from textarea count cells
	"""
	nCells = 0
	for row in textAreaData:
		nCells += len(row)
	return nCells


def getDriftFactor(before, after, textAreaData):
	"""
	return rValueDiff / number of data cells
	"""
	return before / after * 100 - 100


def applyDriftFactorToCells(driftFactor, cells):
	"""
	Apply the correction (drift) factor to each cell
	"""
	correctedCells = []
	nCells = getNumberCells(cells)
	f = driftFactor / nCells
	i = 1
	for r in cells:
		tmp = []
		for d in r:
			tmp.append((d / 100) * (100 + (f * i)))
			i += 1
		correctedCells.append(tmp)
	return correctedCells


def getRowMean(row):
	"""
	Get the mean of each row (sample)
	"""
	return sum(row)/len(row)


def getRowMAD(row):
	"""
	Calculate the MAD of each row (sample)

	Find the sum of the data values, and divide the sum by the number of data values.
	Find the absolute value of the difference between each data value and the mean: |data value – mean|.
	Divide the sum of the absolute values of the differences by the number of data values.
	"""
	m = getRowMean(row)
	absDiff = [abs(v - m) for v in row]
	return sum(absDiff) / len(row)


def getAgeCalibration(v, r):
	"""
	r - their input r value
	v - hardness value derived from the boulder - from database (c. 48 for ours, 15 for Mars)
	"""
	return v / r


def getCalibratedValues(data, v, r):
	"""
	multiply means by age calibration
	"""
	# calculate age calibration
	ac = getAgeCalibration(v, r)

	# apply to each cell in the nested list
	return [[d * ac for d in r] for r in data]


def log_func(beta, x):
	"""
	* Log function for fitting using ODR coefficients
	"""
	# logarithmic, m * log(x) + c
	return beta[0] * log10(x) + beta[1]


def linear_func(beta, x):
	"""
	* Linear function for fitting using ODR coefficients
	"""
	# linear, m * x + c
	return beta[0] * x + beta[1]


def prediction_interval(dfdp, n, xn, yerr, signif, popt, pcov):
	"""
	* Calculate Preduction Intervals
	*
	*  dfdp    : derivatives of that function (calculated using sympy.diff)
	*  n       : the number of samples in the original curve
	*  xn	   : the number of preductions being undertaken here
	*  y_err   : the maximum residual on the y axis
	*  signif  : the significance value (68., 95. and 99.7 for 1, 2 and 3 sigma respectively)
	*  popt    : the ODR parameters for the fit, calculated using scipy.odr.run()
	*  pcov    : the covariance matrix for the fit, calculated using scipy.odr.run()
	*
	* based on p.147 of Mathematical, Numerical, and Statistical Methods in Extraterrestrial Physics
	"""
	# get number of fit parameters and data points
	np = len(popt)

	# convert provided value to a significance level (e.g. 95. -> 0.05), then calculate alpha
	alpha = 1. - (1 - signif / 100.0) / 2

	# students t test
	tval = t.ppf(alpha, n - np)

	# ?? some sort of processing of covarianvce matrix and derivatives...
	d = zeros(xn)
	for j in range(np):
	    for k in range(np):
	        d += dfdp[j] * dfdp[k] * pcov[j,k]

	# return prediction band offset for a new measurement
	return tval * sqrt(yerr**2 + d)


def getAges(coefficients, x_data):
	"""
	return the predicted ages and errors
	"""

	# set function and derivatives for linear models
	if coefficients['model'] == "linear":
		f = linear_func
		d = [x_data, ones(len(x_data))]

	# set function and derivatives for logarithmic models
	elif coefficients['model'] == "log":
		f = log_func
		d = [log10(x_data), ones(len(x_data))]

	# predict age and 1-sigma (.68) prediction interval using model coefficients
	y_predictions = f(coefficients['beta'], x_data)
	y_pi = prediction_interval(d, coefficients['samples'], len(x_data), coefficients['eps'], 68., coefficients['beta'], coefficients['cov'])

	# return predictions and 1 sigma confidence
	return y_predictions, y_pi
