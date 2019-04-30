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
#from causalinference import CausalModel as CM
import pickle as pkl
import sys
import os

try: 
    import dowhy
except:
    str1 = '\n\n==> DoWhy causal inference package did not load\n'
    str2 = '==> Installation Instructions:\n'
    str3 = '==>    1. Clone the repository https://github.com/Microsoft/dowhy.git\n'
    str4 = '==>    2. Run python setup.py install from the repo directory'
    sys.exit(str1+str2+str3+str4)

from dowhy.do_why import CausalModel
import dowhy.plotter

#JEM functions
from PerPersVar_condense import PerPersVar_condense
from drop_illogical import drop_illogical
from make_hist_fig import make_hist_fig
from load_data import load_data
from data_exploration import data_exploration
from extract_areas import extract_areas
from lst_not_in import lst_not_in

from load_and_preprocess import load_and_preprocess

#Local locn of datafile
data_fn = 'data/Combined_n170c.csv'
data_fn = os.path.normpath(data_fn) #convert to use OS-specific separators
#Local location of variables descriptor file
variables_fn = 'data/variables.csv'
variables_fn = os.path.normpath(variables_fn) #convert to use OS-specific separators
#Set of variables to include
VariableSet = 'testing'
#flag to: Drop records with missing response variable
#         Drop columns not in the selected set of variables
Drop_extra=True

"""
#Remote location of data file
"""
f = open('data_url.url','r')
URL = f.read()
f.close()

    
#Build the path to the pkl file
pkl_file = '{}_{}_processed.pkl'.format(data_fn.split('.')[0],VariableSet)

#Try to open the file in write binary mode
try: file = open(pkl_file,'rb')
except:
    #If the pickle file doesn't exist, run the load/pre-process script and 
    #save the processed data to disk
    load_and_preprocess(data_fn,variables_fn,VariableSet,URL,Drop_extra)
    #Open the file
    file = open(pkl_file,'rb')
#unpickle the data variables and close the file
pkl_vars = pkl.load(file)
file.close()

#Expand the saved tuple
AreaData,variables,LocVals,LocNames,LocVar = pkl_vars

#build a list of the predictor variables
pred_roots = ['clothing','disc','income']
pred_suffix = ['mean','std','median']
predictor_vars = ['{}_{}'.format(root,suffix) for root in pred_roots for suffix in pred_suffix]

#Build a list of variables to exclude from the matching block. 
#These are the predictor variables and the output variable
not_match_vars = list(predictor_vars)
not_match_vars.extend(['nlosat'])
not_match_vars = list(not_match_vars)

#Make a list of the dataframe keys
all_vars = list(AreaData.keys())

#Extract the variables to do the matching on
match_vars = lst_not_in(all_vars,not_match_vars)

AreaData['treatment'] = 0

AreaData['treatment'][AreaData['total_income']>AreaData['income_median']]=1

#model = CausalModel(
#        data=AreaData,
#        treatment='treatment',
#        outcome = 'nlosat',
#        common_causes = match_vars)


#
#DeprivationVars = variables['Variable'][variables['m_dep']=='y']
#DeprivationVars = [val for val in DeprivationVars if val in set(AreaData.keys())]
#AreaData['mat_dep'] = 0
#for var in DeprivationVars:
#    AreaData['mat_dep'][AreaData[var] == 2]+=1
#
#depvar = list(DeprivationVars)
#depvar.extend(['mat_dep'])
#AreaData = condense_deprivation(AreaData,variables,drop_vars=True)




