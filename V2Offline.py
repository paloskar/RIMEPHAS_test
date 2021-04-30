import pygame
import cv2
import threading
from moviepy.editor import VideoFileClip

import snowboydecoder
import speech_recognition as sr
from gtts import gTTS
import re

pygame.init()
WHITE = (255,255,255)
BACKGROUND = (150, 150, 150)
COLORKEY = (255,170,200)
FPS = 60
LANGUAGE = "danish"

########## Load images ##########
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

########## Functions ##########
def updatePupils():
    pygame.draw.rect(screen, WHITE, eyeL)
    pygame.draw.rect(screen, WHITE, eyeR)
    
def showButtons():
    screen.blit(yesbutton, (720,0))
    screen.blit(nobutton, (0,0))
    #pygame.draw.rect(screen, [255, 0, 0], buttonL)
    #pygame.draw.rect(screen, [0, 255, 0], buttonR)
    
def wait(ms):
    pygame.time.wait(ms)
    
def blitImages(left, right):
    screen.blit(left, (0,0))
    screen.blit(right, (400,0))

def normal():
    screen.blit(normalL, (0,0))
    screen.blit(normalR, (400,0))
    
def question():
    screen.blit(questionL, (0,0))
    screen.blit(questionR, (400,0))
 
def wink():
    screen.blit(winkL, (0,0))
    screen.blit(normalR, (400,0))
    
def signal():
    global interrupted
    interrupted = True
    
def interrupt_callback():
    global interrupted
    global timeout
    timeout += 0.03
    if timeout > 5:
        print("Timeout happened")
        return True
    return interrupted
    
def listen_for_two_cmds(cmd1, cmd2):
    global interrupted
    global yes_detected
    global no_detected
    global timeout
    timeout = 0.
    yes_detected = False
    no_detected = False
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
    
def speech_in(lang):
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
                out = r.recognize_google(audio, language=lang)
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))
            else:
                return out
        return "Error"

