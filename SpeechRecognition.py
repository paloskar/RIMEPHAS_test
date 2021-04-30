'''
from gtts import gTTS
import pygame

def say(text):
    tts = gTTS(text=text, lang='da')
    tts.save("tmp/output.mp3")

    pygame.mixer.init()
    pygame.mixer.music.load("tmp/output.mp3")
    pygame.mixer.music.play()
    #while pygame.mixer.music.get_busy():
     #   pygame.time.Clock().tick(10)

say("Hej, kunne du tænke dig at se en video?")
'''
'''
from gtts import gTTS
import pygame
from io import BytesIO

pygame.init()

def say(text):
    tts = gTTS(text=text, lang='da')
    #tts.save("output.wav")

    fp = BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0,0)
    pygame.mixer.init()
    pygame.mixer.music.load(fp)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

say("Kunne du tænke dig at se en video?")
'''
'''
import subprocess as sp
from gtts import gTTS
import time
import playsound
def speak(text):
    tts = gTTS(text=text, lang='en')
    filename = 'voice.mp3'
    tts.save(filename)
    sp.call(['aplay', '-D', 'ac101', filename])
    
speak("hello")
print("done")
'''
    
'''
from IPython.display import Audio
from gtts import gTTS
from tempfile import TemporaryFile

# To play audio text-to-speech during execution
def speak(my_text):
    f = TemporaryFile()
    tts = gTTS(text=my_text, lang='en')
    tts.write_to_fp(f)
    f.seek(0)
    return Audio(f.read(), autoplay=True)
    f.close()

speak('checkpoint number one : Packages and modules successfully imported')
print("done")
'''
'''
from gtts import gTTS
from tempfile import TemporaryFile
from IPython.display import Audio
import io

def speak(text):
    with io.BytesIO() as f:
        gTTS(text=text, lang='en').write_to_fp(f)
        f.seek(0)
        return Audio(f.read(), autoplay=True)
speak("hello world what is going on here")
print("done")
'''

import speech_recognition as sr


r = sr.Recognizer()
r.pause_threshold = 0.5
with sr.Microphone() as source:
    r.adjust_for_ambient_noise(source, duration=0.5)
    print("Say something!")
    try:
        audio = r.listen(source, timeout=4, phrase_time_limit=3)
    except sr.WaitTimeoutError:
        print("Timeout happened")
    else:
        try:
            print("Google Speech Recognition thinks you said: " + r.recognize_google(audio, language="en-US"))
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))


'''
def speech_in():
    r = sr.Recognizer()
    print("1")
    with sr.Microphone() as source:
        print("2")
        r.adjust_for_ambient_noise(source, duration=1)
        print("Say something!")
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=4)
        except sr.WaitTimeoutError:
            print("Timeout happened")
            return "timeout"
        else:
            try:
                out = r.recognize_google(audio, language="da-DK")
                #print("Google Speech Recognition thinks you said: " + out)
                #return out
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))
            else:
                return out
        return "error"
print(speech_in())
'''
'''
import re

def findWholeWord(w):
    return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search
if findWholeWord('seek')('those who seek shall find'):
    print("ja")
if findWholeWord('word')('swordsmith'):
    print("tja")
else:
    print("naj")
'''
'''
import speech_recognition as sr

r = sr.Recognizer()
with sr.Microphone() as source:
    r.adjust_for_ambient_noise(source, duration=2)
    print("Say something!")
    try:
        audio = r.listen(source, snowboy_configuration=("/home/pi/Eyes", ("/home/pi/Eyes/resources/models/hej.pmdl",)), timeout=5)
    except sr.WaitTimeoutError:
        print("Timeout happened")
    else:
        try:
            print("Google Speech Recognition thinks you said: " + r.recognize_google(audio, language="da-DK"))
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))
'''