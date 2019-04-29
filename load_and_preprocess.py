# -*- coding: utf-8 -*-
"""
Created on Mon Apr 29 15:15:59 2019

@author: jmatt
"""


import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
import pickle as pkl

#JEM functions
from PerPersVar_condense import PerPersVar_condense
from drop_illogical import drop_illogical
from make_hist_fig import make_hist_fig
from load_data import load_data
from data_exploration import data_exploration
from extract_areas import extract_areas


def load_and_preprocess(data_fn,variables_fn,VariableSet,URL,Drop_extra):
    """
    Loads the data, performs pre-processing actions to prepare the data for
    analysis, then saves the relevant data in a pickle file
    
    INPUTS
        data_fn - The location of the data file
        variables_fn - The location of the variables metadata file
        VariableSet - the (user selected) subset of variables to use in the analyss
        URL - the web address of the data (used if not saved locally)
        Drop_extra - flag to: Drop records with missing response variable
                              Drop columns not in the selected set of variables
    
    OUTPUTS
        Pickle file saved in the same directory as data_fn
    """
        
        
    
    #Load the data and begin processing
    DataSubset,variables,responseVar=load_data(data_fn,variables_fn,URL,VariableSet,Drop_extra)
    
    
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
    
    DoExplore = True
    if DoExplore:
        data_exploration(DataSubset,responseVar,DiscVars)
    
    
    plt.figure()
    sns.pairplot(DataSubset[['total_income','disposable_income','DiscCon','ClothCon',responseVar]])
    #
    #t = DataSubset[DataSubset.keys()][DataSubset['total_income']==1457066]
    #todrop = t.index
    #
    #DataSubset.drop(todrop,inplace=True)
    
    
    NumRecords = DataSubset.shape[0]
    #Drop the records with untrustworth disposable income data
    t = DataSubset[DataSubset.keys()][DataSubset['disposable_income']==837797]
    todrop = t.index
    DataSubset.drop(todrop,inplace=True)
    print('\n{} records dropped due to unexpected disposable income of exactly $837,797 over multiple households'.format(NumRecords-DataSubset.shape[0]))
    
    
    
    plt.figure()
    sns.pairplot(DataSubset[['total_income','disposable_income','DiscCon','ClothCon',responseVar]])
    
    
    
    """
    Drop source variables used to create other variables
    """
    #Drop the discretionary spending source variables
    DataSubset.drop(DiscVars,axis='columns',inplace=True)
    #Drop the clothing spending source variables
    DataSubset.drop(ClothVars,axis='columns',inplace=True)
    #Drop total income and discretionary income source columns
    DataSubset.drop(['nhifeftp','nhifeftn','nhifditp','nhifditn'],axis='columns',inplace=True)
    #Drop records where economic data is questionable
    DataSubset = drop_illogical(DataSubset,'disposable_income','total_income')
    DataSubset = drop_illogical(DataSubset,'ClothCon','total_income')
    DataSubset = drop_illogical(DataSubset,'DiscCon','total_income')
    #Set negative values to NAN (these entries may be flags)
    DataSubset['DiscCon'][DataSubset['DiscCon']<0] = np.nan     #negative spending on alc/cig/meal
    DataSubset['ClothCon'][DataSubset['ClothCon']<0] = np.nan   #neg spend on clothing
    DataSubset['njbhruw'][DataSubset['njbhruw']>7*24] = np.nan  # number of hours worked per week greater than number of hours in a week
    
    #name of the location variable
    LocVar = 'nhhsgcc'
    
    #dict of Names of areas to numberic designation
    LocVals = {'Sydney':11,
               'Melbourne':21,
               'Brisbane':31,
               'Adelaide':41,
               'Perth':51}
    
    LocList = list(LocVals.values())
    LocName = list(LocVals.keys())
    
    #dict of numeric area designations to area names
    LocNames = dict(zip(LocList,LocName))
    
    #Keep only the data from urban areas
    AreaData = extract_areas(DataSubset,LocNames,LocVar)
    
    plt.figure()
    sns.pairplot(AreaData[['total_income','disposable_income','DiscCon','ClothCon',responseVar]])
    
    
    
    
    #Extract the per-person variables in the current data set
    PerPersVars = variables['Variable'][(variables[VariableSet]=='y')&(variables['per_person']=='y')]
    #Find the roots of the per-person variables
    VarRoots = set([val[:re.search('\d',val).start(0)] for val in PerPersVars])
    per_num_var = 'nhhpno'
    for root in VarRoots:
        AreaData = PerPersVar_condense(AreaData,root,per_num_var,DropSource=True)
    
    #make histograms of each variable
    makeplots = True
    if makeplots:
        save_dir = 'Figures\\simple_hist\\'
        var_descriptions = dict(zip(list(variables['Variable']),list(variables['Label'])))
        for var_name in AreaData.keys()[4:]:
            data = list(AreaData[var_name])
            num_bins = np.sqrt(len(data)).round().astype(int)
            make_hist_fig(data,num_bins,save_dir,var_name,var_descriptions)
    
    
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
    
    #drop variables with no useable info
    AreaData.drop(NoInfoToDrop,axis='columns',inplace=True)
    
    #Build the save file string
    save_file = '{}_{}_processed.pkl'.format(data_fn.split('.')[0],VariableSet)
    
    #Open the file in write binary mode
    file = open(save_file,'ab')
    #make a tuple of the variables to retain
    ToSave = (AreaData,variables,LocVals,LocNames,LocVar)
    
    #Save the processed data file
    pkl.dump(ToSave,file)
    #close the file
    file.close()

    