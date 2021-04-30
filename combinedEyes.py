import snowboydecoder
import pygame
import cv2
import threading
from moviepy.editor import VideoFileClip

pygame.init()
WHITE = (255,255,255)
BLACK = (0,0,0)
COLORKEY = (255,170,200)
FPS = 30
NORMALSTATE = 0
BLINKSTATE = 1
WINKSTATE  = 2
HAPPYSTATE = 3
QUESTIONSTATE = 4

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
#questionR = pygame.image.load("images/questionRkey.bmp")
questionR = pygame.image.load("images/question2Rkey.bmp")
questionR.set_alpha(None)
questionR.set_colorkey(COLORKEY)

winkL = pygame.image.load("images/wink2L.bmp")
winkR = pygame.image.load("images/wink2R.bmp")

#happyL = pygame.image.load("images/happy2L.bmp")
#happyR = pygame.image.load("images/happy2R.bmp")

happyL = pygame.image.load("images/happy3L.bmp")
happyR = pygame.image.load("images/happy3R.bmp")

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
videoCap = cv2.VideoCapture(-1)
videoCap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
videoCap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
center = (400, 240)
#cv2.namedWindow('Video')
#cv2.moveWindow('Video', 1250, 0)
buttonL = pygame.Rect(0,0,100,70)
buttonR = pygame.Rect(800-100,0,100,70)

def show_buttons():
    pygame.draw.rect(screen, [255, 0, 0], buttonL)
    pygame.draw.rect(screen, [0, 255, 0], buttonR)

def wait(ms):
    pygame.time.wait(ms)

def normal():
    screen.blit(normalL, (0,0))
    screen.blit(normalR, (400,0))
    #pygame.display.flip()
    
def question():
    screen.blit(questionL, (0,0))
    screen.blit(questionR, (400,0))
    #pygame.display.flip()
    
def happy():
    screen.fill(WHITE)
    screen.blit(winkL, (0,0))
    screen.blit(winkR, (400,0))
    pygame.display.flip()
 
def wink():
    screen.blit(winkL, (0,0))
    screen.blit(normalR, (400,0))
    #pygame.display.flip()
    
def updateEyes():
    pygame.draw.rect(screen, WHITE, eyeL)
    pygame.draw.rect(screen, WHITE, eyeR)
    #pygame.display.update((eyeL, eyeR)
    
def signal():
    global interrupted
    interrupted = True
    
def interrupt_callback():
    global interrupted
    return interrupted

def detected_callback():
    signal()
    snowboydecoder.play_audio_file(snowboydecoder.DETECT_DING)
    pygame.event.post(ev)
    
def detected_callback2():
    print("callback 2")
    signal()
    pygame.event.post(ev2)
    
def listen_for_cmd(cmd):
    global interrupted
    interrupted = False
    #pygame.time.set_timer(LISTENEVENT, 10000, True)
    detector = snowboydecoder.HotwordDetector(f"resources/models/{cmd}.pmdl", sensitivity=0.5)
    detector.start(detected_callback=detected_callback,
               interrupt_check=interrupt_callback,
               sleep_time=0.03)
    detector.terminate()
    print("Terminated")
    
def listen_for_two_cmds(cmd1, cmd2):
    global interrupted
    interrupted = False
    detector = snowboydecoder.HotwordDetector([f"resources/models/{cmd1}.pmdl",f"resources/models/{cmd2}.pmdl"], sensitivity=[0.5,0.5])
    detector.start(detected_callback=[detected_callback,detected_callback2],
               interrupt_check=interrupt_callback,
               sleep_time=0.03)
    detector.terminate()
    print("Terminated")

interrupted = False

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
LISTENEVENT = pygame.USEREVENT + 6
HAPPYSTARTEVENT = pygame.USEREVENT + 7
QUESTIONEVENT = pygame.USEREVENT + 8
pygame.time.set_timer(BLINKEVENT, 15000)
ev = pygame.event.Event(HAPPYSTARTEVENT)
ev2 = pygame.event.Event(QUESTIONEVENT)

#normal()
#pygame.display.flip()
state = NORMALSTATE
done = False

clip = VideoFileClip('coronavirus.mp4', target_resolution=(480,800))
clip.preview()
screen.fill(WHITE)

#listenhappy = threading.Thread(target=listen_for_cmd, args=("happy",))
listenhappy = threading.Thread(target=listen_for_two_cmds, args=("happy","tak"))
listenhappy.start()

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
                #interrupted = True
                happy()
                wait(500)
                screen.fill(WHITE)
            elif event.key == pygame.K_w:
                print("w")
                pygame.time.set_timer(NORMALEVENT, 400, True)
                state = WINKSTATE
                screen.fill(WHITE)
                #listen = threading.Thread(target=listen_for_cmd, args=("hej",))
                #listen.start()
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
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if buttonL.collidepoint(event.pos):
                print("Left button clicked")
            if buttonR.collidepoint(event.pos):
                print("Right button clicked")
                            
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
            #boole = True
        elif event.type == HAPPYSTARTEVENT:
            pygame.time.set_timer(HAPPYEVENT, 70, True)
            state = HAPPYSTATE
            screen.fill(WHITE)
        elif event.type == HAPPYEVENT:
            screen.blit(happyL, (0,0))
            screen.blit(happyR, (400,0))
            pygame.display.flip()
            wait(1500)
            state = NORMALSTATE
            screen.fill(WHITE)
            listenhappy = threading.Thread(target=listen_for_cmd, args=("happy",))
            listenhappy.start()
        elif event.type == LISTENEVENT:
            signal()
            print("Timeout")
        elif event.type == QUESTIONEVENT:
            pygame.time.set_timer(NORMALEVENT, 1500, True)
            state = QUESTIONSTATE
            screen.fill(WHITE)

    # Tracking
    ret, frame = videoCap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.rotate(gray, cv2.ROTATE_180) 
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
            recSize = w

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
        #pygame.display.flip()
    elif state == WINKSTATE:
        wink()
    elif state == HAPPYSTATE:
        screen.blit(happy2L, (0,0))
        screen.blit(happy2R, (400,0))
        #pygame.display.flip()
    elif state == QUESTIONSTATE:
        question()
    
    show_buttons()
    pygame.display.flip()
    
    cv2.imshow('Video', gray)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    clock.tick(FPS)
    
interrupted = True
pygame.display.quit()
pygame.quit()
videoCap.release()
cv2.destroyAllWindows()

