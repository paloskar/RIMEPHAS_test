import pygame
import datetime as dt
import threading
import random
import globdef

moveLeft = False
moveRight = False
moveUp = False
moveDown = False

greet1 = "sounds/oz/heythere.mp3"
greet2 = "sounds/oz/hello.mp3"
greet3 = "sounds/oz/howdy.mp3"
greet4 = "sounds/oz/haveaminute.mp3"
greet = [greet1, greet2, greet2, greet4]

offer1 = "sounds/oz/wouldlikesan.mp3"
offer2 = "sounds/oz/didyourecently.mp3"
offer3 = "sounds/oz/doyouwantclean.mp3"
offer = [offer1, offer2, offer3]

answer_yes = "sounds/Great_dispenser.mp3"

kind_no1 = "sounds/oz/oknexttime.mp3"
kind_no2 = "sounds/oz/okbutsanoften.mp3"
kind_no = [kind_no1, kind_no2]

agg_no1 = "sounds/oz/butsanoften.mp3"
agg_no2 = "sounds/oz/butsanthispoint.mp3"
agg_no = [agg_no1, agg_no2]

video = "sounds/oz/videorubhands.mp3"

rub30 = "sounds/oz/remember30.mp3"


edu1 = "sounds/oz/eliminatevirus.mp3"
edu2 = "sounds/oz/reduceepidemic.mp3"
edu3 = "sounds/oz/sanwashhands.mp3"
edu4 = "sounds/oz/keepdistance.mp3"
edu = [edu1, edu2, edu3, edu4]

parting1 = "sounds/oz/haveaniceday.mp3"
parting2 = "sounds/oz/nicedayclean.mp3"
parting = [parting1, parting2]

ozText = ["Hey, there!", "Hello!", "Howdy!", "Hey, do you have a minute?", "Would you like some hand sanitizer?",
          "Did you sanitize your hands recently?", "Do you want to clean your hands?", "Great, just put your hand under the dispenser, please!",
          "Okay, maybe next time", "OK, but it's important to  sanitize your hands often", "But it's important to sanitize your hands often",
          "But your really should sanitize your hands at this point", "Do you want to watch a video on how to properly rub your hands",
          "Remember to rub your hands for at least 30 seconds", "Did you know that hand sanitizer can eliminate many known viruses, including the corona virus?",
          "Did you know that frequent hand sanitization can reduce the spread of the epidemic?",
          "Did you know it's recommended to use hand sanitizer whenever you can't wash your hands?",
          "Remember to keep a distance of at least one meter from other people whenever possible",
          "Have a nice day!", "Have a nice day and remember to keep your hands clean!"]
          
def OzKeydownEvents(event, interactionItems, threadevent, flow, logfile):
    global moveLeft, moveRight, moveUp, moveDown
    pressed = pygame.key.get_pressed()
    addSpeech = None
    textIndex = None
    timestamp = dt.datetime.now()
    if event.key == pygame.K_1:
        print("1: Greeting added")
        rand = random.randint(0,3)
        addSpeech = greet[rand]
        textIndex = 0+rand
        logfile.write(f"{timestamp} | Greeting: {ozText[textIndex]} \n")
    elif event.key == pygame.K_2:
        print("2: Offer added")
        rand = random.randint(0,2)
        addSpeech = offer[rand]
        textIndex = 4+rand
        logfile.write(f"{timestamp} | Offer: {ozText[textIndex]} \n")
    elif event.key == pygame.K_3:
        print("3: Yes added")
        addSpeech = answer_yes
        textIndex = 7
        logfile.write(f"{timestamp} | Yes: {ozText[textIndex]} \n")
    elif event.key == pygame.K_4:
        print("4: Kind no added")
        rand = random.randint(0,1)
        addSpeech = kind_no[rand]
        textIndex = 8+rand
        logfile.write(f"{timestamp} | Kind no: {ozText[textIndex]} \n")
    elif event.key == pygame.K_5:
        print("5: Agg no added")
        rand = random.randint(0,1)
        addSpeech = agg_no[rand]
        textIndex = 10+rand
        logfile.write(f"{timestamp} | Kind no: {ozText[textIndex]} \n")
    elif event.key == pygame.K_6:
        print("6: Ask video")
        addSpeech = video
        textIndex = 12
        logfile.write(f"{timestamp} | Video: {ozText[textIndex]} \n")
    elif event.key == pygame.K_7:
        print("7: Rub 30 added")
        addSpeech = rub30
        textIndex = 13
        logfile.write(f"{timestamp} | Rub: {ozText[textIndex]} \n")
    elif event.key == pygame.K_8:
        print("8: Educational added")
        rand = random.randint(0,3)
        addSpeech = edu[rand]
        textIndex = 14+rand
        logfile.write(f"{timestamp} | Edu: {ozText[textIndex]} \n")
    elif event.key == pygame.K_9:
        print("9: Parting added")
        rand = random.randint(0,1)
        addSpeech = parting[rand]
        textIndex = 18+rand
        logfile.write(f"{timestamp} | Parting: {ozText[textIndex]} \n")
    elif event.key == pygame.K_0:
        print("Abort interaction")
        if flow.is_alive():
            threadevent.set()
    elif event.key == pygame.K_LEFT:
        moveLeft = True
    elif event.key == pygame.K_RIGHT:
        moveRight = True
    elif event.key == pygame.K_UP:
        moveUp = True
    elif event.key == pygame.K_DOWN:
        moveDown = True
    return addSpeech, textIndex
    if addSpeech is not None and not flow.is_alive():
        flow = threading.Thread(target=OzSpeechOut, args=(addSpeech,textIndex))
        flow.start()

def OzKeyupEvents(event):
    global moveLeft, moveRight, moveUp, moveDown
    if event.key == pygame.K_LEFT:
        moveLeft = False
    elif event.key == pygame.K_RIGHT:
        moveRight = False
    elif event.key == pygame.K_UP:
        moveUp = False
    elif event.key == pygame.K_DOWN:
        moveDown = False
        
def OzMovePupils(pupilL, pupilR, pupilV):
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
    return pupilL, pupilR, pupilV

def OzSpeechOut(outSpeech, textIndex):
    global textList
    textList = createTextSurface(finalSurface, textIndex, top_screen_height, top_screen_width)
    pygame.mixer.init()
    pygame.mixer.music.load(outSpeech)
    pygame.mixer.music.play()


