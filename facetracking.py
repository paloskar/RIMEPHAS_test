from edgetpu.detection.engine import DetectionEngine
from PIL import Image
import cv2
import pygame
import time
import math

def wholeFrame(engine, currentID, faceTrackers, peopleCount, frame):
    framePIL = Image.fromarray(frame)
    faces = engine.detect_with_image(framePIL,
                                     threshold=0.05,
                                     keep_aspect_ratio=True,
                                     relative_coord=False,
                                     top_k=10,
                                     resample=4)
    for face in faces:
        (x, y, x2, y2) = (int(i) for i in face.bounding_box.flatten().tolist())
        w = x2-x
        h = y2-y
        center = (int(x+w*0.5), int(y+h*0.5))
        fidMatch = False
        for fid in faceTrackers.keys():
            (tx, ty, tw, th, n, u, c) =  faceTrackers.get(fid)
            if not u and tx <= center[0] <= tx+tw and ty <= center[1] <= ty+th:
                if n < 50: n += 1
                if n >= 35 and c == False:
                    c = True
                    peopleCount += 1                        
                faceTrackers.update({fid:(x,y,w,h,n,True,c)})
                fidMatch = True
                break
        if not fidMatch:
            faceTrackers.update({currentID:(x,y,w,h,1,True,False)})
            currentID += 1
            print("ID: ", currentID)
 
    return currentID, faceTrackers, peopleCount

def frameCutout(engine, currentID, faceTrackers, peopleCount, frame, vOff, hOff, faceAtBoundary = False):
    frameRGB = frame[vOff:320+vOff, hOff:320+hOff]
    framePIL = Image.fromarray(frameRGB)
    faces = engine.detect_with_image(framePIL,
                                     threshold=0.05,
                                     keep_aspect_ratio=True,
                                     relative_coord=False,
                                     top_k=10,
                                     resample=4)
    for face in faces:
        (x, y, x2, y2) = (int(i) for i in face.bounding_box.flatten().tolist())
        w = x2-x
        h = y2-y

        if not hOff and x2 > 320-3:
            faceAtBoundary = True
            w = h
        elif hOff and faceAtBoundary and x < 2:
            continue
            #x = x-h/2
            #w = h
        
        x = x+hOff
        y = y+vOff
        center = (int(x+w*0.5), int(y+h*0.5))
        fidMatch = False
        for fid in faceTrackers.keys():
            (tx, ty, tw, th, n, u, c) =  faceTrackers.get(fid)
            print("x: ", tx-tw, center[0], tx+tw+tw)
            print("y: ", ty-th, center[1], ty+th+th)
            if not u and tx-tw <= center[0] <= tx+tw+tw and ty-th <= center[1] <= ty+th+th:
                if n < 50: n += 1
                if n >= 35 and c == False:
                    c = True
                    peopleCount += 1                        
                faceTrackers.update({fid:(x,y,w,h,n,True,c)})
                fidMatch = True
                break
        if not fidMatch:
            faceTrackers.update({currentID:(x,y,w,h,1,True,False)})
            currentID += 1
            print("ID: ", currentID)
        
    return currentID, faceTrackers, peopleCount, faceAtBoundary

########## Function for tracking faces - running in seperate process ##########
def faceTracking(sender):
    engine = DetectionEngine("ssd_mobilenet_v2_face_quant_postprocess_edgetpu.tflite")
    cap = cv2.VideoCapture(-1)
    currentID = 1   
    faceTrackers = {}
    term = False
    peopleCount = 0
    # change behaviour after interaction started to do eye gaze. pipe. if var = True change resolution.
    #cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    #cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 960)
    counter = 0
    start = time.time()
    fps = 0
    old = 0.
    split = True
    while not term:
        _, frame = cap.read()
        frame = cv2.rotate(frame, cv2.ROTATE_180)
        frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        #print("frame ", len(frame))
        #frameRGB = cv2.resize(frameRGB, (640, 480))
        
        currentID, faceTrackers, peopleCount = wholeFrame(engine, currentID, faceTrackers, peopleCount, frameRGB)
        """
        if sender.poll():
            (term, split) = sender.recv()
        if not split:
            print("Looking at close")
            frameRGB = cv2.resize(frameRGB, (640,480))
            #frameRGB = frameRGB[100:480+100, int((1280-640)/2):int(640+(1280-640)/2)]
            currentID, faceTrackers, peopleCount = wholeFrame(engine, currentID, faceTrackers, peopleCount, frameRGB)
        else:
            print("Looking at far")
            faceAtBoundary = False
            currentID, faceTrackers, peopleCount, faceAtBoundary = frameCutout(engine, currentID, faceTrackers, peopleCount, frameRGB, 400, 400)
            currentID, faceTrackers, peopleCount, _ = frameCutout(engine, currentID, faceTrackers, peopleCount, frameRGB, 400, 720, faceAtBoundary)
        """
        """
        if not faceTrackers:
            print("looking far")
            faceAtBoundary = False
            currentID, faceTrackers, peopleCount, faceAtBoundary = frameCutout(engine, currentID, faceTrackers, peopleCount, frameRGB, 400, 400)
            currentID, faceTrackers, peopleCount, _ = frameCutout(engine, currentID, faceTrackers, peopleCount, frameRGB, 400, 720, faceAtBoundary)
        else:
            print("looking close")
        #frameRGB, currentID, faceTrackers, peopleCount = frameCutout(engine, currentID, faceTrackers, peopleCount, frameRGB, 160, 0)
        #frameRGB, currentID, faceTrackers, peopleCount = frameCutout(engine, currentID, faceTrackers, peopleCount, frameRGB, 160, 320)
        """
        fidsToDelete = []
        for fid in faceTrackers.keys():
            (tx, ty, tw, th, n, u, c) =  faceTrackers.get(fid)
            if not u:
                # if center is close to frame edge then decay faster
                #if res[0]-tw-20 < tx < 20:
                    #n-=5
                n -= 1
            if n < 1: fidsToDelete.append(fid)
            else:
                faceTrackers.update({fid:(tx,ty,tw,th,n,False,c)})

        for fid in fidsToDelete:
            faceTrackers.pop(fid, None)   
        sender.send((faceTrackers, peopleCount, frameRGB))       
        if sender.poll():  
            term = sender.recv()
        #pygame.time.Clock().tick(100)
        
        fps += 1
        now = time.time()
        tid = math.trunc(now-start)
        if tid != old:
            #print(fps)
            fps = 0
        old = tid
    print("Closing facetracking")    
    cap.release()
    
