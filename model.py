# -*- coding: utf-8 -*-

# 
# The MIT License(MIT)
# Copyright Isaac Karth 2017
# Based on WaveFunctionCollapse in C#, which is Copyright(c) mxgmn 2016.
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# The software is provided "as is", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the software.
#

import common

import math
import random

try:
    import Image
except ImportError:
    from PIL import Image

hackstring = ""
hackcount = 0

  
class Model:
    def __init__(self, width, height):
        #initialize

        
        self.stationary = []
                

        self.FMX = width
        self.FMY = height
        self.T = 2
        #self.limit = 0
        
        self.rng = random.Random() #todo: set rng

        self.wave = [[[False for _ in range(self.T)] for _ in range(self.FMY)] for _ in range(self.FMX)]
        self.changes = [[False for _ in range(self.FMY)] for _ in range(self.FMX)]
        self.observed = None#[[0 for _ in range(self.FMY)] for _ in range(self.FMX)]

        self.log_prob = 0
        self.log_t = math.log(self.T)
        
        self.observe_count = 0
        
        self.count_prop_passes = 0
        
        self.SAVE_IN_PROGRESS = False

    def Observe(self):
        self.observe_count += 1
        observed_min = 1e+3
        observed_sum = 0
        main_sum = 0
        log_sum = 0
        noise = 0
        entropy = 0
        
        argminx = -1
        argminy = -1
        amount = None
        w = []
        
        # Find the point of minimum entropy
        for x in range(0, self.FMX):
            for y in range(0, self.FMY):
                if self.OnBoundary(x, y):
                    pass
                else:
                    w = self.wave[x][y]
                    amount = 0
                    observed_sum = 0
                    t = 0
                    while t < self.T:
                        if w[t]:
                            amount += 1
                            observed_sum += self.stationary[t]
                        t += 1
                    if 0 == observed_sum:
                        return False
                    noise = 1e-6 * self.rng.random()
                    if 1 == amount:
                        entropy = 0
                    elif self.T == amount:
                        entropy = self.log_t
                    else:
                        main_sum = 0
                        log_sum = math.log(observed_sum)
                        t = 0
                        while t < self.T:
                            if w[t]:
                                main_sum += self.stationary[t] * self.log_prob[t]
                            t += 1
                        entropy = log_sum - main_sum / observed_sum
                    if entropy > 0 and (entropy + noise < observed_min):
                        observed_min = entropy + noise
                        argminx = x
                        argminy = y
                    
        # No minimum entropy, so mark everything as being observed...
        if (-1 == argminx) and (-1 == argminy):
            self.observed = [[0 for _ in range(self.FMY)] for _ in range(self.FMX)]
            for x in range(0, self.FMX):
                self.observed[x] = [0 for _ in range(self.FMY)]
                for y in range(0, self.FMY):
                    for t in range(0, self.T):
                        if self.wave[x][y][t]:
                            self.observed[x][y] = t
                            break
            return True
        
        # A minimum point has been found, so prep it for propogation...
        distribution = [0 for _ in range(0,self.T)]
        for t in range(0,self.T):
            distribution[t] = self.stationary[t] if self.wave[argminx][argminy][t] else 0
        r = common.StuffRandom(distribution, self.rng.random())
        for t in range(0,self.T):
            self.wave[argminx][argminy][t] = (t == r)
        self.changes[argminx][argminy] = True
        return None

    def Run(self, seed, limit):
        self.log_t = math.log(self.T)
        self.log_prob = [0 for _ in range(self.T)]
        for t in range(0,self.T):
            self.log_prob[t] = math.log(self.stationary[t])
        self.Clear()
        self.rng = random.Random()
        self.rng.seed(seed)
        l = 0
        while (l < limit) or (0 == limit): # if limit == 0, then don't stop
            l += 1
            result = self.Observe()
            if None != result:
                return result
            pcount = 0
            presult = True
            global hackcount

            while(presult):
                presult = self.Propagate()
                
                if self.SAVE_IN_PROGRESS:
                    self.Graphics().save("in_progress_{0}_{1}.png".format(hackstring, hackcount), format="PNG")
                hackcount += 1

                #print("Propagate: {0}".format(pcount))
                pcount += 1
        return True
            
        
    def Propagate(self):
        return False
        
    def Clear(self):
        for x in range(0,self.FMX):
            for y in range(0, self.FMY):
                for t in range(0, self.T):
                    self.wave[x][y][t] = True
                self.changes[x][y] = False
    
                
    def OnBoundary(self, x, y):
        return True # Abstract, replaced in child classes
        
    def Graphics(self):
        return Image.new("RGB",(self.FMX, self.FMY),(0,0,0))
    
                    
class SimpleTiledModel(Model):
    def __init__(self, width, height, name, subset_name, periodic_value, black_value):
        super( OverlappingModel, self).__init__(width, height)
        self.propagator = [[[]]]
        self.tiles = []
        self.tilenames = []
        self.tilesize = 0
        self.black = False
        self.periodic = periodic_value
        self.black = black_value
        

        

#def getNextRandom():
#    return random.random()
    
    
