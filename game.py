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

while True:
    
    if(alive):
	hndl.fill(white)
	if(starting):
	    global startButton
	    hndl.blit(mainMenuTxt, (220,50))
	    

	    startButton = pygame.draw.rect(hndl, green, startBounds)
	    hndl.blit(mainMenuStart, (275, 90))
    else:
	hndl.fill(black)
    for event in pygame.event.get():
	if event.type == pygame.MOUSEBUTTONDOWN and event.button==1:
	    
	    pos = pygame.mouse.get_pos()
	    if startButton.collidepoint(pos):
		print "Game start"

    pygame.display.update()
    clock.tick(30)
