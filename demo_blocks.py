#coding:utf-8
#copyright: fiorezhang@sina.com

import sys
import math
import numpy as np
import random
import time
import pygame
from pygame.locals import *
from map import Map, Cross, Road, Car, STATE

#====全局
FPS = 30
BASIC_UNIT = 12
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
MAP_WIDTH = 600
MAP_HEIGHT = 600
MAIN_BIAS = BASIC_UNIT
MAIN_WIDTH = MAP_WIDTH-MAIN_BIAS*2
MAIN_HEIGHT = MAP_HEIGHT-MAIN_BIAS*2
assert BASIC_UNIT >= 6
assert BASIC_UNIT % 2 == 0
assert MAIN_WIDTH % BASIC_UNIT == 0
assert MAIN_HEIGHT % BASIC_UNIT == 0

BLOCK_MIN = 5
BLOCK_MAX = 9
TIME_ADD_CAR = 3
NUM_ADD_CAR = 1
TIME_CROSS = 3
TIME_CAR = 0.5
#====颜色
BLACK           = (  0,   0,   0)
WHITE           = (255, 255, 255)
GREY            = (185, 185, 185)
LIGHTGREY       = (225, 225, 225)
GREEN           = (  0, 155,   0)
LIGHTGREEN      = ( 40, 195,  40)
YELLOW          = (155, 155,   0)
LIGHTYELLOW     = (195, 195,  40)
BLUE            = (  0,   0, 155)
LIGHTBLUE       = ( 40,  40, 195)
RED             = (155,   0,   0)
LIGHTRED        = (195,  40,  40)

COLOR_BG        = BLACK
COLOR_MAP       = GREY
COLOR_ROAD      = WHITE
COLOR_CROSS     = GREEN
COLOR_CAR       = BLACK

#====程序主体架构
def main(): 
    global fps_lock, display_surf

    pygame.init()
    pygame.mixer.init()
    fps_lock = pygame.time.Clock()
    display_surf = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('Blocks Downtown')

    showStartScreen()
    while True:
        score = runGame()
        showGameOverScreen(score)
        
#====主要函数
def showStartScreen():
    pass
    
def showGameOverScreen(score):
    pass
    
