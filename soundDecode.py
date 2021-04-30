import pygame
from pydub import AudioSegment as AS
import numpy as np

sound = AS.from_mp3("sounds/Hej_sprit.mp3")

raw_data = sound.raw_data

channels = sound.channels

sample_rate = sound.frame_rate

sample_size = sound.sample_width

amp_data = np.frombuffer(raw_data, dtype=np.int16)
amp_data = np.absolute(amp_data)

print("channels", channels)
print("sample size", sample_size)
print("sample rate", sample_rate)
print("data", raw_data)
print("data2", amp_data)
print("size", amp_data.size)
print(amp_data.size/sample_rate)

amp_data.tofile('amp_data.csv', sep=' ')

pygame.mixer.init()
pygame.mixer.music.load('sounds/Hej_sprit.mp3')
pygame.mixer.music.play()
i = 0
while pygame.mixer.music.get_busy():
    ms = pygame.time.Clock().tick(30)
    samples = int(sample_rate/(1000/ms))
    out = np.average(amp_data[i*samples:(i+1)*samples])
    print(out)
    i += 1

pygame.mixer.quit()