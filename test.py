# -*- coding: utf-8 -*-
"""
Created on Wed Apr 24 22:04:49 2019

@author: jmatt
"""


var = ['total_income','total_clothing','total_disc','nlosat']
bins = [50,50,50,11]

tpls = list(zip(var,bins))

for var_name,num_bins in tpls:
    data=AreaData[['nhhsgcc',var_name]]
    make_hist_fig(data,num_bins,save_dir,var_name,var_descriptions,by_area=True)
    
    
plt.plot(AreaData['total_income'],AreaData['disposable_income'],'.')
plt.grid()
plt.xlabel('total annual household income($)')
plt.ylabel('total disposable annual household income($)')
