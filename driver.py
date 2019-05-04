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
import pickle as pkl
import sys
import os
from causalinference import CausalModel

try: 
    import dowhy
except:
    str1 = '\n\n==> DoWhy causal inference package did not load, may not be installed\n'
    str2 = '==> Installation Instructions:\n'
    str3 = '==>    1. Clone the repository https://github.com/Microsoft/dowhy.git\n'
    str4 = '==>    2. Run python setup.py install from the repo directory'
    sys.exit(str1+str2+str3+str4)
#
#from dowhy.do_why import CausalModel
#import dowhy.plotter

#JEM functions
from PerPersVar_condense import PerPersVar_condense
from drop_illogical import drop_illogical
from make_hist_fig import make_hist_fig
from load_data import load_data
from data_exploration import data_exploration
from extract_areas import extract_areas
from lst_not_in import lst_not_in
from norm_zero_one import norm_zero_one

from load_and_preprocess import load_and_preprocess

from IPython import get_ipython
from IPython.display import Image, display
get_ipython().run_line_magic('matplotlib', 'inline')

#Local locn of datafile
data_fn = 'data/Combined_n170c.csv'
data_fn = os.path.normpath(data_fn) #convert to use OS-specific separators
#Local location of variables descriptor file
variables_fn = 'data/variables.csv'
variables_fn = os.path.normpath(variables_fn) #convert to use OS-specific separators
#Set of variables to include
VariableSet = 'toy'
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
predictor_centrals = ['{}_{}'.format(root,suffix) for root in pred_roots for suffix in pred_suffix]

#Build a list of variables to exclude from the matching block. 
#These are the predictor variables and the output variable
#not_match_vars = list(predictor_vars)
#not_match_vars.extend(['nlosat'])


#
##Make a list of the dataframe keys
#all_vars = list(AreaData.keys())
#
##Extract the variables to do the matching on
#match_vars = lst_not_in(all_vars,not_match_vars)

#AreaData['treatment'] = 0
#
#     
#AreaData.loc[AreaData['total_income']>AreaData['income_median'],'treatment']=1

#vals = ['nhhsgcc', 'nedsscmp',
#       'njbhruw', 'njbn', 'njbmsall', 'ntchave', 'nrchave', 'nmrcms', 'nlosat',
#        'nlspact', 'nlssmkf',
#       'nlsdrkf', 'nlslanh', 'nlslatr', 'nlsrelsp', 'nlesep', 'nlebth',
#       'nleins', 'total_income','income_median','nhgsex', 'nhgage', 'mat_dep',
#       'treatment']

#vals = ['nhhsgcc', 'nedsscmp',
#       'njbhruw', 'njbn', 'njbmsall', 'ntchave', 'nrchave', 'nmrcms', 'nlosat',
#       'nleins', 'total_income','income_median','nhgsex', 'nhgage', ]
#x_vars = ['nhhsgcc', 'nedsscmp','njbhruw', 'njbn', 'njbmsall', 'ntchave','nhgsex', 'nhgage', ]


num_records = AreaData.shape[0]
AreaData[AreaData.isna()]=-1

percent_missing = [len(AreaData[AreaData[var]==-1])*100/num_records for var in AreaData.keys()]

lz = list(zip(percent_missing,AreaData.keys()))
lz.sort()

force_keep = not_match_vars.extend(predictor_centrals)

cutoff_percent = 1
to_drop = [tpl[1] for tpl in lz if tpl[0]>cutoff_percent]
to_drop = [val for val in to_drop if val not in ['total_disc','total_clothing']]

vars_exclude_from_x = ['xwaveid','nhhrhid','nhhpno','nhhrpid']
vars_exclude_from_x.extend(predictor_centrals)
vars_exclude_from_x.extend(['treatment_binary','nlosat','treatment'])
vars_exclude_from_x.extend(['total_income','total_disc','total_clothing'])

AreaData_small = pd.DataFrame(AreaData)
AreaData_small.drop(to_drop,axis='columns',inplace=True)


#AreaData_test = pd.DataFrame(AreaData)
#AreaData_test[AreaData_test.isna()]=-1

#AreaData_test['treatment'] = AreaData_test['total_income']/AreaData_test['income_median']
source_var = 'income'
central_tendancy = 'mean'
AreaData_small['treatment'] = AreaData_small['total_'+source_var]/AreaData_small[source_var+'_mean']
AreaData_small['treatment_binary'] = 0
AreaData_small.loc[AreaData_small['treatment']>1,'treatment_binary'] = 1

