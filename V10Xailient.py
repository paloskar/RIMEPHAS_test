import pygame
import pygame.freetype
import cv2
import threading
import multiprocessing as mp
from moviepy.editor import VideoFileClip
import math
import socket
import snowboydecoder
import speech_recognition as sr
from gtts import gTTS
import re
from pydub import AudioSegment as AS
import numpy as np
pygame.init()

from xailient import dnn
########## GPIO ##########
import RPi.GPIO as GPIO
import os
import time
from threading import Timer
import sys

import board
import adafruit_dotstar as dotstar

# Pins
PIN_MOTORDETECT = 24
PIN_IRSENOR = 20
PIN_LED = 25

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
dispenserEmptyTemp = 0

def init_GPIO():
    # Init GPIO pins
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PIN_LED, GPIO.OUT)
    GPIO.output(PIN_LED, True)
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

activated = False
print("dav")
def GPIOfunction():
    global numberOfActivations, irSensorThreshhold, dispenserEmpty, turnOffDispenser, dispenserRefilled, dispenserEmptyTemp, activated
    ADCvalue = readAdc(0, PIN_CLK, PIN_MISO, PIN_MOSI, PIN_CS)
    if(dispenserEmpty == False):
        turnOffDispenser = False
    """
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
        timer = Timer(1, timeout)
        timer.start()
        timer.join()
    """
    if not activated and GPIO.input(PIN_MOTORDETECT):          
        print("Motor Activated!")
        #count number of times used
        numberOfActivations += 1
        print("Activations: ", numberOfActivations)
        activated = True
        #timer = Timer(1, timeout)
        #timer.start()
        #timer.join()
    elif activated and not GPIO.input(PIN_MOTORDETECT):
        activated = False
    
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
    screen.blit(text_surface, (5,5))

########## ##########

#BACKGROUND = (150, 150, 170)

WHITE = (255,255,255)
BACKGROUND = WHITE
COLORKEY = (255,170,200)
FPS = 60
LANGUAGE = "da-DK" # en-US
isOnline = False

########## Load images ##########
onlineicon = pygame.image.load("images/bg/online3.png")
offlineicon = pygame.image.load("images/bg/offline3.png")

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
danishbutton = pygame.image.load("images/bg/danishicon.png")
englishbutton = pygame.image.load("images/bg/englishicon.png")
danishbutton = pygame.transform.scale(danishbutton, (120,90))
englishbutton = pygame.transform.scale(englishbutton, (120,90))


colorselector = pygame.image.load("images/bg/ColorPicker.bmp")
colorselector = pygame.transform.flip(colorselector, False, True)
coloricon = pygame.transform.scale(colorselector, (120, 90))
colorselector = pygame.transform.scale(colorselector, (700, 350))

menuicon = pygame.image.load("images/bg/menuicon.bmp")
menuicon.set_alpha(None)
menuicon.set_colorkey(COLORKEY)

########## Load sounds ##########
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
def checkInternet(host="8.8.8.8", port=53, timeout=3):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error as ex:
        print(ex)
        return False
    
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
    if not isOnline:
        listen_for_two_cmds(cmd1, cmd2)
    else:    
        gin = google_in()
        if findWholeWord(cmd1)(gin): yes_detected = True
        elif findWholeWord(cmd2)(gin): no_detected = True
