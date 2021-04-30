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
import random
import subprocess

import matplotlib
matplotlib.use("Agg")
import matplotlib.backends.backend_agg as agg
import matplotlib.pyplot as plt, mpld3
from matplotlib.ticker import MaxNLocator
from pygame.locals import *
import datetime as dt
from pushbullet import Pushbullet

import board
import adafruit_dotstar as dotstar

from edgetpu.detection.engine import DetectionEngine
from edgetpu.utils import dataset_utils
from PIL import Image
from PIL import ImageDraw

pygame.init()

import RPi.GPIO as GPIO
import os
import time
#from threading import Timer
#import sys

##########  Settings  ##########
size = (800,480)
WHITE = (255,255,255)
BACKGROUND = WHITE
COLORKEY = (255,170,200)
FPS = 60
LANGUAGE = "en-US" # en-US
isOnline = True
eyeDesign = "normal"

##########  GPIO  ##########
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
    GPIO.output(PIN_LED, False)
    GPIO.setup(PIN_MOTORDETECT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    
    # Spi pins Init
    GPIO.setup(PIN_CLK, GPIO.OUT)
    GPIO.setup(PIN_MISO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(PIN_MOSI, GPIO.OUT)
    GPIO.setup(PIN_CS, GPIO.OUT)

# Read SPI data from ADC  
def recvBits(numBits, clkPin, misoPin):
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

myfont = pygame.freetype.SysFont(pygame.freetype.get_default_font(), 20)

activated = False
def GPIOfunction():
    global numberOfActivations, irSensorThreshhold, dispenserEmpty, turnOffDispenser, dispenserRefilled, dispenserEmptyTemp, activated
    ADCvalue = readAdc(0, PIN_CLK, PIN_MISO, PIN_MOSI, PIN_CS)
    if not turnOffDispenser and not activated and GPIO.input(PIN_MOTORDETECT):          
        print("Motor Activated!")
        #count number of times used
        numberOfActivations += 1
        print("Activations: ", numberOfActivations)
        activated = True

    elif activated and not GPIO.input(PIN_MOTORDETECT):
        activated = False
    
    if(dispenserEmpty):
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

########## Frequency and plot ##########
fig = plt.figure(figsize=[8, 4.8], dpi=100)

numberOfActivationsMinute = 0
trailingFiveMinSum = 0
lastMinute = 0
firstMinSkipped = False
hours = "%H"
minutes = "%M"
seconds = "%S"
# Set the time format here
#---------------------------------------------------------------
timeFormat = minutes
#---------------------------------------------------------------
hoursStart = 19
hoursEnd = 25
#hoursStart = int(dt.datetime.now().strftime(timeFormat))
#hoursEnd = (hoursStart + 10) % 60
numberOfActivations = 0
numberOfActivationsHour = 0
lastHour = 0
operatingTime = False
hoursList = []
peopleListPlot = []
fiveMinQue = []

def trailing_five_min_activations():
    global lastMinute, fiveMinQue, numberOfActivationsMinute, numberOfActivations, firstMinSkipped, trailingFiveMinSum

    dailyMinute = dt.datetime.now()
    dailyMinute = dailyMinute.strftime(timeFormat)
    minute = int(dailyMinute)

    if minute != lastMinute:
        if lastMinute != 0 and firstMinSkipped == True:
            if len(fiveMinQue) == 5:
                fiveMinQue.pop(0)

            trailingActivations = numberOfActivations - numberOfActivationsMinute
            fiveMinQue.append(trailingActivations)
            numberOfActivationsMinute = numberOfActivations

        if len(fiveMinQue) == 5:
            trailingFiveMinSum = sum(fiveMinQue)

        lastMinute = minute
        firstMinSkipped = True
        
PIN_SERVO = 19
PULSE_FREQ = 50
DUTY_CYCLE = 2
GPIO.setmode(GPIO.BCM)        
def setup_servo(pin, pwmFreq):
    GPIO.setup(pin, GPIO.OUT)
    servo = GPIO.PWM(pin, pwmFreq)
    servo.start(0)
    return servo
servo = setup_servo(PIN_SERVO, PULSE_FREQ) # 50 Hz pulse
        
def set_angle(servo, angle):
    dutyCycle = 2 + (float(angle) / 18)
    servo.ChangeDutyCycle(dutyCycle) #Recalculate with values from datasheet of servo
    
def move_servo_to_random_position():
    global servo
    
    randomPosition = random.randint(80, 100)
    set_angle(servo, randomPosition)
    print("Position: ", randomPosition)

########## Load images ##########
normalL = pygame.image.load("images/png/normalL.png")
normalR = pygame.transform.flip(normalL, True, False)
normalwhiteL = pygame.image.load("images/png/normalLwhite.png")
normalwhiteR = pygame.transform.flip(normalwhiteL, True, False)

closedL = pygame.image.load("images/png/closedL.png")
closedR = pygame.transform.flip(closedL, True, False)

happyL = pygame.image.load("images/png/happyL.png")
happyR = pygame.transform.flip(happyL, True, False)

confusedL = pygame.image.load("images/png/confusedL.png")
confusedR = pygame.image.load("images/png/confusedR.png")
confusedLwhite = pygame.image.load("images/png/normalAltLwhite.png")
confusedRwhite = pygame.image.load("images/png/confusedRwhite.png")

onlineicon = pygame.image.load("images/png/online.png")
offlineicon = pygame.image.load("images/png/offline.png")

danishbutton = pygame.image.load("images/bg/danishicon.png")
englishbutton = pygame.image.load("images/bg/englishicon.png")
danishbutton = pygame.transform.scale(danishbutton, (120,90))
englishbutton = pygame.transform.scale(englishbutton, (120,90))

nobutton = pygame.image.load("images/png/nobutton.png")
yesbutton = pygame.image.load("images/png/yesbutton.png")

pupil = pygame.image.load("images/png/pupil.png")

colorselector = pygame.image.load("images/bg/ColorPicker.bmp")
colorselector = pygame.transform.flip(colorselector, False, True)
coloricon = pygame.transform.scale(colorselector, (120, 90))
colorselector = pygame.transform.scale(colorselector, (700, 350))

menuicon = pygame.image.load("images/png/menuicon.png")
graphicon = pygame.image.load("images/png/graphicon.png")
graphicon = pygame.transform.scale(graphicon, (90,90))

monster = pygame.image.load("images/png/monstereyes.png")
monsterpupil = pygame.image.load("images/png/monsterpupil.png")
monsterpupilsmall = pygame.image.load("images/png/monsterpupilsmall.png")
monsterblinkL = pygame.image.load("images/png/monsterclosedL.png")
monsterblinkM = pygame.image.load("images/png/monsterclosedM.png")
monsterblinkR = pygame.image.load("images/png/monsterclosedR.png")

benderL = pygame.image.load("images/bg/benderL.png")
benderR = pygame.transform.flip(benderL, True, False)
benderpupil = pygame.image.load("images/bg/benderpupil.png")

##########     Alts        ##########
happyAltL = pygame.image.load("images/bg/bghappy4L.png")
happyAltL.set_alpha(None)
happyAltL.set_colorkey(COLORKEY)
happyAltR = pygame.transform.flip(happyAltL, True, False)

blinkAltL = pygame.image.load("images/bg/bgclosedgrey3L.png")
blinkAltL.set_alpha(None)
blinkAltL.set_colorkey(COLORKEY)
blinkAltR = pygame.transform.flip(blinkAltL, True, False)

spookyouter = pygame.image.load("images/png/outer.png")
spookyinner = pygame.image.load("images/png/Inner.png")
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
Okay_video = "sounds/Okay_video.mp3"

thirtysec = "sounds/30sec.mp3"
joke1_1 = "sounds/joke1_1.mp3"
joke1_2 = "sounds/joke1_2.mp3"
joke2_1 = "sounds/joke2_1.mp3"
joke2_2 = "sounds/joke2_2.mp3"
joke3_1 = "sounds/joke3_1.mp3"
joke3_2 = "sounds/joke3_2.mp3"
nudge1 = "sounds/nudge1.mp3"
nudge2 = "sounds/nudge2.mp3"
nudge1da = "sounds/nudge1da.mp3"
Okay_video_da = "sounds/Okay_video_da.mp3"
thirtysecda = "sounds/30sec_da.mp3"
caring = "sounds/thanks_for_caring.mp3"
often = "sounds/sanitize_often.mp3"

'''
sounds_EN = [Hi_sanitizer, Video, Great_dispenser, Okay_video, Sorry_sanitizer, Sorry_video,  Nice_day, Sorry_bye,
          often, nudge1, thirtysec, caring, joke1_1, joke1_2, joke2_1, joke2_2, joke3_1, joke3_2,
          Hej_sprit, Video_da, Under_automaten, Okay_video_da, Undskyld_sprit, Undskyld_video, God_dag, Undskyld_farvel,
          nudge1da, nudge1da, thirtysecda, caring]
'''
sounds_EN = [Hi_sanitizer, Video, Great_dispenser, Okay_video, Sorry_sanitizer, Sorry_video,  Nice_day, Sorry_bye,
          often, nudge1, thirtysec, caring, joke1_1, joke1_2, joke2_1, joke2_2, joke3_1, joke3_2]
          
sounds_DA = [Hej_sprit, Video_da, Under_automaten, Okay_video_da, Undskyld_sprit, Undskyld_video, God_dag, Undskyld_farvel,
          nudge1da, nudge1da, thirtysecda, caring]
########## Functions ##########

activationsList = []
numberOfPeopleHour = 0

numberOfDispenses = 10
dispensesEmptyThreshold = 0.8
almostEmpty = numberOfDispenses * dispensesEmptyThreshold

notification = "notification"
sms = "sms"

typeOfNotification = notification
msg = "The dispenser is under 20" + "%" + " full."

def update_activations_plot(operatingTimeList):
    global lastHour, activationsList, numberOfActivationsHour, numberOfActivations
    dailyHour = dt.datetime.now()
    dailyHour = dailyHour.strftime(timeFormat)
    hour = int(dailyHour)
    hourString = ""

    if hour < 10:
        hourString = "0" + str(hour) + ":00"
    else:
        hourString = str(hour) + ":00"

    if hourString in operatingTimeList:
        operatingHours = len(operatingTimeList) - 1
        #print("no hours: ", operatingHours)
        indexHour = operatingTimeList.index(hourString)
        operatingTime = True
    else:
        #print("no hours: ", operatingHours)
        operatingTime = False
    if hour != lastHour and operatingTime == True:
        trailingActivations = numberOfActivations - numberOfActivationsHour
        #print("Activations: ", trailingActivations)
        activationsList.insert(indexHour, round(trailingActivations))
        activationsList.pop(indexHour + 1)
        #print("acti list: ", activationsList)
        numberOfActivationsHour = numberOfActivations

    lastHour = hour
        
def update_people_plot(operatingTimeList, numberOfPeople):
    global lastHour, peopleListPlot, numberOfPeopleHour, activationsList, numberOfActivationsHour, numberOfActivations 
    dailyHour = dt.datetime.now()
    dailyHour = dailyHour.strftime(timeFormat)
    hour = int(dailyHour)
    hourString = ""
    
    if hoursEnd - hoursStart > 10:
        hourString = str(hour) 
    else:
        if hour < 10:
            hourString = "0" + str(hour) + ":00"
        else:
            hourString = str(hour) + ":00"       
    if hourString in operatingTimeList:
        operatingHours = len(operatingTimeList) - 1
        indexHour = operatingTimeList.index(hourString)
        operatingTime = True
    else:
        operatingTime = False
        numberOfActivationsHour = numberOfActivations
        numberOfPeopleHour = numberOfPeople     
    if hour != lastHour and operatingTime == True:
        trailingPeople = numberOfPeople - numberOfPeopleHour
        peopleListPlot.insert(indexHour, round(trailingPeople))
        peopleListPlot.pop(indexHour + 1)
        numberOfPeopleHour = numberOfPeople
        trailingActivations = numberOfActivations - numberOfActivationsHour
        activationsList.insert(indexHour, round(trailingActivations))
        activationsList.pop(indexHour + 1)
        numberOfActivationsHour = numberOfActivations

    lastHour = hour

def list_with_operating_hours(hoursStart, hoursEnd):
    global activationsList, peopleListPlot
    hours = []
    for i in range(hoursStart + 1, hoursEnd + 1):   
        if (hoursEnd - hoursStart) > 10:
            hours.append(str(i))
        else:
            if i < 10:
                hours.append("0" + str(i) + ":00")
            else:
                hours.append(str(i) + ":00")
    length = len(hours)
    for i in range(length):
        activationsList.append(0)
        peopleListPlot.append(0)
    return hours

def pushbullet_notification(notificationType, message):
    pb = Pushbullet("o.xgWW2FkTk3pGt2oQXM9m9TiQXF2GvUPQ")
    # Get all devices that the current user has access to.      
    # Select a device 
    phone = pb.devices[0] 
    phone = pb.get_device('OnePlus 7 Pro') 
    if notificationType == "notification":
        push = phone.push_note("Alert!", message)
    elif notificationType == "sms":
        push = pb.push_sms(phone, "+4521378019", message)

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
    interrupted = False
    timeout = 0.
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
    r.pause_threshold = 0.5
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.5)
        print("Say something!")
        try:
            audio = r.listen(source, timeout=4, phrase_time_limit=3)
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
    if cmd1 == "yes" and LANGUAGE == "da-DK":
        cmdList1 = ["ja", "gerne", "jo", "ok"]
        cmdList2 = ["nej", "ellers tak"]
    elif cmd1 == "yes" and LANGUAGE == "en-US":
        cmdList1 = [cmd1, "please", "ok", "alright", "why not", "yeah", "i guess"]
        cmdList2 = [cmd2, "don't"]
    else:
        cmdList1 = [cmd1]
        cmdList2 = [cmd2]
    if not isOnline:
        listen_for_two_cmds(cmd1, cmd2)
    else:    
        gin = google_in()
        for cmd in cmdList1:
            if findWholeWord(cmd)(gin):
                yes_detected = True
                return
        for cmd in cmdList2:
            if findWholeWord(cmd)(gin):
                no_detected = True
                return
            
#------------ Functions to convert amplitudes to brightness -------
#Normalized Data
def normalize_data(sample, data):
    normalizedSample = (sample - min(data)) / (max(data) - min(data))
    return normalizedSample

# convert the normalized data to a brightness
def convert_normData_to_brightness(normData):
    if not math.isnan(normData):
        maxBrightValue = 255
        brightValue = int(normData * maxBrightValue)
    else: brightValue = 0
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
dots = dotstar.DotStar(board.D6, board.D5, 13, brightness=0.8)

# Using a DotStar Digital LED Strip with 72 LEDs connected to digital pins
# 5V - Yellow wire to gpio6 and green wire to gpio5
#dots = dotstar.DotStar(board.D6, board.D5, 72, brightness=0.1)
 
red = "red"
green = "green"
blue = "blue"
allColors = "all"

chosenColor = allColors
 
dots.fill(NOCOLOR)

numberOfDots = len(dots)
indexLED = 5

def change_brightness_when_speaking(sample_rate, amp_data):
    global indexLED
    
    ms = pygame.time.Clock().tick(30)
    samples = int(sample_rate/(1000/ms))
    out = np.average(amp_data[indexLED*samples:(indexLED+1)*samples])
    #Normalize sample
    normalizedSample = normalize_data(out, amp_data)
    #convert amp to brightness
    brightnessScale = 4
    brightnessAmp = convert_normData_to_brightness(normalizedSample) * brightnessScale
    if(brightnessAmp > 255):
        brightnessAmp = 255
    #convert brightness to color
    brightValue = set_brightness(chosenColor, brightnessAmp)
    lengthOfDots = len(dots)
    middleOfDots = round(lengthOfDots/2)
    # Fill all LEDs
    dots.fill(brightValue)
    #insideOut()
    indexLED += 1

def speech_out(index):
    global indexLED
    if LANGUAGE == "da-DK":
       sounds = sounds_DA
    else:
        sounds = sounds_EN
    pygame.mixer.init()
    pygame.mixer.music.load(sounds[index])
    sound = AS.from_mp3(sounds[index])
    raw_data = sound.raw_data
    sample_rate = sound.frame_rate * 2.3
    amp_data = np.frombuffer(raw_data, dtype=np.int16)
    amp_data = np.absolute(amp_data)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        if threadevent.is_set():
            pygame.mixer.quit()
            break
        change_brightness_when_speaking(sample_rate, amp_data)
    dots.fill(NOCOLOR)
    indexLED = 5

def interaction(*items):
    skip = False
    for item in items:
        if item == "nudge":
            speech_out(8+items[1])
        elif item == "30s":
            rand = random.randint(0,2)
            if rand: speech_out(10)
            else: speech_out(11)
        elif item == "joke":
            speech_out(11+items[1])
            wait(2000)
            speech_out(12+items[1])
        elif item == "sanitizer":
            skip = interactionQuestion(0)
        elif item == "video" and not skip:
            interactionQuestion(1)
        elif item == "monster":
            global eyeDesign, state
            speech_in(items[0], items[1])
            if yes_detected:
                eyeDesign = items[0]
                state = NORMALSTATE
            elif no_detected:
                eyeDesign = items[1]
                state = NORMALSTATE
        elif item == "novideo":
            skip = interactionQuestion(3)
        threadevent.clear()
                      
def interactionQuestion(question):
    if question == 3:
        novid = True
        question = 0
    else: novid = False
    global show_buttons
    skip = False
    lastNumberOfActivations = numberOfActivations
    speech_out(question)
    i = 0 
    while not threadevent.is_set():   
        speech_in("yes", "no")
        if yes_detected:
            pygame.event.post(happyevent)
            speech_out(question+2)
            if question == 0:
                if novid:
                    #just break and activation will trigger sound?
                    wait(3000)
                    if numberOfActivations != lastNumberOfActivations:
                        speech_out(10)
                    #else: add speech if no activation
                else:
                    wait(2000)
                break
            else:
                global state
                state = VIDEOSTATE
                break
        elif no_detected:
            speech_out(6)
            skip = True
            break
        elif question == 0 and numberOfActivations != lastNumberOfActivations:
            pygame.event.post(happyevent)
            if novid:
                speech_out(10)
            else: wait(2000)
            break
        elif i < 1:
            pygame.event.post(questionevent)      # dont repeat if sound level low?
            speech_out(question+4)
            show_buttons = True
            i += 1
        else:
            speech_out(7)
    show_buttons = False
    #threadevent.clear()
    print("Flow ended")
    return skip

def findWholeWord(w):
    return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search

def playVideo():
    clip = VideoFileClip(f'videos/{eyeDesign}video.mp4')#, target_resolution=(480,800))
    clip.preview(fullscreen = True)
    
res0 = (320,320)
res1 = (320,240)
res2 = (640,480)
res3 = (1280,720)
res = res2

def faceTracking(sender):
    engine = DetectionEngine("ssd_mobilenet_v2_face_quant_postprocess_edgetpu.tflite")
    cap = cv2.VideoCapture(-1)
    #cap.set(cv2.CAP_PROP_FRAME_WIDTH, res[0])
    #cap.set(cv2.CAP_PROP_FRAME_HEIGHT, res[1])
    currentID = 1   
    faceTrackers = {}
    term = False
    peopleCount = 0
    """
    start = time.time()
    fps = 0
    old = 0.
    """
    while not term:
        _, frame = cap.read()
        frame = cv2.rotate(frame, cv2.ROTATE_180)
        frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        framePIL = Image.fromarray(frameRGB)
        faces = engine.detect_with_image(framePIL,
                                         threshold=0.05,
                                         keep_aspect_ratio=True,
                                         relative_coord=False,
                                         top_k=10,
                                         resample=4)
        for face in faces:
            (x, y, x2, y2) = (int(i) for i in face.bounding_box.flatten().tolist())
            w = x2-x
            h = y2-y
            center = (int(x+w*0.5), int(y+h*0.5))
            fidMatch = False
            for fid in faceTrackers.keys():
                (tx, ty, tw, th, n, u, c) =  faceTrackers.get(fid)
                if tx <= center[0] <= tx+tw and ty <= center[1] <= ty+th:
                    if n < 50: n += 1
                    if n >= 35 and c == False:
                        c = True
                        peopleCount += 1                        
                    faceTrackers.update({fid:(x,y,w,h,n,True,c)})
                    fidMatch = True
                    break
            if not fidMatch:
                faceTrackers.update({currentID:(x,y,w,h,1,True,False)})
                currentID += 1

        fidsToDelete = []
        for fid in faceTrackers.keys():
            (tx, ty, tw, th, n, u, c) =  faceTrackers.get(fid)
            if not u:
                # if center is close to frame edge then decay faster
                #if res[0]-tw-20 < tx < 20:
                    #n-=5
                n -= 1
            if n < 1: fidsToDelete.append(fid)
            else:
                faceTrackers.update({fid:(tx,ty,tw,th,n,False,c)})

        for fid in fidsToDelete:
            faceTrackers.pop(fid, None)
            
        sender.send((faceTrackers, peopleCount))
        
        if sender.poll():  
            term = sender.recv()
        """
        fps += 1
        now = time.time()
        tid = math.trunc(now-start)
        if tid != old:
            print(fps)
            fps = 0
        old = tid
        """
        pygame.time.Clock().tick(100)
        
    cap.release()

def calculateAngles(x, y, w, h):
    #globals
    WIDTH = res[0]/2
    HEIGHT = res[1]/2
    EYE_DEPTH = 2
    hFOV = 62/2
    vFOV = 49/2
    ppcm = WIDTH*2/15.5# * 1.5

    center = (int(x+w*0.5), int(y+h*0.5))
    hAngle = (1 - center[0]/WIDTH) * hFOV
    vAngle = (1 - center[1]/HEIGHT) * vFOV            
    c = -0.26*w+103
    global pupilL, pupilR, pupilV
    # horizontal
    b = 4
    angleA = (90 - hAngle)*math.pi/180
    a = math.sqrt(b*b + c*c - 2*b*c*math.cos(angleA))
    angleC = math.acos((a*a + b*b - c*c)/(2*a*b))
    #print(a, angleC)
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
    
def drawMonsterPupils():
    centerLmonster = (158-43, 218-50)
    centerMmonster = (390-25, 250-27)
    centerRmonster = (640-43, 222-50)
    pupilposL = (centerLmonster[0]+pupilL, centerLmonster[1]-pupilV)
    pupilposR = (centerRmonster[0]+pupilR, centerRmonster[1]-pupilV)
    pupilposM = (centerMmonster[0]+int((pupilL+pupilR)/2), centerMmonster[1]-pupilV) 
    screen.blit(monsterpupil, pupilposL)
    screen.blit(monsterpupil, pupilposR)
    screen.blit(monsterpupilsmall, pupilposM)

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
INTERACTIONEVENT = pygame.USEREVENT + 9
GAZEEVENT = pygame.USEREVENT + 10
MONSTERBLINKEVENT = pygame.USEREVENT + 11
MULTIEVENT = pygame.USEREVENT + 12
NECKSERVOEVENT = pygame.USEREVENT + 13
happyevent = pygame.event.Event(HAPPYSTARTEVENT)
questionevent = pygame.event.Event(QUESTIONEVENT)

multiGestureLock = False

########## States ##########
NORMALSTATE = 0
BLINKSTATE = 1
WINKSTATE  = 2
HAPPYSTATE = 3
CONFUSEDSTATE = 4
VIDEOSTATE = 5
BLINKSTATE2 = 6
HAPPYSTATE2 = 7
MENUSTATE = 8
COLORSTATE = 9
MONSTERSTATE = 10
MONSTERBLINKSTATE = 11
MONSTERBLINKSTATE2 = 12
MONSTERBLINKSTATE3 = 13
SPOOKYSTATE = 14
state = NORMALSTATE

if __name__ == '__main__':
    
    subprocess.run(["xinput", "map-to-output", "8", "DSI-1"])
    if isOnline and not checkInternet():
        isOnline = False
    receiver, sender = mp.Pipe(True)
    mp.set_start_method('spawn',force=True)
    tracking_proc = mp.Process(target=faceTracking, args=(sender,))
    tracking_proc.start()
    
    init_GPIO()
    
    pygame.time.set_timer(BLINKEVENT, 10000, True)
    monsterblinks = [monsterblinkL, monsterblinkM, monsterblinkR]
    #pygame.time.set_timer(NECKSERVOEVENT, 5000)
    ########## init interaction vars ##########
    flow = threading.Thread(target=interaction)
    threadevent = threading.Event()
    trackID = 0
    altTrackID = 0
    gazeAtClosest = True
    pygame.time.set_timer(GAZEEVENT, 8000, True)
    videoKeys = []
    prevKeys = []
    prevInteraction = 0
    interactionWait = False
    interactionIndex = 0
    lastNumberOfActivations = 0
    peopleAmount = 1 #len(trackedList)
    frequency = 1    #from trailing_five
    interactionItems = []
    runInteraction = False
    ##########     Stats vars     ##########
    hoursList = list_with_operating_hours(hoursStart, hoursEnd)
    oldNumberOfPeople = 0
    numberOfPeople = 0
    
    pygame.mouse.set_visible(False)
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode(size)#, pygame.NOFRAME)
    #pygame.display.toggle_fullscreen()
    done = False
    start = time.time()
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    print("ESC")
                    done = True
                elif event.key == pygame.K_r:
                    pygame.time.set_timer(INTERACTIONEVENT, 1, True)
                    #interactionWait = False
                    runInteraction = not runInteraction
                    print("Run: ", runInteraction)
                elif event.key == pygame.K_o:
                    turnOffDispenser = not turnOffDispenser
                    print(turnOffDispenser)
                elif event.key == pygame.K_1:
                    screen.fill(BACKGROUND)
                    blitImages(happyL, happyR)
                    pygame.display.flip()
                    wait(3000)
                elif event.key == pygame.K_2:
                    screen.fill(BACKGROUND)
                    blitImages(happyAltL, happyAltR)
                    pygame.display.flip()
                    wait(3000)
                elif event.key == pygame.K_3:
                    screen.fill(BACKGROUND)
                    blitImages(winkL, winkR)
                    pygame.display.flip()
                    wait(3000)
                elif event.key == pygame.K_4:
                    screen.fill(BACKGROUND)
                    blitImages(closedL, closedR)
                    pygame.display.flip()
                    wait(300)
                elif event.key == pygame.K_5:
                    screen.fill(BACKGROUND)
                    blitImages(blinkAltL, blinkAltR)
                    pygame.display.flip()
                    wait(300)
                elif event.key == pygame.K_6:
                    screen.fill(BACKGROUND)
                    blitImages(confusedLwhite, confusedRwhite)
                    drawPupils()
                    blitImages(confusedL, confusedR)
                    pygame.display.flip()
                    wait(2000)
                elif event.key == pygame.K_7:
                    screen.fill(BACKGROUND)
                    blitImages(benderL, benderR)
                    pupilposL = (centerL[0]+pupilL, centerL[1]-pupilV)
                    pupilposR = (centerR[0]+pupilR, centerR[1]-pupilV)
                    screen.blit(benderpupil, pupilposL)
                    screen.blit(benderpupil, pupilposR)
                    pygame.display.flip()
                    wait(5000)
                elif event.key == pygame.K_a:
                    numberOfActivations += 1
                    print("Activation!")
                elif event.key == pygame.K_f:
                    if frequency == 1: frequency = 10
                    else: frequency = 1
                    print("Frequency: ", frequency)
                elif event.key == pygame.K_p:
                    if peopleAmount == 1: peopleAmount = 10
                    else: peopleAmount = 1
                    print("Number of people: ", peopleAmount)
                elif event.key == pygame.K_g:
                    plt.clf()
                    xlist = np.arange(len(hoursList))
                    plt.bar(xlist-0.2, activationsList, width=0.3)
                    plt.bar(xlist+0.2, peopleListPlot, width=0.3)
                    plt.title('Number Of People')
                    plt.xticks(xlist, hoursList)
                    ax = plt.gca()
                    ax.yaxis.set_major_locator(MaxNLocator(integer=True))

                    canvas = agg.FigureCanvasAgg(fig)
                    canvas.draw()
                    renderer = canvas.get_renderer()
                    raw_data = renderer.tostring_rgb()

                    size = canvas.get_width_height()

                    surf = pygame.image.fromstring(raw_data, size, "RGB")
                    screen.blit(surf, (0,0))
                    pygame.display.flip()
                    wait(10000)
            elif event.type == pygame.FINGERDOWN:
                if show_buttons:
                    if event.x*size[0] < nobutton.get_width() and event.y*size[1] < nobutton.get_height():
                        print("Left button pressed")
                        interrupted = True
                        no_detected = True
                    if event.x*size[0] > size[0]-yesbutton.get_width() and event.y*size[1] < yesbutton.get_height():
                        print("Right button pressed")
                        interrupted = True
                        yes_detected = True
                if event.x*size[0] < 5+menuicon.get_width() and event.y*size[1] > size[1]-menuicon.get_height()-20: 
                    if state == MENUSTATE:
                        state = NORMALSTATE
                        pygame.time.set_timer(BLINKEVENT, 15000, True)
                    else: state = MENUSTATE
                elif state == MENUSTATE:
                    if 160 < event.x*size[0] < 160+120 and 100 < event.y*size[1] < 100+90:
                        state = NORMALSTATE
                        if LANGUAGE == "en-US":
                            threadevent.set()
                            LANGUAGE = "da-DK"
                            pygame.time.set_timer(INTERACTIONEVENT, 1, True)
                            #interactionWait = False
                            interactionIndex = 0
                    elif 160 < event.x*size[0] < 160+120 and 250 < event.y*size[1] < 250+90:
                        state = NORMALSTATE
                        if LANGUAGE == "da-DK":
                            threadevent.set()
                            LANGUAGE = "en-US"
                            pygame.time.set_timer(INTERACTIONEVENT, 1, True)
                            #interactionWait = False
                            interactionIndex = 0
                    elif size[0]-160-120 < event.x*size[0] < size[0]-160 and 250 < event.y*size[1] < 250+90:
                        state = COLORSTATE
                    elif size[0]-160-120 < event.x*size[0] < size[0]-160 and 100 < event.y*size[1] < 100+90:
                        if isOnline: isOnline = False
                        elif not isOnline and checkInternet(): isOnline = True
                elif state == COLORSTATE:
                    BACKGROUND = screen.get_at((int(event.x*size[0]), int(size[1]*event.y)))
            """elif event.type == pygame.FINGERMOTION and not multiGestureLock:
                if eyeDesign == "monster": eyeDesign = "normal"
                elif eyeDesign == "normal": eyeDesign = "monster"
                multiGestureLock = True
                pygame.time.set_timer(MULTIEVENT, 1000, True)"""
            ########## User Events ##########
            if state != MENUSTATE:
                if event.type == BLINKEVENT and state == NORMALSTATE and eyeDesign == "normal":
                    pygame.time.set_timer(NORMALEVENT, 300, True)
                    state = BLINKSTATE2
                elif event.type == BLINKEVENT and state == NORMALSTATE and eyeDesign == "monster":
                    pygame.time.set_timer(MONSTERBLINKEVENT, 50, True)
                    state = MONSTERBLINKSTATE
                    random.shuffle(monsterblinks)
                elif event.type == MONSTERBLINKEVENT:
                    if state == MONSTERBLINKSTATE:
                        pygame.time.set_timer(MONSTERBLINKEVENT, 50, True)
                        state = MONSTERBLINKSTATE2
                    elif state == MONSTERBLINKSTATE2:
                        pygame.time.set_timer(MONSTERBLINKEVENT, 50, True)
                        state = MONSTERBLINKSTATE3
                    elif state == MONSTERBLINKSTATE3:
                        blinktime = random.randrange(5000, 20000, 1000)
                        pygame.time.set_timer(BLINKEVENT, blinktime, True)
                        state = NORMALSTATE
                elif event.type == NORMALEVENT:
                    blinktime = random.randrange(5000, 20000, 1000)
                    pygame.time.set_timer(BLINKEVENT, blinktime, True)
                    state = NORMALSTATE
                elif event.type == HAPPYSTARTEVENT and eyeDesign == "normal":
                    pygame.time.set_timer(HAPPYEVENT, 70, True)
                    state = HAPPYSTATE
                elif event.type == HAPPYEVENT and eyeDesign == "normal":
                    pygame.time.set_timer(NORMALEVENT, 1500, True)
                    state = HAPPYSTATE2
                elif event.type == QUESTIONEVENT and eyeDesign == "normal":
                    pygame.time.set_timer(NORMALEVENT, 3000, True)
                    state = CONFUSEDSTATE
            if event.type == INTERACTIONEVENT:
                interactionWait = False
                print("Interaction timer reset")
            elif event.type == GAZEEVENT:
                gazeAtClosest = not gazeAtClosest
                altTrackID = 0
                if gazeAtClosest:
                    gazeTime = 8000 + random.randrange(-3, 3)*1000
                else:
                    gazeTime = 5000 + random.randrange(-2, 2)*1000
                pygame.time.set_timer(GAZEEVENT, gazeTime, True)
            elif event.type == MULTIEVENT:
                multiGestureLock = False
            elif event.type == NECKSERVOEVENT:
                move_servo_to_random_position()
        ########## Interaction ##########
        #update_activations_plot(hoursList)
        trailing_five_min_activations()
        
        manyPeople = 3
        frequentUse = 5
        waitTimer = 0
        if receiver.poll():  
            (trackedList, peopleCount) = receiver.recv()
            trackedList = {k:v for (k,v) in trackedList.items() if v[4]>35}
            if runInteraction:                
                if not interactionWait and not flow.is_alive() and trackedList:
                    keys = trackedList.keys()
                    recurrents = set(keys) & set(prevKeys)
                    recurrentsVideo = set(keys) & set(videoKeys)
                    interactionItems = []
                    if frequency >= frequentUse:           # interaction 1
                        waitTimer = 30000
   
                    elif peopleAmount >= manyPeople:       # interaction 2
                        if prevInteraction == 2: interactionIndex += 1
                        else: interactionIndex = 0
                        """
                        if interactionIndex == 0:
                            interactionItems.append("nudge")
                            interactionItems.append(0)
                        elif interactionIndex == 1:
                            jokeIndex = random.choice((0,2,4))
                            interactionItems.append("joke")
                            interactionItems.append(jokeIndex)
                        """
                        if interactionIndex == 0:              #elif 2
                            interactionItems.append("nudge")
                            interactionItems.append(0)
                            waitTimer = 15000
                        elif interactionIndex == 1:            #     3
                            interactionItems.append("novideo")
                            #if not recurrentsVideo or len(keys - recurrentsVideo) >= 2:
                            #    interactionItems.append("video")
                            #    videoKeys = keys
                            prevKeys = keys
                            waitTimer = 30000
                        else:
                            interactionIndex = 0
                            if len(keys - prevKeys) >= 2:
                                interactionIndex = 0
                        prevInteraction = 2
                        #waitTimer = 50000 + interactionIndex*10000
                        # check in between if use or new people
                        
                    else:                                  # interaction 3
                        if prevInteraction == 3: interactionIndex += 1
                        else: interactionIndex = 0
                        if interactionIndex >= 2:
                            if len(keys - recurrents) >= 1:
                                interactionIndex = -1
                            waitTimer = 5000
                            interactionIndex = 0
                            #maybe save number and check if used during the wait
                        else:
                            if interactionIndex == 1:        # 0
                                interactionItems.append("nudge")
                                interactionItems.append(0)
                                #interactionItems.append(random.randrange(1))
                                waitTimer = 13000 #30000
                            elif interactionIndex == 0:      # 1
                                interactionItems.append("sanitizer")
                                interactionItems.append("video")
                                waitTimer = 60000
                                """
                                if numberOfActivations == numberOfActivationsInteraction:
                                    interactionItems.append("sanitizer")
                                    if not recurrentsVideo or len(keys - recurrentsVideo) >= 2:
                                        interactionItems.append("video")
                                        videoKeys = keys
                                    waitTimer = 10000 #60000
                                """
                            prevKeys = keys
                        numberOfActivationsInteraction = numberOfActivations
                        prevInteraction = 3

                    # if used dont proceed unless new people
                    # check length without recurrents to see if any new
                    # len(keys - recurrents)
                    # if many new still play video despite few recurrents?
                    # if person who triggered is not there anymore, stop interaction early

                elif interactionWait and not flow.is_alive(): # and activation
                    if lastNumberOfActivations != numberOfActivations:    
                        pygame.event.post(happyevent)
                        interactionItems.append("30s")
                
                if interactionItems:
                        print("Arguments: ", interactionItems)       
                        flow = threading.Thread(target=interaction, args=interactionItems)
                        flow.start()
                        interactionItems = []
            if waitTimer > 0:
                interactionWait = True
                pygame.time.set_timer(INTERACTIONEVENT, waitTimer, True)            
            lastNumberOfActivations = numberOfActivations
            
            if trackedList:
                if gazeAtClosest:
                    if altTrackID == 0:
                        trackID = max(trackedList.items(), key = lambda i : i[1][2])[0]
                        altTrackID = trackID
                    elif trackID not in trackedList:
                        trackID = max(trackedList.items(), key = lambda i : i[1][2])[0]
                else:
                    if altTrackID == 0:
                        peopleList = list(trackedList.keys())
                        if len(peopleList) > 1:
                            maxID = max(trackedList.items(), key = lambda i : i[1][2])[0]
                            peopleList.remove(maxID)
                        altTrackID = random.choice(peopleList)
                    if altTrackID in trackedList:
                        trackID = altTrackID
                    else:
                        trackID = max(trackedList.items(), key = lambda i : i[1][2])[0]

                (x, y, w, h, n, u, c) = trackedList.get(trackID)
                calculateAngles(x, y, w, h)
                
                if peopleCount > oldNumberOfPeople:
                    newPeople = peopleCount - oldNumberOfPeople
                    numberOfPeople += newPeople
                    oldNumberOfPeople = peopleCount
        
        update_people_plot(hoursList, numberOfPeople)
                
        ########## State Machine ##########
        screen.fill(BACKGROUND)
        
        if state == NORMALSTATE:
            if eyeDesign == "normal":
                blitImages(normalwhiteL, normalwhiteR)
                drawPupils()
                blitImages(normalL, normalR)
            elif eyeDesign == "monster":
                screen.blit(monster, (0,0))
                drawMonsterPupils()
        elif state == BLINKSTATE:
            blitImages(closingwhiteL, closingwhiteR)
            drawPupils()
            blitImages(closingL, closingR)
        elif state == BLINKSTATE2:
            blitImages(closedL, closedR)
        elif state == WINKSTATE:
            blitImages(winkL, normalR)
        elif state == HAPPYSTATE:
            blitImages(happyL, happyR)
        elif state == HAPPYSTATE2:
            blitImages(happyL, happyR)
        elif state == CONFUSEDSTATE:
            blitImages(confusedLwhite, confusedRwhite)
            drawPupils()
            blitImages(confusedL, confusedR)
        elif state == VIDEOSTATE:
            playVideo()
            state = NORMALSTATE
        elif state == MENUSTATE:
            screen.blit(danishbutton, (160, 100))
            screen.blit(englishbutton, (160, 250))
            screen.blit(coloricon, (800-160-120, 250))
            if isOnline: screen.blit(onlineicon, (800-160-120, 100))
            else: screen.blit(offlineicon, (800-160-120, 100))
            screen.blit(graphicon, (400-32, 370))
            if not flow.is_alive():
                flow = threading.Thread(target=interaction, args=("monster", "normal"))
                flow.start()
            text_surface, rect = myfont.render(f"Activations: {numberOfActivations}", (0,0,0))
            screen.blit(text_surface, (5,5))
        elif state == COLORSTATE:
            screen.blit(colorselector, (50, 50))
        elif state == MONSTERBLINKSTATE:
            screen.blit(monster, (0,0))
            drawMonsterPupils()
            screen.blit(monsterblinks[0], (0,0))
        elif state == MONSTERBLINKSTATE2:
            screen.blit(monster, (0,0))
            drawMonsterPupils()
            screen.blit(monsterblinks[1], (0,0))
        elif state == MONSTERBLINKSTATE3:
            screen.blit(monster, (0,0))
            drawMonsterPupils()
            screen.blit(monsterblinks[2], (0,0))
        elif state == SPOOKYSTATE:
            screen.blit(spookyinner, (pupilL,pupilV))
            screen.blit(spookyouter, (0,0))
        if show_buttons:
            showButtons()
        '''
        if numberOfActivations >= almostEmpty:
            numberOfActivations = 0
            pushbullet_notification(typeOfNotification, msg)
            print("Notification sent!")
        '''
        screen.blit(menuicon, (5, size[1]-50))
        GPIOfunction()   
        pygame.display.flip()

    interrupted = True
    threadevent.set()
    receiver.send(True)
    while receiver.poll():  
        (trackedList, peopleCount) = receiver.recv()
    tracking_proc.terminate()
    tracking_proc.join()
    pygame.display.quit()
    pygame.quit()
    GPIO.cleanup()
    servo.stop()
    print("Cleaned up")
    exit(0)


