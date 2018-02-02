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
# fix the cellular automata map gen
# continue USB controller support
# finish start menu
# optimize search algos

import sys, pygame, random, struct
from pygame.locals import *
import numpy as np
#import numpy.random
#import matplotlib.pyplot as pp


up, down, left, right = False, False, False, False
tiles = {} # a dict maching tileIds to lists of walls
tileSpaces = {} # a dict matching tileIds to Rects of its bounds
activeTile = 0 # int representation of a tile ID
bullets = {} # a dict matching bullet ID's to their (x,y) pos
weapons = {} # a dict matching weapon ID's to a list of wep info
tileSize = 64*50
spawned = False

pygame.joystick.init()

# Format: name, dmg, self dmg, delay, default ammo
weapons[0] = ["Fists", 100, 20, 500, 0]
weapons[1] = ["Knife", 250, 0, 1000, 0]
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
    
    hmSize = (64, 64) # size of 2d array
    
    hm = np.empty((64, 64))
    hm.fill(0)
    hm = hm.tolist()
    
    tileWalls = [] # blank array which will become the tile walls
    for x in xrange(0, hmSize[0]):
	for y in xrange(0, hmSize[1]):
	    hm[x][y] = random.uniform(0, 1)
    #for z in xrange(0, 15):
#	hm = caRules(hm, hmSize, tileId)
    
    fixCorners(hm, hmSize, tileId)
    

wallVal = 0.1

def fixCorners(hm, hmSize, tileId):
    tileWalls = []
    for x in xrange(0, hmSize[0]):
        for y in xrange(0, hmSize[1]):
	    if hm[x][y]<=wallVal: tileWalls.append((x*50, y*50, 50, 50)) # add existing walls
	    if x-1>=0 and y-1>=0 and hm[x-1][y-1]<=wallVal:
		# wall has a neighbor NW, check for jagged-ness
		if hm[x-1][y]>wallVal and hm[x][y-1]>wallVal:
		    # wall is jagged in respect to NW neighbor
		    # because it has no north or west neighbors
		    # pick a direction at random to place new wall
		    randDir = random.randint(0,1)
		    if randDir==0:
			tileWalls.append(((x-1)*50, y*50, 50, 50))
		    else:
			tileWalls.append((x*50, (y-1)*50, 50, 50))
	    if x+1<hmSize[0] and y-1>=0 and hm[x+1][y-1]<=wallVal:
		# wall has a neighbor NE
		if hm[x][y-1]>wallVal and hm[x+1][y]>wallVal:
		    # wall is jagged in respect to NE neighbor
		    # no north or east neightbors, pick randomly
		    randDir = random.randint(0,1)
		    if randDir==0:
			tileWalls.append(((x+1)*50, y*50, 50, 50))
		    else:
			tileWalls.append((x*50, (y-1)*50, 50, 50))
	    if x+1<hmSize[0] and y+1<hmSize[1] and hm[x+1][y+1]<=wallVal:
		# wall has a SE neighbor
		if hm[x+1][y]>wallVal and hm[x][y+1]>wallVal:
		    # wall is jagged in respect to SE neighbor
		    # no south or east neighbors, pick randomly
		    randDir = random.randint(0,1)
		    if randDir==0:
			tileWalls.append(((x+1)*50, y*50, 50, 50))
		    else:
			tileWalls.append((x*50, (y+1)*50, 50, 50))
	    if x-1>=0 and y+1<hmSize[1] and hm[x-1][y+1]<=wallVal:
		# wall has a SW neighbor
		if hm[x-1][y]>wallVal and hm[x][y+1]>wallVal:
		    # wall is jagged in respect to SW neighbor
		    # no south or west neighbors, pick randomly
		    randDir = random.randint(0,1)
		    if randDir==0:
			tileWalls.append(((x+1)*50, y*50, 50, 50))
		    else:
			tileWalls.append((x*50, (y+1)*50, 50, 50))
    tiles[tileId] = tileWalls