"""
#------------ Functions to convert amplitudes to brightness -------
#Normalized Data
def normalize_data(sample, data):
    
    normalizedSample = (sample - min(data)) / (max(data) - min(data)) 
    
    return normalizedSample

# convert the normalized data to a brightness
def convert_normData_to_brightness(normData):
    
    maxBrightValue = 255
    brightValue = int(normData * maxBrightValue)
        
    return brightValue


# Choose color and set the brightness
def set_brightness(color, brightness):
    #return (0, 0, 255-brightness)
    if color == "red":
        return (255-brightness, 0, 0)
    elif color == "green":
        return (0, 255-brightness, 0)
    elif color == "blue":
        return (0, 0, 255-brightness)
    elif color == "all":
        return (brightness, brightness, brightness)

def insideOut():
    for dot in range(round(numberOfDots/2)):
        color = random_brightness(blue)
        #print(color)
        dots[round(numberOfDots/2) + dot] = color
        dots[round(numberOfDots/2) - dot -1] = color

#----------------LEDS init---------------------
NOCOLOR = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Using a DotStar Digital LED Strip with 72 LEDs connected to hardware SPI
# 5V - Yellow wire to gpio11 and green wire to gpio10
#dots = dotstar.DotStar(board.SCK, board.MOSI, 72, brightness=0.1)

# Using a DotStar Digital LED Strip with 72 LEDs connected to digital pins
# 5V - Yellow wire to gpio6 and green wire to gpio5
dots = dotstar.DotStar(board.D6, board.D5, 72, brightness=0.1)
 
red = "red"
green = "green"
blue = "blue"
allColors = "all"

chosenColor = blue
 
dots.fill(BLUE)

numberOfDots = len(dots)
i = 0

def change_brightness_when_speaking(sample_rate, amp_data):
    global i
    
    ms = pygame.time.Clock().tick(30)
    samples = int(sample_rate/(1000/ms))
    out = np.average(amp_data[i*samples:(i+1)*samples])
    #Normalize sample
    normalizedSample = normalize_data(out, amp_data)
    #convert amp to brightness
    brightnessScale = 4
    brightnessAmp = convert_normData_to_brightness(normalizedSample) * brightnessScale
    if(brightnessAmp > 255):
        brightnessAmp = 255
    #convert brightness to color
    brightValue = set_brightness(chosenColor, brightnessAmp)
    print("color: ", brightValue)    
    dots.fill(brightValue)
    i += 1
"""
def speech_out(index):
    if LANGUAGE == "da-DK":
       index += 7
    pygame.mixer.init()
    pygame.mixer.music.load(sounds[index])
    sound = AS.from_mp3(sounds[index])
    raw_data = sound.raw_data
    sample_rate = sound.frame_rate
    amp_data = np.frombuffer(raw_data, dtype=np.int16)
    amp_data = np.absolute(amp_data)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        if threadevent.is_set():
            pygame.mixer.quit()
            return
        pygame.time.Clock().tick(10)
        #change_brightness_when_speaking(sample_rate, amp_data)
 
def interaction():
    global show_buttons
    flowState = 0
    speech_out(0)
    i = 0
    while not threadevent.is_set():
        speech_in("yes", "no")
        if yes_detected:
            if flowState == 0:
                pygame.event.post(happyevent)
                speech_out(4)
                flowState += 1
                i = 0
                #while not GPIO.input(PIN_MOTORDETECT): pygame.time.Clock().tick(10)
                wait(3000)
                speech_out(1)
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
    
def faceTracking(sender):
    res1 = (320,240)
    res2 = (480, 320)
    res3 = (640,480)
    res4 = (1280,720)
    res = res1

    detectum = dnn.Detector()
    THRESHOLD = 0.55 # Value between 0 and 1 for confidence score
    cap = cv2.VideoCapture(-1)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, res[0])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, res[1])
    frameCounter = 0
    currentID = 0   
    faceTrackers = {}
    
    WIDTH = res[0]/2
    HEIGHT = res[1]/2
    EYE_DEPTH = 2
    hFOV = 125/2 #62/2
    vFOV = 85/2 #49/2
    ppcm = WIDTH*2/15.5 * 1.5
    term = False
    while not term:
        _, frame = cap.read()
        frame = cv2.rotate(frame, cv2.ROTATE_180)
        frameCounter += 1
        if frameCounter % 1 == 0:
            _, bboxes = detectum.process_frame(frame, THRESHOLD)
            for (x1, y1, x2, y2) in bboxes:
                w = x2-x1
                h = y2-y1
                print(x1, y1, x2, y2)
                center = (int(x1+(x2-x1)*0.5), int(y1+(y2-y1)*0.5))
                fidMatch = False
                for fid in faceTrackers.keys():
                    (tx1, ty1, tx2, ty2, n, u) =  faceTrackers.get(fid)
                    if tx1-w*0.5 <= center[0] <= tx2+w*0.5 and ty1-h*0.5 <= center[1] <= ty2+h*0.5:
                        if n < 50: n += 1
                        faceTrackers.update({fid:(x1,y1,x2,y2,n,True)})
                        fidMatch = True
                        break
                if not fidMatch:
                    faceTrackers.update({currentID:(x1,y1,x2,y2,1,True)})
                    currentID += 1
                    
        trackID = -1
        fidsToDelete = []
        for fid in faceTrackers.keys():
            (tx1, ty1, tx2, ty2, n, u) =  faceTrackers.get(fid)
            if not u: n -= 1
            if n < 1: fidsToDelete.append(fid)
            else:
                faceTrackers.update({fid:(tx1,ty1,tx2,ty2,n,False)})
                if n < 25:
                    pass
                else:
                    trackID = fid
       
        for fid in fidsToDelete:
            faceTrackers.pop(fid, None)
        print(faceTrackers)
        if trackID != -1:
            # determine who to track
            (x1, y1, x2, y2, n, u) = faceTrackers.get(trackID)
            center = (int(x1+(x2-x1)*0.5), int(y1+(y2-y1)*0.5))
            hAngle = (1 - center[0]/WIDTH) * hFOV
            vAngle = (1 - center[1]/HEIGHT) * vFOV            
            c = -0.26*(x2-x1)+103
            
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
            
            sender.send((pupilL, pupilR, pupilV))
        if sender.poll():  
            term = sender.recv()
    cap.release()

