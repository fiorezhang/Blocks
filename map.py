#coding:utf-8
#copyright: fiorezhang@sina.com

'''
每辆车自带时间戳，每次行动前先判断是否在“当前位置”（一个街道段）呆了足够长时间，即记录time_last_move，只有time_current大于它一定阈值才能进行后面的移动判断
出生点和目的地，用红蓝色带alpha通道的颜色标记
车辆走过的格子保留痕迹，也是alpha通道，若干回合后消失
车辆挂靠在道路的list内，到了十字路口，经过判断，挂靠到十字路口（独占），然后挂靠到下一条路的list内
'''

import numpy as np

BLOCK_MIN = 5
BLOCK_MAX = 9

def generateRandList(len, min, max):
    ''' Generate list in [0, x1, x2, x3, ... len]
    x(n+1) - x(n) randomly in range [min, max]
    '''
    assert len >= min and max >= min
    while True:
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
        if list[-1] - list[-2] <= max:
            break
    return list        
        

class Map():
    def __init__(self, w, h):
        self.__w = w
        self.__h = h
        self.__cross_list = []
        self.__road_list = []
        self.__car_list = []

        self.__cross_x_list = generateRandList(w-1, BLOCK_MIN, BLOCK_MAX)
        self.__cross_y_list = generateRandList(h-1, BLOCK_MIN, BLOCK_MAX)

        for y in self.__cross_y_list:
            for x in self.__cross_x_list: 
                self.__cross_list.append(Cross((x, y)))

        for cross in self.__cross_list:
            for direct in ['E', 'S', 'W', 'N']:
                cross_next = self.getCrossNext(cross, direct)
                if cross_next is not None:
                    road = Road(cross.getPos(), cross_next.getPos())
                    self.__road_list.append(road)
                    cross.linkRoad(road)
                    cross_next.linkRoad(road)
                    road.linkCross(cross)
                    road.linkCross(cross_next)

    def getSize(self):
        return self.__w, self.__h

    def getCrossList(self):
        return self.__cross_list

    def getCrossByOrd(self, i, j):
        return self.__cross_list[i + j*len(self.__cross_x_list)]

    def getCrossByPos(self, x, y):
        assert x in self.__cross_x_list and y in self.__cross_y_list
        i = self.__cross_x_list.index(x)
        j = self.__cross_y_list.index(y)
        return self.getCrossByOrd(i, j)

    def getCrossNext(self, cross, direct):
        assert cross in self.__cross_list
        order = self.__cross_list.index(cross)
        i = order % len(self.__cross_x_list)
        j = order //len(self.__cross_x_list)
        if direct == 'E' and i < len(self.__cross_x_list)-1:
            return self.getCrossByOrd(i+1, j)
        elif direct == 'S' and j < len(self.__cross_y_list)-1:
            return self.getCrossByOrd(i, j+1)
        elif direct == 'W' and i > 0: 
            return self.getCrossByOrd(i-1, j)
        elif direct == 'N' and j > 0:
            return self.getCrossByOrd(i, j-1)
        else: 
            return None

    def getRoadList(self):
        return self.__road_list

    def getRoadByOrd(self, i_en, j_en, i_ex, j_ex):
        cross_en = self.getCrossByOrd(i_en, j_en)
        if i_en < i_ex and j_en == j_ex:
            direct = 'E'
        if i_en == i_ex and j_en < j_ex:
            direct = 'S'
        if i_en > i_ex and j_en == j_ex:
            direct = 'W'
        if i_en == i_ex and j_en > j_ex:
            direct = 'N'
        return cross_en.getRoadEntry(direct) 

    def getRoadByPos(self, x_en, y_en, x_ex, y_ex):
        cross_en = self.getCrossByPos(x_en, y_en)
        if x_en < x_ex and y_en == y_ex:
            direct = 'E'
        if x_en == x_ex and y_en < y_ex:
            direct = 'S'
        if x_en > x_ex and y_en == y_ex:
            direct = 'W'
        if x_en == x_ex and y_en > y_ex:
            direct = 'N'
        return cross_en.getRoadEntry(direct) 

