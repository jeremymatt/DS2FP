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
import os

#JEM functions
from PerPersVar_condense import PerPersVar_condense
from drop_illogical import drop_illogical
from make_hist_fig import make_hist_fig
from load_data import load_data

#Local locn of datafile
data_fn = 'data/Combined_n170c.csv'
data_fn = os.path.normpath(data_fn)
#Local location of variables descriptor file
variables_fn = 'data/variables.csv'
variables_fn = os.path.normpath(variables_fn)
#Set of variables to include
VariableSet = 'toy'
#Remote location of data file
URL = 'https://www.dropbox.com/s/mdyfysm8t583v9p/Combined_n170c.csv?dl=1'
#Drop records with missing response variable
#Drop columns not in the selected set of variables
Drop_extra=True

#Load the data and begin processing
DataSubset,variables,responseVar=load_data(data_fn,variables_fn,URL,VariableSet,Drop_extra)
#
##If the data file exists locally, load it using pandas
#try: df = pd.read_csv(data_fn)
#except: 
#    #If the data file does not exist locally, download and save locally, then open
#    print('Downloading data file (~430mb)')
#    urllib.request.urlretrieve(URL,data_fn)
#    print('Download Complete')
#    df = pd.read_csv(data_fn)
#
##Read the variables descriptor file
#variables = pd.read_csv(variables_fn)
#
#responseVar = variables['Variable'][variables['Response']=='y'].values[0]
#
##remove entries with negative response variables (non-responding person, N/A, not asked, etc)
#VariableSet = 'toy'
#NumRecords = df.shape[0]
#DataSubset = pd.DataFrame(df[df[responseVar]>-1])
#print('\n{} records dropped due to lack of response variable (non-responding person, N/A, etc)'.format(NumRecords-DataSubset.shape[0]))
#
#
#KeepVars = variables['Variable'][variables[VariableSet]=='y']
#
#DataSubset = DataSubset[KeepVars]



#Variables of 'discretionary' consumption (cigarettes, alcohol, meals out, etc)
DiscVars = variables['Variable'][variables['Disc']=='y']
#Build a 'discretionary' consumption variable add to the dataset
DataSubset['DiscCon'] = DataSubset[DiscVars].sum(axis=1)

#List of clothing spending variables
ClothVars = variables['Variable'][variables['Clothing']=='y']
#Build clothign spending variable and add to the dataset
DataSubset['ClothCon'] = DataSubset[ClothVars].sum(axis=1)


#Find flags (values less than 0) and set all flags to -1.
DataSubset[DataSubset<0] = -1

plt.figure()
plt.hist(DataSubset[responseVar],bins=11)
plt.xlabel('Response Variable (nlosat)')

var = 'nhifeft' #total income
#var2 = 'nhifdit' #Disposable income
var_p = var+'p'
var_n = var+'n'

plt.figure()
plt.hist(DataSubset[var_p]-DataSubset[var_n],log=True,bins=100)
plt.xlabel('Total income (including negative incomes)')
DataSubset[var_p].max()
DataSubset[var_n].mode()

#Check for differences between imputed and non-imputed variables
dv1 = list(DiscVars) #non-imputed
dv2 = [val+'i' for val in dv1]  #imputed
print('\nCheck for differences between imputed and non-imputed variables')
for i in range(3):
    test = DataSubset[dv1[i]]-DataSubset[dv1[i]]
    print('{} minus {}==> min:{} max:{}'.format(dv1[i],dv2[i],test.min(),test.max()))

#Drop the source variables
DataSubset.drop(DiscVars,axis='columns',inplace=True)

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

plt.figure()
plt.plot(d_inc,t_inc,'.')
plt.xlabel('disposable income')
plt.ylabel('total income')

plt.figure()
plt.plot(t_inc,DataSubset['DiscCon'],'.')
plt.xlabel('total income')
plt.ylabel('disposable consumption')

plt.figure()
plt.plot(t_inc,DataSubset['ClothCon'],'.')
plt.xlabel('total income')
plt.ylabel('cloting consumption')

