# -*- coding: utf-8 -*-

import math
import PIL
import random
import xml.etree.ElementTree as ET


class Model:
    def __init__(self, width, height):
        #initialize

        self.wave = [[[]]]
        self.changes = [[]]
        self.stationary = []
        self.observed = [[]]

        self.fmodel_x = width
        self.fmodel_y = height
        self.T = 3
        #self.limit = 0
        
        self.rng = 0 #todo: set rng

        self.wave = [[[False]]*self.fmodel_x]*self.fmodel_y
        self.changes = [[False]*self.fmodel_x]*self.fmodel_y

        self.log_prob = 0
        self.log_t = 0

    def Observe(self):
        observed_min = 1e+3
        observed_sum = 0
        main_sum = 0
        log_sum = 0
        noise = 0
        entropy = 0
        
        argminx = -1
        argminy = -1
        amount = 0
        w = []
        
        for x in range(0, self.fmodel_x):
            for y in range(0, self.fmodel_y):
                if not self.onBoundary(x,y):
                    w = self.wave[x][y]
                    amount = 0
                    observed_sum = 0
                    for t in range(0, self.T):
                        if w[t]:
                            amount += 1
                            observed_sum += self.stationary[t]
                    if 0 == sum:
                        return False
                noise = 1e-6 * getNextRandom()
                if(1 == amount):
                    entropy = 0
                else:
                    if (self.T == amount):
                        entropy = self.log_t
                    else:
                        main_sum = 0
                        log_sum = math.log(observed_sum)
                        for t in range(0, self.T):
                            if w[t]:
                                main_sum += self.stationary[t] * self.log_prob[t]
                            entropy = log_sum - main_sum / observed_sum
                if ((entropy > 0) and ((entropy + noise) < observed_min)):
                    observed_min = entropy + noise
                    argminx = x
                    argminy = y
        if (-1 == argminx) and (-1 == argminy):
            observed = [[[]]*self.fmodel_x]*self.fmodel_y
            for x in range(0, self.fmodel_x):
                for y in range(0, self.fmodel_y):
                    for t in range(0, self.T):
                        if self.wave[x][y][t]:
                            observed[x][y] = t
                            break
            return True
        distribution = []*self.T
        for t in range(0, self.T):
            if self.wave[argminx][argminy][t]:
                distribution[t] = self.stationary[t]
            else:
                distribution[t] = 0
        r = StuffRandom(distribution, getNextRandom())
        for t in range(0, self.T):
            self.wave[argminx][argminy][t] = (t == r)
        self.changes[argminx][argminy] = True
        return None
        
    def Run(self, seed, limit):
        self.log_t = math.log(self.T)
        self.log_prob = []*self.T
        for t in range(0,self.T):
            self.log_prob[t] = math.log(self.stationary[t])
        self.Clear()
        self.rng = 0 # todo: set random seed
        for l in range(0,limit):
            if 0 == limit:
                break
            result = self.Observe()
            if None != result:
                return result
            while(self.Propogate()):
                pass
            
        
    def Propogate(self):
        return False
        
    def Clear(self):
        for x in range(0,self.fmodel_x):
            for y in range(0, self.fmodel_y):
                for t in range(0, self.T):
                    self.wave[x][y][t] = True
                    self.changes[x][y] = False
    
                
    def onBoundary(x, y):
        return True # TODO
    
