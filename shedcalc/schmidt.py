# -*- coding: utf-8 -*-

# from scipy.stats import linregress, t
# from scipy.optimize import curve_fit
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from django import http

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


def fitLine(data):
	"""
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
	y = np.array([15.931,13.053,13.433,14.102,13.682,15.082,13.249,14.174,12.582,22.416,19.771,20.161,22.151,15.228,14.872,15.58,11.813,12.661,12.125,12.769,13.403,17.051,19.260,16.397,20.928,15.853,14.225,16.648,16.755,15.127,16.025,2.789,1.656,5.53,0.869,2.413,11.154,11.344,12.658,11.558,11.321,12.04,21.934,21.397,21.501,23.796,21.929,22.314,22.745,22.897,20.955,18.222,15.838,16.67]) 
	
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