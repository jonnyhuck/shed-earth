# -*- coding: utf-8 -*-

# from scipy.stats import linregress, t
# from scipy.optimize import curve_fit
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from django import http
from math import log10

'''
# If it whinges about matplotlib, do this:
# Create a file ~/.matplotlib/matplotlibrc there and add the following code: backend: TkAgg
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
	return before/after*100-100


def applyDriftFactorToCells(driftFactor, cells):
	"""
	Apply the correction factor to each cell
	"""
	correctedCells = []
	nCells = getNumberCells(cells)
	f = driftFactor/nCells
	i = 1
	for r in cells:
		tmp = []
		for d in r: 
			tmp.append( (d / 100) * (100 + (f*i)) )
			i += 1
		correctedCells.append(tmp)	
	return correctedCells
	

def getRowMean(row):
	"""
	Get the mean of each column (sample)
	"""
	return sum(row)/len(row)
	
	
def getRowMAD(row):
	"""
	Calculate the MAD
		
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
	return v/r


def getCalibratedValues(data, v, r):
	"""
	multiply means by age calibration
	"""
# 	v = 48.08
	
	# calculate age calibration
	ac = getAgeCalibration(v, r)
	
	# apply to each cell in the nested list
	return [[d * ac for d in r] for r in data]


def fitLineGB(data, prodrate):
	"""
	* For Great Britain
	*
	* Fit a curve to the data using a least squares 1st order polynomial fit 
	* Based upon: 
	*	http://central.scipy.org/item/50/1/line-fit-with-confidence-interval
	*
	* Useful info on how it works can be found here:
	*	http://sciencefair.math.iit.edu/analysis/linereg/hand/
	*
	* TODO: Get rid of unused code (AFTER) the output image is done...
	* TODO: Add third return for plot image
	"""
	
	# one sigma (68%)
	alpha = 0.32
	
	# calibration curve data
	x = np.array([39.406,49.014,47.516,39.570,36.732,39.247,41.792,42.547,42.490,26.529,30.672,27.876,30.999,41.083,41.672,40.386,45.705,41.387,41.689,45.398,43.304,39.669,35.844,38.867,28.850,34.470,35.130,35.160,39.570,36.310,36.000,59.499,63.003,58.122,63.692,60.791,47.246,46.481,42.943,45.285,46.525,44.757,27.233,30.233,29.533,25.567,28.033,30.267,28.712,29.015,28.811,33.083,38.923,37.835,46.589,47.086,44.401,40.961,44.665,45.471,42.889,40.007,43.644,42.138,40.656])
	
	# (ages based upon selected production rate)
	if prodrate == 0:	# Rannoch Moor
		y = np.array([16.241,13.322,13.706,14.383,13.956,15.378,13.522,14.458,12.843,22.781,20.086,20.482,22.5,15.479,15.117,15.841,11.992,12.855,12.31,12.965,13.61,17.345,19.260,16.687,21.278,16.141,14.488,16.933,17.045,15.395,16.3,2.838,1.685,5.642,0.885,2.457,11.356,11.55,12.882,11.767,11.525,12.254,22.282,21.736,21.841,24.169,22.275,22.667,23.201,23.348,21.284,18.509,16.076,16.919,11.518,9.489,11.729,14.004,13.796,13.438,16.153,15.632,15.011,12.937,14.638]) 
	elif prodrate == 1:	# Glen Roy
		y = np.array([14.864,12.178,12.532,13.156,12.764,14.071,12.361,13.224,11.737,20.914,18.448,18.811,20.668,14.212,13.879,14.539,11.027,11.818,11.318,11.918,12.51,15.913,18.96821516,15.302,19.528,14.793,13.273,15.535,15.634,14.115,14.955,2.602,1.545,5.16,0.811,2.252,10.409,10.586,11.812,10.786,10.565,11.235,20.467,19.966,20.063,22.204,20.462,20.822,21.223,21.366,19.555,17.005,14.781,15.557]) 
	elif prodrate == 2:	# CRONUS-calc default
		y = np.array([15.268,12.527,12.887,13.524,13.123,14.458,12.714,13.594,12.078,21.416,18.884,19.255,21.152,14.553,14.212,14.893,11.274,12.085,11.573,12.188,12.795,16.31,19.260,15.691,20.007,15.175,13.623,15.92,16.025,14.474,15.325,2.669,1.584,5.304,0.83,2.311,10.678,10.859,12.113,11.064,10.837,11.523,20.946,20.433,20.532,22.721,20.941,21.308,21.818,21.956,20.009,17.402,15.115,15.908,10.834,8.911,11.033,13.167,12.972,12.635,15.185,14.698,14.114,12.165,13.763]) 
	
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
	
	# appropriate t value						
	tval = stats.t.isf(alpha / 2., df)	
	
	# confidence intervals
	ci_a = a + tval * se_a * np.array([-1,1])
	ci_b = b + tval * se_b * np.array([-1,1])
	
	# standard error functions
	se_fit	   = lambda x: sd_res * np.sqrt(	1. / n + (x-mean_x)**2 / Sxx)
	se_predict = lambda x: sd_res * np.sqrt(1 + 1. / n + (x-mean_x)**2 / Sxx)

	# calculate ages and uncertainty to return
	ages = []
	errors = []
	for d in data:
		age = fit(d)
		ages.append(age)
		errors.append(fit(d) + tval * se_predict(d) - age)
		
	return ages, errors
	

def fitLinePY(data, prodrate):
	"""
	* For the Pyrenees 
	*
	* Fit a curve to the data using a least squares 1st order polynomial fit 
	* Based upon: 
	*	http://central.scipy.org/item/50/1/line-fit-with-confidence-interval
	*
	* Useful info on how it works can be found here:
	*	http://sciencefair.math.iit.edu/analysis/linereg/hand/
	*
	* TODO: Get rid of unused code (AFTER) the output image is done...
	* TODO: Add third return for plot image
	"""
	
	# one sigma (68%)
	alpha = 0.32
	
	# calibration curve data
	x = np.array([54.034,57.601,61.934,59.234,51.135,57.802,49.502,48.602,47.202,46.603,46.904,51.638,55.372,51.905,53.072,42.904,42.705,39.971,39.671,38.905,52.140,49.506,53.507,41.950,23.409,26.477,25.811,40.584,45.152,45.820,45.820,41.585,40.084,45.487,40.318,38.451,45.488,42.920,46.755,45.955,48.857,47.223,51.025,47.790,48.224,50.092,48.124,49.258,47.524,48.836,59.836,49.603])
	
	if prodrate == 0:	# Rannoch Moor
		y = np.array([14.229,12.890,4.307,5.492,12.112,8.966,14.282,14.076,15.285,16.247,16.623,12.531,9.094,12.658,12.192,22.051,21.849,23.312,23.963,24.879,11.581,12.604,12.584,22.183,54.666,46.158,44.653,21.503,18.041,18.236,18.270,22.021,24.529,19.932,23.230,26.469,19.076,20.619,19.321,19.834,17.684,17.377,15.968,17.741,17.860,17.509,17.460,16.134,18.385,18.131,9.438,18.864]) 
	elif prodrate == 1:	# Glen Roy
		y = np.array([12.666,11.37,3.842,4.828,10.583,7.617,12.72,12.543,13.675,14.56,14.902,11.052,7.75,11.175,10.713,19.907,19.729,21.075,21.669,22.502,10.05,11.083,11.058,20.041,47.188,40.813,39.605,19.339,16.151,16.325,16.354,19.836,22.131,17.85,20.936,23.863,17.061,18.477,17.283,17.753,15.807,15.531,14.267,15.859,15.966,15.669,15.624,14.425,16.482,16.316,8.142,16.939]) 
	elif prodrate == 2:	# CRONUS-calc default
		y = np.array([12.866,12.436,4.138,5.285,11.740,8.944,13.828,13.600,14.761,15.644,15.982,12.130,8.714,12.178,11.783,20.982,20.609,22.634,23.234,23.858,10.967,11.988,11.987,21.307,51.862,43.874,42.212,20.431,17.226,17.374,17.453,20.949,22.503,18.887,22.052,24.974,18.005,19.417,18.157,18.720,16.550,16.414,15.022,16.475,16.699,16.452,16.406,15.151,17.410,16.924,8.673,17.910]) 
	
	# log the R values
	x = np.array([log10(i) for i in x])
	
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
	
	# appropriate t value						
	tval = stats.t.isf(alpha / 2., df)	
	
	# confidence intervals
	ci_a = a + tval * se_a * np.array([-1,1])
	ci_b = b + tval * se_b * np.array([-1,1])
	
	# standard error functions
	se_fit	   = lambda x: sd_res * np.sqrt(	1. / n + (x-mean_x)**2 / Sxx)
	se_predict = lambda x: sd_res * np.sqrt(1 + 1. / n + (x-mean_x)**2 / Sxx)

	# calculate ages and uncertainty to return
	ages = []
	errors = []
	for d in data:
		
		# log the users point
		d2 = log10(d)
		
		#  calculate age and SE
		age = fit(d2)
		ages.append(age)
		errors.append(fit(d2) + tval * se_predict(d2) - age)
		
	return ages, errors