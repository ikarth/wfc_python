# -*- coding: utf-8 -*-
"""
Created on Mon Mar 12 20:45:58 2018

@author: Isaac
"""

import random
import xml.etree.ElementTree as ET
import uuid

import common
import model
import overlapmodel
import learnmodel


class Program:
    def __init__(self):
        pass
    
    def Main(self):
        self.random = random.Random()
        xdoc = ET.ElementTree(file="learning.xml")
        counter = 1
        for xnode in xdoc.getroot():
            if("#comment" == xnode.tag):
                continue
            a_model = None
            
            name = xnode.get('name', "NAME")
            global hackstring 
            hackstring = name
            

        
            print("< {0} ".format(name), end='')
            if "learning" == xnode.tag:
                #print(xnode.attrib)
                add_samp_string = xnode.get('additional', "NONE")
                               
                add_samp = []
                if "NONE" != add_samp_string:
                    add_samp = add_samp_string.split(':')
                    
                add_peri = xnode.get('additional_periodic', "")

                a_model = learnmodel.LearningModel(int(xnode.get('width', 48)), int(xnode.get('height', 48)), xnode.get('name', "NAME"), int(xnode.get('N', 2)), common.string2bool(xnode.get('periodicInput', True)), common.string2bool(xnode.get('periodic', False)), int(xnode.get('symmetry', 8)), int(xnode.get('ground',0)), int(xnode.get('ground_end',0)), additional_samples=add_samp, additional_periodic=add_peri, antipatterns=xnode.get('antipatterns', '0'))
                pass
            elif "overlapping" == xnode.tag:
                #print(xnode.attrib)
                add_samp_string = xnode.get('additional', "NONE")
                               
                add_samp = []
                if "NONE" != add_samp_string:
                    add_samp = add_samp_string.split(':')
                    
                add_peri = xnode.get('additional_periodic', "")

                a_model = overlapmodel.OverlappingModel(int(xnode.get('width', 48)), int(xnode.get('height', 48)), xnode.get('name', "NAME"), int(xnode.get('N', 2)), common.string2bool(xnode.get('periodicInput', True)), common.string2bool(xnode.get('periodic', False)), int(xnode.get('symmetry', 8)), int(xnode.get('ground',0)), int(xnode.get('ground_end',0)), additional_samples=add_samp, additional_periodic=add_peri, antipatterns=xnode.get('antipatterns', '0'))
                pass
            elif "simpletiled" == xnode.tag:
                    print("> ", end="\n")
                    continue
            else:
                    continue
        
        
        
            for i in range(0, int(xnode.get("screenshots", 2))):
                for k in range(0, 10):
                    print("> ", end="")
                    seed = self.random.random()
                    finished = a_model.Run(seed, int(xnode.get("limit", 0)))
                    if finished:
                        print("DONE")
                        a_model.Graphics().save("{0}_{1}_{2}_{3}.png".format(counter, name, i, uuid.uuid4()), format="PNG")
                        break
                    else:
                        print("CONTRADICTION")
            counter += 1
        
    
prog = Program()    
prog.Main()

#a_model = OverlappingModel(8, 8, "Chess", 2, True, True, 8,0)
#a_model = OverlappingModel(48, 48, "Hogs", 3, True, True, 8,0)
#gseed = random.Random()
#finished = a_model.Run(364, 0)
#if(finished):
    #test_img = a_model.Graphics()
#else:
#    print("CONTRADICTION")
#test_img
