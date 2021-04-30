import cv2
from edgetpu.detection.engine import DetectionEngine
from PIL import Image
import time
import math

engine = DetectionEngine("ssd_mobilenet_v2_face_quant_postprocess_edgetpu.tflite")
#engine = DetectionEngine("face-detector-quantized_edgetpu.tflite")
cap = cv2.VideoCapture(-1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 960)
cv2.namedWindow('image', cv2.WINDOW_AUTOSIZE)
"""
cv2.namedWindow('imageL', cv2.WINDOW_AUTOSIZE)
cv2.namedWindow('imageR', cv2.WINDOW_AUTOSIZE)
cv2.namedWindow('imageBL', cv2.WINDOW_AUTOSIZE)
cv2.namedWindow('imageBR', cv2.WINDOW_AUTOSIZE)
"""
term = False

def frameCutout(frame, vOff, hOff, first, faceAtBoundary=False):
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
        #print(x, x2)
        w = x2-x
        h = y2-y
        
        if first and x2 > 320-3-5:
            faceAtBoundary = True
            w = h
        elif not first and faceAtBoundary and x < 2:
            print("skipping")
            continue
        
        x = x+hOff
        y = y+vOff
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
        #print(h/w)
        
    return frame, faceAtBoundary

start = time.time()
fps = 0
old = 0.

while not term:
    _, frame = cap.read()
    frame = cv2.rotate(frame, cv2.ROTATE_180)
    frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    faceAtBoundary = False
    frameRGB, faceAtBoundary = frameCutout(frameRGB, 400, 400, True)
    frameRGB, _ = frameCutout(frameRGB, 400, 720, False, faceAtBoundary)
    #frameRGB = frameCutout(frameRGB, 160, 0)
    #frameRGB = frameCutout(frameRGB, 160, 320)
    
    cv2.rectangle(frameRGB, (720, 400), (1040, 720), (0, 0, 255), 2)
    cv2.rectangle(frameRGB, (400, 400), (720, 720), (0, 0, 255), 2)
    cv2.imshow("image", cv2.resize(frameRGB,(640,480)))
    """
    cv2.imshow("imageL", frameL)
    cv2.imshow("imageR", frameR)
    cv2.imshow("imageBL", frameBL)
    cv2.imshow("imageBR", frameBR)
    """
    fps += 1
    now = time.time()
    tid = math.trunc(now-start)
    if tid != old:
        print(fps)
        fps = 0
    old = tid
    if cv2.waitKey(1) == ord('q'):
        break
cap.release()    
cv2.destroyAllWindows()
exit(0)

"""
frameL = frame[0:320, 0:320]
frameRGB = cv2.cvtColor(frameL, cv2.COLOR_BGR2RGB)
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
    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
    
frameR = frame[0:320, 320:640]
frameRGB = cv2.cvtColor(frameR, cv2.COLOR_BGR2RGB)
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
    x = x+320
    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
    
vOff = 480-320

frameBL = frame[vOff:480, 0:320]
frameRGB = cv2.cvtColor(frameBL, cv2.COLOR_BGR2RGB)
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
    y = y+vOff
    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)

frameBR = frame[vOff:480, 320:640]
frameRGB = cv2.cvtColor(frameBR, cv2.COLOR_BGR2RGB)
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
    x = x+320
    y = y+vOff
    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
"""
