#coding:utf-8
#copyright: fiorezhang@sina.com

import numpy as np

BLOCK_MIN = 5
BLOCK_MAX = 9

def closeCell(a_x, a_y, b_x, b_y):
    if a_x == b_x and abs(a_y - b_y) == 1:
        return True
    elif abs(a_x - b_x) == 1 and a_y == b_y: 
        return True
    else:
        return False

def generateRandList(len, min, max):
    list = [0]
    cnt = 0
    while True:
        if len - cnt <= max and len - cnt >= min: 
            list.append(len)
            break
        elif len - cnt < min: 
            list[-1] = len
            break
        else: 
            this = np.random.randint(min, max+1)
            cnt += this
            list.append(cnt)
    return list        
        
class Map():
    def __init__(self, w, h):
        self.__cross_list = []
        self.__
        for i in generateRandList(w-1, BLOCK_MIN, BLOCK_MAX):
            for j in generateRandList(h-1, BLOCK_MIN, BLOCK_MAX):
                

class Road():
    def __init__(self, a_x, a_y, b_x, b_y):
        assert a_x == b_x or a_y == b_y
        self.__a_x = a_x
        self.__a_y = a_y
        self.__b_x = b_x
        self.__b_y = b_y
        
        self.__a = [a_x, a_y]
        self.__b = [b_x, b_y]
        
    def get(self):
        return self.__a, self.__b
        
    def setCross(self, cross_a, cross_b):
        a = cross_a.get()
        b = cross_b.get()
        assert self.__a == a and self.__b == b
        self.__cross_a = cross_a
        self.__cross_b = cross_b

class Cross():
    def __init__(self, a_x, a_y):
        self.__a_x = a_x
        self.__a_y = a_y
        self.__a = [a_x, a_y]
        self.__road_i = []
        self.__road_o = []
        
    def get(self):
        return self.__a
        
    def setRoad(self, road):
        a, b = road.get()
        assert self.__a == a or self.__a == b
        if self.__a == a and road is not in self.__road_i: 
            self.__road_i.append(road)
        elif self.__a == b and road is not in self.__road_o:
            self.__road_o.append(road)
        
class Car():
    def __init__(self, init_x, init_y, dest_x, dest_y):
        self.__init_x = init_x
        self.__init_y = init_y
        self.__dest_x = dest_x
        self.__dest_y = dest_y
        self.__crnt_x = init_x
        self.__crnt_y = init_y
        
        self.__init = [init_x, init_y]
        self.__dest = [dest_x, dest_y]
        self.__crnt = [init_x, init_y]
        
    def move(self, next_x, next_y):
        assert closeCell(self.__crnt_x, self.__crnt_y, next_x, next_y)
        self.__crnt_x, self.__crnt_y = next_x, next_y
        self.__crnt = [self.__crnt_x, self.__crnt_y]
        
    def get(self):
        return self.__crnt
        
    def dest(self):
        if self.__crnt_x == self.__dest_x and self.__crnt_y == self.__dest_y:
            return True
        else:
            return False

if __name__ == '__main__':
    list = generateRandList(100, 5, 9)
    print(list)