class OverlappingModel(Model):
    #def __init__(self, width, height):
    #    super( OverlappingModel, self).__init__(width, height)
    #    self.propogator = [[[[]]]]
    #    self.N = 0
    #    self.patterns= [[]]
    #    self.colors = []
    #    self.ground = 0
        
    def __init__(self, width, height, name, N_value, periodic_input_value, periodic_output_value, symmetry_value, ground_value):
        super( OverlappingModel, self).__init__(width, height)
        self.propogator = [[[[]]]]
        self.N = N_value
        self.periodic = periodic_output_value
        self.bitmap = PIL.Image.open("samples/{0}.png".format(name))
        self.SMX = self.bitmap.size[0]
        self.SMY = self.bitmap.size[1]
        self.sample = [[0] * self.SMX] * self.SMY
        self.colors = []
        for x in range(0, self.SMX):
            for y in range(0, self.SMY):
                a_color = self.bitmap.getpixel((x, y))
                color_exists = [c for c in self.colors if c == a_color]
                if len(color_exists) < 1:
                    self.colors.append(a_color)
                self.sample[x][y] = (i for i,v in enumerate(self.colors) if v == a_color)
        self.color_count = len(self.colors)
        self.W = StuffPower(self.color_count, self.N * self.N)
        
        self.patterns= [[]]
        self.ground = 0
        
        def FuncPattern(passed_func):
            result = [None] * (self.N * self.N)
            for y in range(0, self.N):
                for x in range(0, self.N):
                    result[x + (y * self.N)] = passed_func(x, y)
            return result
            
        def PatternFromSample(x, y):
            FuncPattern(lambda dx, dy: self.sample[(x + dx) % self.SMX, (y + dy) % self.SMY])
        def Rotate(p):
            FuncPattern(lambda x, y: p[self.N - 1 - y + x * self.N])
        def Reflect(p):
            FuncPattern(lambda x, y: p[self.N - 1 - x + y * self.N])
            
        def Index(p):
            result = 0
            power = 1
            for i in range(0, len(p)):
                result = result + (p[len(p) - 1 - i] * power)
                power = power * self.color_count
            return result
                                    
            
        def PatternFromIndex(ind):
            residue = ind
            power = self.W
            result = [None] * (self.N * self.N)
            for i in range(0, len(result)):
                power = power / self.color_count
                count = 0
                while residue >= power:
                    residue = residue - power
                    count = count + 1
                result[i] = count
            return result
            
        self.weights = {}
        self.ordering = []
        
        ylimit = self.SMY - self.N + 1
        xlimit = self.SMX - self.N + 1
        if periodic_input_value:
            ylimit = self.SMY
            xlimit = self.SMX
        for y in range (0, ylimit):
            for x in range(0, xlimit):
                ps = [[None] * 8]
                ps[0] = PatternFromSample(x,y)
                ps[1] = Reflect(ps[0])
                ps[2] = Rotate(ps[0])
                ps[3] = Reflect(ps[2])
                ps[4] = Rotate(ps[2])
                ps[5] = Reflect(ps[4])
                ps[6] = Rotate(ps[4])
                ps[7] = Reflect(ps[6])
                
                for k in range(0,symmetry_value):
                    ind = Index(ps[k])
                    if ind in self.weights:
                        self.weights[ind] += 1
                    else:
                        self.weights[ind] = 1
                        self.ordering.append(ind)
        self.T = len(self.weights)
        self.ground = (self.ground + self.T) % self.T
        
        self.patterns = [[None] * self.T]
        self.stationary = [None] * self.T
        self.propogator = [[[[0] * (2 * self.N - 1)]]]
        
        counter = 0
        for w in self.ordering:
            self.patterns[counter] = PatternFromIndex(w)
            self.stationary[counter] = self.weights[w]
            counter += 1
            
        for x in range(0, self.fmodel_x):
            for y in range(0, self.fmodel_y):
                self.wave[x][y] = [] * self.T
                
        def Agrees(p1, p2, dx, dy):
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
                        return False
            return True
                                                        
        for x in range(0, 2 * self.N - 1):
            self.propogator[x] = [[[0] * (2 * self.N - 1)]]
            for t in range(0, self.T):
                a_list = []
                for t2 in range(0, self.T):
                    if Agrees(self.patterns[t], self.patterns[t2], x - self.N + 1, y - self.N + 1):
                        a_list.append(t2)
                self.propogator[x][y][t] = [0] * len(a_list)
                for c in range(0, len(a_list)):
                    self.propogator[x][y][t][c] = a_list[c]
                    
    def OnBoundary(self, x, y):
        return (not self.periodic) and ((x + self.N > self.fmodel_x ) or (y + self.N > self.fmodel_y))
    
    def Propogate(self):
        change = False
        b = None
        
        x2 = None
        y2 = None
        for x1 in range(0, self.fmodel_x):
            for y1 in range(0, self.fmodel_y):
                if (self.changes[x1][y1]):
                    self.changes[x1][y1] = False
                    for dx in range(1 - self.N, self.N):
                        for dy in range(1 - self.N, self.N):
                            x2 = x1 + dx
                            if x2 < 0:
                                x2 += self.fmodel_x
                            else:
                                if x2 >= self.fmodel_x:
                                    x2 -= self.fmodel_x
                            y2 = y1 + dy
                            if y2 < 0:
                                y2 += self.fmodel_y
                            else:
                                if y2 >= self.fmodel_y:
                                    y2 -= self.fmodel_y
                            if (not self.periodic) and (x2 + self.N > self.fmodel_x or y2 + self.N > self.fmodel_y):
                                continue
                            
                            w1 = self.wave[x1][y1]
                            w2 = self.wave[x2][y2]
                            
                            p = self.propogator[self.N - 1 - dx][self.N - 1 - dy]
                            
                            for t2 in range(0,self.T):
                                if (not w2[t2]):
                                    continue
                                b = False
                                prop = p[t2]
                                for i1 in range(0, len(prop)):
                                    if not b:
                                        continue
                                    b = w1[prop[i1]]
                                    
                                if not b:
                                    self.changes[x2][y2] = True
                                    change = True
                                    w2[t2] = True
        return change
        
    def Graphics(self):
        result = PIL.Image.new("RGB",(self.fmodel_x, self.fmodel_y),(0,0,0))
        bitmap_data = list(result.getdata())#[None] * (result.height * result.width)
        if(self.observed != None):
            for y in range(0, self.fmodel_y):
                dy = 0
                if not (y < self.fmodel_y - self.N + 1):
                    dy = self.N - 1
                for x in range(0, self.fmodel_x):
                    dx = 0
                    if not (x < self.fmodel_x - self.N + 1):
                        dx = self.N - 1
                    c = self.colors[self.patterns[self.observed[x - dx][y - dy]][dx + dy * self.N]]
                    #bitmap_data[x + y * self.fmodel_x] = (0xff000000 | (c.R << 16) | (c.G << 8) | c.B)
                    bitmap_data[x + y * self.fmodel_x] = (c.R, c.G, c.B)
                    
        else:
            for y in range(0, self.fmodel_y):
                for x in range(0, self.fmodel_x):
                    contributors = 0
                    r = 0
                    g = 0
                    b = 0
                    for dy in range(0, self.N):
                        for dx in range(0, self.N):
                            sx = x - dx
                            if sx < 0:
                                sx += self.fmodel_x
                            sy = y - dy
                            if sy < 0:
                                sy += self.fmodel_y
                            if (self.OnBoundary(sx, sy)):
                                continue
                            for t in range(0, self.T):
                                if self.wave[sx][sy][t]:
                                    contributors += 1
                                    color = self.colors[self.patterns[t][dx + dy * self.N]]
                                    r += color.R
                                    g += color.G
                                    b += color.B
                    #bitmap_data[x + y * self.fmodel_x] = (0xff000000 | ((r / contributors) << 16) | ((g / contributors) << 8) | (b / contributors))
                    bitmap_data[x + y * self.fmodel_x] = ((r / contributors), (g / contributors), (b / contributors))
        result.putdata(bitmap_data)
        return result
        
    def Clear(self):
        super(OverlappingModel, self).Clear(self)
        if(self.ground != 0 ):
            for x in range(0, self.fmodel_x):
                for t in range(0, self.T):
                    if t != self.ground:
                        self.wave[x][self.fmodel_x - 1][t] = False
                    self.changes[x][self.fmodel_x - 1] = True
                    
                    for y in range(0, self.fmodel_y - 1):
                        self.wave[x][y][self.ground] = False
                        self.changes[x][y] = True
            while self.Propogate():
                pass
            
                        
                        
                    
