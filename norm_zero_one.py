#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  3 19:18:43 2019

@author: jmatt
"""

def norm_zero_one(series,rng=None):
    """
    Takes a pandas data series or 1d numpy array and normalizes on the 
    range of 0-1.  Can optionally take a custom range rng=(min,max)
    
    INPUTS
        series - the input data series/array
        rng - (min,max) of the series in a tuple (default=None)
        
    OUTPUTS
        series - the normalized data series/array
    """
    
    #Determine the range
    if rng==None:
        min_val = series.min()
        max_val = series.max()
    else:
        min_val,max_val = rng
        
    #Normalize the series
    series = (series-min_val)/(max_val-min_val)
    
    return series
    
    
#mi = -10
#ma = 10
#val = -10
#norm = (val-mi)/(ma-mi)
#print('norm:{}'.format(norm)
    