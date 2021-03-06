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
FONT_SIZE = 20

BASIC_UNIT = 20
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
MAP_WIDTH = 600
MAP_HEIGHT = 600
MAIN_WIDTH = 1080
MAIN_HEIGHT = 960
BIAS_WIDTH_BASIC = (MAP_WIDTH - MAIN_WIDTH) // 2
BIAS_HEIGHT_BASIC = (MAP_HEIGHT - MAIN_HEIGHT) // 2
BIAS_WIDTH_MAX = BASIC_UNIT
BIAS_HEIGHT_MAX = BASIC_UNIT
BIAS_WIDTH_MIN = MAP_WIDTH - MAIN_WIDTH - BASIC_UNIT
BIAS_HEIGHT_MIN = MAP_HEIGHT - MAIN_HEIGHT - BASIC_UNIT
BIAS_TIME = 0.1
assert BASIC_UNIT >= 6
assert BASIC_UNIT % 2 == 0
assert MAIN_WIDTH % BASIC_UNIT == 0
assert MAIN_HEIGHT % BASIC_UNIT == 0

BLOCK_MIN = 4
BLOCK_MAX = 8
TIME_CROSS = 1
TIME_CAR = 0.2

BASIC_TIME_ADD_CAR = 0.2
BASIC_NUM_ADD_CAR = 1

OPTION_ADD_CAR = \
[[ 1, 0], 
 [ 5, 1],
 [ 4, 1], 
 [ 3, 1], 
 [ 2, 1], 
 [ 1, 1], 
 [ 1, 2],
 [ 1, 3],
 [ 1, 4],
 [ 1, 5]]