def runGame():
    map = Map(MAIN_WIDTH//BASIC_UNIT, MAIN_HEIGHT//BASIC_UNIT, BLOCK_MIN, BLOCK_MAX, TIME_ADD_CAR, NUM_ADD_CAR, TIME_CROSS, TIME_CAR)
    option = 0
    while True:
        #检测退出事件
        checkForQuit()
        
        map.update()
        
        key = checkForKeyEvent()
        if key == K_SPACE:
            map.addCarRandom(1) 
        for i, k in enumerate([K_0, K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9]):
            if key == k:
                option = i

        #绘图步骤 --------
        drawBackground()
        drawMap(map, option)
        
        pygame.display.update()
        fps_lock.tick(FPS)
    return score             

#====功能函数
def drawBackground():
    ''' Draw background for main routine
    '''
    display_surf.fill(COLOR_BG)

    
def clearKeyEvent():
    ''' Clear existing button event
    Used like before ladder raise. Ensure no residual button state interference the logics. 
    '''
    pygame.event.get([KEYDOWN, KEYUP])

def checkForKeyEvent():
    ''' Check for button down, ignore and clear other button event
    '''
    for event in pygame.event.get(KEYUP):
        if event.key in [K_SPACE, K_0, K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9]:
            return event.key
    return None
    
def checkForQuit():
    ''' Check for quit by system or esc button
    Throw back all button event to avoid missing in following routine
    '''
    for event in pygame.event.get(QUIT):
        terminate()
    for event in pygame.event.get(KEYUP):
        if event.key == K_ESCAPE:
            terminate()
        pygame.event.post(event) #放回所有的事件
        
def terminate():
    ''' Quit game
    '''
    pygame.quit()
    sys.exit()            
    
def calculateColorFromId(uuid):
    uuid_int = uuid.int
    r = uuid_int & 0xff
    g = (uuid_int >> 8) & 0xff
    b = (uuid_int >> 16) & 0xff
    return(r, g, b)

def drawMap(map, option=0):
    # Map
    x, y, w, h = 0, 0, MAP_WIDTH, MAP_HEIGHT
    pygame.draw.rect(display_surf, COLOR_MAP, (x, y, w, h))

    # Road
    for road in map.getRoadList():
        pos_en, pos_ex = road.getPos()
        direct = road.getDirect()
        length = road.getLength()
        if direct == "E":
            x, y, w, h = pos_en[0]*BASIC_UNIT, pos_en[1]*BASIC_UNIT+BASIC_UNIT//2, length*BASIC_UNIT, BASIC_UNIT//2
        elif direct == "S":
            x, y, w, h = pos_en[0]*BASIC_UNIT, pos_en[1]*BASIC_UNIT, BASIC_UNIT//2, length*BASIC_UNIT
        elif direct == "W":
            x, y, w, h = pos_ex[0]*BASIC_UNIT, pos_ex[1]*BASIC_UNIT, length*BASIC_UNIT, BASIC_UNIT//2
        elif direct == "N":
            x, y, w, h = pos_ex[0]*BASIC_UNIT+BASIC_UNIT//2, pos_ex[1]*BASIC_UNIT, BASIC_UNIT//2, length*BASIC_UNIT
        x, y, w, h = x+MAIN_BIAS, y+MAIN_BIAS, w, h
        pygame.draw.rect(display_surf, COLOR_ROAD, (x, y, w, h))
    
    #Cross
    for cross in map.getCrossList():
        pos = cross.getPos()
        direct = cross.getDirectEnabled()
        if direct == "E":
            x, y, w, h = pos[0]*BASIC_UNIT, pos[1]*BASIC_UNIT, BASIC_UNIT//3, BASIC_UNIT
        elif direct == "S":
            x, y, w, h = pos[0]*BASIC_UNIT, pos[1]*BASIC_UNIT, BASIC_UNIT, BASIC_UNIT//3
        elif direct == "W":
            x, y, w, h = (pos[0]+1)*BASIC_UNIT-BASIC_UNIT//3, pos[1]*BASIC_UNIT, BASIC_UNIT//3, BASIC_UNIT
        elif direct == "N":
            x, y, w, h = pos[0]*BASIC_UNIT, (pos[1]+1)*BASIC_UNIT-BASIC_UNIT//3, BASIC_UNIT, BASIC_UNIT//3
        x, y, w, h = x+MAIN_BIAS, y+MAIN_BIAS, w, h
        pygame.draw.rect(display_surf, COLOR_CROSS, (x, y, w, h))
        
    # Car
    for car in map.getCarList():
        color_car = COLOR_CAR
        color_car = calculateColorFromId(car.getId())
        state = car.getState()
        road_src = car.getRoadSrc()
        offset_src = car.getOffsetSrc()
        road_dst = car.getRoadDst()
        offset_dst = car.getOffsetDst()
        if True:
            pos_en, pos_ex = road_src.getPos()
            offset = offset_src
            direct = road_src.getDirect()
            length = road_src.getLength()
            if direct == "E":
                x, y, w, h = (pos_ex[0]-offset)*BASIC_UNIT, (pos_ex[1]+1)*BASIC_UNIT, BASIC_UNIT, BASIC_UNIT
            elif direct == "S": 
                x, y, w, h = (pos_ex[0]-1)*BASIC_UNIT, (pos_ex[1]-offset)*BASIC_UNIT, BASIC_UNIT, BASIC_UNIT
            elif direct == "W":
                x, y, w, h = (pos_ex[0]+offset)*BASIC_UNIT, (pos_ex[1]-1)*BASIC_UNIT, BASIC_UNIT, BASIC_UNIT
            elif direct == "N":
                x, y, w, h = (pos_ex[0]+1)*BASIC_UNIT, (pos_ex[1]+offset)*BASIC_UNIT, BASIC_UNIT, BASIC_UNIT
            x, y, w, h = x+1, y+1, w-2, h-2
            x, y, w, h = x+MAIN_BIAS, y+MAIN_BIAS, w, h
            pygame.draw.rect(display_surf, color_car, (x, y, w, h))        
        if True:
            pos_en, pos_ex = road_dst.getPos()
            offset = offset_dst
            direct = road_dst.getDirect()
            length = road_dst.getLength()
            if direct == "E":
                x, y, w, h = (pos_ex[0]-offset)*BASIC_UNIT, (pos_ex[1]+1)*BASIC_UNIT, BASIC_UNIT, BASIC_UNIT
            elif direct == "S": 
                x, y, w, h = (pos_ex[0]-1)*BASIC_UNIT, (pos_ex[1]-offset)*BASIC_UNIT, BASIC_UNIT, BASIC_UNIT
            elif direct == "W":
                x, y, w, h = (pos_ex[0]+offset)*BASIC_UNIT, (pos_ex[1]-1)*BASIC_UNIT, BASIC_UNIT, BASIC_UNIT
            elif direct == "N":
                x, y, w, h = (pos_ex[0]+1)*BASIC_UNIT, (pos_ex[1]+offset)*BASIC_UNIT, BASIC_UNIT, BASIC_UNIT
            x, y, w, h = x+1, y+1, w-2, h-2
            x, y, w, h = x+MAIN_BIAS, y+MAIN_BIAS, w, h
            pygame.draw.rect(display_surf, color_car, (x, y, w, h))        
        if state == STATE["MOVE"]:
            road = car.getRoad()
            pos_en, pos_ex = road.getPos()
            offset = car.getOffset()
            direct = road.getDirect()
            length = road.getLength()
            if direct == "E":
                x, y, w, h = (pos_ex[0]-offset)*BASIC_UNIT, pos_ex[1]*BASIC_UNIT+BASIC_UNIT//2, BASIC_UNIT, BASIC_UNIT//2
            elif direct == "S": 
                x, y, w, h = pos_ex[0]*BASIC_UNIT, (pos_ex[1]-offset)*BASIC_UNIT, BASIC_UNIT//2, BASIC_UNIT
            elif direct == "W":
                x, y, w, h = (pos_ex[0]+offset)*BASIC_UNIT, pos_ex[1]*BASIC_UNIT, BASIC_UNIT, BASIC_UNIT//2
            elif direct == "N":
                x, y, w, h = pos_ex[0]*BASIC_UNIT+BASIC_UNIT//2, (pos_ex[1]+offset)*BASIC_UNIT, BASIC_UNIT//2, BASIC_UNIT
            x, y, w, h = x+1, y+1, w-2, h-2
            x, y, w, h = x+MAIN_BIAS, y+MAIN_BIAS, w, h
            pygame.draw.rect(display_surf, color_car, (x, y, w, h))        
        if state == STATE["CROSS"]:
            cross = car.getCross()
            pos = cross.getPos()
            direct = cross.getDirectEnabled()
            if direct == "E":
                x, y, w, h = pos[0]*BASIC_UNIT, pos[1]*BASIC_UNIT+BASIC_UNIT//2, BASIC_UNIT, BASIC_UNIT//2
            elif direct == "S":
                x, y, w, h = pos[0]*BASIC_UNIT, pos[1]*BASIC_UNIT, BASIC_UNIT//2, BASIC_UNIT
            elif direct == "W":
                x, y, w, h = pos[0]*BASIC_UNIT, pos[1]*BASIC_UNIT, BASIC_UNIT, BASIC_UNIT//2
            elif direct == "N":
                x, y, w, h = pos[0]*BASIC_UNIT+BASIC_UNIT//2, pos[1]*BASIC_UNIT, BASIC_UNIT//2, BASIC_UNIT
            x, y, w, h = x+1, y+1, w-2, h-2
            x, y, w, h = x+MAIN_BIAS, y+MAIN_BIAS, w, h
            pygame.draw.rect(display_surf, color_car, (x, y, w, h))            
            
#====入口
if __name__ == '__main__':
    main()    
