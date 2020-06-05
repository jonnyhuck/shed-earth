# -*- coding: utf-8 -*-

from django import http
from scipy.stats import t
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
<<<<<<< HEAD
from numpy import zeros, ones, array, sqrt, log10
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
=======
from django import http
from math import log10
import pandas as pd

>>>>>>> 4b5398d6b512323ecac2ce03f4dde6ce2193887b

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
<<<<<<< HEAD
	"""
	return v / r
=======
>>>>>>> 4b5398d6b512323ecac2ce03f4dde6ce2193887b

        Update by MT 10/04/2020, if their input r value is within the uncertainty bounds,
        e.g. 47.8 > 48.08 - 0.82, then no correction is made.

        Before, we would apply a correction (in this case) of 0.99417637 (negligible)

        Given the uncertainty of the technique (e.g. surface weathering, moisture),
        this is probably a more sensible approach.
        
	"""
	# Sets errors (v_err), based on Table in shedcalc/templates/shedcalc/index.html
        if v = 48.08:
                v_err = 0.82
        if v = 52.60:
                v_err = 0.74         
        if v = 44.14:
                v_err = 0.60
        if v = 48.67:
                v_err = 0.65

	
	if r < v-v_err or r > v+v_err:
                return v/r
        else:
                return 1


def getCalibratedValues(data, v, v_err, r):
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

<<<<<<< HEAD
=======
	# one sigma (68%)
	alpha = 0.32

	# Loads calibration data from Supplementary File (update file path), and subsets to Pyrenees only
        df = pd.read_csv("./data/Calibration_Summary.csv")
        df = data.loc[(data['Region'] == 'British')]

        # load calibration data for curve creation
        x = df.loc[:, 'SH_Mean'].values

        if prodrate == 0:	# Default, Balco calculator
		y = df.loc[:, 'Balco_Age'].values
	elif prodrate == 1:	# Next, CRONUS v2
		y = df.loc[:, 'CRONUS_Age'].values
	elif prodrate == 2:	# Loch Lomond
		y = df.loc[:, 'Lomond_Age'].values 
	elif prodrate == 3:	# Rannoch Moor
		y = df.loc[:, 'Rannoch_Age'].values
	elif prodrate == 4:     # Glen Roy
               y = df.loc{:, 'Roy_Age'].values
               

        '''
        Original version of code

	# calibration curve data
	x = np.array([39.406,49.014,47.516,39.570,36.732,39.247,41.792,42.547,42.490,26.529,30.672,27.876,30.999,41.083,41.672,40.386,45.705,41.387,41.689,45.398,43.304,39.669,35.844,38.867,28.850,34.470,35.130,35.160,39.570,36.310,36.000,59.499,63.003,58.122,63.692,60.791,47.246,46.481,42.943,45.285,46.525,44.757,27.233,30.233,29.533,25.567,28.033,30.267,28.712,29.015,28.811,33.083,38.923,37.835,46.589,47.086,44.401,40.961,44.665,45.471,42.889,40.007,43.644,42.138,40.656])

	# (ages based upon selected production rate)
	if prodrate == 0:	# Rannoch Moor
		y = np.array([16.241,13.322,13.706,14.383,13.956,15.378,13.522,14.458,12.843,22.781,20.086,20.482,22.5,15.479,15.117,15.841,11.992,12.855,12.31,12.965,13.61,17.345,19.260,16.687,21.278,16.141,14.488,16.933,17.045,15.395,16.3,2.838,1.685,5.642,0.885,2.457,11.356,11.55,12.882,11.767,11.525,12.254,22.282,21.736,21.841,24.169,22.275,22.667,23.201,23.348,21.284,18.509,16.076,16.919,11.518,9.489,11.729,14.004,13.796,13.438,16.153,15.632,15.011,12.937,14.638])
	elif prodrate == 1:	# Glen Roy
		y = np.array([15.279,12.536,12.896,13.533,13.132,14.469,12.723,13.603,12.086,21.431,18.897,19.268,21.167,14.563,14.222,14.904,11.282,12.093,11.581,12.197,12.804,16.322,19.146,15.702,20.021,15.186,13.632,15.931,16.036,14.485,15.336,2.671,1.585,5.308,0.831,2.313,10.685,10.867,12.121,11.072,10.844,11.531,20.961,20.448,20.547,22.737,20.955,21.323,21.833,21.972,20.023,17.415,15.126,15.919,10.842,8.918,11.04,13.176,12.981,12.644,15.196,14.708,14.124,12.174,13.773])
	elif prodrate == 2:	# CRONUS-calc
		y = np.array([15.268,12.527,12.887,13.524,13.123,14.458,12.714,13.594,12.078,21.416,18.884,19.255,21.152,14.553,14.212,14.893,11.274,12.085,11.573,12.188,12.795,16.31,19.260,15.691,20.007,15.175,13.623,15.92,16.025,14.474,15.325,2.669,1.584,5.304,0.83,2.311,10.678,10.859,12.113,11.064,10.837,11.523,20.946,20.433,20.532,22.721,20.941,21.308,21.818,21.956,20.009,17.402,15.115,15.908,10.834,8.911,11.033,13.167,12.972,12.635,15.185,14.698,14.114,12.165,13.763])
	elif prodrate == 3:	# Loch Lomond
		y = np.array([16.069,13.18,13.561,14.23,13.809,15.215,13.378,14.304,12.707,22.539,19.873,20.264,22.261,15.314,14.956,15.673,11.864,12.718,12.179,12.827,13.465,17.162,19.260,16.51,21.052,15.969,14.334,16.753,16.864,15.231,16.127,2.808,1.667,5.583,0.876,2.431,11.236,11.427,12.745,11.642,11.403,12.124,22.045,21.504,21.609,23.912,22.039,22.426,22.955,23.101,21.058,18.313,15.906,16.74,11.397,9.389,11.606,13.855,13.65,13.295,15.981,15.466,14.852,12.8,14.483])
        

        '''

	# number of samples
	n = len(x)

	# intermediate values used later (sum(x^2) - sum(x)^2 / n)
	Sxx = np.sum(x**2) - np.sum(x)**2 / n
	Sxy = np.sum(x*y) - np.sum(x) * np.sum(y) / n

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
>>>>>>> 4b5398d6b512323ecac2ce03f4dde6ce2193887b

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

