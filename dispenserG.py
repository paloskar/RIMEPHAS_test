import RPi.GPIO as GPIO
import globdef as gl

#global variables
#numberOfActivations = 0
# Pins
PIN_MOTORDETECT = 24
PIN_IRSENOR = 20
PIN_LED = 25

# SPI Pins
PIN_CLK = 11
PIN_MOSI = 10
PIN_MISO = 9
PIN_CS = 8

class Dispenser:
    def __init__(self):
        self.irSensorThreshold = 0
        self.dispenserEmpty = False
        self.turnOffDispenser = False
        self.dispenserRefilled = False
        self.dispenserEmptyTemp = 0
        self.activated = False
        #self.numberOfActivations = 0

    def init_GPIO(self):
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
    def recvBits(self, numBits, clkPin, misoPin):
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

    def readAdc(self, channel, clkPin, misoPin, mosiPin, csPin):
        if (channel < 0) or (channel > 7):
            print("Invalid ADC Channel number, must be between [0,7]")
            return -1        
        # Datasheet says chip select must be pulled high between conversions
        GPIO.output(csPin, GPIO.HIGH)
        
        # Start the read with both clock and chip select low
        GPIO.output(csPin, GPIO.LOW)
        GPIO.output(clkPin, GPIO.HIGH)
        
        adc = self.recvBits(10, clkPin, misoPin)    
        # Set chip select high to end the read
        GPIO.output(csPin, GPIO.HIGH)  
        return round(adc)

    def update(self):
        #global numberOfActivations, irSensorThreshhold, dispenserEmpty, turnOffDispenser, dispenserRefilled, dispenserEmptyTemp, activated
        ADCvalue = self.readAdc(0, PIN_CLK, PIN_MISO, PIN_MOSI, PIN_CS)
        if not self.turnOffDispenser and not self.activated and GPIO.input(PIN_MOTORDETECT):          
            print("Motor Activated!")
            #count number of times used
            gl.numberOfActivations += 1
            print("Activations: ", gl.numberOfActivations)
            self.activated = True

        elif self.activated and not GPIO.input(PIN_MOTORDETECT):
            self.activated = False
        
        if(self.dispenserEmpty):
            # If dispenser refilled - button pushed in gui - rest all conditions and turn on system/motor again
            if(self.dispenserRefilled):
                self.dispenserEmptyTemp = 0
                self.dispenserEmpty = False
                self.dispenserRefilled = False
                self.turnOffDispenser = False
             
        # Test MOSFET
        if(self.turnOffDispenser == False):
            GPIO.output(PIN_LED, True)
        else:
            GPIO.output(PIN_LED, False)

