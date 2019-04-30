# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 22:59:05 2019

@author: jmatt
"""

def drop_illogical(df,var1,var2):
    """
    Drops records from the dataframe df is var1 is greater than var2
    For example, if var1 is spending on clothing and var2 is total income
    it is not logical that var1 is greater than var2
    """
    #Mask the illogical entries
    mask = df[var1]>df[var2]
    #Record the number of entries
    NumRecords = df.shape[0]
    #drop the illogical entries
    df = df[df.keys()][~mask]
    #Notify the user how many records were dropped
    print('{} records dropped because {} is greater than {}'.format(NumRecords-df.shape[0],var1,var2))
    
    return df
