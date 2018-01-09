# Cody DallaValle
# PyHard

import sys, pygame, random, struct
from pygame.locals import *
import numpy as np
import numpy.random
import matplotlib.pyplot as pp
#from collections import defaultdict

up, down, left, right = False, False, False, False
tiles = {} # a dict maching tileIds to lists of walls
tileSpaces = {} # a dict matching tileIds to Rects of its bounds
activeTile = 0

def genHeatmap(seed):
    if seed==0: seed = 64
    seed = abs(64%seed)+3
    rX = np.random.randn(128*seed)
    rY = np.random.randn(128*seed)
    heatmap, xe, ye = np.histogram2d(rX, rY, bins=(64,64))
    #ext = [xe[0], xe[-1], ye[0], ye[-1]]
    return heatmap

def generateMap(tileId):
    global tiles
    hm = genHeatmap(tileId)
    hmSize = np.shape(hm) # size of 2d array
    tileWalls = []
    for x in xrange(0, hmSize[0]):
	for y in xrange(0, hmSize[1]):
	    if hm[x][y]==0.0: continue
	    tileWalls.append([x*50, y*50, 50, 50])
	    # print "\n" + str(x) + " " + str(y) + " = " + " " + str(hm[x][y])
    #raw_input()
    tiles[tileId] = tileWalls

def generateTile():
    newTile = (plyPos[0], plyPos[1], 64*50, 64*50)
    tileCount = len(tileSpaces)
    
    if tileCount<1:
            tileSpaces[0] = newTile
	    generateMap(0)
	    return 0
    act = tileSpaces[activeTile]

    if up:
        newTile = (act[0], act[1]-64*50, newTile[2], newTile[3])
	tileSpaces[tileCount]=newTile
	generateMap(tileCount)
	return tileCount
    if down:
	newTile = (act[0], act[1]+64*50, newTile[2], newTile[3])
	tileSpaces[tileCount]=newTile
	generateMap(tileCount)
	return tileCount
    if left:
	newTile = (act[0]-64*50, act[1], newTile[2], newTile[3])
	tileSpaces[tileCount]=newTile
	generateMap(tileCount)
	return tileCount
    if right:
	newTile = (act[0]+64*50, act[1], newTile[2], newTile[3])
	tileSpaces[tileCount]=newTile
	generateMap(tileCount)
	return tileCount

def randomSpawn():
    randX, randY = random.randint(125,250), random.randint(125, 250)
    # check for obstructions first
    return (randX, randY) 	

W, H = 500, 300
offsetX, offsetY = 0, 0
pygame.init()
clock = pygame.time.Clock()
hndl = pygame.display.set_mode((W, H))
pygame.display.set_caption("PyHard")
pygame.key.set_repeat(45, 20)

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
plyPos = (50, 50)
plyHp = 1000
plySpeed = 6
scrollLimit = 100

hudHealthTxt = font1.render("Health: " + str(plyHp/10), 1, black)

def updateActiveTile():
    global activeTile
    print "starting search @ " +str(pygame.time.get_ticks())

    for tileId, bounds in tileSpaces.items():
	if pygame.Rect(bounds).collidepoint(plyPos[0]-offsetX, plyPos[1]-offsetY):
	    activeTile = tileId
	    
	    print "Ply is in tile number " + str(tileId)
	    return
    
    print "new tile @"
    print plyPos[0]-offsetX
    print plyPos[1]-offsetY
    print tileSpaces[activeTile]
    activeTile = generateTile()
	

