import pygame
import random
pygame.init()

size = (800,480)
WHITE = (255,255,255)
BACKGROUND = WHITE

#Eye movement variables
pupilL = 0
pupilR = 0
pupilV = 0

offset = 800-170-100
centerL = (185-30+10, 295-30) 
centerR =(offset+85-30-10,295-30)

moveLeft = False
moveRight = False
moveUp = False
moveDown = False

########## Load images ##########
normalL = pygame.image.load("images/png/normalL.png")
normalR = pygame.transform.flip(normalL, True, False)
normalwhiteL = pygame.image.load("images/png/normalLwhite.png")
normalwhiteR = pygame.transform.flip(normalwhiteL, True, False)

closedL = pygame.image.load("images/png/closedL.png")
closedR = pygame.transform.flip(closedL, True, False)

pupil = pygame.image.load("images/png/pupil.png")

def blitImages(left, right):
    screen.blit(left, (0,0))
    screen.blit(right, (400,0))
    
# Draw the pupils on the eyes
def drawPupils():
    pupilposL = (centerL[0]+pupilL, centerL[1]-pupilV)
    pupilposR = (centerR[0]+pupilR, centerR[1]-pupilV)
    screen.blit(pupil, pupilposL)
    screen.blit(pupil, pupilposR)
        
def movePupils():
    global pupilL, pupilR, pupilV
    if moveLeft:
        if pupilL > -80:
            pupilL -= 5
            pupilR -= 5
    if moveRight:
        if pupilL < 60:
            pupilL += 5
            pupilR += 5
    if moveUp:
        if pupilV < 40:
            pupilV += 5
    if moveDown:
        if pupilV > -40:
            pupilV -= 5
    
########## Events ##########
BLINKEVENT = pygame.USEREVENT + 1
NORMALEVENT = pygame.USEREVENT + 2

########## States ##########
NORMALSTATE = 0
BLINKSTATE = 1

state = NORMALSTATE

if __name__ == '__main__':
    pygame.time.set_timer(BLINKEVENT, 10000, True)
    pygame.mouse.set_visible(False) #Hide mouse from GUI
    screen = pygame.display.set_mode(size)#, pygame.NOFRAME)
    #pygame.display.toggle_fullscreen()
    
    done = False
    while not done:
        # Event loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            # Keyboard events
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    print("ESC")
                    done = True
                elif event.key == pygame.K_LEFT:
                    moveLeft = True
                elif event.key == pygame.K_RIGHT:
                    moveRight = True
                elif event.key == pygame.K_UP:
                    moveUp = True
                elif event.key == pygame.K_DOWN:
                    moveDown = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    moveLeft = False
                elif event.key == pygame.K_RIGHT:
                    moveRight = False
                elif event.key == pygame.K_UP:
                    moveUp = False
                elif event.key == pygame.K_DOWN:
                    moveDown = False
            # User events
            elif event.type == BLINKEVENT and state == NORMALSTATE:
                pygame.time.set_timer(NORMALEVENT, 300, True)
                state = BLINKSTATE
            elif event.type == NORMALEVENT:
                blinktime = random.randrange(5000, 20000, 1000)
                pygame.time.set_timer(BLINKEVENT, blinktime, True)
                state = NORMALSTATE
                    
        movePupils()
        
        ########## State Machine ##########
        screen.fill(BACKGROUND)
        
        if state == NORMALSTATE:
            blitImages(normalwhiteL, normalwhiteR)
            drawPupils()
            blitImages(normalL, normalR)
        elif state == BLINKSTATE:
            blitImages(closedL, closedR)
            
        pygame.display.flip()
        
    pygame.display.quit()
    pygame.quit()
    exit(0)
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
    