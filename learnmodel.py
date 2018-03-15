# -*- coding: utf-8 -*-
"""
Created on Mon Mar 12 20:41:23 2018

@author: Isaac
"""

import model
import common

import collections

from sklearn import tree

try:
    import Image
except ImportError:
    from PIL import Image

class LearningModel(model.Model):
        
    def __init__(self, width, height, name, N_value = 2, periodic_input_value = True, periodic_output_value = False, symmetry_value = 8, ground_value = 0, ground_end = 0, additional_samples=[], additional_periodic="", antipatterns=""):
        """
        Initializes the model.
        """
        super(LearningModel, self).__init__(width, height)
        self.propagator =  [[[[]]]]
        self.whitelist =   [[[[]]]]
        self.blacklist =   [[[[]]]]
        self.possiblelist =   [[[[]]]]
        self.allowedlist = [[[[]]]]
        self.disallowedlist = [[[[]]]]
        self.observedlist= [[[[]]]]
        
        self.N = N_value
        self.periodic = periodic_output_value
        self.bitmaps = [Image.open("samples/{0}.png".format(name)).convert("RGBA")]
        self.SMXs = [self.bitmaps[0].size[0]]
        self.SMYs = [self.bitmaps[0].size[1]]
        self.samples = [[[0 for _ in range(self.SMYs[0])] for _ in range(self.SMXs[0])]]
        
        self.antipattern_flags = [int(x) for x in list(antipatterns.ljust(len(additional_samples) + 1, '0'))]
        #print(self.antipattern_flags)
        
        add_periodic = 0
        if periodic_input_value:
            add_periodic = 1
        self.periodic_flags = [add_periodic] + [int(x) for x in list(additional_periodic.ljust(len(additional_samples), str(add_periodic)))]
        #print(self.periodic_flags)

        for additional in additional_samples:
            self.bitmaps.append(Image.open("samples/{0}.png".format(additional)).convert("RGBA"))
            add_index = len(self.bitmaps)-1
            self.SMXs.append(self.bitmaps[add_index].size[0])
            self.SMYs.append(self.bitmaps[add_index].size[1])
            self.samples.append([[0 for _ in range(self.SMYs[add_index])] for _ in range(self.SMXs[add_index])])
        
