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
import urllib

#JEM functions
from PerPersVar_condense import PerPersVar_condense
from drop_illogical import drop_illogical
from make_hist_fig import make_hist_fig

#Local locn of datafile
data_fn = 'data\\Combined_n170c.csv'
#Local location of variables descriptor file
variables_fn = 'data\\variables.csv'

#Remote location of data file
URL = 'https://www.dropbox.com/s/mdyfysm8t583v9p/Combined_n170c.csv?dl=1'

#If the data file exists locally, load it using pandas
try: df = pd.read_csv(data_fn)
except: 
    #If the data file does not exist locally, download and save locally, then open
    print('Downloading data file (~430mb)')
    urllib.request.urlretrieve(URL,data_fn)
    print('Download Complete')
    df = pd.read_csv(data_fn)

#Read the variables descriptor file
variables = pd.read_csv(variables_fn)


responseVar = variables['Variable'][variables['Response']=='y'].values[0]

#remove entries with negative response variables (non-responding person, N/A, not asked, etc)
VariableSet = 'toy'
NumRecords = df.shape[0]
DataSubset = pd.DataFrame(df[df[responseVar]>-1])
print('\n{} records dropped due to lack of response variable (non-responding person, N/A, etc)'.format(NumRecords-DataSubset.shape[0]))


KeepVars = variables['Variable'][variables[VariableSet]=='y']

DataSubset = DataSubset[KeepVars]


plt.hist(DataSubset[responseVar],bins=11)


var = 'nhifeft' #total income
#var2 = 'nhifdit' #Disposable income
var_p = var+'p'
var_n = var+'n'

plt.hist(DataSubset[var_p]-DataSubset[var_n],log=True,bins=100)
DataSubset[var_p].max()
DataSubset[var_n].mode()

#Variables of 'discretionary' consumption (cigarettes, alcohol, meals out, etc)
DiscVars = variables['Variable'][variables['Disc']=='y']

#Check for differences between imputed and non-imputed variables
dv1 = list(DiscVars)
dv2 = [val+'i' for val in dv1]
print('\nCheck for differences between imputed and non-imputed variables')
for i in range(3):
    test = DataSubset[dv1[i]]-DataSubset[dv1[i]]
    print('{} minus {}==> min:{} max:{}'.format(dv1[i],dv2[i],test.min(),test.max()))

#Build a 'discretionary' consumption variable add to the dataset
DataSubset['DiscCon'] = DataSubset[DiscVars].sum(axis=1)
#Drop the source variables
DataSubset.drop(DiscVars,axis='columns',inplace=True)

#List of clothing spending variables
ClothVars = variables['Variable'][variables['Clothing']=='y']
#Build clothign spending variable and add to the dataset
DataSubset['ClothCon'] = DataSubset[ClothVars].sum(axis=1)
#Drop the source variables
DataSubset.drop(ClothVars,axis='columns',inplace=True)




total_p = 'nhifeftp' #total income
total_n = 'nhifeftn' #total income
disp_p = 'nhifditp' #Disposable income
disp_n = 'nhifditn' #Disposable income

print('\nConfirm that the positive\\negative income & disposable income variables are greater-than\less-than zero respectively' )
print('min of positive total income: {}'.format(DataSubset[total_p].min()))
#note values in 'negative income' columns are provided as positive values
print('max of negative total income: {}'.format(DataSubset[total_n].min()))
print('min of positive disposable income: {}'.format(DataSubset[disp_p].min()))
#note values in 'negative income' columns are provided as positive values
print('max of negative disposable income: {}'.format(DataSubset[disp_n].min()))

#combine total income variables and add to dataset
t_inc = DataSubset[total_p]-DataSubset[total_n]
DataSubset['total_income'] = t_inc
#combine disposable income variables and add to dataset
d_inc = DataSubset[disp_p]-DataSubset[disp_n]
DataSubset['disposable_income']= d_inc
#Drop source columns
DataSubset.drop([total_p,total_n,disp_p,disp_n],axis='columns',inplace=True)

plt.plot(d_inc,t_inc,'.')

plt.plot(t_inc,DataSubset['DiscCon'],'.')
plt.plot(t_inc,DataSubset['ClothCon'],'.')

sns.pairplot(DataSubset[['total_income','disposable_income','DiscCon','ClothCon',responseVar]])
#
#t = DataSubset[DataSubset.keys()][DataSubset['total_income']==1457066]
#todrop = t.index
#
#DataSubset.drop(todrop,inplace=True)


