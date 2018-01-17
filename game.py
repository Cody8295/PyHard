# Cody DallaValle
# PyHard

# TO DO: #
##########
# center ply on minimap
# wep sprites and integration
# sound
# networking (BT and wifi)
# android port
# terrain sprites
# 2D/3D terrain
# seamless minimap scroll

import sys, pygame, random, struct
from pygame.locals import *
import numpy as np
import numpy.random
import matplotlib.pyplot as pp
#from collections import defaultdict

up, down, left, right = False, False, False, False
tiles = {} # a dict maching tileIds to lists of walls
tileSpaces = {} # a dict matching tileIds to Rects of its bounds
activeTile = 0 # int representation of a tile ID
bullets = {} # a dict matching bullet ID's to their (x,y) pos
weapons = {} # a dict matching weapon ID's to a list of wep info
tileSize = 64*50

# Format: name, dmg, self dmg, delay, default ammo
weapons[0] = ["Fists", 100, 20, 500, 0]
weapons[1] = ["Knive", 250, 0, 1000, 0]
weapons[2] = ["Revolver", 500, 0, 600, 50]
weapons[3] = ["Glock", 300, 0, 100, 100]
weapons[4] = ["AK47", 200, 0, 30, 300]
weapons[5] = ["AWP", 900, 0, 2000, 30]
weapons[6] = ["Grenade", 2000, 2000, 3000, 8]
weapons[7] = ["M16", 230, 0, 100, 250]

def genHeatmap(seed):
    if seed==0: seed = 64
    seed = abs(64%seed)+3
    rX = np.random.randn(4096*seed)
    rY = np.random.randn(4096*seed)
    heatmap, xe, ye = np.histogram2d(rX, rY, bins=(64,64))
    return heatmap

def generateMap(tileId):
    global tiles
    hm = genHeatmap(tileId)
    hmSize = np.shape(hm) # size of 2d array
    tileWalls = [] # blank array which will become the tile walls
    for x in xrange(0, hmSize[0]):
	for y in xrange(0, hmSize[1]):
	    if hm[x][y]==0.0: continue
	    tileWalls.append([x*50, y*50, 50, 50])
	    # print "\n" + str(x) + " " + str(y) + " = " + " " + str(hm[x][y])
    #raw_input()
    tiles[tileId] = tileWalls

def getTileAtPos(xyPos):
    for tileId, tile in tileSpaces.items():
        if tile[0]==xyPos[0] and tile[1]==xyPos[1]: return tileId
    return -1

def generateTile():
    newTile = (plyPos[0], plyPos[1], tileSize, tileSize)
    tileCount = len(tileSpaces)
    
    if tileCount<1:
        tileSpaces[0] = newTile
	generateMap(0)
	return 0

    act = tileSpaces[activeTile] if activeTile in tileSpaces else tileSpaces[tileCount-1]
    
    if up:
        newTile = (act[0], act[1]-tileSize, newTile[2], newTile[3])
	if not getTileAtPos((newTile[0], newTile[1]))==-1: return
	tileSpaces[tileCount]=newTile
	generateMap(tileCount)
	return tileCount
    if down:
	newTile = (act[0], act[1]+tileSize, newTile[2], newTile[3])
	if not getTileAtPos((newTile[0], newTile[1]))==-1: return
	tileSpaces[tileCount]=newTile
	generateMap(tileCount)
	return tileCount
    if left:
	newTile = (act[0]-tileSize, act[1], newTile[2], newTile[3])
	if not getTileAtPos((newTile[0], newTile[1]))==-1: return
	tileSpaces[tileCount]=newTile
	generateMap(tileCount)
	return tileCount
    if right:
	newTile = (act[0]+tileSize, act[1], newTile[2], newTile[3])
	if not getTileAtPos((newTile[0], newTile[1]))==-1: return
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
plyWepId = 0
scrollLimit = 100

hudHealthTxt = font1.render("Health: " + str(plyHp/10), 1, black)

def updateActiveTile():
    global activeTile

    #tileSpaces is a dict matching tileId's to Rects
    for tileId, bounds in tileSpaces.items():
	if pygame.Rect(bounds).collidepoint(plyPos[0]-offsetX, plyPos[1]-offsetY):
	    if activeTile==tileId: return
	    activeTile = tileId
	    print "Ply is in tile number " + str(tileId)
	    return
    
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

    if not activeTile in tileSpaces: return    
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

def plyAttackPrimary():
    if not plyWepId in weapons: return
    wepInfo = weapons[plyWepId]
    # Format: Name, dmg, self dmg, delay, default ammo
    if wepInfo[0]=="Fists":
	return
    

def drawHUD():
    hndl.blit(hudHealthTxt, (5, 5))

