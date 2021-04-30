import pygame
import pygame.freetype
import cv2
import threading
from multiprocessing import Process, Pipe
from moviepy.editor import VideoFileClip
import math

import snowboydecoder
import speech_recognition as sr
from gtts import gTTS
import re
pygame.init()

########## GPIO ##########
import RPi.GPIO as GPIO
import os
import time
from threading import Timer
import sys

# Pins
PIN_MOTORDETECT = 17
PIN_IRSENOR = 20
PIN_LED = 21

# SPI Pins
PIN_CLK = 11
PIN_MOSI = 10
PIN_MISO = 9
PIN_CS = 8

#global variables
numberOfActivations = 0
irSensorThreshhold = 0
dispenserEmpty = False
turnOffDispenser = False
dispenserRefilled = False

def init_GPIO():
    # Init GPIO pins
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PIN_LED, GPIO.OUT)
    GPIO.output(PIN_LED, False)
    GPIO.setup(PIN_MOTORDETECT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    
    # Spi pins Init
    GPIO.setup(PIN_CLK, GPIO.OUT)
    GPIO.setup(PIN_MISO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(PIN_MOSI, GPIO.OUT)
    GPIO.setup(PIN_CS, GPIO.OUT)

# Read SPI data from ADC
     
def recvBits(numBits, clkPin, misoPin):
    #Receives arbitrary number of bits
    retVal = 0
    
    for bit in range(numBits):
        # Pulse clock pin 
        GPIO.output(clkPin, GPIO.HIGH)
        GPIO.output(clkPin, GPIO.LOW)
        
        # Read 1 data bit in
        if GPIO.input(misoPin):
            retVal |= 0x1
        
        # Advance input to next bit
        retVal <<= 1
    
    # Divide by two to drop the NULL bit
    return (retVal/2)


def readAdc(channel, clkPin, misoPin, mosiPin, csPin):
    if (channel < 0) or (channel > 7):
        print("Invalid ADC Channel number, must be between [0,7]")
        return -1
        
    # Datasheet says chip select must be pulled high between conversions
    GPIO.output(csPin, GPIO.HIGH)
    
    # Start the read with both clock and chip select low
    GPIO.output(csPin, GPIO.LOW)
    GPIO.output(clkPin, GPIO.HIGH)
    
    adc = recvBits(10, clkPin, misoPin)
    
    # Set chip select high to end the read
    GPIO.output(csPin, GPIO.HIGH)
  
    return round(adc)



def timeout():
    timeRunOut = True
    

myfont = pygame.freetype.SysFont(pygame.freetype.get_default_font(), 20)

#init_GPIO()

def GPIOfunction():
    global numberOfActivations, irSensorThreshhold, dispenserEmpty, turnOffDispenser, dispenserRefilled
    ADCvalue = readAdc(0, PIN_CLK, PIN_MISO, PIN_MOSI, PIN_CS)
    #if(ADCvalue > 0):
    #print("ADC Result: ", str(ADCvalue))
    #time.sleep(0.2)
    
    if(dispenserEmpty == False):
        turnOffDispenser = False

    # Motor activated and dispenser empty
    if(ADCvalue == 0 and GPIO.input(PIN_MOTORDETECT)):
        dispenserEmptyTemp += 1
        #in case of som random noise
        if(dispenserEmptyTemp == 2):
            dispenserEmpty = True
            #dispenserEmpty()
            turnOffDispenser = True
    # Motor activated and dispenser not empty        
    elif(ADCvalue != 0 and GPIO.input(PIN_MOTORDETECT)):
        print("Motor Activated!")
        #count number of times used
        numberOfActivations += 1
        print("Activations: ", numberOfActivations)
        #textsurface = myfont.render(numberOfActivations, False, (0, 0, 0))
        
        timer = Timer(1, timeout)
        timer.start()
        timer.join()
        
    
    if(dispenserEmpty):
        #dev = pb.get_device('OnePlus 7 Pro')
        #push = dev.push_note("Alert!", "Dispenser is empty!")

        # If dispenser refilled - button pushed in gui - rest all conditions and turn on system/motor again
        if(dispenserRefilled):
            dispenserEmptyTemp = 0
            dispenserEmpty = False
            dispenserRefilled = False
            turnOffDispenser = False
        
    
    # Test MOSFET
    if(turnOffDispenser == False):
        GPIO.output(PIN_LED, True)
    else:
        GPIO.output(PIN_LED, False)
        
    text_surface, rect = myfont.render(f"Activations: {numberOfActivations}", (0,0,0))
    screen.blit(text_surface, (0,0))

########## ##########

BACKGROUND = (150, 150, 170)
WHITE = (255,255,255)
COLORKEY = (255,170,200)
FPS = 60
LANGUAGE = "da-DK" # en-US
isOffline = True

########## Load images ##########
onlineicon = pygame.image.load("images/bg/online.png")
offlineicon = pygame.image.load("images/bg/offline.png")

closingwhiteL = pygame.image.load("images/bg/bgclosingwhiteL.bmp")
closingwhiteL.set_alpha(None)
closingwhiteL.set_colorkey(COLORKEY)
closingwhiteR = pygame.transform.flip(closingwhiteL, True, False)
normalwhiteL = pygame.image.load("images/bg/bgnormalwhiteL.bmp")
normalwhiteL.set_alpha(None)
normalwhiteL.set_colorkey(COLORKEY)
normalwhiteR = pygame.transform.flip(normalwhiteL, True, False)
questionwhiteL = pygame.image.load("images/bg/bgquestionwhiteL.bmp")
questionwhiteL.set_alpha(None)
questionwhiteL.set_colorkey(COLORKEY)
questionwhite2R = pygame.image.load("images/bg/bgquestionwhite2R.bmp")
questionwhite2R.set_alpha(None)
questionwhite2R.set_colorkey(COLORKEY)
questionwhite2L = pygame.transform.flip(questionwhite2R, True, False)

normalL = pygame.image.load("images/bg/bgnormalAlt3L.bmp")
normalL.set_alpha(None)
normalL.set_colorkey(COLORKEY)
normalR = pygame.transform.flip(normalL, True, False)
closedL = pygame.image.load("images/bg/bgclosedgrey2L.bmp")
closedL.set_alpha(None)
closedL.set_colorkey(COLORKEY)
closedR = pygame.transform.flip(closedL, True, False)
closingL = pygame.image.load("images/bg/bgclosinggrey2Lkey.bmp")
closingL.set_alpha(None)
closingL.set_colorkey(COLORKEY)
closingR = pygame.transform.flip(closingL, True, False)

questionL = pygame.image.load("images/bg/bgquestionLkey.bmp")
questionL.set_alpha(None)
questionL.set_colorkey(COLORKEY)
#questionR = pygame.image.load("images/questionRkey.bmp")
questionR = pygame.image.load("images/bg/bgquestion2Rkey.bmp")
questionR.set_alpha(None)
questionR.set_colorkey(COLORKEY)
questionL2 = pygame.transform.flip(questionR, True, False)

winkL = pygame.image.load("images/wink2L.bmp")
winkR = pygame.image.load("images/wink2R.bmp")
#happyL = pygame.image.load("images/happy2L.bmp")
#happyR = pygame.image.load("images/happy2R.bmp")
happyL = pygame.image.load("images/bg/bghappy3L.bmp")
happyL.set_alpha(None)
happyL.set_colorkey(COLORKEY)
happyR = pygame.transform.flip(happyL, True, False)
happy2L = pygame.image.load("images/happyLkey.bmp")
happy2L.set_alpha(None)
happy2L.set_colorkey(COLORKEY)
happy2R = pygame.image.load("images/happyRkey.bmp")
happy2R.set_alpha(None)
happy2R.set_colorkey(COLORKEY)

pupil = pygame.image.load("images/pupil.bmp")
pupil.set_alpha(None)
pupil.set_colorkey(COLORKEY)

yesbutton = pygame.image.load("images/buttonup80.bmp")
yesbutton.set_alpha(None)
yesbutton.set_colorkey(COLORKEY)
nobutton = pygame.image.load("images/buttondown80.bmp")
nobutton.set_alpha(None)
nobutton.set_colorkey(COLORKEY)
homebutton = pygame.image.load("images/homesmall.bmp")
homebutton.set_alpha(None)
homebutton.set_colorkey(COLORKEY)
danishbutton = pygame.image.load("images/danish.bmp")
danishbutton.set_alpha(None)
danishbutton.set_colorkey(COLORKEY)
englishbutton = pygame.image.load("images/english.bmp")
englishbutton.set_alpha(None)
englishbutton.set_colorkey(COLORKEY)
englishbuttonsmall = pygame.transform.scale(englishbutton, (50,50))
englishbutton = pygame.transform.scale(englishbutton, (200,200))
danishbuttonsmall = pygame.transform.scale(danishbutton, (50,50))
danishbutton = pygame.transform.scale(danishbutton, (200,200))

colorselector = pygame.image.load("images/bg/ColorPicker.bmp")
colorselector = pygame.transform.flip(colorselector, False, True)
coloricon = pygame.transform.scale(colorselector, (50, 35))
#colorselector = pygame.transform.scale(colorselector, (600, 300))
colorselector = pygame.transform.scale(colorselector, (700, 350))

menuicon = pygame.image.load("images/bg/menuicon.bmp")
menuicon.set_alpha(None)
menuicon.set_colorkey(COLORKEY)
########## Load sounds ##########
'''
Hi_sanitizer = pygame.mixer.music.load("sounds/Hi_sanitizer.mp3")
Sorry_sanitizer = pygame.mixer.music.load("sounds/Sorry_sanitizer.mp3")
Great_dispenser = pygame.mixer.music.load("sounds/Great_dispenser.mp3")
Nice_day = pygame.mixer.music.load("sounds/Nice_day.mp3")
Sorry_bye = pygame.mixer.music.load("sounds/Sorry_bye.mp3")
Sorry_video = pygame.mixer.music.load("sounds/Sorry_video.mp3")
Video = pygame.mixer.music.load("sounds/Video.mp3")
'''
Hi_sanitizer = "sounds/Hi_sanitizer.mp3"
Sorry_sanitizer = "sounds/Sorry_sanitizer.mp3"
Great_dispenser = "sounds/Great_dispenser.mp3"
Nice_day = "sounds/Nice_day.mp3"
Sorry_bye = "sounds/Sorry_bye.mp3"
Sorry_video = "sounds/Sorry_video.mp3"
Video = "sounds/Video.mp3"

Hej_sprit = "sounds/Hej_sprit.mp3"
Undskyld_sprit = "sounds/Undskyld_sprit.mp3"
Under_automaten = "sounds/Under_automaten.mp3"
God_dag = "sounds/God_dag.mp3"
Undskyld_farvel = "sounds/Undskyld_farvel.mp3"
Undskyld_video = "sounds/Undskyld_video.mp3"
Video_da = "sounds/Video_da.mp3"

sounds = [Hi_sanitizer, Video, Sorry_sanitizer, Sorry_video, Great_dispenser, Nice_day, Sorry_bye,
          Hej_sprit, Video_da, Undskyld_sprit, Undskyld_video, Under_automaten, God_dag, Undskyld_farvel]

########## Functions ##########
def updatePupils():
    pygame.draw.rect(screen, WHITE, eyeL)
    pygame.draw.rect(screen, WHITE, eyeR)
    
def showButtons():
    screen.blit(yesbutton, (720,0))
    screen.blit(nobutton, (0,0))
    
def wait(ms):
    pygame.time.wait(ms)
    
def blitImages(left, right):
    screen.blit(left, (0,0))
    screen.blit(right, (400,0))
    
def signal():
    global interrupted
    interrupted = True
    
def interrupt_callback():
    global interrupted, timeout
    timeout += 0.03
    if threadevent.is_set():
        return True
    if timeout > 5:
        print("Timeout happened")
        return True
    return interrupted
    
def listen_for_two_cmds(cmd1, cmd2):
    global interrupted, timeout
    timeout = 0.
    interrupted = False
    detector = snowboydecoder.HotwordDetector(
        [f"resources/models/{cmd1}.pmdl",f"resources/models/{cmd2}.pmdl"], sensitivity=[0.5,0.5])
    detector.start(detected_callback=[detected_callback1, detected_callback2],
               interrupt_check=interrupt_callback,
               sleep_time=0.03)
    detector.terminate()
    print("Terminated")

def detected_callback1():
    print("callback 1")
    signal()
    global yes_detected
    yes_detected = True
    
def detected_callback2():
    print("callback 2")
    signal()
    global no_detected
    no_detected = True
    
def google_in():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.5)
        print("Say something!")
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=4)
        except sr.WaitTimeoutError:
            return "Timeout"
        else:
            try:
                out = r.recognize_google(audio, language=LANGUAGE)
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))
            else:
                return out
        return "Error"

