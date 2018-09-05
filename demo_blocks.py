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
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
MAIN_WIDTH = 600
MAIN_HEIGHT = 600
BASIC_UNIT = 12
assert BASIC_UNIT % 2 == 0
assert MAIN_WIDTH % BASIC_UNIT == 0
assert MAIN_HEIGHT % BASIC_UNIT == 0

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

COLOR_BG        = GREY
COLOR_ROAD      = LIGHTGREY
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
    map = Map(MAIN_WIDTH//BASIC_UNIT, MAIN_HEIGHT//BASIC_UNIT)
    while True:
        #检测退出事件
        checkForQuit()
        
        map.update()
        
        key = checkForKeyEvent()
        if key == K_SPACE:
            map.addCarRandom() 
        
        #绘图步骤 --------
        drawBackground()
        drawMap(map)
        
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
        if event.key in [K_SPACE, K_1, K_2, K_3, K_4, K_5]:
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
    
def drawMap(map):
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
        pygame.draw.rect(display_surf, COLOR_ROAD, (x, y, w, h))
    
    for cross in map.getCrossList():
        pos = cross.getPos()
        direct = cross.getDirectEnabled()
        if direct == "E":
            x, y, w, h = pos[0]*BASIC_UNIT, pos[1]*BASIC_UNIT, 1, BASIC_UNIT
        elif direct == "S":
            x, y, w, h = pos[0]*BASIC_UNIT, pos[1]*BASIC_UNIT, BASIC_UNIT, 1
        elif direct == "W":
            x, y, w, h = (pos[0]+1)*BASIC_UNIT-1, pos[1]*BASIC_UNIT, 1, BASIC_UNIT
        elif direct == "N":
            x, y, w, h = pos[0]*BASIC_UNIT, (pos[1]+1)*BASIC_UNIT-1, BASIC_UNIT, 1
        pygame.draw.rect(display_surf, COLOR_CROSS, (x, y, w, h))
        
    for car in map.getCarList():
        state = car.getState()
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
            pygame.draw.rect(display_surf, COLOR_CAR, (x, y, w, h))        
        if state == STATE["CROSS"]:
            cross = car.getCross()
            pos = cross.getPos()
            direct = cross.getDirectEnabled()
            if direct == "E":
                x, y, w, h = pos[0]*BASIC_UNIT, pos[1]*BASIC_UNIT+BASIC_UNIT//2, BASIC_UNIT, BASIC_UNIT//2
            elif direct == "S":
                x, y, w, h = pos[0]*BASIC_UNIT, pos[1]*BASIC_UNIT, BASIC_UNIT//2, BASIC_UNIT-1*2
            elif direct == "W":
                x, y, w, h = pos[0]*BASIC_UNIT, pos[1]*BASIC_UNIT, BASIC_UNIT, BASIC_UNIT//2-1*2
            elif direct == "N":
                x, y, w, h = pos[0]*BASIC_UNIT+BASIC_UNIT//2, pos[1]*BASIC_UNIT, BASIC_UNIT//2, BASIC_UNIT
            x, y, w, h = x+1, y+1, w-2, h-2
            pygame.draw.rect(display_surf, COLOR_CAR, (x, y, w, h))            
            
#====入口
if __name__ == '__main__':
    main()    
