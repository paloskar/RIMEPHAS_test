import cv2
import time

faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

def main():
    cap = cv2.VideoCapture(-1)
    cv2.namedWindow('image', cv2.WINDOW_AUTOSIZE)
    #cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
    #cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)
    frameCounter = 0
    currentID = 0   
    faceTrackers = {}
    print(cap.get(cv2.CAP_PROP_FPS))
    start = time.time()
    while True:
        ret, frame = cap.read()
        frame = cv2.rotate(frame, cv2.ROTATE_180)
        #print(frame.shape)
        """
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
                    
        trackID = -1
        fidsToDelete = []
        for fid in faceTrackers.keys():
            (tx, ty, tw, th, n, u) =  faceTrackers.get(fid)
            if not u: n -= 1
            if n < 1: fidsToDelete.append(fid)
            else:
                faceTrackers.update({fid:(tx,ty,tw,th,n,False)})
                if n < 25:
                    cv2.rectangle(frame, (tx, ty), (tx+tw, ty+th), (0, 0, 255), 2)
                else:
                    cv2.rectangle(frame, (tx, ty), (tx+tw, ty+th), (0, 255, 0), 2)
                    trackID = fid
                cv2.putText(frame, f"{fid} : {n}", 
                                (tx, ty-3), 
                                cv2.FONT_HERSHEY_COMPLEX,
                                0.5, (255,255,255), 1)
        
        for fid in fidsToDelete:
            faceTrackers.pop(fid, None)
        
        if trackID != -1:
            # determine who to track
            (x, y, w, h, n, u) = faceTrackers.get(trackID)
            center = (int(x+w*0.5), int(y+h*0.5))

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
        """
        cv2.imshow("image", frame)
        #middle = time.time()
        #print(middle-start)
        if cv2.waitKey(1) == ord('q'):
            break
        
    cv2.destroyAllWindows()
    exit(0)

if __name__ == '__main__':
    main()
    
"""
def faceTracking(center):
    faceCasc = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    videoCap = cv2.VideoCapture(-1)
    videoCap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    videoCap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
    start = time.time()
    while True:
        ret, frame = videoCap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.rotate(gray, cv2.ROTATE_180) 
        faces = faceCasc.detectMultiScale(
            gray,
            scaleFactor = 1.1,
            minNeighbors = 5,
            minSize = (30, 30),                             # test min size of faces
            flags = cv2.CASCADE_SCALE_IMAGE)
        
        recSize = 0
        for (x, y, w, h) in faces:
            if w > recSize:
                center = (int(x+w*0.5), int(y+h*0.5))          # should only change center at the end
                recSize = w
        print(center[:])
        middle = time.time()
        print(middle-start)
    videoCap.release()


def faceTrackingPi():
    global center
    faceCasc = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    res1 = (320,240)
    res2 = (640,480)
    res3 = (1280,720)

    camera = PiCamera()
    camera.rotation = 180
    camera.resolution = res1
    camera.framerate = 30
    print("started")
    rawCapture = PiRGBArray(camera, size=camera.resolution)
    start = time.time()
    
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        frame = frame.array
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = faceCasc.detectMultiScale(
            gray,
            scaleFactor = 1.1,
            minNeighbors = 5,
            minSize = (30, 30),                             # test min size of faces
            flags = cv2.CASCADE_SCALE_IMAGE)
        
        recSize = 0
        for (x, y, w, h) in faces:
            if w > recSize:
                center = (int(x+w*0.5), int(y+h*0.5))      # should only change center at the end
                recSize = w
        rawCapture.truncate(0)
        middle = time.time()
        print(middle-start)
"""