def caRules(hm, hmSize, tileId): # transforms a 2d array by applying
		           # cellular automata rules
    tileWalls = []
    #wallVal = 0.6 # threashold for determining block vs floor
    for x in xrange(0, hmSize[0]):
	for y in xrange(0, hmSize[1]):
	    if hm[x][y]>wallVal:
		continue # is a floor
            nbh = 0 # neighborhood count
            if x+1<hmSize[0] and hm[x+1][y]<=wallVal: nbh=nbh+1
            if x+1<hmSize[0] and y+1<hmSize[1] and hm[x+1][y+1]<=wallVal:
                nbh=nbh+1
            if x+1<hmSize[0] and y-1>=0 and hm[x+1][y-1]<=wallVal:
                nbh=nbh+1
            if y+1<hmSize[1] and hm[x][y+1]<=wallVal: nbh=nbh+1
            if y-1>=0 and hm[x][y-1]<=wallVal: nbh=nbh+1
            if x-1>=0 and hm[x-1][y]<=wallVal: nbh=nbh+1
            if x-1>=0 and y+1<hmSize[1] and hm[x-1][y+1]<=wallVal:
                nbh=nbh+1
            if x-1>=0 and y-1>=0 and hm[x-1][y-1]<=wallVal: nbh=nbh+1
            
            if nbh>5:
		#hm[x][y] = 0
		tileWalls.append((x*50, y*50, 50, 50))
	   # else:
	#	hm[x][y] = 1
    #return hm
    tiles[tileId] = tileWalls
    return hm

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
    
    if up or plyPos[1]-offsetY<act[1]:
        newTile = (act[0], act[1]-tileSize, newTile[2], newTile[3])
	exists = getTileAtPos((newTile[0], newTile[1]))
	if not exists==-1: return exists
	tileSpaces[tileCount]=newTile
	generateMap(tileCount)
	return tileCount
    if down or plyPos[1]-offsetY>act[1]+act[3]:
	newTile = (act[0], act[1]+tileSize, newTile[2], newTile[3])
	exists = getTileAtPos((newTile[0], newTile[1]))
	if not exists==-1: return exists
	tileSpaces[tileCount]=newTile
	generateMap(tileCount)
	return tileCount
    if left or plyPos[0]-offsetX<act[0]:
	newTile = (act[0]-tileSize, act[1], newTile[2], newTile[3])
	exists = getTileAtPos((newTile[0], newTile[1]))
	if not exists==-1: return exists
	tileSpaces[tileCount]=newTile
	generateMap(tileCount)
	return tileCount
    if right or plyPos[0]-offsetX<act[0]+act[2]:
	newTile = (act[0]+tileSize, act[1], newTile[2], newTile[3])
	exists = getTileAtPos((newTile[0], newTile[1]))
	if not exists==-1: return exists
	tileSpaces[tileCount]=newTile
	generateMap(tileCount)
	return tileCount

def randomSpawn():
    global spawned
    act = tileSpaces[activeTile]
    randX, randY = random.randint(0,500), random.randint(0, 500)
    # check for obstructions first, recursively try until good spawn found
    for wall in tiles[activeTile]:
	if pygame.Rect(wall).collidepoint(randX-offsetX+act[0], randY-offsetY+act[1]):
	    randomSpawn()
	    #return (100, 100)
	    break
    spawned = True
    print "Found good spawn"
    return (randX-offsetX+act[0],randY-offsetY+act[1])
    #return (randX, randY) 	

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
scrollLimit = 125

hudHealthTxt = font1.render("Health: " + str(plyHp/10), 1, black)

def updateActiveTile():
    global activeTile

    #tileSpaces is a dict matching tileId's to Rects
    for tileId, bounds in tileSpaces.items():
	#lessBounds = (bounds[0]+50, bounds[1]-50, bounds[2]-100, bounds[3]-100)
	if pygame.Rect(bounds).collidepoint(plyPos[0]-offsetX, plyPos[1]-offsetY):
	    if activeTile==tileId: return
	    activeTile = tileId
	    print "Ply is in tile number " + str(tileId)
	    return
    
    activeTile = generateTile()
	
collideWalls = {}

def offset():
    global plyPos, offsetX, offsetY, collideWalls
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
    collideWalls = {}
    collideWalls[activeTile] = tiles[activeTile]
    if not activeTile2==-1:
	collideWalls[activeTile2] = tiles[activeTile2]
    if not activeTile3==-1:
	collideWalls[activeTile3] = tiles[activeTile3]
    if not activeTile4==-1:
	collideWalls[activeTile4] = tiles[activeTile4]
    cb = 100 # how many pixels away a wall should be to consider collision
    for k, v in collideWalls.items():
	act = tileSpaces[k]
	ppr0 = plyPos[0]-offsetX-act[0] # optimized math
	ppr1 = plyPos[1]-offsetY-act[1] # optimized math
        for wall in v:
      	    if wall[0]<ppr0+cb and wall[0]>ppr0-cb and wall[1]<ppr1+cb and wall[1]>ppr1-cb:
	        if pygame.Rect(wall).collidepoint(ppr0,ppr1):
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