#        self.antibitmaps = []
#        self.aSMXs = []
#        self.aSMYs = []
#        self.antisamples = []
#        for anti in antipatterns:
#            self.antibitmaps.append(Image.open("samples/{0}.png".format(anti)))
#            add_index = len(self.antibitmaps)-1
#            self.SMXs.append(self.antibitmaps[add_index].size[0])
#            self.SMYs.append(self.antibitmaps[add_index].size[1])
#            self.antisamples.append([[0 for _ in range(self.aSMYs[add_index])] for _ in range(self.aSMXs[add_index])])
            
            
        
        self.colors = []
        for samp_n in range(len(self.bitmaps)):
            for y in range(0, self.SMYs[samp_n]):
                for x in range(0, self.SMXs[samp_n]):
                    a_color = self.bitmaps[samp_n].getpixel((x, y))
                    color_exists = [c for c in self.colors if c == a_color]
                    if len(color_exists) < 1:
                        self.colors.append(a_color)
                    samp_result = [i for i,v in enumerate(self.colors) if v == a_color]
                    self.samples[samp_n][x][y] = samp_result
                
        #for c in self.colors:
        #    print(c)
        
        self.color_count = len(self.colors)
        self.W = common.StuffPower(self.color_count, self.N * self.N)
        
        # The pattern matrix, as an array of arrays.
        self.patterns= [[]]
        #self.ground = 0
        
        # Additional samples can individually be marked as periodic/non-periodic
        #periodic_input_values = [periodic_input_value]
        #for _ in range(len(self.bitmaps)):
        #    periodic_input_values.append(periodic_input_value)
        #for idx_peri, peri in enumerate(additional_periodic):
        #     periodic_input_values[idx_peri + 1] = ((1 == peri) or ('T' == peri) or ('True' == peri))
        

        def FuncPattern(passed_func):
            result = [0 for _ in range(self.N * self.N)]
            for y in range(0, self.N):
                for x in range(0, self.N):
                    result[x + (y * self.N)] = passed_func(x, y)
            return result
            
        pattern_func = FuncPattern
            
        def PatternFromSample(x, y, n=0):
            def innerPattern(dx, dy):
                return self.samples[n][(x + dx) % self.SMXs[n]][(y + dy) % self.SMYs[n]]
            return pattern_func(innerPattern)
        def Rotate(p):
            '''
            Returns a rotated version of the pattern.
            '''
            return FuncPattern(lambda x, y: p[self.N - 1 - y + x * self.N])
        def Reflect(p):
            '''
            Returns a reflected version of the pattern.
            '''
            return FuncPattern(lambda x, y: p[self.N - 1 - x + y * self.N])
            
        def Index(p):
            '''
            Converts a color index into a powers-of-two representation for
            bytewise storage.
            '''
            result = 0
            power = 1
            for i in range(0, len(p)):
                result = result + (sum(p[len(p) - 1 - i]) * power)
                power = power * self.color_count
            return result

                                    
            
        def PatternFromIndex(ind):
            '''
            Takes a pattern index and returns the pattern byte array.
            '''
            residue = ind
            power = self.W
            result = [None for _ in range(self.N * self.N)]
            for i in range(0, len(result)):
                power = power / self.color_count
                count = 0
                while residue >= power:
                    residue = residue - power
                    count = count + 1
                result[i] = count
            return result
            
        self.weights = collections.Counter()
        ordering = []
        antiordering = []
        self.anti_adjacency = []
        
        for samp_n in range(len(self.bitmaps)):
            ylimit = self.SMYs[samp_n] - self.N + 1
            xlimit = self.SMXs[samp_n] - self.N + 1
            if 1 == self.periodic_flags[samp_n]:
                ylimit = self.SMYs[samp_n]
                xlimit = self.SMXs[samp_n]
            for y in range (0, ylimit):
                for x in range(0, xlimit):
                    ps = [0 for _ in range(8)]
                    ps[0] = PatternFromSample(x,y,samp_n)
                    ps[1] = Reflect(ps[0])
                    ps[2] = Rotate(ps[0])
                    ps[3] = Reflect(ps[2])
                    ps[4] = Rotate(ps[2])
                    ps[5] = Reflect(ps[4])
                    ps[6] = Rotate(ps[4])
                    ps[7] = Reflect(ps[6])
                    for k in range(0,symmetry_value):
                        ind = Index(ps[k])
                        common.logger.info('pattern: ' + str(ps[k]) + ' index ' + str(ind))
                        if 1 == self.antipattern_flags[samp_n]:
                            if not ind in antiordering:
                                antiordering.append(ind)
                        indexed_weight = collections.Counter({ind : 1})
                        self.weights = self.weights + indexed_weight
                        if not ind in ordering:
                            ordering.append(ind)
                            
        #for indo, o in enumerate(ordering):
        #    print(indo, o, PatternFromIndex(o))                
        self.T = len(self.weights)
        self.ground = (int((ground_value + self.T) % self.T), int((ground_value + self.T) % self.T))#(102,106)# int((ground_value + self.T) % self.T)
        if ground_end > 0 and None != ground_end:
            self.gound = (ground_value, ground_end)
        #print('self.ground',self.ground)
        
        self.patterns = [[None] for _ in range(self.T)]
        self.stationary = [None for _ in range(self.T)]
        self.propagator = [[[[0]]] for _ in range(2 * self.N - 1)]
        self.whitelist =  [[[[0]]] for _ in range(2 * self.N - 1)]
        self.blacklist =  [[[[0]]] for _ in range(2 * self.N - 1)]
        self.possiblelist = [[[[0]]] for _ in range(2 * self.N - 1)]
        self.allowedlist = [[[[0]]] for _ in range(2 * self.N - 1)]
        self.disallowedlist = [[[[0]]] for _ in range(2 * self.N - 1)]
        self.observedlist = [[[[0]]] for _ in range(2 * self.N - 1)]
        
        self.antipatterns = [[None] for _ in antiordering]
        
        for w in antiordering:
            self.antipatterns.append(PatternFromIndex(w))
        
        counter = 0
        for w in ordering:
            self.patterns[counter] = PatternFromIndex(w)
            self.stationary[counter] = self.weights[w]
            counter += 1
        
        
        
        for samp_n in range(len(self.bitmaps)):
            if 1 == self.antipattern_flags[samp_n]:
                #print('sample #',samp_n)
                ylimit = self.SMYs[samp_n] - self.N + 1
                xlimit = self.SMXs[samp_n] - self.N + 1
                if 1 == self.periodic_flags[samp_n]:
                    ylimit = self.SMYs[samp_n]
                    xlimit = self.SMXs[samp_n]
                #print('limits',xlimit, ylimit, self.periodic_flags[samp_n])
                for py in range (0, ylimit):
                    for px in range(0, xlimit):
                        pattern_one = PatternFromIndex(Index(PatternFromSample(px,py,samp_n)))
                        #print('pattern_one', pattern_one)
                        for tx in range(1 - self.N, self.N):
                            for ty in range(1 - self.N,self.N):
                                #print(tx,ty)
                                if not (tx == 0 and ty == 0):
                                    if (1 == self.periodic_flags[samp_n]) or ((px + tx >= 0) and (py + ty >= 0) and (px + tx < xlimit) and (py + ty < ylimit)):
                                        pattern_two = PatternFromIndex(Index(PatternFromSample(px+tx,py+ty,samp_n)))
                                        #print('pattern_two', pattern_two, px + tx, py + ty, tx, ty)
                                        self.anti_adjacency.append((pattern_one, pattern_two, (tx, ty)))
                                        #print('create antipattern', (pattern_one, pattern_two, (tx, ty)))
            
        for x in range(0, self.FMX):
            for y in range(0, self.FMY):
                self.wave[x][y] = [False for _ in range(self.T)]
                
                
        def Disallowed(p1, p2, dx, dy):
            #print(p1,p2,'\n---\n')
            for anti_adj in self.anti_adjacency:
                #print(anti_adj)
                if (anti_adj[0] == p1 and anti_adj[1] == p2):
                    if dx == anti_adj[2][0] and dy == anti_adj[2][1]:
                        #print('antipattern:',p1,p2,dx,dy,'\n',anti_adj,'\n')
                        return True
            return False
            
        def Agrees(p1, p2, dx, dy):
            ifany = True
            xmin = dx
            xmax = self.N
            if dx < 0:
                xmin = 0
                xmax = dx + self.N
            ymin = dy
            ymax = self.N
            if dy < 0:
                ymin = 0
                ymax = dy + self.N
            for y in range(ymin, ymax):
                for x in range(xmin, xmax):
                    if p1[x + self.N * y] != p2[x - dx + self.N * (y - dy)]:
                        common.logger.debug(p1[x + self.N * y] != p2[x - dx + self.N * (y - dy)])
                        ifany = False
                        #return False
            return ifany
            #return True

        # create total whitelist
        for x in range(0, 2 * self.N - 1):
            self.possiblelist[x] = [[[0]] for _ in range(2 * self.N - 1)]
            for y in range(0, 2 * self.N - 1):
                self.possiblelist[x][y] = [[0] for _ in range(self.T)]
                for t in range(0, self.T):
                    a_list = []
                    for t2 in range(0, self.T):
                            a_list.append(t2)
                    self.possiblelist[x][y][t] = [0 for _ in range(len(a_list))]
                    for c in range(0, len(a_list)):
                        self.possiblelist[x][y][t][c] = a_list[c]
        
        
                        
        for x in range(0, 2 * self.N - 1):
            self.observedlist[x] = [[[0]] for _ in range(2 * self.N - 1)]
            self.allowedlist[x] = [[[0]] for _ in range(2 * self.N - 1)]
            self.disallowedlist[x] = [[[0]] for _ in range(2 * self.N - 1)]
            for y in range(0, 2 * self.N - 1):
                self.observedlist[x][y] = [[0] for _ in range(self.T)]
                self.allowedlist[x][y] = [[0] for _ in range(self.T)]
                self.disallowedlist[x][y] = [[0] for _ in range(self.T)]
                                  
                for t in range(0, self.T):
                    o_list = []
                    a_list = []
                    d_list = []
                    for t2 in range(0, self.T):
                        if not Disallowed(self.patterns[t], self.patterns[t2], x - self.N + 1, y - self.N + 1):
                            if Agrees(self.patterns[t], self.patterns[t2], x - self.N + 1, y - self.N + 1):
                                a_list.append(t2)
                                o_list.append(t2)
                        else:
                            d_list.append(t2)
                            if Agrees(self.patterns[t], self.patterns[t2], x - self.N + 1, y - self.N + 1):
                                a_list.append(t2)
                    self.observedlist[x][y][t] = [0 for _ in range(len(o_list))]
                    for c in range(0, len(o_list)):
                        self.observedlist[x][y][t][c] = o_list[c]
                    self.allowedlist[x][y][t] = [0 for _ in range(len(a_list))]
                    for c in range(0, len(a_list)):
                        self.allowedlist[x][y][t][c] = a_list[c]
                    self.disallowedlist[x][y][t] = [0 for _ in range(len(d_list))]
                    for c in range(0, len(d_list)):
                        self.disallowedlist[x][y][t][c] = d_list[c]
                        
        self.propagator = self.observedlist.copy()
        #print(self.FlattenPropagator(self.observedlist))
        self.propagator = self.UnflattenPropagator(self.FlattenPropagator(self.observedlist)).copy()
