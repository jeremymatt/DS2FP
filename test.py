# -*- coding: utf-8 -*-
"""
Created on Wed Apr 24 22:04:49 2019

@author: jmatt
"""


from PerPersVar_condense import PerPersVar_condense

import pandas as pd


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
print('{} subjects in total'.format(NumSubjects)) 
 

#Extract the per-person variables
PerPersVars = variables['Variable'][(variables[VariableSet]=='y')&(variables['per_person']=='y')]
#Find the roots of the per-person variables
VarRoots = set([val[:re.search('\d',val).start(0)] for val in PerPersVars])
per_num_var = 'nhhpno'
for root in VarRoots:
    AreaData = PerPersVar_condense(AreaData,root,per_num_var,DropSource=True)   
