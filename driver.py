# -*- coding: utf-8 -*-
"""
Created on Sat Mar 30 15:50:01 2019

@author: jmatt
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
import re
import pickle as pkl
import sys
import os
from causalinference import CausalModel

#try: 
#    import dowhy
#except:
#    str1 = '\n\n==> DoWhy causal inference package did not load, may not be installed\n'
#    str2 = '==> Installation Instructions:\n'
#    str3 = '==>    1. Clone the repository https://github.com/Microsoft/dowhy.git\n'
#    str4 = '==>    2. Run python setup.py install from the repo directory'
#    sys.exit(str1+str2+str3+str4)
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

#force_keep = not_match_vars.extend(predictor_centrals)

cutoff_percent = 1
to_drop = [tpl[1] for tpl in lz if tpl[0]>cutoff_percent]
to_drop = [val for val in to_drop if val not in ['total_disc','total_clothing']]

vars_exclude_from_x = ['xwaveid','nhhrhid','nhhpno','nhhrpid']
vars_exclude_from_x.extend(predictor_centrals)
vars_exclude_from_x.extend(['treatment_binary','nlosat','treatment'])
vars_exclude_from_x.extend(['total_income','total_disc','total_clothing'])
vars_exclude_from_x.extend(['disposable_income','mat_dep'])

AreaData_small = pd.DataFrame(AreaData)
AreaData_small.drop(to_drop,axis='columns',inplace=True)


#AreaData_test = pd.DataFrame(AreaData)
#AreaData_test[AreaData_test.isna()]=-1

#AreaData_test['treatment'] = AreaData_test['total_income']/AreaData_test['income_median']
source_var_list = ['income','disc','clothing']
var_to_titles = {
        'income':'total income',
        'disc':'discretionary spending',
        'clothing':'clothing spending'}
central_tendancy = 'mean'
#central_tendancy = 'median'


# make figures better for projector:
font = {'weight':'normal','size':14}
matplotlib.rc('font', **font)
matplotlib.rc('figure', figsize=(7.0, 5.0))
matplotlib.rc('xtick', labelsize=18) 
matplotlib.rc('ytick', labelsize=18) 
matplotlib.rc('legend',**{'fontsize':18})

f, axarr = plt.subplots(3, sharex=True, figsize=(13, 11), dpi= 80, facecolor='w', edgecolor='k')

for ax in axarr:
    ax.set_ylabel('Norm. diff. \nin avg. covariate',fontsize=18)
    
cutoff = [.3,.3,.3]
tuples = list(zip(source_var_list,axarr,cutoff))
pre_effect = []
effect_ols = []
effect_match = []


#AreaData_small.drop(admin_variables,axis='columns',inplace=True)
x_vars = [val for val in AreaData_small.keys() if val not in vars_exclude_from_x]

var_to_skip = 'mat_dep3'
x_vars = [val for val in x_vars if val!=var_to_skip]

x_var_descriptions = {}
for var in x_vars:
    x_var_descriptions[var] = list(variables[variables['Variable']==var]['Label'])

for source_var,ax,cut in tuples:
    AreaData_small['treatment'] = AreaData_small['total_'+source_var]/AreaData_small[source_var+'_'+central_tendancy]
    AreaData_small['treatment_binary'] = 0
    AreaData_small.loc[AreaData_small['treatment']>1,'treatment_binary'] = 1
    
    #var_name = 'treatment_binary'
    df = pd.DataFrame(AreaData_small)
    
    area_set = set(df['nhhsgcc'])
    
    
    
    D = np.array(AreaData_small['treatment_binary'])
    Y = np.array(AreaData_small['nlosat'])
    
    X = np.array(AreaData_small[x_vars])
    
    
    
    causal = CausalModel(Y,D,X)
    print(causal.summary_stats)
    
    r_diff_init = causal.summary_stats['rdiff']
    n_diff_init = causal.summary_stats['ndiff']
    
    causal.est_via_ols()
    ate = causal.estimates['ols']['ate']
    ate_se = causal.estimates['ols']['ate_se']
    
    pre_effect.append((ate,ate_se))
    
    
    
    #print(causal.estimates)
    causal.est_propensity()
    #print(causal.propensity)
    causal.cutoff=cut
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
    
    causal.est_via_ols()
    causal.est_via_weighting()
    #causal.est_via_blocking()
    causal.est_via_matching(bias_adj=True)
#    print(causal.estimates)
#    print(causal.summary_stats)
    
    
    r_diff_final = causal.summary_stats['rdiff']
    n_diff_final = causal.summary_stats['ndiff']
    ate = causal.estimates['ols']['ate']
    ate_se = causal.estimates['ols']['ate_se']
    
    effect_ols.append((ate,ate_se))
    
    ate = causal.estimates['matching']['ate']
    ate_se = causal.estimates['matching']['ate_se']
    effect_match.append((ate,ate_se))
    
    #plt.bar(x_vars,n_diff_init)
    #plt.bar(x_vars,n_diff_final)
    
    
#    plt.figure()
    ddff = pd.DataFrame(np.c_[n_diff_init,n_diff_final],index=x_vars)
    ddff.rename({0:'before_match',1:'after_match'},axis='columns',inplace=True)
    ddff.plot.bar(ax=ax)
    ax.set_title(var_to_titles[source_var])


f.savefig('Combined-'+central_tendancy+'-balance.png')
#    plt.close()
    


xlabels = ['income','discretionary','clothing']

matplotlib.rc('figure', figsize=(9.0, 6.0))


pre_y,pre_std = list(zip(*pre_effect))
pre_CE = 1.96*np.array(pre_std)

y_ols,std_ols = list(zip(*effect_ols))
CE_ols = 1.96*np.array(std_ols)

y_match,std_match = list(zip(*effect_match))
CE_match = 1.96*np.array(std_match)

offset = .15
pre_ols_xlocs = np.array([1,2,3])
post_ols_xlocs = pre_ols_xlocs+offset
post_match_xlocs = pre_ols_xlocs+offset*2

plt.figure()
plt.errorbar(pre_ols_xlocs,pre_y,yerr =pre_CE,fmt='m*',capsize = 10, markersize=12,label='pre-match (OLS)')
plt.errorbar(post_ols_xlocs,y_ols,yerr =CE_ols,fmt='bo',capsize = 10, markersize=12,label='post-match (OLS)')
plt.errorbar(post_match_xlocs,y_match,yerr =CE_match,fmt='ro',capsize = 10, markersize=12,label='post-match (matching)')
plt.xticks(post_ols_xlocs,xlabels)
plt.legend()
plt.plot([1,3.5],[0,0],'b:')
plt.ylabel('Effect Size (change in SWB)')
plt.savefig('effect_summary.png')
#plt.show()

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
