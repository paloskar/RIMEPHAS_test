import board
import adafruit_dotstar as dotstar
import pygame
from pydub import AudioSegment as AS
import numpy as np

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
 
dots.fill(NOCOLOR)

numberOfDots = len(dots)
        
#---------- sound decoding -----------------
sound = AS.from_mp3("sounds/Hej_sprit.mp3")

raw_data = sound.raw_data
channels = sound.channels
sample_rate = sound.frame_rate
sample_size = sound.sample_width

amp_data = np.frombuffer(raw_data, dtype=np.int16)
amp_data = np.absolute(amp_data)
amp_data.tofile('amp_data.csv', sep=' ')

pygame.mixer.init()
pygame.mixer.music.load('sounds/Hej_sprit.mp3')
pygame.mixer.music.play()

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
    
    
while pygame.mixer.music.get_busy():
    
    # Change the brightness of the LEDs when its speaking
    change_brightness_when_speaking(sample_rate, amp_data)

pygame.mixer.quit()
dots.fill(BLUE)