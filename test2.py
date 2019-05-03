#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  3 10:23:47 2019

@author: jmatt
"""

import pygraphviz as pgv
G=pgv.AGraph()
G=pgv.AGraph(strict=False,directed=True)
d={'1': {'2': None}, '2': {'1': None, '3': None}, '3': {'2': None}}
A=pgv.AGraph(d)
A.layout()
A.draw('test.png')