NumRecords = DataSubset.shape[0]

t = DataSubset[DataSubset.keys()][DataSubset['disposable_income']==837797]
todrop = t.index

DataSubset.drop(todrop,inplace=True)
print('\n{} records dropped due to unexpected disposable income of exactly $837,797 over multiple households'.format(NumRecords-DataSubset.shape[0]))



sns.pairplot(DataSubset[['total_income','disposable_income','DiscCon','ClothCon',responseVar]])

#
#
#t = DataSubset[[var_p,var_n]]
#
#t['both_pos'] = (DataSubset[var_n]>0) & (DataSubset[var_p]>0)

LocVar = 'nhhsgcc'

LocVals = {'Sydney':11,
           'Melbourne':21,
           'Brisbane':31,
           'Adelaide':41,
           'Perth':51}

LocList = list(LocVals.values())
LocName = list(LocVals.keys())

LocNames = dict(zip(LocList,LocName))


CurData = drop_illogical(CurData,'disposable_income','total_income')
CurData = drop_illogical(CurData,'ClothCon','total_income')
CurData = drop_illogical(CurData,'DiscCon','total_income')

AreaData = pd.DataFrame()
NumSubjects = 0
for loc in LocList:
    CurData = DataSubset[DataSubset.keys()][DataSubset[LocVar]==loc]
    CurNum = CurData.shape[0]
    NumSubjects += CurNum
    print('{} participants in {}'.format(CurNum,LocNames[loc]))
    mean = CurData['total_income'].mean()
    std =  CurData['total_income'].std()
    clothing_mean = CurData['ClothCon'].mean()
    disc_mean = CurData['DiscCon'].mean()
    
    CurData['income_ratio']=CurData['total_income']/mean
    CurData['income_std'] = std
    CurData['clothing_mean'] = CurData['ClothCon']/clothing_mean
    CurData['disc_mean'] = CurData['DiscCon']/disc_mean
    AreaData = pd.concat([AreaData,CurData])
print('{} subjects in total ({} non-capital-city subjects dropped)'.format(NumSubjects,DataSubset.shape[0]-NumSubjects)) 

sns.pairplot(AreaData[['total_income','disposable_income','DiscCon','ClothCon',responseVar]])




#Extract the per-person variables
PerPersVars = variables['Variable'][(variables[VariableSet]=='y')&(variables['per_person']=='y')]
#Find the roots of the per-person variables
VarRoots = set([val[:re.search('\d',val).start(0)] for val in PerPersVars])
per_num_var = 'nhhpno'
for root in VarRoots:
    AreaData = PerPersVar_condense(AreaData,root,per_num_var,DropSource=True)
    
save_dir = 'Figures\\simple_hist\\'
var_descriptions = dict(zip(list(variables['Variable']),list(variables['Label'])))
for var_name in AreaData.keys()[4:]:
    data = list(AreaData[var_name])
    num_bins = np.sqrt(len(data)).round().astype(int)
    make_hist_fig(data,num_bins,save_dir,var_name,var_descriptions)

#
#SydneyData = DataSubset[DataSubset.keys()][DataSubset[LocVar]==LocVals['Sydney']]
#S_part = SydneyData.shape[0]
#print('{} participants in Sydney'.format(S_part))
#
#MelbData = DataSubset[DataSubset.keys()][DataSubset[LocVar]==LocVals['Melbourne']]
#M_part = MelbData.shape[0]
#print('{} participants in Melbourne'.format(M_part))
#
#BrisData = DataSubset[DataSubset.keys()][DataSubset[LocVar]==LocVals['Brisbane']]
#B_part = BrisData.shape[0]
#print('{} participants in Brisbane'.format(B_part))
#
#AdelaideData = DataSubset[DataSubset.keys()][DataSubset[LocVar]==LocVals['Adelaide']]
#A_part = AdelaideData.shape[0]
#print('{} participants in Adelaide'.format(A_part))
#
#PerthData = DataSubset[DataSubset.keys()][DataSubset[LocVar]==LocVals['Perth']]
#P_part = PerthData.shape[0]
#print('{} participants in Perth'.format(P_part))
#print('{} participants in capital city areas'.format(S_part+M_part+B_part+A_part+P_part))
