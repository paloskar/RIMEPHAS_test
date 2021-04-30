"""
from picamera.array import PiRGBArray
from picamera import PiCamera

import time
"""
import pygame
pygame.init()
import cv2
res1 = (320,240)
res4 = (480, 320)
res2 = (640,480)
res3 = (1280,720)
res = res4
"""
camera = PiCamera()
camera.rotation = 180
camera.resolution = res3
camera.framerate = 30
camera.start_preview(fullscreen=False, window=(1000, 20, res[0], res[1]))
#camera.start_preview()
#rawCapture = PiRGBArray(camera, size=camera.resolution)
#time.sleep(0.1)
#cap = cv2.VideoCapture(-1)
#cv2.namedWindow('image', cv2.WINDOW_AUTOSIZE)
#cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
#cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
"""
"""
frameCounter = 0
currentID = 0   
faceTrackers = {}
start = time.time()
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    frame = frame.array
    #cv2.imshow("image", image)
    rawCapture.truncate(0)
    #print(frame.shape)
    #print(camera.framerate)
    
    frameCounter += 1
    if frameCounter % 1 == 0:
        grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(
            grey,
            scaleFactor = 1.1,
            minNeighbors = 5,
            minSize = (30, 30),                           
            flags = cv2.CASCADE_SCALE_IMAGE)
        
        for (x, y, w, h) in faces:
            center = (int(x+w*0.5), int(y+h*0.5))
            fidMatch = False
            #cv2.circle(frame, center, 3, (0, 255, 0))
            for fid in faceTrackers.keys():
                (tx, ty, tw, th, n, u) =  faceTrackers.get(fid)
                #cv2.circle(frame, (tx, ty), 3, (255, 0, 0))
                #cv2.circle(frame, (tx+w, ty+h), 3, (255, 0, 0))
                if tx <= center[0] <= tx+tw and ty <= center[1] <= ty+th:
                    if n < 50: n += 1
                    faceTrackers.update({fid:(x,y,w,h,n,True)})
                    fidMatch = True
                    break
            if not fidMatch:
                faceTrackers.update({currentID:(x,y,w,h,1,True)})
                currentID += 1
                
    
    fidsToDelete = []
    for fid in faceTrackers.keys():
        (tx, ty, tw, th, n, u) =  faceTrackers.get(fid)
        if not u: n -= 1
        if n < 1: fidsToDelete.append(fid)
        else:
            faceTrackers.update({fid:(tx,ty,tw,th,n,False)})
            #print(f"ID: {fid} n: {n}")
            if n < 25:
                cv2.rectangle(frame, (tx, ty), (tx+tw, ty+th), (0, 0, 255), 2)
            else:
                cv2.rectangle(frame, (tx, ty), (tx+tw, ty+th), (0, 255, 0), 2)
            
            cv2.putText(frame, f"{fid} : {n}", 
                            (tx, ty-3), 
                            cv2.FONT_HERSHEY_COMPLEX,
                            0.5, (255,255,255), 1)
    
    for fid in fidsToDelete:
        faceTrackers.pop(fid, None)
    
    cv2.imshow("image", frame)
    middle = time.time()
    print(middle-start)
    
    if cv2.waitKey(1) == ord('q'):
        break
cv2.destroyAllWindows()
exit(0)
"""

"""
while True:
    camera.capture(rawCapture, format="bgr")
    frame = rawCapture.array
    cv2.imshow("image", frame)
    rawCapture.truncate(0)
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.rotate(gray, cv2.ROTATE_180) 
    faces = faceCasc.detectMultiScale(
        gray,
        scaleFactor = 1.1,
        minNeighbors = 5,
        minSize = (30, 30),                             # test min size of faces
        flags = cv2.CASCADE_SCALE_IMAGE)
    
    
    if cv2.waitKey(1) == ord('q'):
        break

cv2.destroyAllWindows()
exit(0)
"""
#import cv2

faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

def main():
    cap = cv2.VideoCapture(-1)
    cv2.namedWindow('image', cv2.WINDOW_AUTOSIZE)
    #cap.set(cv2.CAP_PROP_FRAME_WIDTH, res[0])
    #cap.set(cv2.CAP_PROP_FRAME_HEIGHT, res[1])
    frameCounter = 0
    currentID = 0
    faceTrackers = {}
    #print(cap.get(cv2.CAP_PROP_FPS))
    #start = time.time()
    while True:
        ret, frame = cap.read()
        frame = cv2.rotate(frame, cv2.ROTATE_180)
        #frame = frame[0:320, 0:320]
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        #gray = cv2.rotate(gray, cv2.ROTATE_180)
        
        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor = 1.1,
            minNeighbors = 5,
            minSize = (10, 10),                         
            flags = cv2.CASCADE_SCALE_IMAGE)
        
        recSize = 0
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
        
        """
        camera.capture(rawCapture, format="bgr")
        frame = rawCapture.array
        rawCapture.truncate(0)
        #frame = cv2.rotate(frame, cv2.ROTATE_180)
        #print(frame.shape)
        frameCounter += 1
        if frameCounter % 1 == 0:
            grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = faceCascade.detectMultiScale(
                grey,
                scaleFactor = 1.1,
                minNeighbors = 5,
                minSize = (30, 30),                           
                flags = cv2.CASCADE_SCALE_IMAGE)
            for (x, y, w, h) in faces:
                center = (int(x+w*0.5), int(y+h*0.5))
                fidMatch = False
                #cv2.circle(frame, center, 3, (0, 255, 0))
                for fid in faceTrackers.keys():
                    (tx, ty, tw, th, n, u) =  faceTrackers.get(fid)
                    #cv2.circle(frame, (tx, ty), 3, (255, 0, 0))
                    #cv2.circle(frame, (tx+w, ty+h), 3, (255, 0, 0))
                    if tx <= center[0] <= tx+tw and ty <= center[1] <= ty+th:
                        if n < 50: n += 1
                        faceTrackers.update({fid:(x,y,w,h,n,True)})
                        fidMatch = True
                        break
                if not fidMatch:
                    faceTrackers.update({currentID:(x,y,w,h,1,True)})
                    currentID += 1
                    
        
        fidsToDelete = []
        for fid in faceTrackers.keys():
            (tx, ty, tw, th, n, u) =  faceTrackers.get(fid)
            if not u: n -= 1
            if n < 1: fidsToDelete.append(fid)
            else:
                faceTrackers.update({fid:(tx,ty,tw,th,n,False)})
                #print(f"ID: {fid} n: {n}")
                if n < 25:
                    cv2.rectangle(frame, (tx, ty), (tx+tw, ty+th), (0, 0, 255), 2)
                else:
                    cv2.rectangle(frame, (tx, ty), (tx+tw, ty+th), (0, 255, 0), 2)
                
                cv2.putText(frame, f"{fid} : {n}", 
                                (tx, ty-3), 
                                cv2.FONT_HERSHEY_COMPLEX,
                                0.5, (255,255,255), 1)
        
        for fid in fidsToDelete:
            faceTrackers.pop(fid, None)
        """
        cv2.imshow("image", frame)
        #now = time.time()
        #print(now-start)
        if cv2.waitKey(1) == ord('q'):
            break
    cap.release()    
    cv2.destroyAllWindows()
    exit(0)

if __name__ == '__main__':
    main()