plt.figure()
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



plt.figure()
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


DataSubset = drop_illogical(DataSubset,'disposable_income','total_income')
DataSubset = drop_illogical(DataSubset,'ClothCon','total_income')
DataSubset = drop_illogical(DataSubset,'DiscCon','total_income')

DataSubset['DiscCon'][DataSubset['DiscCon']<0] = np.nan     #negative spending on alc/cig/meal
DataSubset['ClothCon'][DataSubset['ClothCon']<0] = np.nan   #neg spend on clothing
DataSubset['njbhruw'][DataSubset['njbhruw']>7*24] = np.nan  # 

AreaData = pd.DataFrame()
NumSubjects = 0
for loc in LocList:
    CurData = DataSubset[DataSubset.keys()][DataSubset[LocVar]==loc]
    CurNum = CurData.shape[0]
    NumSubjects += CurNum
    print('{} participants in {}'.format(CurNum,LocNames[loc]))
    CurData['income_mean']=CurData['total_income'].mean()
    CurData['clothing_mean'] = CurData['ClothCon'].mean()
    CurData['disc_mean'] = CurData['DiscCon'].mean()
    
    CurData['income_std'] = CurData['total_income'].std()
    CurData['clothing_std'] = CurData['ClothCon'].std()
    CurData['disc_std'] = CurData['DiscCon'].std()
    
    CurData['income_median'] = CurData['total_income'].median()
    CurData['clothing_mmedian'] = CurData['ClothCon'].median()
    CurData['disc_median'] = CurData['DiscCon'].median()
    AreaData = pd.concat([AreaData,CurData])
print('{} subjects in total ({} non-capital-city subjects dropped)'.format(NumSubjects,DataSubset.shape[0]-NumSubjects)) 

plt.figure()
sns.pairplot(AreaData[['total_income','disposable_income','DiscCon','ClothCon',responseVar]])




#Extract the per-person variables in the current data set
PerPersVars = variables['Variable'][(variables[VariableSet]=='y')&(variables['per_person']=='y')]
#Find the roots of the per-person variables
VarRoots = set([val[:re.search('\d',val).start(0)] for val in PerPersVars])
per_num_var = 'nhhpno'
for root in VarRoots:
    AreaData = PerPersVar_condense(AreaData,root,per_num_var,DropSource=True)

 
makeplots = False
if makeplots:
    save_dir = 'Figures\\simple_hist\\'
    var_descriptions = dict(zip(list(variables['Variable']),list(variables['Label'])))
    for var_name in AreaData.keys()[4:]:
        data = list(AreaData[var_name])
        num_bins = np.sqrt(len(data)).round().astype(int)
        make_hist_fig(data,num_bins,save_dir,var_name,var_descriptions)
   
plt.figure()     
plt.hist(AreaData['nhwnetwn'][AreaData['nhwnetwn']<200000],bins=10,log=True)
plt.xlabel('total net worth for households w/ networth under 200k')


#Variables that have a very high proportion of missingness and/or are duplicated
#by another variable that appears to have less missingness
NoInfoToDrop = [
        'ncnsc_gu',
        'ncnsc_ge',
        'ncnsc_au',
        'ncnsc_ae',
        'ncnsc_fo',
        'ncnsc_ft',
        'ncnsc_ps',
        'ncnsc_fd',
        'ncnsc_pd',
        'ncnsc_fc',
        'nmdhagt',
        'nmdhamt',
        'nmdhafu',
        'nmdhash',
        'nmdhapm',
        'nmdhawc',
        'nmdhatv',
        'nmdhasm',
        'nmdhawh',
        'nmdharg',
        'nmdhaph',
        'nmdhahci',
        'nmdhawm',
        'nmdhaai',
        'nmdhamv',
        'nmdhamvi',
        'nmdhasa',
        'nmdhasl',
        'nmdhadt',
        'nmdhabp',
        'nmdhahaw']

Questionable_todrop = [
        'nchctc']

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