def offset():
    global plyPos, offsetX, offsetY
    if plyPos[0]<scrollLimit:
	plyPos=(scrollLimit,plyPos[1])
	offsetX=offsetX+plySpeed
    if plyPos[0]>W-scrollLimit:
	plyPos=(W-scrollLimit,plyPos[1])
	offsetX=offsetX-plySpeed
    if plyPos[1]<scrollLimit:
	plyPos=(plyPos[0],scrollLimit)
	offsetY=offsetY+plySpeed
    if plyPos[1]>H-scrollLimit:
	plyPos=(plyPos[0], H-scrollLimit)
	offsetY=offsetY-plySpeed
    
    act = tileSpaces[activeTile]
    cb = 100 # how many pixels away a wall should be to consider collision
    for wall in tiles[activeTile]:
	if wall[0]<plyPos[0]+cb-offsetX-act[0] and wall[0]>plyPos[0]-cb-offsetX-act[0] and wall[1]<plyPos[1]+cb-offsetY-act[1] and wall[1]>plyPos[1]-cb-offsetY-act[1]:
            
	    if pygame.Rect(wall).collidepoint(plyPos[0]-offsetX-act[0],plyPos[1]-offsetY-act[1]):
	        return False
    return True

def plyUp():
    global plyPos
    plyPos = (plyPos[0], plyPos[1]-plySpeed)
    if not offset(): plyPos = (plyPos[0], plyPos[1]+plySpeed)

def plyDown():
    global plyPos
    plyPos = (plyPos[0], plyPos[1]+plySpeed)
    if not offset(): plyPos = (plyPos[0], plyPos[1]-plySpeed)

def plyLeft():
    global plyPos
    plyPos = (plyPos[0]-plySpeed, plyPos[1])
    if not offset(): plyPos = (plyPos[0]+plySpeed, plyPos[1])

def plyRight():
    global plyPos
    plyPos = (plyPos[0]+plySpeed, plyPos[1])
    if not offset(): plyPos = (plyPos[0]-plySpeed, plyPos[1])

def drawHUD():
    hndl.blit(hudHealthTxt, (5, 5))

def drawWalls(): # only draws walls near player
    if not activeTile in tiles:
	# not a real active tile id
	print "Tile ID invalid"
	return

    for wall in tiles[activeTile]:
        act = tileSpaces[activeTile]
	if wall[0]<plyPos[0]+W-offsetX-act[0] and wall[0]>plyPos[0]-W-offsetX-act[0] and wall[1]<plyPos[1]+H-offsetY-act[1] and wall[1]>plyPos[1]-H-offsetY-act[1]:
	    wallOffset = (wall[0]+offsetX+act[0], wall[1]+offsetY+act[1], wall[2], wall[3])
	    pygame.draw.rect(hndl, green, wallOffset)


def drawPly():
    if up: plyUp()
    if down: plyDown()
    if left: plyLeft()
    if right: plyRight()
    pygame.draw.rect(hndl, blue, (plyPos[0], plyPos[1], 5, 5))

def tileTimer(): # checks every second if the ply is close
		 # to the end of any tile, and updates screen
		 # with new tile. too wasteful doing this every 30 ticks
    #print pygame.time.get_ticks()
    if pygame.time.get_ticks()%7==0:
	updateActiveTile()
    #DEBUGGING stuff below
    #print str(plyPos[0]) + "," + str(plyPos[1])
    #print str(plyPos[0]+offsetX) +","+ str(plyPos[1]+offsetY)
        print str(plyPos[0]-offsetX) +","+ str(plyPos[1]-offsetY)
        print tileSpaces[activeTile]
    #print str(plyPos[0]+offsetX) +","+ str(plyPos[1]-offsetY)


#GEN MAP ORIGINAL
#generateMap()
generateTile()

while True:
    
    if(alive):
	hndl.fill(white)
	if(starting): # show start menu
	    global startButton
	    hndl.blit(mainMenuTxt, (220,50)) # first draw title text
	    #then draw green background for start button
	    startButton = pygame.draw.rect(hndl, green, startBounds)
	    hndl.blit(mainMenuStart, (275, 90)) # finally draw start text
	    plyPos = randomSpawn()
	else:
	    drawWalls()
	    drawHUD()
	    drawPly()
	    tileTimer()
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