x,y = W-80, 5
mm = pygame.Rect(x,y,75, 75)
def drawMinimap():
    global x,y,mm
    #x, y = W-80, 5
    #mm = pygame.Rect(x, y, 75, 75)
    pygame.draw.rect(hndl, white, mm)
    pygame.draw.rect(hndl, black, mm, 1)
    if not activeTile in tiles: return
    for k, v in collideWalls.items():
	act = tileSpaces[k]
	b0=plyPos[0]+W*2-offsetX-act[0]
	b1=plyPos[0]-W-offsetX-act[0]
	b2=plyPos[1]+H*2-offsetY-act[1]
	b3=plyPos[1]-H-offsetY-act[1]
	#b4=plyPos[0]+offsetX+act[0] for some reason these 2
	#b5=plyPos[1]+offsetY+act[1] optimizations dont work...
        for wall in v:
            if wall[0]<b0 and wall[0]>b1 and wall[1]<b2 and wall[1]>b3:
#                wallOffset = (wall[0]-b4, wall[1]-plyPos[1]+offsetY+act[1], wall[2], wall[3])
                wallOffset = (wall[0]-plyPos[0]+offsetX+act[0], wall[1]-plyPos[1]+offsetY+act[1], wall[2], wall[3])

	        wallOffset = (wallOffset[0]/10+x+39, wallOffset[1]/10+y+39, wallOffset[2]/10, wallOffset[3]/10)
                if mm.contains(wallOffset):
		    pygame.draw.rect(hndl, green, wallOffset)
    pygame.draw.rect(hndl, red, (37+x, 37+y, 2, 2))

def getTileAtPos(xyPos):
    for tileId, tile in tileSpaces.items():
	if tile[0]==xyPos[0] and tile[1]==xyPos[1]: return tileId
    return -1

activeTile2, activeTile3, activeTile4 = -1, -1, -1 # 4 tiles is max ply will see at once

def ncTile(tile): # puts the no collide tile into an empty
		  # "active tile" variable for drawing
    global activeTile2, activeTile3, activeTile4
    if tile==-1: return # tile doesnt exist, do nothing
    if activeTile2==-1:
	activeTile2 = tile
    elif activeTile3==-1:
	activeTile3 = tile
    elif activeTile4==-1:
	activeTile4 = tile


def noCollideWalls(): # tells drawWalls about walls of tile(s) that the
			# ply is/are close to but not actually in.
			  # Collision only considers the local tile
			  # but sometimes the ply sees into others.
    global activeTile2
    global activeTile3
    global activeTile4
    activeTile2, activeTile3, activeTile4 = -1,-1,-1 # reset
    act = tileSpaces[activeTile]
    
    rightTile = getTileAtPos((act[0]+tileSize, act[1]))
    leftTile = getTileAtPos((act[0]-tileSize, act[1]))
    bottomTile = getTileAtPos((act[0], act[1]+tileSize))
    topTile = getTileAtPos((act[0], act[1]-tileSize))
    nwTile = getTileAtPos((act[0]-tileSize, act[1]-tileSize))
    neTile = getTileAtPos((act[0]+tileSize, act[1]-tileSize))
    swTile = getTileAtPos((act[0]-tileSize, act[1]+tileSize))
    seTile = getTileAtPos((act[0]+tileSize, act[1]+tileSize))

    if plyPos[0]-offsetX>act[0]+act[2]-W and plyPos[1]-offsetY>act[1]+act[3]-H:
	ncTile(seTile)
    if plyPos[0]-offsetX<act[0]+W and plyPos[1]-offsetY>act[1]+act[3]-H:
	ncTile(swTile)
    if plyPos[0]-offsetX>act[0]+act[2]-W and plyPos[1]-offsetY<act[1]+H:
	ncTile(neTile)
    if plyPos[0]-offsetX<act[0]+W and plyPos[1]-offsetY<act[1]+H:
	ncTile(nwTile)
    if plyPos[0]-offsetX>act[0]+act[2]-W: # user sees right tile
	ncTile(rightTile)
    if plyPos[0]-offsetX<act[0]+W: # user sees left tile
	ncTile(leftTile)
    if plyPos[1]-offsetY>act[1]+act[3]-H: # user sees bottom tile
	ncTile(bottomTile)
    if plyPos[1]-offsetY<act[1]+H: # user sees top tile
	ncTile(topTile)