class Cross():
    def __init__(self, pos):
        ''' Init as Cross((x, y))
        '''
        self.__pos = pos

        self.__road_en_dict = {'E':None, 'S':None, 'W':None, 'N':None}
        self.__road_ex_dict = {'E':None, 'S':None, 'W':None, 'N':None}

        self.__car = None
        
    def getPos(self):
        return self.__pos

    def getRoadEntryDict(self):
        return self.__road_en_dict
        
    def getRoadExitDict(self):
        return self.__road_ex_dict

    def getRoadEntry(self, direct):
        return self.__road_en_dict[direct]

    def getRoadExit(self, direct):
        return self.__road_ex_dict[direct]

    def getCrossNext(self, direct):
        road = self.__road_en_dict[direct]
        if road is not None:
            return road.getCrossExit()
        return None

    def linkRoad(self, road):
        ''' link roads to related entry and exit crosses. 
        Each cross record up to 4 roads which entry from here, and up to 4 roads which exit here. 
        '''
        pos_en, pos_ex = road.getPos()
        if self.__pos == pos_en:
            if pos_en[0] < pos_ex[0] and pos_en[1] == pos_ex[1]:
                self.__road_en_dict['E'] = road
            elif pos_en[0] == pos_ex[0] and pos_en[1] < pos_ex[1]:
                self.__road_en_dict['S'] = road
            elif pos_en[0] > pos_ex[0] and pos_en[1] == pos_ex[1]:
                self.__road_en_dict['W'] = road
            elif pos_en[0] == pos_ex[0] and pos_en[1] > pos_ex[1]:
                self.__road_en_dict['N'] = road
        elif self.__pos == pos_ex:
            if pos_en[0] < pos_ex[0] and pos_en[1] == pos_ex[1]:
                self.__road_ex_dict['W'] = road
            elif pos_en[0] == pos_ex[0] and pos_en[1] < pos_ex[1]:
                self.__road_ex_dict['N'] = road
            elif pos_en[0] > pos_ex[0] and pos_en[1] == pos_ex[1]:
                self.__road_ex_dict['E'] = road
            elif pos_en[0] == pos_ex[0] and pos_en[1] > pos_ex[1]:
                self.__road_ex_dict['S'] = road

    def getCar(self):
        return self.__car

class Road():
    def __init__(self, pos_en, pos_ex):
        assert pos_en[0] == pos_ex[0] or pos_en[1] == pos_ex[1]
        self.__pos_en = pos_en
        self.__pos_ex = pos_ex
        
        if pos_en[0] < pos_ex[0] and pos_en[1] == pos_ex[1]:
            self.__direct = 'E'
            self.__length = pos_ex[0] - pos_en[1] + 1
        elif pos_en[0] == pos_ex[0] and pos_en[1] < pos_ex[1]:
            self.__direct = 'S'
            self.__length = pos_ex[1] - pos_en[1] + 1
        elif pos_en[0] > pos_ex[0] and pos_en[1] == pos_ex[1]:
            self.__direct = 'W'
            self.__length = pos_en[0] - pos_ex[0] + 1
        elif pos_en[0] == pos_ex[0] and pos_en[1] > pos_ex[1]:
            self.__direct = 'N'
            self.__length = pos_en[1] - pos_ex[1] + 1

        self.__car_list = []
        
    def getPos(self):
        return self.__pos_en, self.__pos_ex

    def getDirect(self):
        return self.__direct

    def getLength(self):
        return self.__length
        
    def getRoadReverse(self):
        ''' Find the entry cross firstly, then find the cross' exit dict, then select the 'same' direction road, that's the reverse one
        '''
        return self.__cross_en.getRoadExit(self.__direct)
    
    def getCrossEntry(self):
        return self.__cross_en

    def getCrossExit(self):
        return self.__cross_ex    

    def linkCross(self, cross):
        pos = cross.getPos()
        if self.__pos_en == pos:
            self.__cross_en = cross
        elif self.__pos_ex == pos:
            self.__cross_ex = cross 

    def insertCar(self, car):
        pass

    def deleteCar(self, car):
        pass

    def getCarList(self):
        return self.__car_list

    def getCarLast(self, car):
        assert car in self.__car_list
        i = self.__car_list.index(car)
        if i > 0:
            return self.__car_list[i-1]
        else:
            return None

    def getCarNext(self, car):
        assert car in self.__car_list
        i = self.__car_list.index(car)
        if i < len(self.__car_list) - 1:
            return self.__car_list[i+1]
        else:
            return None

class Car():
    def __init__(self, road_src, offset_src, road_dst, offset_dst):
        self.__road_src = road_src
        self.__offset_src = offset_src
        self.__road_dst = road_dst
        self.__offset_dst = offset_dst

        self.__state = STATE["START"]
        self.__road_crt = road_src
        self.__offset_crt = offset_src

    def getRoad(self):
        return self.__road_crt

    def getOffset(self):
        return self.__offset_crt

    def move(self):
        pass


