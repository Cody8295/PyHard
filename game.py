# Cody DallaValle
# PyHard

import sys, pygame
from pygame.locals import *

def generateMap():
    print "generating"

pygame.init()
clock = pygame.time.Clock()
hndl = pygame.display.set_mode((500, 300))
pygame.display.set_caption("PyHard")
pygame.key.set_repeat(60, 55)

red = pygame.Color(255, 0, 0)
green = pygame.Color(0, 255, 0)
blue = pygame.Color(0, 0, 255)
black = pygame.Color(0, 0, 0)
white = pygame.Color(255, 255, 255)

mainMenuFont = pygame.font.SysFont("monospace", 36)
mainMenuTxt = mainMenuFont.render("PyHard", 1, red)

font1 = pygame.font.SysFont("monospace", 18)
mainMenuStart = font1.render("Start", 1, black)
startBounds = pygame.Rect(250, 90, 100, 25)

starting = True;
alive = True
plyPos = (0, 0)
plyHp = 1000
plySpeed = 10

up, down, left, right = False, False, False, False

def plyUp():
    global plyPos
    plyPos = (plyPos[0], plyPos[1]-plySpeed)
def plyDown():
    global plyPos
    plyPos = (plyPos[0], plyPos[1]+plySpeed)
def plyLeft():
    global plyPos
    plyPos = (plyPos[0]-plySpeed, plyPos[1])
def plyRight():
    global plyPos
    plyPos = (plyPos[0]+plySpeed, plyPos[1])

def drawHUD():
    font1.render("Health: "+str(plyHp/10), 1, green)


def drawPly():
    if up: plyUp()
    if down: plyDown()
    if left: plyLeft()
    if right: plyRight()
    pygame.draw.rect(hndl, blue, (plyPos[0], plyPos[1], 5, 5))

while True:
    
    if(alive):
	hndl.fill(white)
	if(starting): # show start menu
	    global startButton
	    hndl.blit(mainMenuTxt, (220,50)) # first draw title text
	    #then draw green background for start button
	    startButton = pygame.draw.rect(hndl, green, startBounds)
	    hndl.blit(mainMenuStart, (275, 90)) # finally draw start text
	else:
	    drawHUD();
	    drawPly();
	    
    else:
	hndl.fill(black)
    for event in pygame.event.get():
	if starting and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
	    # the user left clicked somewhere on the start screen
	    pos = pygame.mouse.get_pos()
	    if startButton.collidepoint(pos):
		starting = False; # a user clicked on start button
	elif not starting: # game in progress
	    if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
		pos = pygame.mouse.get_pos()
	        # mouse click in gameplay
	    elif event.type==pygame.KEYDOWN: # key down
		if event.key==pygame.K_UP or event.key==pygame.K_w: up=True
		if event.key==pygame.K_DOWN or event.key==pygame.K_s: down=True
		if event.key==pygame.K_LEFT or event.key==pygame.K_a: left=True
		if event.key==pygame.K_RIGHT or event.key==pygame.K_d: right=True
	    elif event.type==pygame.KEYUP:
		if event.key==pygame.K_UP or event.key==pygame.K_w: up=False
		if event.key==pygame.K_DOWN or event.key==pygame.K_s: down=False
		if event.key==pygame.K_LEFT or event.key==K_a: left=False
		if event.key==pygame.K_RIGHT or event.key==K_d: right=False
    pygame.display.update()
    clock.tick(30)
