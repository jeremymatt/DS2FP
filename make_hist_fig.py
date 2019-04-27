# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 23:21:27 2019

@author: jmatt
"""
import matplotlib.pyplot as plt
import numpy as np

def make_hist_fig(data,num_bins,save_dir,var_name,var_descriptions):
    """
    
    """
    
    fig, ax1 = plt.subplots(figsize=(13, 11), dpi= 80, facecolor='w', edgecolor='k')
    
    ax1.hist(data,bins=num_bins)
    
    #Add x and y labels
    ax1.set_ylabel('Count')
#    ax1.set_ylim(0,175)
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
        
    fig.savefig(save_dir+var_name+'.png')
    plt.close(fig)