class SimpleTiledModel(Model):
    def __init__(self, width, height, name, subset_name, periodic_value, black_value):
        super( OverlappingModel, self).__init__(width, height)
        self.propogator = [[[]]]
        self.tiles = []
        self.tilenames = []
        self.tilesize = 0
        self.black = False
        self.periodic = periodic_value
        self.black = black_value
        

        

def getNextRandom():
    return random.random()
    
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
    
class Program:
    def __init__(self):
        pass
    
    def Main(self):
        self.random = random.Random()
        xdoc = ET.ElementTree(file="samples.xml")
        counter = 1
        for xnode in xdoc.getroot():
            if("#comment" == xnode.tag):
                continue
            a_model = None
            
            name = xnode.tag
            print("< {0} ".format(name))
            if "overlapping" == xnode.tag:
                print(xnode.attrib)
                a_model = OverlappingModel(xnode.get('width', 48), xnode.get('height', 48), xnode.get('name', "NAME"), xnode.get('N', 2), xnode.get('periodicInput', True), xnode.get('periodic', False), xnode.get('symmetry', 8), xnode.get('ground',0))
                pass
            else:
                if "simpletiled" == xnode.tag:
                    pass
                else:
                    continue
                
            #print(xnode)
            #print(xnode.attrib)
        pass
    