def drawPupils():
    pupilposL = (centerL[0]+pupilL, centerL[1]-pupilV)
    pupilposR = (centerR[0]+pupilR, centerR[1]-pupilV)
    screen.blit(pupil, pupilposL)
    screen.blit(pupil, pupilposR)

########## Setup face detection ##########
pupilL = 0
pupilR = 0
pupilV = 0

########## Setup misc ##########
interrupted = False
yes_detected = False
no_detected = False
timeout = 0.
show_buttons = False

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

if __name__ == '__main__':        
    receiver, sender = mp.Pipe(True)
    mp.set_start_method('spawn',force=True)
    tracking_proc = mp.Process(target=faceTracking, args=(sender,))
    tracking_proc.start()

    threadevent = threading.Event()
    init_GPIO()
    pygame.mouse.set_visible(False)
    clock = pygame.time.Clock()
    size = (800,480)
    screen = pygame.display.set_mode(size) # pygame.NOFRAME
    #pygame.display.toggle_fullscreen()
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
                    flow = threading.Thread(target=interaction)
                    flow.start()
            elif event.type == pygame.FINGERDOWN:
                if show_buttons:
                    if event.x < 0.12 and event.y < 0.12:
                        print("Left button pressed")
                        interrupted = True
                        no_detected = True
                    elif event.x > 0.88 and event.y < 0.12:
                        print("Right button pressed")
                        interrupted = True
                        yes_detected = True
                if event.x < 0.06 and event.y > 0.88:
                    if state == MENUSTATE:
                        state = NORMALSTATE
                    else: state = MENUSTATE
                elif state == MENUSTATE:
                    if 160 < event.x*800 < 160+120 and 100 < event.y*480 < 100+90:
                        state = NORMALSTATE
                        if LANGUAGE == "en-US":
                            threadevent.set()
                            LANGUAGE = "da-DK"
                    elif 160 < event.x*800 < 160+120 and 250 < event.y*480 < 250+90:
                        state = NORMALSTATE
                        if LANGUAGE == "da-DK":
                            threadevent.set()
                            LANGUAGE = "en-US"
                    elif 800-160-120 < event.x*800 < 800-160 and 250 < event.y*480 < 250+90:
                        state = COLORSTATE
                    elif 800-160-120 < event.x*800 < 800-160 and 100 < event.y*480 < 100+90:
                        if isOnline: isOnline = False
                        elif not isOnline and checkInternet(): isOnline = True
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
        if receiver.poll():  
            (pupilL, pupilR, pupilV) = receiver.recv()
        screen.fill(BACKGROUND)
        
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
        elif state == MENUSTATE:
            screen.blit(danishbutton, (160, 100))
            screen.blit(englishbutton, (160, 250))
            screen.blit(coloricon, (800-160-120, 250))
            if isOnline: screen.blit(onlineicon, (800-160-120, 100))
            else: screen.blit(offlineicon, (800-160-120, 100))
        elif state == COLORSTATE:
            screen.blit(colorselector, (50, 50))
        if show_buttons:
            showButtons()

        screen.blit(menuicon, (5, 480-50))   
        GPIOfunction()   
        pygame.display.flip()
        #middle = time.time()
        #print(middle-start)

    interrupted = True
    threadevent.set()
    receiver.send(True)
    while receiver.poll():  
        (pupilL, pupilR, pupilV) = receiver.recv()
    tracking_proc.terminate()
    tracking_proc.join()
    receiver.close()
    pygame.display.quit()
    pygame.quit()
    GPIO.cleanup()
    print("Cleaned up")
    exit(0)
