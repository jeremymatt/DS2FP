# -*- coding: utf-8 -*-
"""
Created on Mon Apr 29 20:07:21 2019

@author: jmatt
"""

def lst_not_in(l1,l2):
    """
    Returns all the values of l1 that are not present in l2
    
    INPUT
        l1 - list or set containing values to potentially keep
        l2 - list or set of values to reject from l1
        
    OUTPUT
        not_in - list of values in l1 but not in l2
    """
    
    not_in = [val for val in l1 if not val in l2]
    
    return not_in