"""    
def faceTracking(sender):
    engine = DetectionEngine("ssd_mobilenet_v2_face_quant_postprocess_edgetpu.tflite")
    cap = cv2.VideoCapture(-1)
    currentID = 1   
    faceTrackers = {}
    term = False
    peopleCount = 0
    while not term:
        _, frame = cap.read()
        frame = cv2.rotate(frame, cv2.ROTATE_180)
        #frame = frame[0:320, 0:320]
        frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        framePIL = Image.fromarray(frameRGB)
        faces = engine.detect_with_image(framePIL,
                                         threshold=0.05,
                                         keep_aspect_ratio=True,
                                         relative_coord=False,
                                         top_k=10,
                                         resample=4)
        for face in faces:
            (x, y, x2, y2) = (int(i) for i in face.bounding_box.flatten().tolist())
            w = x2-x
            h = y2-y
            center = (int(x+w*0.5), int(y+h*0.5))
            fidMatch = False
            for fid in faceTrackers.keys():
                (tx, ty, tw, th, n, u, c) =  faceTrackers.get(fid)
                if tx <= center[0] <= tx+tw and ty <= center[1] <= ty+th:
                    if n < 50: n += 1
                    if n >= 35 and c == False:
                        c = True
                        peopleCount += 1                        
                    faceTrackers.update({fid:(x,y,w,h,n,True,c)})
                    fidMatch = True
                    break
            if not fidMatch:
                faceTrackers.update({currentID:(x,y,w,h,1,True,False)})
                currentID += 1
                print("ID: ", currentID)
        
        fidsToDelete = []
        for fid in faceTrackers.keys():
            (tx, ty, tw, th, n, u, c) =  faceTrackers.get(fid)
            if not u:
                # if center is close to frame edge then decay faster
                #if res[0]-tw-20 < tx < 20:
                    #n-=5
                n -= 1
            if n < 1: fidsToDelete.append(fid)
            else:
                faceTrackers.update({fid:(tx,ty,tw,th,n,False,c)})

        for fid in fidsToDelete:
            faceTrackers.pop(fid, None)   
        sender.send((faceTrackers, peopleCount, frameRGB))       
        if sender.poll():  
            term = sender.recv()
        pygame.time.Clock().tick(100)
        
    cap.release()
"""
class Snapshot():
    def __init__(self):
        self.engine = DetectionEngine("ssd_mobilenet_v2_face_quant_postprocess_edgetpu.tflite")
        #self.cap = cv2.VideoCapture(-1)
    
    def take(self):
        cap = cv2.VideoCapture(-1)
        _, frame = cap.read()
        frame = cv2.rotate(frame, cv2.ROTATE_180)
        frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        framePIL = Image.fromarray(frameRGB)
        faces = self.engine.detect_with_image(framePIL,
                                         threshold=0.05,
                                         keep_aspect_ratio=True,
                                         relative_coord=False,
                                         top_k=10,
                                         resample=4)
        widest = 0
        (a, b, c, d) = (0, 0, 0, 0)
        for face in faces:
            (x, y, x2, y2) = (int(i) for i in face.bounding_box.flatten().tolist())
            h = y2-y
            w = x2-x
            if w > widest:
                (a, b, c, d) = (x, y, h, w)
        print(a,b,c,d)
        return frameRGB, a, b, c, d
    
    