# -*- coding: utf-8 -*-
"""
Created on Mon Apr 29 13:32:28 2019

@author: jmatt
"""
import pandas as pd
def extract_areas(DataSubset,LocNames,LocVar):
    """
    Keep only records of people in denser urban areas (the values in LocNames)
    
    INPUTS
        DataSubset - pandas dataframe of the data
        LocNames - dict of location names as values and location numeric IDs as keys
        LocVar - the header name of the location variable
        
    OUTPUS
        AreaData - A pandas dataframe containing only data from denser areas
    """
    
    #Extract the numberic 
    LocList = LocNames.keys()
    
    #Init empty dataframe
    AreaData = pd.DataFrame()
    #Init subjects counter
    NumSubjects = 0
    for loc in LocList:
        #extract the data for the current area
        CurData = DataSubset[DataSubset.keys()][DataSubset[LocVar]==loc]
        #Find the number of records for the current area
        CurNum = CurData.shape[0]
        #Update the number of subjects
        NumSubjects += CurNum
        #let user know how many subjects there are in the current loc
        print('{} participants in {}'.format(CurNum,LocNames[loc]))
        #Extract and store the variable means
        CurData['income_mean']=CurData['total_income'].mean()
        CurData['clothing_mean'] = CurData['total_clothing'].mean()
        CurData['disc_mean'] = CurData['total_disc'].mean()
        
        #Extract and store the variable standard deviations
        CurData['income_std'] = CurData['total_income'].std()
        CurData['clothing_std'] = CurData['total_clothing'].std()
        CurData['disc_std'] = CurData['total_disc'].std()
        
        #Extract and store the variable medians
        CurData['income_median'] = CurData['total_income'].median()
        CurData['clothing_median'] = CurData['total_clothing'].median()
        CurData['disc_median'] = CurData['total_disc'].median()
        #Append the current area's data to the output dataframe
        AreaData = pd.concat([AreaData,CurData])
    #Give number of subjects info to the user
    print('{} subjects in total ({} non-capital-city subjects dropped)'.format(NumSubjects,DataSubset.shape[0]-NumSubjects)) 

    return AreaData