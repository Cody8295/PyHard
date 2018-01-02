# Cody DallaValle
# PyHard

import sys, pygame, random, struct
from pygame.locals import *

walls = []

def floatToBin(fl):
    return struct.unpack("Q", struct.pack("d", fl))[0]

def generateMap():
    print "generating"
    rSeed = random.random()
    mapTxt = ""
    initVector = 255*rSeed
    
    for chr in str(initVector).replace(".", ""):
	for x in xrange(0, 32):
	    mapTxt = mapTxt + str(floatToBin(int(chr)*x*x*x*x-initVector*x*x))

    mapHeight, mapWidth = len(mapTxt)/70, len(mapTxt)/70

    for y in xrange(1, len(mapTxt)):
	if mapTxt[y-1]>5:
	     walls.append((y*50,(mapWidth%y)*50 ,50, 50))

    print mapTxt

def randomSpawn():
    randX, randY = random.randint(50,250), random.randint(50, 250)
    for wall in walls:
	if pygame.Rect(wall).collidepoint(randX, randY):
	    randomSpawn()
    return (randX, randY) 
	

W, H = 500, 300
offsetX, offsetY = 0, 0
pygame.init()
clock = pygame.time.Clock()
hndl = pygame.display.set_mode((W, H))
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
plyPos = (50, 50)
plyHp = 1000
plySpeed = 10

hudHealthTxt = font1.render("Health: " + str(plyHp/10), 1, black)

up, down, left, right = False, False, False, False


def offset():
    global plyPos, offsetX, offsetY
    if plyPos[0]<25:
	plyPos=(25,plyPos[1])
	offsetX=offsetX+plySpeed
    if plyPos[0]>W-25:
	plyPos=(W-25,plyPos[1])
	offsetX=offsetX-plySpeed
    if plyPos[1]<25:
	plyPos=(plyPos[0],25)
	offsetY=offsetY+plySpeed
    if plyPos[1]>H-25:
	plyPos=(plyPos[0], H-25)
	offsetY=offsetY-plySpeed
    for wall in walls:
	if wall[0]<plyPos[0]+W-offsetX and wall[0]>plyPos[0]-W-offsetX and wall[1]<plyPos[1]+H-offsetY and wall[1]>plyPos[1]-H-offsetY:
            
	    if pygame.Rect(wall).collidepoint(plyPos[0]-offsetX,plyPos[1]-offsetY):
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
    for wall in walls:
	if wall[0]<plyPos[0]+W-offsetX and wall[0]>plyPos[0]-W-offsetX and wall[1]<plyPos[1]+H-offsetY and wall[1]>plyPos[1]-H-offsetY:
	    wallOffset = (wall[0]+offsetX, wall[1]+offsetY, wall[2], wall[3])
	    pygame.draw.rect(hndl, green, wallOffset)

def drawPly():
    if up: plyUp()
    if down: plyDown()
    if left: plyLeft()
    if right: plyRight()
    pygame.draw.rect(hndl, blue, (plyPos[0], plyPos[1], 5, 5))

generateMap()

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
