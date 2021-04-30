import board
import adafruit_dotstar as dotstar
import math
import numpy as np
import pygame

#------------ Functions to convert amplitudes to brightness -------
class LEDinit:
    def __init__(self):
        # Using a DotStar Digital LED Strip with 72 LEDs connected to hardware SPI
        # 5V - Yellow wire to gpio11 and green wire to gpio10
        self.dots = dotstar.DotStar(board.D6, board.D5, 13, brightness=0.8)
        self.NOCOLOR = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 0, 255)
         
        self.red = "red"
        self.green = "green"
        self.blue = "blue"
        self.allColors = "all"
        
        self.chosenColor = self.allColors     
        self.dots.fill(self.NOCOLOR)
        self.numberOfDots = len(self.dots)
        self.brightnessScale = 4
        self.indexLED = 5

    #Normalized Data
    def normalize_data(self, sample, data):
        normalizedSample = (sample - min(data)) / (max(data) - min(data))
        return normalizedSample

    # convert the normalized data to a brightness
    def convert_normData_to_brightness(self, normData):
        if not math.isnan(normData):
            maxBrightValue = 255
            brightValue = int(normData * maxBrightValue)
        else: brightValue = 0
        return brightValue

    # Choose color and set the brightness
    def set_brightness(self, color, brightness):
        #return (0, 0, 255-brightness)
        if color == "red":
            return (255-brightness, 0, 0)
        elif color == "green":
            return (0, 255-brightness, 0)
        elif color == "blue":
            return (0, 0, 255-brightness)
        elif color == "all":
            return (brightness, brightness, brightness)

    def change_brightness_when_speaking(self, sample_rate, amp_data):
        ms = pygame.time.Clock().tick(30)
        samples = int(sample_rate/(1000/ms))
        out = np.average(amp_data[self.indexLED*samples:(self.indexLED+1)*samples])
        #Normalize sample
        normalizedSample = self.normalize_data(out, amp_data)
        #convert amp to brightness      
        brightnessAmp = self.convert_normData_to_brightness(normalizedSample) * self.brightnessScale
        if(brightnessAmp > 255):
            brightnessAmp = 255
        #convert brightness to color
        brightValue = self.set_brightness(self.chosenColor, brightnessAmp)
        # Fill all LEDs
        self.dots.fill(brightValue)
        self.indexLED += 1