def drawMinimap():
    x, y = W-80, 5
    mm = pygame.Rect(x, y, 75, 75)
    pygame.draw.rect(hndl, white, mm)
    pygame.draw.rect(hndl, black, mm, 1)
    if not activeTile in tiles: return
    for wall in tiles[activeTile]:
        act = tileSpaces[activeTile]
        if wall[0]<plyPos[0]+W*2-offsetX-act[0] and wall[0]>plyPos[0]-W-offsetX-act[0] and wall[1]<plyPos[1]+H*2-offsetY-act[1] and wall[1]>plyPos[1]-H-offsetY-act[1]:
            wallOffset = (wall[0]+offsetX+act[0], wall[1]+offsetY+act[1], wall[2], wall[3])
	    wallOffset = (wallOffset[0]/10+x, wallOffset[1]/10+y, wallOffset[2]/10, wallOffset[3]/10)
            if mm.contains(wallOffset):
		pygame.draw.rect(hndl, green, wallOffset)
    pygame.draw.rect(hndl, red, (plyPos[0]/10+x, plyPos[1]/10+y, 2, 2))

def getTileAtPos(xyPos):
    for tileId, tile in tileSpaces.items():
	if tile[0]==xyPos[0] and tile[1]==xyPos[1]: return tileId
    return -1

activeTile2, activeTile3, activeTile4 = -1, -1, -1 # 4 tiles is max ply will see at once

def noCollideWalls(): # tells drawWalls about walls of tile(s) that the
			# ply is/are close to but not actually in.
			  # Collision only considers the local tile
			  # but sometimes the ply sees into others.
    global activeTile2
    global activeTile3
    activeTile2, activeTile3, activeTile4 = -1,-1, -1 # reset
    act = tileSpaces[activeTile]
    
    rightTile = getTileAtPos((act[0]+tileSize, act[1]))
    leftTile = getTileAtPos((act[0]-tileSize, act[1]))
    bottomTile = getTileAtPos((act[0], act[1]+tileSize))
    topTile = getTileAtPos((act[0], act[1]-tileSize))

    if plyPos[0]-offsetX>act[0]+act[2]-W: # user sees right tile
	print "checking right tile for visiblity"
	print tileSpaces
	print getTileAtPos((act[0]+tileSize, act[1]))
	if not rightTile==-1:
	    print "visible"
	    activeTile2 = rightTile # early bird gets the worm
    if plyPos[0]-offsetX<act[0]+W: # user sees left tile
	if not leftTile==-1:
	    activeTile3 = leftTile # maybe used, now we have to check
    if plyPos[1]-offsetY>act[1]+act[3]-H: # user sees bottom tile
	if not bottomTile==-1:
	    activeTile4 = bottomTile
    if plyPos[1]-offsetY<act[1]+H: # user sees top tile
	if not topTile==-1:
	    if not activeTile2==-1:
		activeTile3 = topTile
	    elif not activeTile3==-1: activeTile4 = topTile

def drawWalls(): # only draws walls near player
    if not activeTile in tiles:
	# not a real active tile id
	print "Tile ID invalid"
	return
    
    visibleTiles = [] # tile id's
    visibleTiles.append(activeTile)
    noCollideWalls()
        
    if not activeTile2==-1:
	visibleTiles.append(activeTile2)
    if not activeTile3==-1:
	visibleTiles.append(activeTile3)
    if not activeTile4==-1:
	visibleTiles.append(activeTile4)

    for tileId in visibleTiles:
        for wall in tiles[tileId]:
            act = tileSpaces[tileId]
	    if wall[0]<plyPos[0]+W-offsetX-act[0] and wall[0]>plyPos[0]-W-offsetX-act[0] and wall[1]<plyPos[1]+H-offsetY-act[1] and wall[1]>plyPos[1]-H-offsetY-act[1]:
	        wallOffset = (wall[0]+offsetX+act[0], wall[1]+offsetY+act[1], wall[2], wall[3])
	        pygame.draw.rect(hndl, green, wallOffset)
    
  
def drawPly():
    if up: plyUp()
    if down: plyDown()
    if left: plyLeft()
    if right: plyRight()
    pygame.draw.rect(hndl, blue, (plyPos[0], plyPos[1], 5, 5))

def tileTimer(): # checks every couple ms if the ply is close
		 # to the end of any tile, and updates screen
		 # with new tile. too wasteful doing this every 30 ticks
    #print pygame.time.get_ticks()
    if pygame.time.get_ticks()%7==0:
	updateActiveTile()
    
    #DEBUGGING stuff below
    #print str(plyPos[0]) + "," + str(plyPos[1])
    #print str(plyPos[0]+offsetX) +","+ str(plyPos[1]+offsetY)
        #print str(plyPos[0]-offsetX) +","+ str(plyPos[1]-offsetY)
        #act = tileSpaces[activeTile] if activeTile in tileSpaces else (-1,-1,-1,-1)
	#print str(activeTile2) + ","+str(activeTile3)+","+str(activeTile4)
    #print str(plyPos[0]+offsetX) +","+ str(plyPos[1]-offsetY)

generateTile()

# MAIN GAME LOOP
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
	else: # ply is alive and already clicked start
	    drawWalls()
	    drawHUD()
	    drawPly()
	    drawMinimap()
	    tileTimer()
    else: # ply is dead
	hndl.fill(black)

    # EVENT LOOP
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