<<<<<<< HEAD
	# convert provided value to a significance level (e.g. 95. -> 0.05), then calculate alpha
	alpha = 1. - (1 - signif / 100.0) / 2
=======
	# one sigma (68%)
	alpha = 0.32

	
        # Loads calibration data from Supplementary File (update file path), and subsets to Pyrenees only
        df = pd.read_csv("./data/Calibration_Summary.csv")
        df = data.loc[(data['Region'] == 'Pyrenees')]

        # load calibration data for curve creation
        x = df.loc[:, 'SH_Mean'].values

        if prodrate == 0:	# Default, Balco calculator
		y = df.loc[:, 'Balco_Age'].values
	elif prodrate == 1:	# Next, CRONUS v2
		y = df.loc[:, 'CRONUS_Age'].values
	elif prodrate == 2:	# Loch Lomond
		y = df.loc[:, 'Lomond_Age'].values 
	elif prodrate == 3:	# Rannoch Moor
		y = df.loc[:, 'Rannoch_Age'].values
	elif prodrate == 4:     # Glen Roy
               y = df.loc{:, 'Roy_Age'].values

        '''

	Original version of code.

	# calibration curve data
	x = np.array([54.034,57.601,61.934,59.234,51.135,57.802,49.502,48.602,47.202,46.603,46.904,51.638,55.372,51.905,53.072,42.904,42.705,39.971,39.671,38.905,52.140,49.506,53.507,41.950,23.409,26.477,25.811,40.584,45.152,45.820,45.820,41.585,40.084,45.487,40.318,38.451,45.488,42.920,46.755,45.955,48.857,47.223,51.025,47.790,48.224,50.092,48.124,49.258,47.524,48.836,59.836,49.603])

	if prodrate == 0:	# Rannoch Moor
		y = np.array([14.229,12.890,4.307,5.492,12.112,8.966,14.282,14.076,15.285,16.247,16.623,12.531,9.094,12.658,12.192,22.051,21.849,23.312,23.963,24.879,11.581,12.604,12.584,22.183,54.666,46.158,44.653,21.503,18.041,18.236,18.270,22.021,24.529,19.932,23.230,26.469,19.076,20.619,19.321,19.834,17.684,17.377,15.968,17.741,17.860,17.509,17.460,16.134,18.385,18.131,9.438,18.864])
	elif prodrate == 1:	# Glen Roy
		y = np.array([13.435,12.211,4.044,5.151,11.485,8.318,13.483,13.289,14.424,15.298,15.658,11.869,8.439,11.988,11.556,20.834,20.637,21.982,22.585,23.456,10.934,11.944,11.925,20.957,51.02,43.339,42.005,20.308,17.007,17.187,17.218,20.812,23.124,18.801,21.915,24.959,17.982,19.455,18.218,18.709,16.663,16.373,15.05,16.719,16.835,16.495,16.45,15.191,17.325,17.087,8.822,17.778])
	elif prodrate == 2:	# CRONUS-calc default
		y = np.array([12.866,12.436,4.138,5.285,11.740,8.944,13.828,13.600,14.761,15.644,15.982,12.130,8.714,12.178,11.783,20.982,20.609,22.634,23.234,23.858,10.967,11.988,11.987,21.307,51.862,43.874,42.212,20.431,17.226,17.374,17.453,20.949,22.503,18.887,22.052,24.974,18.005,19.417,18.157,18.720,16.550,16.414,15.022,16.475,16.699,16.452,16.406,15.151,17.410,16.924,8.673,17.910])
	elif prodrate == 3:	# Loch Lomond
		y = np.array([14.081,12.77,4.261,5.434,12.001,8.847,14.132,13.932,15.129,16.078,16.451,12.41,8.974,12.538,12.078,21.833,21.634,23.07,23.718,24.625,11.471,12.485,12.464,21.962,54.042,45.62,44.173,21.292,17.855,18.047,18.08,21.805,24.276,19.73,22.99,26.2,18.882,20.412,19.123,19.634,17.501,17.2,15.8,17.556,17.675,17.33,17.282,15.958,18.194,17.942,9.34,18.67])

        '''

	# log the R values
	x = np.array([log10(i) for i in x])
>>>>>>> 4b5398d6b512323ecac2ce03f4dde6ce2193887b

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