#        print()
#        for ix, x in enumerate(self.propagator):
#            for iy, y in enumerate(x):
#                for it, t in enumerate(y):
#                    print(ix, ',', iy, ':', it, '>>', t)
        
        return
    
    def FlattenPropagator(self, prop):
        def Dehydrate(node):
            return '{}_{}_{}'.format(node[0], node[1], node[2])
        flatprop = []
        for x in range(0, 2 * self.N - 1):
            for y in range(0, 2 * self.N - 1):
                for t in range(0, self.T):
                    for t2 in prop[x][y][t]:
                        flatprop.append([Dehydrate([t, x, y]), t2])
        prop_dict = collections.defaultdict(list)
        for x in flatprop:
            prop_dict[x[0]].append(x[1])

        return prop_dict.copy()
    
    def UnflattenPropagator(self, prop_dict):
        prop = []
        for d in prop_dict:
            for p in prop_dict[d]:
                prop.append([d, p])
        hydratedlist = [[[[0]]] for _ in range(2 * self.N - 1)]
        for x in range(0, 2 * self.N - 1):
            hydratedlist[x] = [[[0]] for _ in range(2 * self.N - 1)]
            for y in range(0, 2 * self.N - 1):
                hydratedlist[x][y] = [[0] for _ in range(self.T)]
                for t in range(0, self.T):
                    hydratedlist[x][y][t] = []
        def Rehydrate(node):
            return [int(x) for x in node.split('_')]
        for p in prop:
            t, x, y = Rehydrate(p[0])
            hydratedlist[x][y][t].append(p[1])
            

        return hydratedlist
                    
    def OnBoundary(self, x, y):
        return (not self.periodic) and ((x + self.N > self.FMX ) or (y + self.N > self.FMY))
    
    def Propagate(self):
        change = False
        b = False
        
        #x2 = None
        #y2 = None
        for x1 in range(0, self.FMX):
            for y1 in range(0, self.FMY):
                if (self.changes[x1][y1]):
                    self.changes[x1][y1] = False
                    dx = (0 - self.N) + 1
                    while dx < self.N:
                    #for dx in range(1 - self.N, self.N):
                        dy = (0 - self.N) + 1
                        while dy < self.N:
                        #for dy in range(1 - self.N, self.N):
                            x2 = x1 + dx
                            if x2 < 0:
                                x2 += self.FMX
                            elif x2 >= self.FMX:
                                    x2 -= self.FMX
                            y2 = y1 + dy
                            if y2 < 0:
                                y2 += self.FMY
                            elif y2 >= self.FMY:
                                    y2 -= self.FMY
                                    
                            if (not self.periodic) and (x2 + self.N > self.FMX or y2 + self.N > self.FMY):
                                pass
                            else:
                            
                                w1 = self.wave[x1][y1]
                                w2 = self.wave[x2][y2]
                                
                                p = self.propagator[(self.N - 1) - dx][(self.N - 1) - dy]
                                
                                for t2 in range(0,self.T):
                                    if (not w2[t2]):
                                        pass
                                    else:
                                        b = False
                                        prop = p[t2]
                                        #print("Prop: {0}".format(prop))
                                        i_one = 0
                                        while (i_one < len(prop)) and (False == b):
                                            b = w1[prop[i_one]]
                                            i_one += 1                                    
                                        if False == b:
                                            self.changes[x2][y2] = True
                                            change = True
                                            w2[t2] = False
                            dy += 1
                        dx += 1
                                  
        return change
        
    def Graphics(self, monochrome=True):
        result = Image.new("RGB",(self.FMX, self.FMY),(0,0,0))
        bitmap_data = list(result.getdata())
        if(self.observed != None):
            print(self.observed)
            print(self.patterns)
            for y in range(0, self.FMY):
                dy = self.N - 1
                if (y < (self.FMY - self.N + 1)):
                    dy = 0
                for x in range(0, self.FMX):
                    dx = 0
                    if (x < (self.FMX - self.N + 1)):
                        dx = self.N - 1
                    local_obsv = self.observed[x - dx][y - dy]
                    local_patt = self.patterns[local_obsv][dx + dy * self.N]
                    c = self.colors[local_patt]
                    #bitmap_data[x + y * self.FMX] = (0xff000000 | (c.R << 16) | (c.G << 8) | c.B)               
                    if isinstance(c, (int, float)):
                        bitmap_data[x + y * self.FMX] = (c, c, c)
                    else:
                        bitmap_data[x + y * self.FMX] = (c[0], c[1], c[2])
                    
        else:
            for y in range(0, self.FMY):
                for x in range(0, self.FMX):
                    contributors = 0
                    r = 0
                    g = 0
                    b = 0
                    for dy in range(0, self.N):
                        for dx in range(0, self.N):
                            sx = x - dx
                            if sx < 0:
                                sx += self.FMX
                            sy = y - dy
                            if sy < 0:
                                sy += self.FMY
                            if (self.OnBoundary(sx, sy)):
                                pass
                            else:
                                for t in range(0, self.T):
                                    if self.wave[sx][sy][t]:
                                        contributors += 1
                                        color = self.colors[self.patterns[t][dx + dy * self.N]]
                                        if isinstance(color, (int, float)):
                                            r = int(color)
                                            g = int(color)
                                            b = int(color)
                                        else:
                                            r += int(color[0])#.R
                                            g += int(color[1])#.G
                                            b += int(color[2])#.B
                    #bitmap_data[x + y * self.FMX] = (0xff000000 | ((r / contributors) << 16) | ((g / contributors) << 8) | (b / contributors))
                    if contributors > 0:
                        bitmap_data[x + y * self.FMX] = (int(r / contributors), int(g / contributors), int(b / contributors))
                    else:
                        common.logger.info("INFO: No contributors")
                        bitmap_data[x + y * self.FMX] = (int(r), int(g), int(b))
        result.putdata(bitmap_data)
        return result
        
    def Clear(self):
        super(LearningModel, self).Clear()
        if(self.ground != (0,0) ):
           
            for x in range(0, self.FMX):
                for t in range(0, self.T):
                    #print('clear?',x,t,(t != self.ground),self.wave[x][self.FMY - 1][t],self.changes[x][self.FMY - 1], self.FMY - 1)
                    if not (t in self.ground):
                        self.wave[x][self.FMY - 1][t] = False
                    self.changes[x][self.FMY - 1] = True
                    
                    for y in range(0, self.FMY - 1):
                        for g in range(self.ground[0], self.ground[1]):
                            print(self.wave)
                            print(self.wave[x])
                            print(self.wave[x][y])
                            print(x,y,g)
                            print(self.wave[x][y][g])
                            self.wave[x][y][g] = False
                        self.changes[x][y] = True
            while self.Propagate():
                pass
            
                        
                        
