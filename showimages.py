import pygame
import os

images = []
size = (800,600)

timerImg = 0
currImg = 0
fade = 0


def wrapInc(v, n):
    if v >= n-1:
        return 0
    else:
        return v + 1
    

def imagesInit(path):
    for image in os.listdir(path):
        if image.endswith('.png') or image.endswith('.jpg'):    
            img = pygame.transform.scale(pygame.image.load(path+image), size )
            images.append(img)
            print('# loaded', image,'from',path)


def showImage(surface, x, y, timer):
    global timerImg, images, size, timerImg, currImg, fade
    if timerImg:
        timerImg -= 1
        surface.blit(images[currImg], (x, y) )
    else:
        if fade < size[0]:
            fade += 10
            surface.blit(images[currImg], (x-fade, y) )
            surface.blit(images[wrapInc(currImg, len(images))], (x+size[0]-fade, y))
        else:
            fade = 0
            timerImg = timer
            currImg = wrapInc(currImg, len(images))
            surface.blit(images[currImg], (x, y ))    