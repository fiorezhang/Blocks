#coding:utf-8
#copyright: fiorezhang@sina.com

import sys
import math
import numpy as np
import random
import time
import pygame
from pygame.locals import *

#====全局
FPS = 30
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
BASIC_UNIT = 10
assert WINDOW_WIDTH % BASIC_UNIT == 0
assert WINDOW_HEIGHT % BASIC_UNIT == 0

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
    while True:
        #检测退出事件
        checkForQuit()
        
        #绘图步骤 --------
        drawBackground()
        
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

#====入口
if __name__ == '__main__':
    main()    