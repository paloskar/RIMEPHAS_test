import pygame
import snowboydecoder
import speech_recognition as sr
#from gtts import gTTS
import re
from pydub import AudioSegment as AS
import numpy as np
import globdef as gl

########## Set up speech recognition globals ##########
LANGUAGE = "en-US" # en-US or da-DK

interrupted = False
yes_detected = False
no_detected = False
timeout = 0.

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
# List of English voice lines
sounds_EN = [Hi_sanitizer, Video, Great_dispenser, Okay_video, Sorry_sanitizer, Sorry_video,  Nice_day, Sorry_bye,
          often, nudge1, thirtysec, caring, joke1_1, joke1_2, joke2_1, joke2_2, joke3_1, joke3_2]
# List of Danish voice lines
sounds_DA = [Hej_sprit, Video_da, Under_automaten, Okay_video_da, Undskyld_sprit, Undskyld_video, God_dag, Undskyld_farvel,
          nudge1da, nudge1da, thirtysecda, caring]

########## Functions for Snowboy keyword detection - used when not connected to internet ##########
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

# Callback function for detected "yes"
def detected_callback1():
    print("callback 1")
    signal()
    global yes_detected
    yes_detected = True
    
# Callback function for detected "no"
def detected_callback2():
    print("callback 2")
    signal()
    global no_detected
    no_detected = True

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

########## Function for Google Speech Recognition - used when connected to internet ###########
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
    
# Search for keywords in string from Google SR
def findWholeWord(w):
    return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search

########## Speech recognition main function ##########
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

########## Text-to-Speech function ##########
def speech_out(index):
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
        leds.change_brightness_when_speaking(sample_rate, amp_data)
    leds.dots.fill(leds.NOCOLOR)
    leds.indexLED = 5
    
########## Main interaction function going through interaction items to be executed ##########
def interaction(*items):
    global textList, show_buttons
    if gl.wizardOfOz:
        for item in items:
            speech_out
    else:    
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
                if len(items)<=1:
                    skip = interactionQuestion(3)
                else: skip = interactionQuestion(0)
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
            textList = []
            if threadevent.is_set(): break
    threadevent.clear()    
    show_buttons = False

########## Interaction function for two-way interaction ##########
def interactionQuestion(question):
    if question == 3:
        novideo = True
        question = 0
    else: novideo = False
    global show_buttons
    skip = False
    lastNumberOfActivations = gl.numberOfActivations
    speech_out(question)
    i = 0 
    while not threadevent.is_set():   
        speech_in("yes", "no")
        if yes_detected:
            pygame.event.post(happyevent)
            speech_out(question+2)
            if question == 0:
                if novideo:
                    iwait = 100
                    while iwait:
                        if gl.numberOfActivations != lastNumberOfActivations:
                            speech_out(10)
                            break
                        #else: add speech if no activation
                else:
                #if not novideo:
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
        elif question == 0 and gl.numberOfActivations != lastNumberOfActivations:
            pygame.event.post(happyevent)
            if novideo:
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
            skip = True
            break
    print("Interaction ended")
    return skip