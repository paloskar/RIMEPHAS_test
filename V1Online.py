import pygame
import cv2
import threading
from moviepy.editor import VideoFileClip

import speech_recognition as sr
from gtts import gTTS
import re

pygame.init()
WHITE = (255,255,255)
COLORKEY = (255,170,200)
FPS = 30

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

########## Functions ##########
def updatePupils():
    pygame.draw.rect(screen, WHITE, eyeL)
    pygame.draw.rect(screen, WHITE, eyeR)

def wait(ms):
    pygame.time.wait(ms)

def normal():
    screen.blit(normalL, (0,0))
    screen.blit(normalR, (400,0))
    
def question():
    screen.blit(questionL, (0,0))
    screen.blit(questionR, (400,0))
 
def wink():
    screen.blit(winkL, (0,0))
    screen.blit(normalR, (400,0))    

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
        si = speech_in("da-DK")
        print(si)
        if findWholeWord('ja')(si):
            speech_out("Så bare sæt din hånd under automaten", "da")
            break
        elif findWholeWord('nej')(si):
            speech_out("Okay, hav en god dag!", "da")
            return
        elif i < 2:
            speech_out("Undskyld, jeg hørte ikke hvad du sagde. Vil du have noget håndsprit?", "da")
        else:
            speech_out("Jeg kan desværre ikke forstå dig. Hav en god dag!", "da")
            return

    speech_out("Vil du se en video om hvordan man gør?", "da")
    for i in range(3):
        si = speech_in("da-DK")
        print(si)
        if findWholeWord('ja')(si):
            global state
            state = VIDEOSTATE
            break
        elif findWholeWord('nej')(si):
            speech_out("Okay, det er bare i orden", "da")
            break
        elif i < 2:
            speech_out("Undskyld, jeg hørte ikke hvad du sagde. Vil du se en video?", "da")
        
def english_flow():
    lang = "en-us"
    print("English flow")
    speech_out("Hi, would you like some hand sanitizer?", lang)
    for i in range(3):   
        si = speech_in("en-US")
        print(si)
        if findWholeWord('yes')(si):
            pygame.event.post(happyevent)
            speech_out("Great! Just put your hand under the dispenser please", lang)
            break
        elif findWholeWord('no')(si):
            speech_out("Okay, have a nice day!", "en-us")
            return
        elif i < 2:
            pygame.event.post(questionevent)
            speech_out("Sorry, I didn't hear you. Would you like some hand sanitizer?", lang)
        else:
            speech_out("Sorry, I do not understand. Have a nice day!", lang)
            return

    speech_out("Would you like to see a video on how to do it?", lang)
    for i in range(3):
        si = speech_in("en-US")
        print(si)
        if findWholeWord('yes')(si):
            global state
            state = VIDEOSTATE
            break
        elif findWholeWord('no')(si):
            speech_out("Okay, that's fine", lang)
            break
        elif i < 2:
            speech_out("Sorry, I didn't hear you. Would you like to see a video?", lang)

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
state = NORMALSTATE

stop = False
done = False
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
            #return
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                print("ESC")
                done = True
            elif event.key == pygame.K_s:
                flow = threading.Thread(target=danish_flow)
                flow.start()
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
        elif event.type == LISTENEVENT:
            signal()
            print("Timeout")
        elif event.type == QUESTIONEVENT:
            pygame.time.set_timer(NORMALEVENT, 3000, True)
            state = QUESTIONSTATE
            screen.fill(WHITE)

    ########## Detect faces ##########
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
            recSize = w

    ########## Draw pupils ##########
    updatePupils()
    pupilpos = ((size[0]/2 - center[0])/7, (size[1]/2 - center[1])/7)
    pupilposL = (centerL[0]+pupilpos[0], centerL[1]-pupilpos[1])
    pupilposR = (centerR[0]+pupilpos[0], centerR[1]-pupilpos[1])
    screen.blit(pupil, pupilposL)
    screen.blit(pupil, pupilposR)
    
    if state == NORMALSTATE:
        normal()
    elif state == BLINKSTATE:
        screen.blit(closingL, (0,0))
        screen.blit(closingR, (400,0))
    elif state == WINKSTATE:
        wink()
    elif state == HAPPYSTATE:
        screen.blit(happy2L, (0,0))
        screen.blit(happy2R, (400,0))
    elif state == QUESTIONSTATE:
        question()
    elif state == VIDEOSTATE:
        playVideo()
        state = NORMALSTATE
    
    #show_buttons()
    pygame.display.flip()
    clock.tick(FPS)

pygame.display.quit()
pygame.quit()
videoCap.release()
cv2.destroyAllWindows()