INIT_TIME_ADD_CAR = OPTION_ADD_CAR[0][0]
INIT_NUM_ADD_CAR = OPTION_ADD_CAR[0][1]

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
    pygame.mixer.music.load("resource/sound/BGM01.at3.mp3")
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1, 0.0)
    
    map = Map(MAIN_WIDTH//BASIC_UNIT, MAIN_HEIGHT//BASIC_UNIT, BLOCK_MIN, BLOCK_MAX, INIT_TIME_ADD_CAR, INIT_NUM_ADD_CAR, TIME_CROSS, TIME_CAR)
    option = 0
    bias_w, bias_h = BIAS_WIDTH_BASIC, BIAS_HEIGHT_BASIC
    bias_time_last = time.time()
    bias_direct = None
    while True:
        #检测退出事件
        checkForQuit()
        
        map.update()
        
        key_d = checkForKeyDown()
        key_u = checkForKeyUp()
        for i, k in enumerate([K_0, K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9]):
            if key_d == k:
                option = i

        if key_d == K_LEFT:
            bias_direct = "E"
        elif key_d == K_UP:
            bias_direct = "S"
        elif key_d == K_RIGHT:
            bias_direct = "W"
        elif key_d == K_DOWN:
            bias_direct = "N"

        if bias_direct == "E":
            if time.time() - bias_time_last > BIAS_TIME and bias_w >= BIAS_WIDTH_MIN + BASIC_UNIT:
                bias_w -= BASIC_UNIT
                bias_time_last = time.time()
            if key_u == K_LEFT:
                bias_direct = None
        elif bias_direct == "S":
            if time.time() - bias_time_last > BIAS_TIME and bias_h >= BIAS_HEIGHT_MIN + BASIC_UNIT: 
                bias_h -= BASIC_UNIT
                bias_time_last = time.time()
            if key_u == K_UP:
                bias_direct = None
        elif bias_direct == "W":
            if time.time() - bias_time_last > BIAS_TIME and bias_w <= BIAS_WIDTH_MAX - BASIC_UNIT: 
                bias_w += BASIC_UNIT
                bias_time_last = time.time()
            if key_u == K_RIGHT:
                bias_direct = None
        elif bias_direct == "N":
            if time.time() - bias_time_last > BIAS_TIME and bias_h <= BIAS_HEIGHT_MAX - BASIC_UNIT: 
                bias_h += BASIC_UNIT
                bias_time_last = time.time()
            if key_u == K_DOWN:
                bias_direct = None
        #print("BIAS: ", bias_direct, bias_w, bias_h)
             
        map.setTimeAddCar(OPTION_ADD_CAR[option][0] * BASIC_TIME_ADD_CAR)
        map.setNumAddCar(OPTION_ADD_CAR[option][1] * BASIC_NUM_ADD_CAR) 

        num_start, num_move, num_cross, num_end, avg_distance, avg_time, avg_speed = map.count()        
                
        #绘图步骤 --------
        drawBackground()
        drawMap(map, option, bias_w, bias_h)
        drawMessage(num_start, num_move, num_cross, num_end, avg_distance, avg_time, avg_speed, OPTION_ADD_CAR[option][0], OPTION_ADD_CAR[option][1])
        
        pygame.display.update()
        #clearKeyEvent()
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

def checkForKeyUp():
    ''' Check for button up, ignore and clear other button event
    '''
    for event in pygame.event.get(KEYUP):
        if event.key in [K_SPACE, K_UP, K_DOWN, K_LEFT, K_RIGHT, K_0, K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9]:
            return event.key
    return None
    
def checkForKeyDown():
    ''' Check for button up, ignore and clear other button event
    '''
    for event in pygame.event.get(KEYDOWN):
        if event.key in [K_SPACE, K_UP, K_DOWN, K_LEFT, K_RIGHT, K_0, K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9]:
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

def drawMap(map, option=0, bias_w=BIAS_WIDTH_BASIC, bias_h=BIAS_HEIGHT_BASIC):
    # Map
    x, y, w, h = 0, 0, MAP_WIDTH, MAP_HEIGHT
    pygame.draw.rect(display_surf, COLOR_MAP, (x, y, w, h))

    # Road
    for road in map.getRoadList():
        pos_en, pos_ex = road.getPos()
        direct = road.getDirect()
        length = road.getLength()
        busy = road.getBusyDegree()
        if direct == "E":
            x, y, w, h = pos_en[0]*BASIC_UNIT, pos_en[1]*BASIC_UNIT+BASIC_UNIT//2, length*BASIC_UNIT, BASIC_UNIT//2
        elif direct == "S":
            x, y, w, h = pos_en[0]*BASIC_UNIT, pos_en[1]*BASIC_UNIT, BASIC_UNIT//2, length*BASIC_UNIT
        elif direct == "W":
            x, y, w, h = pos_ex[0]*BASIC_UNIT, pos_ex[1]*BASIC_UNIT, length*BASIC_UNIT, BASIC_UNIT//2
        elif direct == "N":
            x, y, w, h = pos_ex[0]*BASIC_UNIT+BASIC_UNIT//2, pos_ex[1]*BASIC_UNIT, BASIC_UNIT//2, length*BASIC_UNIT
        x, y, w, h = x+bias_w, y+bias_h, w, h
        pygame.draw.rect(display_surf, COLOR_ROAD, (x, y, w, h))
        if True: #Busy
            color_busy = []
            for i in range(3): #RGB
                color_busy.append(int(RED[i] * busy + COLOR_ROAD[i] * (1-busy)))
            if direct == "E":
                x, y, w, h = (pos_en[0]+1)*BASIC_UNIT, (pos_en[1]+1)*BASIC_UNIT-BASIC_UNIT//4, (length-2)*BASIC_UNIT, BASIC_UNIT//4
            elif direct == "S":
                x, y, w, h = pos_en[0]*BASIC_UNIT, (pos_en[1]+1)*BASIC_UNIT, BASIC_UNIT//4, (length-2)*BASIC_UNIT
            elif direct == "W":
                x, y, w, h = (pos_ex[0]+1)*BASIC_UNIT, pos_ex[1]*BASIC_UNIT, (length-2)*BASIC_UNIT, BASIC_UNIT//4
            elif direct == "N":
                x, y, w, h = (pos_ex[0]+1)*BASIC_UNIT-BASIC_UNIT//4, (pos_ex[1]+1)*BASIC_UNIT, BASIC_UNIT//4, (length-2)*BASIC_UNIT
            x, y, w, h = x+bias_w, y+bias_h, w, h
            pygame.draw.rect(display_surf, color_busy, (x, y, w, h))
    
    #Cross
    for cross in map.getCrossList():
        pos = cross.getPos()
        direct = cross.getDirectEnabled()
        if direct == "E":
            x, y, w, h = pos[0]*BASIC_UNIT, pos[1]*BASIC_UNIT, BASIC_UNIT//4, BASIC_UNIT
        elif direct == "S":
            x, y, w, h = pos[0]*BASIC_UNIT, pos[1]*BASIC_UNIT, BASIC_UNIT, BASIC_UNIT//4
        elif direct == "W":
            x, y, w, h = (pos[0]+1)*BASIC_UNIT-BASIC_UNIT//4, pos[1]*BASIC_UNIT, BASIC_UNIT//4, BASIC_UNIT
        elif direct == "N":
            x, y, w, h = pos[0]*BASIC_UNIT, (pos[1]+1)*BASIC_UNIT-BASIC_UNIT//4, BASIC_UNIT, BASIC_UNIT//4
        x, y, w, h = x+bias_w, y+bias_h, w, h
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
        if False: #Start Point
            pos_en, pos_ex = road_src.getPos()
            offset = offset_src
            direct = road_src.getDirect()
            length = road_src.getLength()
            if direct == "E":
                x, y, w, h = (pos_ex[0]-offset)*BASIC_UNIT, (pos_ex[1]+1)*BASIC_UNIT, BASIC_UNIT, BASIC_UNIT*2//3
            elif direct == "S": 
                x, y, w, h = pos_ex[0]*BASIC_UNIT-BASIC_UNIT*2//3, (pos_ex[1]-offset)*BASIC_UNIT, BASIC_UNIT*2//3, BASIC_UNIT
            elif direct == "W":
                x, y, w, h = (pos_ex[0]+offset)*BASIC_UNIT, pos_ex[1]*BASIC_UNIT-BASIC_UNIT*2//3, BASIC_UNIT, BASIC_UNIT*2//3
            elif direct == "N":
                x, y, w, h = (pos_ex[0]+1)*BASIC_UNIT, (pos_ex[1]+offset)*BASIC_UNIT, BASIC_UNIT*2//3, BASIC_UNIT
            x, y, w, h = x+1, y+1, w-2, h-2
            x, y, w, h = x+bias_w, y+bias_h, w, h
            pygame.draw.rect(display_surf, color_car, (x, y, w, h))        
        if True: #End Point
            pos_en, pos_ex = road_dst.getPos()
            offset = offset_dst
            direct = road_dst.getDirect()
            length = road_dst.getLength()
            if direct == "E":
                x, y, w, h = (pos_ex[0]-offset)*BASIC_UNIT, (pos_ex[1]+1)*BASIC_UNIT, BASIC_UNIT, BASIC_UNIT*2//3
            elif direct == "S": 
                x, y, w, h = pos_ex[0]*BASIC_UNIT-BASIC_UNIT*2//3, (pos_ex[1]-offset)*BASIC_UNIT, BASIC_UNIT*2//3, BASIC_UNIT
            elif direct == "W":
                x, y, w, h = (pos_ex[0]+offset)*BASIC_UNIT, pos_ex[1]*BASIC_UNIT-BASIC_UNIT*2//3, BASIC_UNIT, BASIC_UNIT*2//3
            elif direct == "N":
                x, y, w, h = (pos_ex[0]+1)*BASIC_UNIT, (pos_ex[1]+offset)*BASIC_UNIT, BASIC_UNIT*2//3, BASIC_UNIT
            x, y, w, h = x+1, y+1, w-2, h-2
            x, y, w, h = x+bias_w, y+bias_h, w, h
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
            x, y, w, h = x+bias_w, y+bias_h, w, h
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
            x, y, w, h = x+bias_w, y+bias_h, w, h
            pygame.draw.rect(display_surf, color_car, (x, y, w, h))            
            
def drawText(string, index):
    font = pygame.font.Font('resource/font/courbd.ttf', FONT_SIZE)
    textSurfaceObj = font.render(string, True, WHITE, BLACK)
    textRectObj = textSurfaceObj.get_rect()
    textRectObj.topleft = (MAP_WIDTH, index * FONT_SIZE)
    display_surf.blit(textSurfaceObj, textRectObj)
    return index

def drawMessage(num_start, num_move, num_cross, num_end, avg_distance, avg_time, avg_speed, add_car_time, add_car_num):
    pygame.draw.rect(display_surf, BLACK, (MAP_WIDTH, 0, WINDOW_WIDTH-MAP_WIDTH, WINDOW_HEIGHT))
    index = 0
    index = drawText("Car Number", index) + 1
    index = drawText("  Start: "+str(num_start), index) + 1
    index = drawText("  Move : "+str(num_move), index) + 1
    index = drawText("  Cross: "+str(num_cross), index) + 1
    index = drawText("  End  : "+str(num_end), index) + 1
    index = drawText("Statistics", index) + 1
    index = drawText("  Dist : "+str(avg_distance), index) + 1
    index = drawText("  Time : "+str(avg_time), index) + 1
    index = drawText("  Speed: "+str(avg_speed), index) + 1
    index = drawText("Option", index) + 1
    index = drawText("  Time : "+str(add_car_time), index) + 1
    index = drawText("  Num  : "+str(add_car_num), index) + 1

#====入口
if __name__ == '__main__':
    main()    