def speech_in(cmd1, cmd2):
    global yes_detected, no_detected
    yes_detected = False
    no_detected = False
    if LANGUAGE == "da-DK":
        cmd1 = "ja"
        cmd2 = "nej"
    if isOffline:
        listen_for_two_cmds(cmd1, cmd2)
    else:    
        gin = google_in()
        if findWholeWord(cmd1)(gin): yes_detected = True
        elif findWholeWord(cmd2)(gin): no_detected = True

#pygame.mixer.init(22050, -8 * 2, 2, 1024)
def speech_out(index):
    if LANGUAGE == "da-DK":
       index += 7
    pygame.mixer.init()
    pygame.mixer.music.load(sounds[index])
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        if threadevent.is_set():
            pygame.mixer.quit()
            return
        pygame.time.Clock().tick(10)
    
        
def flow_machine():
    global show_buttons
    flowState = 0
    speech_out(0)
    i = 0
    while not threadevent.is_set():
        speech_in("yes", "no")
        if yes_detected:
            if flowState == 0:
                pygame.event.post(happyevent)
                speech_out(1)
                flowState += 1
                i = 0
            else:                                 
                global state
                state = VIDEOSTATE
                break
        elif no_detected:
            speech_out(5)
            break
        elif i < 2:
            pygame.event.post(questionevent)
            speech_out(flowState+2)
            show_buttons = True
            i += 1
        else:
            speech_out(6)
            break
    show_buttons = False
    threadevent.clear()
    print("Flow ended")
 
