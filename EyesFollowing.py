import pygame
import cv2
import subprocess

pygame.init()
WHITE = (255,255,255)
BLACK = (0,0,0)
COLORKEY = (255,170,200)
NORMALSTATE = 0
BLINKSTATE = 1
WINKSTATE  = 2
HAPPYSTATE = 3
QUESTIONSTATE = 4


#normalL = pygame.image.load("normalgreyL")
#normalR = pygame.image.load("normalgreyR")
normalL = pygame.image.load("images/normalAlt3Lkey.bmp")
normalL.set_alpha(None)
normalL.set_colorkey(COLORKEY)
normalR = pygame.image.load("images/normalAlt3Rkey.bmp")
normalR.set_alpha(None)
normalR.set_colorkey(COLORKEY)

closedL = pygame.image.load("images/closedgrey2L.bmp")
closedR = pygame.image.load("images/closedgrey2R.bmp")

closingL = pygame.image.load("images/closinggrey2Lkey.bmp")
closingL.set_alpha(None)
closingL.set_colorkey(COLORKEY)
closingR = pygame.image.load("images/closinggrey2Rkey.bmp")
closingR.set_alpha(None)
closingR.set_colorkey(COLORKEY)

questionL = pygame.image.load("images/questionLkey.bmp")
questionL.set_alpha(None)
questionL.set_colorkey(COLORKEY)
questionR = pygame.image.load("images/questionRkey.bmp")
questionR.set_alpha(None)
questionR.set_colorkey(COLORKEY)

winkL = pygame.image.load("images/wink2L.bmp")
winkR = pygame.image.load("images/wink2R.bmp")

happyL = pygame.image.load("images/happy2L.bmp")
happyR = pygame.image.load("images/happy2R.bmp")

happy2L = pygame.image.load("images/happyLkey.bmp")
happy2L.set_alpha(None)
happy2L.set_colorkey(COLORKEY)
happy2R = pygame.image.load("images/happyRkey.bmp")
happy2R.set_alpha(None)
happy2R.set_colorkey(COLORKEY)

pupil = pygame.image.load("images/pupil.bmp")
pupil.set_alpha(None)
pupil.set_colorkey(COLORKEY)

faceCasc = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
videoCap = cv2.VideoCapture(0)
videoCap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
videoCap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
center = (400, 240)
#cv2.namedWindow('Video')
#cv2.moveWindow('Video', 1250, 0)

def wait(ms):
    pygame.time.wait(ms)

def normal():
    screen.blit(normalL, (0,0))
    screen.blit(normalR, (400,0))
    pygame.display.flip()
    
def question():
    screen.blit(questionL, (0,0))
    screen.blit(questionR, (400,0))
    pygame.display.flip()
    
def happy():
    screen.fill(WHITE)
    screen.blit(winkL, (0,0))
    screen.blit(winkR, (400,0))
    pygame.display.flip()
    
def wink():
    screen.blit(winkL, (0,0))
    screen.blit(normalR, (400,0))
    pygame.display.flip()
    
def updateEyes():
    pygame.draw.rect(screen, WHITE, eyeL)
    pygame.draw.rect(screen, WHITE, eyeR)
    #pygame.display.update((eyeL, eyeR)
    
def listenforhej():
    detector = snowboydecoder.HotwordDetector("hej.pmdl", sensitivity=0.5)
    detector.start(detected_callback=snowboydecoder.play_audio_file,
               interrupt_check=interrupt_callback,
               sleep_time=0.03)

    detector.terminate()

#pygame.mouse.set_visible(False)
clock = pygame.time.Clock()
size = (800,480)
screen = pygame.display.set_mode(size) # pygame.NOFRAME
screen.fill(WHITE)
#pygame.display.toggle_fullscreen()
offset = 800-170-100
eyeL = pygame.Rect(100, 210, 170, 170)
eyeR = pygame.Rect(offset, 210, 170, 170)
centerL = (185-30, 295-30) 
centerR =(offset+85-30,295-30)

