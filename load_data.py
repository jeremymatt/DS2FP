# -*- coding: utf-8 -*-
"""
Created on Sun Apr 28 22:15:24 2019

@author: jmatt
"""
import pandas as pd
import urllib


def load_data(data_fn,variables_fn,URL,VariableSet,Drop_extra=True):
    """
    Takes the filename of the data file (data_fn) and the path/filename of the
    variables description file, loads them, and returns the associated pandas
    dataframes
    
    INPUTS
        data_fn - path/filename of the data file
        variables_fn - path/filename of a file describing the variables
        URL - http address of download link for the data file (if not available
              locally)
        Drop_extra - (default: True) drop:
                                        rows where the response variable is missing
                                        columns not in the selected variable list
        
    OUTPUTS
        DataSubset - pandas dataframe containing the data
        variables - pandas dataaframe containing variable metadata
        responseVar - the response variable column name
    """
    
    #If the data file exists locally, load it using pandas
    breakhere=1
    try: df = pd.read_csv(data_fn)
    except: 
        #If the data file does not exist locally, download and save locally, then open
        print('Downloading data file (~430mb)')
        urllib.request.urlretrieve(URL,data_fn)
        print('Download Complete')
        df = pd.read_csv(data_fn)
        
    print('\n************\nNOTE RE: MIXED TYPE WARNING - These variables contain:')
    print('    294 - HQ ID of person providing most of the information for this form')
    print('    295 - HQ ID of 1st Other providing information for this form')
    print('    701 - HF2 Cross wave ID (xwaveid) - 0001')
    print('    702 - HF2 Cross wave ID (xwaveid) - 0002')
    print('These variables are not used in this project so the mixed type warning can be ignored\n************')
    
    #Read the variables descriptor file
    variables = pd.read_csv(variables_fn)
    
    #extract the name of the response variable
    responseVar = variables['Variable'][variables['Response']=='y'].values[0]
    
    if Drop_extra:
        #Store the current number of recores
        NumRecords = df.shape[0]
        #remove entries with negative response variables (non-responding person, N/A, not asked, etc)
        DataSubset = pd.DataFrame(df[df[responseVar]>-1])
        #Notify the user how of how many records were dropped
        print('\n{} records dropped due to lack of response variable (non-responding person, N/A, etc)'.format(NumRecords-DataSubset.shape[0]))
        
        #Extract the variable names for the variable set being analyzed
        KeepVars = variables['Variable'][variables[VariableSet]=='y']
        
        #Keep only the variables in the variable set
        DataSubset = DataSubset[KeepVars]
        
    else:
        #Return all variables and records
        DataSubset = df
        
    return DataSubset,variables,responseVar
        