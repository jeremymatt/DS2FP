#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  3 20:44:58 2019

@author: jmatt
"""

import dowhy.api
import dowhy.datasets

data = dowhy.datasets.linear_dataset(beta=5,
    num_common_causes=1,
    num_instruments = 0,
    num_samples=1000,
    treatment_is_binary=True)

# data['df'] is just a regular pandas.DataFrame
data['df'].causal.do(x='v',
                     variable_types={'v': 'b', 'y': 'c', 'X0': 'c'},
                     outcome='y',
                     common_causes=['X0']).groupby('v').mean().plot(y='y', kind='bar')