if __name__ == '__main__':
    print("==TEST== Class Map")
    map = Map(20, 10)

    print("-- 1 -- getSize")
    print(map.getSize())

    print("-- 2 -- getCrossList")
    cross_list = map.getCrossList()
    print(cross_list)
    for cross in cross_list:
        print(cross)
        print(cross.getPos())

    '''
    print("-- 3 -- getCrossByOrd")
    i = int(input("i="))
    j = int(input("j="))
    cross = map.getCrossByOrd(i, j)
    print(cross)
    print(cross.getPos())
    '''
    
    '''
    print("-- 4 -- getCrossByPos")
    x = int(input("x="))
    y = int(input("y="))
    cross = map.getCrossByPos(x, y)
    print(cross.getPos())
    '''
    
    '''
    print("-- 5 -- getCrossNext")
    i, j = 0, 0
    cross = map.getCrossByOrd(i, j)
    print("cross ", cross.getPos())
    cross_next = map.getCrossNext(cross, 'E')
    print("nextE ", cross_next.getPos())
    cross_next = map.getCrossNext(cross, 'S')
    print("nextS ", cross_next.getPos())
    i, j = 1, 1
    cross = map.getCrossByOrd(i, j)
    print("cross ", cross.getPos())
    cross_next = map.getCrossNext(cross, 'W')
    print("nextW ", cross_next.getPos())
    cross_next = map.getCrossNext(cross, 'N')
    print("nextN ", cross_next.getPos())
   '''

    print("-- 7 -- getRoadList")
    road_list = map.getRoadList()
    print(road_list)
    for road in road_list:
        print(road)
        print(road.getPos())

    '''
    print("-- 8 -- getRoadByOrd")
    i1 = int(input("i="))
    j1 = int(input("j="))
    i2 = int(input("i="))
    j2 = int(input("j="))
    road = map.getRoadByOrd(i1, j1, i2, j2)
    print(road)
    print(road.getPos())
    '''
    
    '''
    print("-- 9 -- getCrossByPos")
    x1 = int(input("x="))
    y1 = int(input("y="))
    x2 = int(input("x="))
    y2 = int(input("y="))
    road = map.getRoadByPos(x1, y1, x2, y2)
    print(road)
    print(road.getPos())
    '''
    
    print("==TEST== Class Cross")
    cross = map.getCrossByOrd(1, 1)
    print("cross ", cross.getPos())
    
    print("-- 1 -- getRoadEntryDict")
    for road in cross.getRoadEntryDict().values():
        if road is not None:
            print(road.getPos())
        else:
            print("NONE")
        
    print("-- 2 -- getRoadExitDict")
    for road in cross.getRoadExitDict().values():
        if road is not None:
            print(road.getPos())
        else:
            print("NONE")

    print("-- 3 -- getRoadEntry")
    for direct in ['E', 'S', 'W', 'N']:
        road = cross.getRoadEntry(direct)
        if road is not None:
            print(road.getPos())
        else:
            print("NONE")

    print("-- 4 -- getRoadExit")
    for direct in ['E', 'S', 'W', 'N']:
        road = cross.getRoadExit(direct)
        if road is not None:
            print(road.getPos())
        else:
            print("NONE")

    print("-- 5 -- getCrossNext")
    i, j = 0, 0
    cross = map.getCrossByOrd(i, j)
    print("cross ", cross.getPos())
    cross_next = cross.getCrossNext('E')
    print("nextE ", cross_next.getPos())
    cross_next = cross.getCrossNext('S')
    print("nextS ", cross_next.getPos())
    i, j = 1, 1
    cross = map.getCrossByOrd(i, j)
    print("cross ", cross.getPos())
    cross_next = cross.getCrossNext('W')
    print("nextW ", cross_next.getPos())
    cross_next = cross.getCrossNext('N')
    print("nextN ", cross_next.getPos())

    print("==TEST== Class Road")
    road = map.getRoadByOrd(1, 1, 0, 1)
    print("road ", road.getPos())
    
    print("-- 1 -- getRoadReverse")
    road_rev = road.getRoadReverse()
    print(road_rev)
    print(road_rev.getPos())
    
    print("-- 2 -- getCrossEntry")
    print(road.getCrossEntry().getPos())

    print("-- 3 -- getCrossExit")
    print(road.getCrossExit().getPos())

    print("-- 4 -- getDirect")
    print(road.getDirect())

    print("-- 5 -- getDirect")
    print(road.getLength())
