# -*- coding: utf-8 -*-

from django import http
from scipy.stats import t
from math import log10
import matplotlib.pyplot as plt
from numpy import zeros, array, sqrt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

'''
# If it whinges about matplotlib, do this:
# Create a file ~/.matplotlib/matplotlibrc there and add the following code:
	backend: TkAgg

# needed to undo this for Python 3
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


def prediction_interval(func, dfdp, x, y, yerr, signif, popt, pcov):
	"""
	* Calculate Preduction Intervals
	*
	*  func    : function that we are using
	*  dfdp    : derivatives of that function (calculated using sympy.diff)
	*  x       : the x values (calculated using numpy.linspace)
	*  y       : the y values (calculated by passing the ODR parameters and x to func)
	*  y_err   : the maximum residual on the y axis
	*  signif  : the significance value (68., 95. and 99.7 for 1, 2 and 3 sigma respectively)
	*  popt    : the ODR parameters for the fit, calculated using scipy.odr.run()
	*  pcov    : the covariance matrix for the fit, calculated using scipy.odr.run()
	"""
	# get number of fit parameters and data points
	np = len(popt)
	n = len(x)

	# convert provided value to a significance level (e.g. 95. -> 0.05), then calculate alpha
	alpha = 1. - (1 - signif / 100.0) / 2

	# students t test
	tval = t.ppf(alpha, n - np)

	# ?? some sort of processing of covarianvce matrix and derivatives...
	d = zeros(n)
	for j in range(np):
	    for k in range(np):
	        d += dfdp[j] * dfdp[k] * pcov[j,k]

	# return prediction band offset for a new measurement
	return tval * sqrt(yerr**2 + d)


def getAges(coefficients, x_data):
	"""
	return the predicted ages and errors
	"""

	# for linear models
	if coefficients['model'] == "linear":

		# predict age and 1-sigma (.68) prediction interval using model coefficients
		y_predictions =  array([ linear_func(coefficients['beta'], x) for x in x_data ])
		y_pi = prediction_interval(linear_func, [x_data, 1], x_data, y_predictions,
			coefficients['eps'], 68., coefficients['beta'], coefficients['cov'])

	# for logarithmic models
	elif coefficients['model'] == "log":

		# predict age and 1-sigma (.68) prediction interval using model coefficients
		y_predictions = array([ log_func(coefficients['beta'], x) for x in x_data ])
		y_pi = prediction_interval(log_func, [log10(x_data), 1], x_data, y_predictions,
			coefficients['eps'], 68., coefficients['beta'], coefficients['cov'])

	return y_predictions, y_pi