var_name = 'treatment_binary'
df = pd.DataFrame(AreaData_small)

D = np.array(AreaData_small['treatment_binary'])
Y = np.array(AreaData_small['nlosat'])
AreaData_small.drop(admin_variables,axis='columns',inplace=True)
x_vars = [val for val in AreaData_small.keys() if val not in vars_exclude_from_x]
X = np.array(AreaData_small[x_vars])

causal = CausalModel(Y,D,X)
print(causal.summary_stats)
causal.est_via_ols()
#print(causal.estimates)
causal.est_propensity()
#print(causal.propensity)
causal.cutoff
causal.trim()
#causal.cutoff
#print(causal.summary_stats)
#causal.stratify()
##print(causal.strata)
#
#for stratum in causal.strata:
#    stratum.est_via_ols(adj=1)
#
#ate = [stratum.estimates['ols']['ate'] for stratum in causal.strata]

#causal.est_via_ols()
#causal.est_via_weighting()
#causal.est_via_blocking()
causal.est_via_matching(bias_adj=True)
print(causal.estimates)






#
##AreaData_small.drop('total_income',axis='columns',inplace=True)
#mask = (df['treatment_binary']==1)&(df[var_name]!=-1)
#treatment_vals = pd.Series(df.loc[mask,var_name])
#mask = (df['treatment_binary']==0)&(df[var_name]!=-1)
#control_vals = pd.Series(df.loc[mask,var_name])
#max_val = max([treatment_vals.max(),control_vals.max()])
#min_val = min([treatment_vals.min(),control_vals.min()])
#rng = (min_val,max_val)
#
#treatment_vals = norm_zero_one(treatment_vals,rng)
#control_vals = norm_zero_one(control_vals,rng)
#
#
##mi = -10
##ma = 10
##val = pd.Series([-10,-5,0,5,7,10])
##norm = norm_zero_one(val,(mi,ma))
##print('norm:{}'.format(norm))
#
#tv_len = len(treatment_vals)
#cv_len = len(control_vals)
#num_neg = len(AreaData_small[AreaData_small[var_name]==-1])
#num_records = AreaData_small.shape[0]
#print('{} total records. {}(treatment)+{}(control)+{}(-1)={}'.format(
#        num_records,
#        tv_len,
#        cv_len,
#        num_neg,
#        tv_len+cv_len+num_neg))
#
#association = treatment_vals.mean()-control_vals.mean()
#print('Association: {}'.format(association))








#
#             
#model = CausalModel(
#        data=AreaData_small,
#        treatment='treatment',
#        outcome = 'nlosat',
#        common_causes = match_vars)
#
#identified_estimand = model.identify_effect()
#
#
#get_ipython().run_line_magic('matplotlib', 'qt5')
#model.view_model()
#display(Image(filename="causal_model.png"))
#
#estimate = model.estimate_effect(identified_estimand,
#        method_name="backdoor.linear_regression",
#        test_significance=True
#        )
#print(estimate)
#print("Causal Estimate is " + str(estimate.value))
#
#res_random=model.refute_estimate(identified_estimand, estimate, method_name="random_common_cause")
#print(res_random)
#
#res_placebo=model.refute_estimate(identified_estimand, estimate,
#        method_name="placebo_treatment_refuter", placebo_type="permute")
#print(res_placebo)
#
#causal_estimate_reg = model.estimate_effect(identified_estimand,
#        method_name="backdoor.linear_regression",
#        test_significance=True)
#print(causal_estimate_reg)
#print("Causal Estimate is " + str(causal_estimate_reg.value))
#
#causal_estimate_strat = model.estimate_effect(identified_estimand,
#        method_name="backdoor.propensity_score_stratification")
#print(causal_estimate_strat)
#print("Causal Estimate is " + str(causal_estimate_strat.value))
#
#causal_estimate_match = model.estimate_effect(identified_estimand,
#        method_name="backdoor.propensity_score_matching")
#print(causal_estimate_match)
#print("Causal Estimate is " + str(causal_estimate_match.value))
#
#causal_estimate_ipw = model.estimate_effect(identified_estimand,
#        method_name="backdoor.propensity_score_weighting")
#print(causal_estimate_ipw)
#print("Causal Estimate is " + str(causal_estimate_ipw.value))

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
#
#
#
#
