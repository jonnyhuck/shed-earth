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


def getCalibratedValues(data, r):
	"""
	multiply means by age calibration
	"""
	# TODO: get data from db
	v = 48.08
	
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
	x = np.array([39.4,49.0,47.5,39.6,36.7,39.2,41.8,42.5,42.5,26.5,30.7,27.9,31.0,41.1,41.7,40.4,45.7,41.4,41.7,45.4,43.3,39.7,35.8,38.9,28.9,34.5,35.1,35.2,39.6,36.3,36.0,59.5,63.0,58.1,63.7,60.8,47.2,46.5,42.9,45.3,46.5,44.8,27.2,30.2,29.5,25.6,28.0,30.3,28.7,29.0,28.8,33.1,38.923,37.835])
	
	# (ages based upon selected production rate)
	if prodrate == 0:	# Loch Lomond
		y = np.array([15.931,13.053,13.433,14.102,13.682,15.082,13.249,14.174,12.582,22.416,19.771,20.161,22.151,15.228,14.872,15.58,11.813,12.661,12.125,12.769,13.403,17.051,19.260,16.397,20.928,15.853,14.225,16.648,16.755,15.127,16.025,2.789,1.656,5.53,0.869,2.413,11.154,11.344,12.658,11.558,11.321,12.04,21.934,21.397,21.501,23.796,21.929,22.314,22.745,22.897,20.955,18.222,15.838,16.67]) 
	elif prodrate == 1:	# Glen Roy
		y = np.array([14.864,12.178,12.532,13.156,12.764,14.071,12.361,13.224,11.737,20.914,18.448,18.811,20.668,14.212,13.879,14.539,11.027,11.818,11.318,11.918,12.51,15.913,18.96821516,15.302,19.528,14.793,13.273,15.535,15.634,14.115,14.955,2.602,1.545,5.16,0.811,2.252,10.409,10.586,11.812,10.786,10.565,11.235,20.467,19.966,20.063,22.204,20.462,20.822,21.223,21.366,19.555,17.005,14.781,15.557]) 
	elif prodrate == 2:	# CRONUS-calc default
		y = np.array([16.040,13.143,13.525,14.199,13.776,15.186,13.341,14.272,12.668,22.570,19.907,20.299,22.303,15.333,14.973,15.687,11.894,12.748,12.208,12.856,13.495,17.168,20.156,16.510,21.072,15.961,14.322,16.762,16.869,15.231,16.135,2.808,1.667,5.568,0.875,2.430,11.230,11.422,12.745,11.638,11.398,12.122,22.084,21.544,21.648,23.959,22.079,22.467,22.902,23.054,21.099,18.347,15.946,16.784]) 
	
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
	x = np.array([54.03368396,57.60061836,61.93426224,59.23447584,51.13453623,57.80160755,49.50158588,48.60176758,47.20191692,46.60348264,46.90370451,51.63763229,55.37151306,51.90476614,53.07176254,42.90448686,42.70464598,39.97118604,39.67132362,38.90473325,52.13989717,49.50644397,53.50719023,41.95006324,23.4094335,26.47745241,25.8106217,40.5837167,45.15249304,45.81963775,45.81983488,41.58484362,40.08435908,45.48693888,40.31814028,38.45079804,45.48751973,42.91986244,46.75516721,45.95498962,48.85656394,47.22265643,51.02469707,47.79000009,48.22375316,50.09155454,48.12411378,49.2582244,47.5242191,48.83552464,59.83627399,49.60264646])
	
	if prodrate == 0:	# Loch Lomond
		# TODO: This is for GB - needs calculating for PY
		y = np.array([15.931,13.053,13.433,14.102,13.682,15.082,13.249,14.174,12.582,22.416,19.771,20.161,22.151,15.228,14.872,15.58,11.813,12.661,12.125,12.769,13.403,17.051,19.260,16.397,20.928,15.853,14.225,16.648,16.755,15.127,16.025,2.789,1.656,5.53,0.869,2.413,11.154,11.344,12.658,11.558,11.321,12.04,21.934,21.397,21.501,23.796,21.929,22.314,22.745,22.897,20.955,18.222,15.838,16.67]) 
	elif prodrate == 1:	# Glen Roy
		# TODO: This is for GB - needs calculating for PY
		y = np.array([14.864,12.178,12.532,13.156,12.764,14.071,12.361,13.224,11.737,20.914,18.448,18.811,20.668,14.212,13.879,14.539,11.027,11.818,11.318,11.918,12.51,15.913,18.96821516,15.302,19.528,14.793,13.273,15.535,15.634,14.115,14.955,2.602,1.545,5.16,0.811,2.252,10.409,10.586,11.812,10.786,10.565,11.235,20.467,19.966,20.063,22.204,20.462,20.822,21.223,21.366,19.555,17.005,14.781,15.557]) 
	elif prodrate == 2:	# CRONUS-calc default
		y = np.array([13.955,12.547,4.218,5.311,11.674,8.413,14.013,13.82,15.046,16.006,16.378,12.191,8.557,12.327,11.815,21.445,21.256,22.691,23.324,24.219,11.081,12.227,12.202,21.589,51.107,43.909,42.589,20.836,17.393,17.581,17.613,21.368,23.812,19.232,22.536,25.692,18.377,19.908,18.617,19.127,17.021,16.724,15.372,17.077,17.191,16.874,16.826,15.542,17.752,17.933,8.988,18.62]) 
	
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
		d2 = log(d)
		
		#  calculate age and SE
		age = fit(d2)
		ages.append(age)
		errors.append(fit(d2) + tval * se_predict(d2) - age)
		
	return ages, errors