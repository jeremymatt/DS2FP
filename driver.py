# -*- coding: utf-8 -*-
"""
Created on Sat Mar 30 15:50:01 2019

@author: jmatt
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import pickle as pkl
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
from load_and_preprocess import load_and_preprocess

from IPython import get_ipython
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

#find the number of records and set nan valuse to -1
num_records = AreaData.shape[0]
AreaData[AreaData.isna()]=-1

#Identify the percent of missing values in each variable and flag any variable
#missing more than the cutoff_percent for removal from the data table
percent_missing = [len(AreaData[AreaData[var]==-1])*100/num_records for var in AreaData.keys()]
lz = list(zip(percent_missing,AreaData.keys()))
lz.sort()
cutoff_percent = 1
to_drop = [tpl[1] for tpl in lz if tpl[0]>cutoff_percent]
#Make sure not to drop any of the treatment variables
to_drop = [val for val in to_drop if val not in ['total_income','total_disc','total_clothing']]

#Build a list of variables that should not be included in the matching process
#subject tracking variables
vars_exclude_from_x = ['xwaveid','nhhrhid','nhhpno','nhhrpid']
#central tendencies
vars_exclude_from_x.extend(predictor_centrals)
#treatment variables and the response variable
vars_exclude_from_x.extend(['treatment_binary','nlosat','treatment'])
vars_exclude_from_x.extend(['total_income','total_disc','total_clothing'])
#disposable income is strongly correlated with total income
#mat_dep is a linear combination of other variables
vars_exclude_from_x.extend(['disposable_income','mat_dep'])

#Export to a new dataframe and drop variables with too much missingness
AreaData_small = pd.DataFrame(AreaData)
AreaData_small.drop(to_drop,axis='columns',inplace=True)


source_var_list = ['income','disc','clothing']
var_to_titles = {
        'income':'total income',
        'disc':'discretionary spending',
        'clothing':'clothing spending'}

#Set the central tendancy to be used in the analysis
central_tendancy = 'mean' #mean or median
#central_tendancy = 'median'


# make figures better for display:
font = {'weight':'normal','size':14}
matplotlib.rc('font', **font)
matplotlib.rc('figure', figsize=(7.0, 5.0))
matplotlib.rc('xtick', labelsize=18) 
matplotlib.rc('ytick', labelsize=18) 
matplotlib.rc('legend',**{'fontsize':18})

#initialize the covariate balance figure and set the ylabels
f, axarr = plt.subplots(3, sharex=True, figsize=(13, 11), dpi= 80, facecolor='w', edgecolor='k'
for ax in axarr:
    ax.set_ylabel('Norm. diff. \nin avg. covariate',fontsize=18)
    
#cutoff values for dropping subjects based on the propensity score
cutoff = [.3,.3,.3]
tuples = list(zip(source_var_list,axarr,cutoff))
pre_effect = []
effect_ols = []
effect_match = []


#AreaData_small.drop(admin_variables,axis='columns',inplace=True)
x_vars = [val for val in AreaData_small.keys() if val not in vars_exclude_from_x]

#Extract the descriptoins of each matching variable
x_var_descriptions = {}
for var in x_vars:
    x_var_descriptions[var] = list(variables[variables['Variable']==var]['Label'])

for source_var,ax,cut in tuples:
    #Calculate the binary treatment
    AreaData_small['treatment'] = AreaData_small['total_'+source_var]/AreaData_small[source_var+'_'+central_tendancy]
    AreaData_small['treatment_binary'] = 0
    AreaData_small.loc[AreaData_small['treatment']>1,'treatment_binary'] = 1
    df = pd.DataFrame(AreaData_small)
    
    #Find the values of all area designations
    area_set = set(df['nhhsgcc'])
    
    
    #Extract the treatment, response, and matching data and store in arrays
    D = np.array(AreaData_small['treatment_binary'])
    Y = np.array(AreaData_small['nlosat'])
    X = np.array(AreaData_small[x_vars])
    
    
    #Init the causal model
    causal = CausalModel(Y,D,X)
#    print(causal.summary_stats)
    
    #collect the pre-match balance and OLS estimates
    r_diff_init = causal.summary_stats['rdiff']
    n_diff_init = causal.summary_stats['ndiff']
    causal.est_via_ols()
    ate = causal.estimates['ols']['ate']
    ate_se = causal.estimates['ols']['ate_se']
    pre_effect.append((ate,ate_se))
    
    #Estimate the propensity score, set the propensty cutoff, trim and estimate the effect
    causal.est_propensity()
    causal.cutoff=cut
    causal.trim()
    causal.est_via_ols()
    causal.est_via_weighting()
    causal.est_via_matching(bias_adj=True)
    
    #Store the post-match balance and effect estimates
    r_diff_final = causal.summary_stats['rdiff']
    n_diff_final = causal.summary_stats['ndiff']
    
    ate = causal.estimates['ols']['ate']
    ate_se = causal.estimates['ols']['ate_se']
    effect_ols.append((ate,ate_se))
    
    ate = causal.estimates['matching']['ate']
    ate_se = causal.estimates['matching']['ate_se']
    effect_match.append((ate,ate_se))
    
    #Plot the balance summary
    ddff = pd.DataFrame(np.c_[n_diff_init,n_diff_final],index=x_vars)
    ddff.rename({0:'before_match',1:'after_match'},axis='columns',inplace=True)
    ddff.plot.bar(ax=ax)
    ax.set_title(var_to_titles[source_var])


f.savefig('Combined-'+central_tendancy+'-balance.png')
    

#Plot the pre and post match effect summary figure
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
plt.savefig('effect_summary_'+central_tendancy+'.png')