def findWholeWord(w):
    return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search

def playVideo():
    clip = VideoFileClip('handwashing.mp4', target_resolution=(480,800))
    clip.preview()
    
def faceTracking():
    global pupilL, pupilR, pupilV, faceTrackers, currentID
    ret, frame = cap.read()
    frame = cv2.rotate(frame, cv2.ROTATE_180)
    grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(
        grey,
        scaleFactor = 1.1,
        minNeighbors = 5,
        minSize = (30, 30),                           
        flags = cv2.CASCADE_SCALE_IMAGE)
    for (x, y, w, h) in faces:
        center = (int(x+w*0.5), int(y+h*0.5))
        fidMatch = False
        for fid in faceTrackers.keys():
            (tx, ty, tw, th, n, u) =  faceTrackers.get(fid)
            if tx <= center[0] <= tx+tw and ty <= center[1] <= ty+th:
                if n < 50: n += 1
                faceTrackers.update({fid:(x,y,w,h,n,True)})
                fidMatch = True
                break
        if not fidMatch:
            faceTrackers.update({currentID:(x,y,w,h,1,True)})
            currentID += 1
            
    trackID = -1
    fidsToDelete = []
    for fid in faceTrackers.keys():
        (tx, ty, tw, th, n, u) =  faceTrackers.get(fid)
        if not u: n -= 1
        if n < 1: fidsToDelete.append(fid)
        else:
            faceTrackers.update({fid:(tx,ty,tw,th,n,False)})
            if n < 25:
                pass
            else:
                trackID = fid
   
    for fid in fidsToDelete:
        faceTrackers.pop(fid, None)
    
    if trackID != -1:
        # determine who to track
        (x, y, w, h, n, u) = faceTrackers.get(trackID)
        center = (int(x+w*0.5), int(y+h*0.5))
        hAngle = (1 - center[0]/WIDTH) * hFOV
        vAngle = (1 - center[1]/HEIGHT) * vFOV            
        c = -0.26*w+103
        
        # horizontal
        b = 4
        angleA = (90 - hAngle)*math.pi/180
        a = math.sqrt(b*b + c*c - 2*b*c*math.cos(angleA))
        angleC = math.acos((a*a + b*b - c*c)/(2*a*b))
        pupilL = int((angleC - math.pi/2) * EYE_DEPTH * ppcm)
        
        b_hat = 2*b
        c_hat = math.sqrt(a*a + b_hat*b_hat - 2*a*b_hat*math.cos(angleC))
        angleA_hat = math.acos((b_hat*b_hat + c_hat*c_hat - a*a)/(2*b_hat*c_hat))
        pupilR = int((math.pi/2 - angleA_hat) * EYE_DEPTH * ppcm)
        
        # vertical
        b = 6
        angleA = (90 - vAngle)*math.pi/180
        a = math.sqrt(b*b + c*c - 2*b*c*math.cos(angleA))
        angleC = math.acos((a*a + b*b - c*c)/(2*a*b))
        pupilV = int((angleC - math.pi/2) * EYE_DEPTH * ppcm)
    