def drawWalls(): # only draws walls near player
    if not activeTile in tiles:
	# not a real active tile id
	print "Tile ID invalid: " + str(activeTile)
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
	act = tileSpaces[tileId]
	b0=plyPos[0]+W-offsetX-act[0]
	b1=plyPos[0]-W-offsetX-act[0]
	b2=plyPos[1]+H-offsetY-act[1]
	b3=plyPos[1]-H-offsetY-act[1]
	b4=offsetX+act[0]
	b5=offsetY+act[1]
        for wall in tiles[tileId]:
	    if wall[0]<b0 and wall[0]>b1 and wall[1]<b2 and wall[1]>b3:
	        wallOffset = (wall[0]+b4, wall[1]+b5, wall[2], wall[3])
	        pygame.draw.rect(hndl, green, wallOffset)
    
  
def drawPly():
    if up: plyUp()
    if down: plyDown()
    if left: plyLeft()
    if right: plyRight()
    pygame.draw.rect(hndl, blue, (plyPos[0], plyPos[1], 5, 5))

lastUpdate = 0
def tileTimer(): # checks every couple ms if the ply is close
		 # to the end of any tile, and updates screen
		 # with new tile. too wasteful doing this every 30 ticks
    global lastUpdate
    if pygame.time.get_ticks()-lastUpdate>100:
	updateActiveTile()
	lastUpdate = pygame.time.get_ticks()
    
    #DEBUGGING stuff below
    #print str(plyPos[0]) + "," + str(plyPos[1])
    #print str(plyPos[0]+offsetX) +","+ str(plyPos[1]+offsetY)
        #print str(plyPos[0]-offsetX) +","+ str(plyPos[1]-offsetY)
        #act = tileSpaces[activeTile] if activeTile in tileSpaces else (-1,-1,-1,-1)
	#print str(activeTile2) + ","+str(activeTile3)+","+str(activeTile4)
    #print str(plyPos[0]+offsetX) +","+ str(plyPos[1]-offsetY)

generateTile()

for i in range(pygame.joystick.get_count()):
    pygame.joystick.Joystick(i).init()

kbOverride = False
js = 0
if pygame.joystick.get_count()>0:
    js = pygame.joystick.Joystick(0)

def joyControl():
    global up, down, left, right, kbOverride
    if kbOverride: return
    if js==0: return
    #for i in range(pygame.joystick.get_count()):
	#js = pygame.joystick.Joystick(i)
	#js.init()
	#print js.get_numaxes()
    axisH, axisV = js.get_axis(0), js.get_axis(1)
    if axisH<-0.7 and axisH>-1.1:
        left = True
    else: left = False
    if axisH>0.7 and axisH<1.1:
        right = True
    else: right = False
    if axisV<-0.7 and axisV>-1.1:
        up = True
    else: up = False
    if axisV>0.7 and axisV<1.1:
        down = True
    else: down = False
#	for x in range(js.get_numbuttons()):
#	    print (x,js.get_button(x))
	#print js.get_numbuttons()

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
	else: # ply is alive and already clicked start
	    drawWalls()
	    drawHUD()
	    drawPly()
	    drawMinimap()
	    tileTimer()
	    joyControl()
	    if not spawned:
		print "Finding spawn"
		plyPos = randomSpawn()
    else: # ply is dead
	hndl.fill(black)

    # EVENT LOOP
    for event in pygame.event.get():
	if starting and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
	    # the user left clicked somewhere on the start screen
	    pos = pygame.mouse.get_pos()
	    if startButton.collidepoint(pos):
		starting = False; # a user clicked on start button
	elif starting and event.type == pygame.JOYBUTTONDOWN:
	    if js.get_button(1)==1 or js.get_button(2)==1:
		starting = False
	elif not starting: # game in progress
	    if event.type==pygame.JOYBUTTONDOWN:
		print "Joycon btn down"		
	    if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
		pos = pygame.mouse.get_pos()
		
	        # mouse click in gameplay
	    
	    elif event.type==pygame.KEYDOWN: # key down
		kbOverride = True
		if event.key==pygame.K_UP or event.key==pygame.K_w: up=True
		if event.key==pygame.K_DOWN or event.key==pygame.K_s: down=True
		if event.key==pygame.K_LEFT or event.key==pygame.K_a: left=True
		if event.key==pygame.K_RIGHT or event.key==pygame.K_d: right=True
	    elif event.type==pygame.KEYUP:
		#if not up and not down and not left and not right: kvOverride = False
		if event.key==pygame.K_UP or event.key==pygame.K_w: up=False
		if event.key==pygame.K_DOWN or event.key==pygame.K_s: down=False
		if event.key==pygame.K_LEFT or event.key==K_a: left=False
		if event.key==pygame.K_RIGHT or event.key==K_d: right=False
    		if not left and not right and not up and not down: kbOverride = False
    pygame.display.update()
    clock.tick(30)
