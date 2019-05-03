# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 23:21:27 2019

@author: jmatt
"""
import matplotlib.pyplot as plt
import numpy as np
import os

def make_hist_fig(data,num_bins,save_dir,var_name,var_descriptions):
    """
    Generates a histogram of the input data and saves the result to the specified 
    directory.
    
    INPUTS
        data - input dataframe of all data
        num_bins - the number of bins to use when generating the histograme
        save_dir - the directory to save the histograms in
        var_name - the name of the variable to generate the histograme for
        var_descriptions - Descriptive names of variables for histogram x axis
        
    OUTPUTS
        none
    """
    
    #Init figure    
    fig, ax1 = plt.subplots(figsize=(13, 11), dpi= 80, facecolor='w', edgecolor='k')
    ax1.hist(data,bins=num_bins)
    
    #Add x and y labels
    ax1.set_ylabel('Count')
    var_desc = '{} ==> {}'.format(var_name,var_descriptions[var_name])
    if len(var_desc)>80:
        var_desc = var_desc[:80]+'\n'+var_desc[80:]
    ax1.set_xlabel(var_desc)
    
    #Add the title string
    titlestr4 = '\n{} points binned into {} bins'.format(len(data),num_bins)
    title_str=titlestr4+'\nMean:{:.3f}, median:{:.3f}'.format(np.mean(data),np.median(data))
    plt.title(title_str)
    
    
    font_size = 20
    #Resize the fonts for all items in axis 1
    for item in ([ax1.title, ax1.xaxis.label, ax1.yaxis.label] +
             ax1.get_xticklabels() + ax1.get_yticklabels()):
        item.set_fontsize(font_size)
    
    #Output the histogram to disk
    save_dir = os.path.normpath(save_dir+var_name+'.png')
    fig.savefig(save_dir)
    plt.close(fig)