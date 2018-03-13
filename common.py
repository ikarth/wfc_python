# -*- coding: utf-8 -*-
"""
Created on Mon Mar 12 20:43:12 2018

@author: Isaac
"""

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def StuffRandom(source_array, random_value):
    a_sum = sum(source_array)
    
    if 0 == a_sum:
        for j in range(0, len(source_array)):
            source_array[j] = 1
        a_sum = sum(source_array)
    for j in range(0, len(source_array)):
        source_array[j] /= a_sum
    i = 0
    x = 0
    while (i < len(source_array)):
        x += source_array[i]
        if random_value <= x:
            return i
        i += 1
    return 0
    
def StuffPower(a, n):
    product = 1
    for i in range(0, n):
        product *= a
    return product
    
# TODO: finish StuffGet
def StuffGet(xml_node, xml_attribute, default_t):
    s = ""
    if s == "":
        return default_t
    return s
    
def string2bool(strn):
    if isinstance(strn, bool):
        return strn
    return strn.lower() in ["true"]
