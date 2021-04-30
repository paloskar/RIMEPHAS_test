import cv2
import math
import numpy as np

res1 = (320,240)
res2 = (640,480)
res3 = (1280,720)

res = res2

cap = cv2.VideoCapture(-1)
cv2.namedWindow('image', cv2.WINDOW_AUTOSIZE)
cv2.namedWindow('eyes', cv2.WINDOW_AUTOSIZE)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, res[0])
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, res[1])
faceCasc = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

WIDTH = res[0]/2
HEIGHT = res[1]/2
EYE_DEPTH = 2
hFOV = 62/2
vFOV = 49/2
ppcm = WIDTH*2/15.5

disp1 = 0
disp2 = 0
disp3 = 0
while True:
    res, frame = cap.read()
    frame = cv2.rotate(frame, cv2.ROTATE_180) 
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = faceCasc.detectMultiScale(
        gray,
        scaleFactor = 1.1,
        minNeighbors = 5,
        minSize = (10, 10),
        flags = cv2.CASCADE_SCALE_IMAGE)
    
    recSize = 0
    
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        if w > recSize:
            center = (int(x+w*0.5), int(y+h*0.5))
            recSize = w
        
            hAngle = (1 - center[0]/WIDTH) * hFOV
            vAngle = (1 - center[1]/HEIGHT) * vFOV
            
            c = -0.26*w+103
            
            # horizontal
            b = 4
            angleA = (90 - hAngle)*math.pi/180
            a = math.sqrt(b*b + c*c - 2*b*c*math.cos(angleA))
            angleC = math.acos((a*a + b*b - c*c)/(2*a*b))
            disp1 = (angleC - math.pi/2) * EYE_DEPTH * ppcm
            
            b_hat = 2*b
            c_hat = math.sqrt(a*a + b_hat*b_hat - 2*a*b_hat*math.cos(angleC))
            angleA_hat = math.acos((b_hat*b_hat + c_hat*c_hat - a*a)/(2*b_hat*c_hat))
            disp2 = (math.pi/2 - angleA_hat) * EYE_DEPTH * ppcm
            
            # vertical
            b = 6
            angleA = (90 - vAngle)*math.pi/180
            a = math.sqrt(b*b + c*c - 2*b*c*math.cos(angleA))
            angleC = math.acos((a*a + b*b - c*c)/(2*a*b))
            disp3 = (angleC - math.pi/2) * EYE_DEPTH * ppcm
               
    eyesimg = np.ones((480,800,3), np.uint8) * 255
    cv2.circle(eyesimg,(200,240),130,(0,0,0), 10)
    cv2.circle(eyesimg,(600,240),130,(0,0,0), 10)
    
    cv2.circle(eyesimg,(200+int(disp2),240-int(disp3)),25,(0,0,0), -1)
    cv2.circle(eyesimg,(600+int(disp1),240-int(disp3)),25,(0,0,0), -1)
    
    cv2.imshow("image", frame)
    cv2.imshow("eyes", eyesimg)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
exit(0)






"""
18cm

1: 80
2: 45
3: 28
"""