def drawPupils():
    pupilposL = (centerL[0]+pupilL, centerL[1]-pupilV)
    pupilposR = (centerR[0]+pupilR, centerR[1]-pupilV)
    screen.blit(pupil, pupilposL)
    screen.blit(pupil, pupilposR)

########## Setup face detection ##########
pupilL = 0
pupilR = 0
pupilV = 0

#receiver, sender = Pipe(True)
#rec, sen = Pipe(False)
res1 = (320,240)
res2 = (640,480)
res3 = (1280,720)
res = res1

faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
cap = cv2.VideoCapture(-1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, res[0])
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, res[1])
currentID = 0   
faceTrackers = {}

WIDTH = res[0]/2
HEIGHT = res[1]/2
EYE_DEPTH = 2
hFOV = 62/2
vFOV = 49/2
ppcm = WIDTH*2/15.5
########## Setup misc ##########
interrupted = False
yes_detected = False
no_detected = False
timeout = 0.
show_buttons = False

pygame.mouse.set_visible(False)
clock = pygame.time.Clock()
size = (800,480)
screen = pygame.display.set_mode(size) # pygame.NOFRAME
pygame.display.toggle_fullscreen()

offset = 800-170-100
eyeL = pygame.Rect(100, 210, 170, 170)
eyeR = pygame.Rect(offset, 210, 170, 170)
centerL = (185-30+10, 295-30) 
centerR =(offset+85-30-10,295-30)
buttonL = pygame.Rect(0,0,100,70)
buttonR = pygame.Rect(800-100,0,100,70)

