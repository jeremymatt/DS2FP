# -*- coding: utf-8 -*-
"""
Created on Sat Mar 30 15:50:01 2019

@author: jmatt
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
from causalinference import CausalModel as CM
import pickle as pkl

#JEM functions
from PerPersVar_condense import PerPersVar_condense
from drop_illogical import drop_illogical
from make_hist_fig import make_hist_fig
from load_data import load_data
from data_exploration import data_exploration
from extract_areas import extract_areas

from load_and_preprocess import load_and_preprocess

#Local locn of datafile
data_fn = 'data\\Combined_n170c.csv'
#Local location of variables descriptor file
variables_fn = 'data\\variables.csv'
#Set of variables to include
VariableSet = 'toy'
#Remote location of data file
URL = 'https://www.dropbox.com/s/mdyfysm8t583v9p/Combined_n170c.csv?dl=1'
#flag to: Drop records with missing response variable
#         Drop columns not in the selected set of variables
Drop_extra=True

    
#Build the path to the pkl file
pkl_file = '{}_{}_processed.pkl'.format(data_fn.split('.')[0],VariableSet)

#Open the file in write binary mode
try: file = open(pkl_file,'rb')
except:
    load_and_preprocess(data_fn,variables_fn,VariableSet,URL,Drop_extra)
    file = open(pkl_file,'rb')

pkl_vars = pkl.load(file)

file.close()


AreaData,variables,LocVals,LocNames,LocVar = pkl_vars


