import cv2


face_detector = cv2.CascadeClassifier(r'/home/dima/PycharmProjects/face_id_jetsonNano/app_faceId_jetsonNano/data/haarcascade_frontalface_default.xml')

def get_face(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_detector.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        print(w,h)
        if w >=250:
            cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)
    #
    cv2.imshow("sds", image)

import numpy as np
import cv2

cap = cv2.VideoCapture(0)


while(cap.isOpened()):
    ret, frame = cap.read()
    if ret==True:
        #frame = cv2.flip(frame,0)

        get_face(frame)
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

# Release everything if job is finished
cap.release()

cv2.destroyAllWindows()