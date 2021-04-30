
class irSensor():

    def __init__(self, adc, numberOfSensors, sensorThreshold):
        self.adc = adc
        self.numberOfSensors=numberOfSensors
        self.sensorThreshold = sensorThreshold
        self.values = [0] * self.numberOfSensors
        self.cups = [0] * self.numberOfSensors
        self.adcStandardValue = [0] * self.numberOfSensors
        self.adcThreshold = [0] * self.numberOfSensors
        self.handRemoved = [0] * self.numberOfSensors
        self.handInFront = [0] * self.numberOfSensors
        self.handNotRemoved = [0] * self.numberOfSensors


    def initSensors(self):
        # Load all the first values into a list to have a default / threshold ir value for each sensor
        adcValues = [0] * self.numberOfSensors
        
        for i in range(self.numberOfSensors):
        # The read_adc function will get the value of the specified channel (0-7).
            adcValues[i] = self.adc.read_adc(i)
            # Set the threshold for each individual sensor
            self.adcThreshold[i] = adcValues[i] * self.sensorThreshold
       
            if adcValues[i] == 0:
                print("Ir sensor" + str(i) + " does not work! - Check connections")

        print("ADC first value: ", adcValues[:self.numberOfSensors])
        print("ADC threshold: ", self.adcThreshold)


    def detectHands(self, adc):  
        values = [0]*self.numberOfSensors
        for i in range(self.numberOfSensors):
            values[i] = adc.read_adc(i)
            #print(values[i])
            # check if sensor value goes over threshold - cup removed/placed back

            if values[i] < self.adcThreshold[i]:
                self.handRemoved[i] = True
                self.handInFront[i] = False
            if self.handRemoved[i] and values[i] >= self.adcThreshold[i]:
                self.handInFront[i] = True
                self.handRemoved[i] = False
                print("Hand" + str(i) + " in front")


            #print(values)
            # Print the ADC values.
            #print('| {0:>4} | {1:>4} | {2:>4} | {3:>4} |'.format(*values))
            # Pause for half a second.
            #time.sleep(0.5)
            
    def getHandList(self):
        return self.handInFront
