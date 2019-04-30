# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 13:16:41 2019

@author: jmatt
"""
import re
def PerPersVar_condense(df,var_root,per_num_var,DropSource=True):
    """
    Takes a dataframe,  a 'per-person variable' root (IE nhgage as the root
    for nhgage1 through nhgage20), and the name of the person-number variable
    and condenses into a single column for the specific person in question.
    After condensing and adding to the dataframe, the source variables are 
    removed unless DropSource is set to False
    """
    #Extract the value specific to each subject and put in a list
    ValList = [df['{}{}'.format(var_root,df[per_num_var][i])][i] for i in df.index]
    #If drop source
    if DropSource:
        #build a list of the source variables
        ToDrop = [val for val in df.keys() if bool(re.search(var_root,val))]
        #Drop the source variables
        df.drop(ToDrop,axis='columns',inplace=True)
    #Add the extracted values as a column in the dataframe
    df[var_root] = ValList
    breakhere=1
    
    return df