BLINKEVENT = pygame.USEREVENT + 1
BLINKEVENT2 = pygame.USEREVENT + 2
NORMALEVENT = pygame.USEREVENT + 3
WINKEVENT = pygame.USEREVENT + 4
HAPPYEVENT = pygame.USEREVENT + 5
pygame.time.set_timer(BLINKEVENT, 8000)

normal()
#pygame.display.flip()
state = NORMALSTATE
done = False
boole = False
sp = False
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                print("ESC")
                done = True
            elif event.key == pygame.K_h:
                print("h")
                happy()
                wait(500)
                screen.fill(WHITE)
            elif event.key == pygame.K_w:
                print("w")
                pygame.time.set_timer(NORMALEVENT, 400, True)
                state = WINKSTATE
                screen.fill(WHITE)
                snow = subprocess.Popen(['python3','snowboyTest.py','resources/models/hej.pmdl'],cwd="/home/pi/snowboy/snowboy/examples/Python3/",stdout=subprocess.PIPE)         # added snowboy
                print("SUBPROCESS STARTED")
                sp = True
            elif event.key == pygame.K_k:
                print("k")
                pygame.time.set_timer(HAPPYEVENT, 200, True)
                state = HAPPYSTATE
                screen.fill(WHITE)
            elif event.key == pygame.K_q:
                print("q")
                pygame.time.set_timer(NORMALEVENT, 1500, True)
                state = QUESTIONSTATE
                screen.fill(WHITE)
                            
        if event.type == BLINKEVENT:
            state = BLINKSTATE
            pygame.time.set_timer(BLINKEVENT2, 200, True)
        elif event.type == BLINKEVENT2:
            screen.blit(closedL, (0,0))
            screen.blit(closedR, (400,0))
            pygame.display.flip()
            wait(700)
            pygame.time.set_timer(NORMALEVENT, 100, True)
            screen.fill(WHITE)
        elif event.type == NORMALEVENT:
            screen.fill(WHITE)
            state = NORMALSTATE
            boole = True
        elif event.type == HAPPYEVENT:
            screen.blit(happyL, (0,0))
            screen.blit(happyR, (400,0))
            pygame.display.flip()
            wait(1000)
            state = NORMALSTATE
            screen.fill(WHITE)
    
    if sp is True:
        poll = snow.poll()
        if poll is not None:
            outs, errs = snow.communicate()
            print("Outs: ", outs)
            print("Errors: ", errs)
            sp = False
        else:
            print("running")
        
    
    # Tracking
    ret, frame = videoCap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = faceCasc.detectMultiScale(
        gray,
        scaleFactor = 1.1,
        minNeighbors = 5,
        minSize = (30, 30),
        flags = cv2.CASCADE_SCALE_IMAGE)
    
    recSize = 0
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        if w > recSize:
            center = (int(x+w*0.5), int(y+h*0.5))

    # Eyes
    updateEyes()
    pupilpos = ((size[0]/2 - center[0])/7, (size[1]/2 - center[1])/7)
    pupilposL = (centerL[0]+pupilpos[0], centerL[1]-pupilpos[1])
    pupilposR = (centerR[0]+pupilpos[0], centerR[1]-pupilpos[1])
    screen.blit(pupil, pupilposL)
    screen.blit(pupil, pupilposR)
    
    if state == NORMALSTATE:
        normal()
        #pygame.display.update((eyeL,eyeR))
    elif state == BLINKSTATE:
        screen.blit(closingL, (0,0))
        screen.blit(closingR, (400,0))
        pygame.display.flip()
    elif state == WINKSTATE:
        wink()
    elif state == HAPPYSTATE:
        screen.blit(happy2L, (0,0))
        screen.blit(happy2R, (400,0))
        pygame.display.flip()
    elif state == QUESTIONSTATE:
        question()
                    
    #cv2.imshow('Video', frame)
    #if cv2.waitKey(1) & 0xFF == ord('q'):
    #    break
    #clock.tick(60)
    
pygame.display.quit()
pygame.quit()
videoCap.release()
cv2.destroyAllWindows()