########## Events ##########
BLINKEVENT = pygame.USEREVENT + 1
BLINKEVENT2 = pygame.USEREVENT + 2
NORMALEVENT = pygame.USEREVENT + 3
WINKEVENT = pygame.USEREVENT + 4
HAPPYEVENT = pygame.USEREVENT + 5
LISTENEVENT = pygame.USEREVENT + 6
HAPPYSTARTEVENT = pygame.USEREVENT + 7
QUESTIONEVENT = pygame.USEREVENT + 8
happyevent = pygame.event.Event(HAPPYSTARTEVENT)
questionevent = pygame.event.Event(QUESTIONEVENT)

########## States ##########
NORMALSTATE = 0
BLINKSTATE = 1
WINKSTATE  = 2
HAPPYSTATE = 3
QUESTIONSTATE = 4
VIDEOSTATE = 5
BLINKSTATE2 = 6
HAPPYSTATE2 = 7
MENUSTATE = 8
COLORSTATE = 9
state = NORMALSTATE
pygame.time.set_timer(BLINKEVENT, 8000)

#tracking_thread = Process(target=faceTracking, args=(sender,))
#tracking_thread.start()
threadevent = threading.Event()

done = False
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                print("ESC")
                done = True
            elif event.key == pygame.K_s:
                flow = threading.Thread(target=flow_machine)
                flow.start()
        elif event.type == pygame.FINGERDOWN:
            print("Pos: ", event.x, event.y)
            #print("Color: ", screen.get_at((int(event.x*size[0]), int(size[1]*event.y))))
            if show_buttons and event.x < 0.12 and event.y < 0.12:  # values differ for only touchscreen
                print("Left button pressed")
                interrupted = True
                no_detected = True
            if show_buttons and event.x > 0.88 and event.y < 0.12:
                print("Right button pressed")
                interrupted = True
                yes_detected = True
            if state == MENUSTATE and 0.15 < event.x < 0.40 and 0.27 < event.y < 0.59:
                state = NORMALSTATE
                if LANGUAGE == "en-US":
                    threadevent.set()
                    LANGUAGE = "da-DK"
            if state == MENUSTATE and 0.60 < event.x < 0.85 and 0.27 < event.y < 0.59:
                state = NORMALSTATE
                if LANGUAGE == "da-DK":
                    threadevent.set()
                    LANGUAGE = "en-US"                # put all these under one if MENUSTATE
            if event.x < 0.06 and event.y > 0.88:
                if state == MENUSTATE:
                    state = NORMALSTATE
                else: state = MENUSTATE
            if event.x > 0.94 and event.y > 0.88 and state is MENUSTATE:
                state = COLORSTATE
            elif state == COLORSTATE:
                BACKGROUND = screen.get_at((int(event.x*size[0]), int(size[1]*event.y)))
        ########## User Events ##########
        if state != MENUSTATE:                           # maybe not optimal
            if event.type == BLINKEVENT and state == NORMALSTATE:
                pygame.time.set_timer(BLINKEVENT2, 1, True)
                state = BLINKSTATE
            elif event.type == BLINKEVENT2:
                pygame.time.set_timer(NORMALEVENT, 100, True)
                state = BLINKSTATE2
            elif event.type == NORMALEVENT:
                state = NORMALSTATE
            elif event.type == HAPPYSTARTEVENT:
                pygame.time.set_timer(HAPPYEVENT, 70, True)
                state = HAPPYSTATE
            elif event.type == HAPPYEVENT:
                pygame.time.set_timer(NORMALEVENT, 1500, True)
                state = HAPPYSTATE2
            elif event.type == QUESTIONEVENT:
                pygame.time.set_timer(NORMALEVENT, 3000, True)
                state = QUESTIONSTATE

    ########## Check for face tracking ##########
    screen.fill(BACKGROUND)
    faceTracking()
    ########## State Machine ##########
    if state == NORMALSTATE:
        blitImages(normalwhiteL, normalwhiteR)
        drawPupils()
        blitImages(normalL, normalR)
    elif state == BLINKSTATE:
        blitImages(closingwhiteL, closingwhiteR)
        drawPupils()
        blitImages(closingL, closingR)
    elif state == BLINKSTATE2:
        blitImages(closedL, closedR)
    elif state == WINKSTATE:
        blitImages(winkL, normalR)
    elif state == HAPPYSTATE:
        blitImages(happy2L, happy2R)
    elif state == HAPPYSTATE2:
        blitImages(happyL, happyR)
    elif state == QUESTIONSTATE:
        blitImages(questionwhiteL, questionwhite2R)
        drawPupils()
        blitImages(questionL, questionR)
    elif state == VIDEOSTATE:
        playVideo()
        state = NORMALSTATE
    elif state == MENUSTATE:                   # make sure we can't change state from here (from timers)
        screen.blit(danishbutton, (120, 100))
        screen.blit(englishbutton, (800-120-200, 100))
        screen.blit(coloricon, (800-50-5, 480-50+5))
        text_surface, rect = myfont.render("CHOOSE CONNECTIVITY", (0,0,0))
        screen.blit(text_surface, (300,400))
    elif state == COLORSTATE:
        screen.blit(colorselector, (50, 50))
    if show_buttons:
        showButtons()
        '''
    if state != MENUSTATE:
        if LANGUAGE == "da-DK":
            screen.blit(danishbuttonsmall, (5, 480-50))
        elif LANGUAGE == "en-US":
            screen.blit(englishbuttonsmall, (5, 480-50))
        
        '''
    screen.blit(menuicon, (5, 480-50))   
    #GPIOfunction()   
    pygame.display.flip()
    #clock.tick(FPS)

interrupted = True
#receiver.send(True)
#while receiver.poll():  
#    (pupilL, pupilR, pupilV) = receiver.recv()
#tracking_thread.terminate()
#receiver.close()
#tracking_thread.join()
pygame.display.quit()
pygame.quit()
#GPIO.cleanup()
print("cleaned up")
exit(0)