def speech_out(text, lang):
    tts = gTTS(text=text, lang=lang)
    tts.save("tmp/output.mp3")
    pygame.mixer.init()
    pygame.mixer.music.load("tmp/output.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

def danish_flow():
    print("Dansk flow")
    speech_out("Hej, kunne du tænke dig lidt håndsprit?", "da")
    for i in range(3):   
        listen_for_two_cmds("ja", "nej")
        if yes_detected:
            speech_out("Så bare sæt din hånd under automaten", "da")
            break
        elif no_detected:
            speech_out("Okay, hav en god dag!", "da")
            return
        elif i < 2:
            speech_out("Undskyld, jeg hørte ikke hvad du sagde. Vil du have noget håndsprit?", "da")
        else:
            speech_out("Jeg kan ikke forstå dig. Hav en god dag!", "da")
            return

    speech_out("Vil du se en video om hvordan man gør?", "da")
    for i in range(3):
        listen_for_two_cmds("ja", "nej")
        if yes_detected:
            global state
            state = VIDEOSTATE
            break
        elif no_detected:
            speech_out("Okay, det er bare i orden", "da")
            break
        elif i < 2:
            speech_out("Undskyld, jeg hørte ikke hvad du sagde. Vil du se en video?", "da")
        
def english_flow():
    global show_buttons
    lang = "en-us"
    print("English flow")
    speech_out("Hi, would you like some hand sanitizer?", lang)
    for i in range(3):
        listen_for_two_cmds("yes", "no")
        if yes_detected:
            pygame.event.post(happyevent)
            speech_out("Great! Just put your hand under the dispenser please", lang)
            break
        elif no_detected:
            speech_out("Okay, have a nice day!", "en-us")
            show_buttons = False
            return
        elif i < 2:
            pygame.event.post(questionevent)
            speech_out("Sorry, I didn't hear you. Would you like some hand sanitizer?", lang)
            show_buttons = True
        else:
            speech_out("Sorry, I do not understand. Have a nice day!", lang)
            show_buttons = False
            return

    speech_out("Would you like to see a video on how to do it?", lang)
    for i in range(3):
        listen_for_two_cmds("yes", "no")
        if yes_detected:
            global state
            state = VIDEOSTATE
            break
        elif no_detected:
            speech_out("Okay, have a nice day!", lang)
            break
        elif i < 2:
            speech_out("Sorry, I didn't hear you. Would you like to see a video?", lang)
            show_buttons = True
        else:
            speech_out("Sorry, I do not understand. Have a nice day!", lang)
    show_buttons = False
    
def findWholeWord(w):
    return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search

def playVideo():
    clip = VideoFileClip('coronavirus.mp4', target_resolution=(480,800))
    clip.preview()
    screen.fill(WHITE)

########## Setup face detection ##########
faceCasc = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
videoCap = cv2.VideoCapture(-1)
videoCap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
videoCap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
center = (400, 240)

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
screen.fill(WHITE)

offset = 800-170-100
eyeL = pygame.Rect(100, 210, 170, 170)
eyeR = pygame.Rect(offset, 210, 170, 170)
centerL = (185-30, 295-30) 
centerR =(offset+85-30,295-30)
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
state = NORMALSTATE
pygame.time.set_timer(BLINKEVENT, 5000)

stop = False
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
                if LANGUAGE == "danish":
                    flow = threading.Thread(target=danish_flow)
                elif LANGUAGE == "english":
                    flow = threading.Thread(target=english_flow)
                flow.start()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if show_buttons and buttonL.collidepoint(event.pos):
                print("Left button clicked")
                interrupted = True
                no_detected = True
            if show_buttons and buttonR.collidepoint(event.pos):
                print("Right button clicked")
                interrupted = True
                yes_detected = True
        elif event.type == pygame.FINGERDOWN:
            print(event.x, event.y)
            print(state)
            if show_buttons and event.x < 0.12 and event.y < 0.12:  # values differ for only touchscreen
                print("Left button clicked")
                interrupted = True
                no_detected = True
            if show_buttons and event.x > 0.88 and event.y < 0.12:
                print("Right button clicked")
                interrupted = True
                yes_detected = True
            if state == MENUSTATE and 0.15 < event.x < 0.40 and 0.27 < event.y < 0.59:
                state = NORMALSTATE
                LANGUAGE = "danish"
                screen.fill(WHITE)
            if state == MENUSTATE and 0.60 < event.x < 0.85 and 0.27 < event.y < 0.59:
                state = NORMALSTATE
                LANGUAGE = "english"
                screen.fill(WHITE)
            if event.x < 0.06 and event.y > 0.88:
                state = MENUSTATE
        ########## User Events ##########
        if state != MENUSTATE:                           # maybe not optimal
            if event.type == BLINKEVENT:
                pygame.time.set_timer(BLINKEVENT2, 1, True)
                state = BLINKSTATE
            elif event.type == BLINKEVENT2:
                pygame.time.set_timer(NORMALEVENT, 100, True)
                state = BLINKSTATE2
            elif event.type == NORMALEVENT:
                screen.fill(WHITE)
                state = NORMALSTATE
            elif event.type == HAPPYSTARTEVENT:
                pygame.time.set_timer(HAPPYEVENT, 70, True)
                state = HAPPYSTATE
                screen.fill(WHITE)
            elif event.type == HAPPYEVENT:
                pygame.time.set_timer(NORMALEVENT, 1500, True)
                state = HAPPYSTATE2
            elif event.type == QUESTIONEVENT:
                pygame.time.set_timer(NORMALEVENT, 3000, True)
                state = QUESTIONSTATE
                screen.fill(WHITE)

    ########## Detect faces ##########
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

    ########## Draw pupils ##########
    updatePupils()
    pupilpos = ((size[0]/2 - center[0])/7, (size[1]/2 - center[1])/7)
    pupilposL = (centerL[0]+pupilpos[0], centerL[1]-pupilpos[1])
    pupilposR = (centerR[0]+pupilpos[0], centerR[1]-pupilpos[1])
    screen.blit(pupil, pupilposL)
    screen.blit(pupil, pupilposR)
    
    ########## State Machine ##########
    if state == NORMALSTATE:
        blitImages(normalL, normalR)
    elif state == BLINKSTATE:
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
        blitImages(questionL, questionR)
    elif state == VIDEOSTATE:
        playVideo()
        state = NORMALSTATE
    elif state == MENUSTATE:                   # make sure we can't change state from here (from timers)
        screen.fill(BACKGROUND)
        screen.blit(danishbutton, (120, 100))
        screen.blit(englishbutton, (800-120-200, 100))
    if show_buttons:
        showButtons()
    if state != MENUSTATE:
        if LANGUAGE == "danish":
            screen.blit(danishbuttonsmall, (5,480-50))
        elif LANGUAGE == "english":
            screen.blit(englishbuttonsmall, (5, 480-50))
    pygame.display.flip()
    clock.tick(FPS)

interrupted = True
pygame.display.quit()
pygame.quit()
videoCap.release()
cv2.destroyAllWindows()

