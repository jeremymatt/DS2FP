# -*- coding: utf-8 -*-
"""
Created on Tue Apr 30 18:25:37 2019

@author: jmatt
"""

def condense_deprivation(df,variables,drop_vars=True):
    """
    Generates a condensed material deprivation variable given a list of flags 
    of material deprivation in the 'm_dep' column in the variables dataframe.
    For the source deprivation columns 1=yes and 2=no.  The condensed 
    deprivation variable is the number of deprivation variables equal to 2
    for each individual
    
    INPUTS
        df - the input dataframe containing the data
        variables - the dataframe of variable metadata
        drop_vars - boolean True=drop source variables (default)
    
    OUTPUTS
        df - the output dataframe
    """
    
    #Extract a list of the deprivation variables
    DeprivationVars = variables['Variable'][variables['m_dep']=='y']
    #Confirm that all deprivation vars are in the dataframe
    DeprivationVars = [val for val in DeprivationVars if val in set(df.keys())]
    #init material deprivation variable
    df['mat_dep'] = 0
    for var in DeprivationVars:
        #For each deprivation variable equal to 2, increment the material dep variable
        df['mat_dep'][df[var] == 2]+=1
        
    if drop_vars:
        #Drop source variables
        df.drop(DeprivationVars,axis='columns',inplace=True)
    
    return df