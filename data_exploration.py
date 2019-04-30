# -*- coding: utf-8 -*-
"""
Created on Sun Apr 28 22:54:56 2019

@author: jmatt
"""
import matplotlib.pyplot as plt

def data_exploration(DataSubset,responseVar,DiscVars):
    """
    Performs preliminary exploration of the dataset
    
    IMPUTS
        DataSubset - pandas dataframe of the data
        responseVar - the column name of the response variable
        DiscVar - the column names of the discretionary spending variables
        
    OUTPUT
        None
    """
    
    
    plt.figure()
    plt.hist(DataSubset[responseVar],bins=11)
    plt.xlabel('Subjective Wellbeing')
    
    
    var = 'nhifeft' #total income
    #var2 = 'nhifdit' #Disposable income
    var_p = var+'p'
    var_n = var+'n'
    
    plt.figure()
    plt.hist(DataSubset[var_p]-DataSubset[var_n],log=True,bins=100)
    plt.xlabel('Total Income')
    DataSubset[var_p].max()
    DataSubset[var_n].mode()
    
    #Check for differences between imputed and non-imputed variables
    dv1 = list(DiscVars) #non-imputed
    dv2 = [val+'i' for val in dv1]  #imputed
    print('\nCheck for differences between imputed and non-imputed variables')
    for i in range(3):
        test = DataSubset[dv1[i]]-DataSubset[dv1[i]]
        print('{} minus {}==> min:{} max:{}'.format(dv1[i],dv2[i],test.min(),test.max()))
    
       
    
    
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
    
    plt.figure()
    plt.plot(d_inc,t_inc,'.')
    plt.xlabel('Annual disposable income ($)')
    plt.ylabel('Annual total income ($)')
    
    plt.figure()
    plt.plot(t_inc,DataSubset['DiscCon'],'.')
    plt.ylabel('Annual spending on alcohol/cigarettes/meals-eaten-out ($)')
    plt.xlabel('Annual total income ($)')
    
    plt.figure()
    plt.plot(t_inc,DataSubset['ClothCon'],'.')
    plt.ylabel('Annual spending on clothing ($)')
    plt.xlabel('Annual total income ($)')
    
    plt.figure()
    plt.plot(DataSubset['DiscCon'],DataSubset['ClothCon'],'.')
    plt.ylabel('Annual spending on clothing ($)')
    plt.xlabel('Annual spending on alcohol/cigarettes/meals-eaten-out ($)')