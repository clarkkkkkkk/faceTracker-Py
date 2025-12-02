import os
import pickle
from uu import encode
import numpy as np
import cvzone
import cv2
import face_recognition
from importlib.metadata import files
from EncodeGenerator import encodeListKnownWithIds

cap = cv2.VideoCapture(0) # use the camera
cap.set(3, 640) #Video width Dimension
cap.set(4, 480) #Video height Dimension

# Read and resize the background image
imgBackground = cv2.imread("Resources/background.png") # accessing bg
imgBackground = cv2.resize(imgBackground, (1220, 720)) # bg - setting it size

# Importing the mode images into a list
folderModePath = 'Resources/Modes' # accessing file directory
modePathList = os.listdir(folderModePath) # purpose of "os.listdir" is to call inside the folder one by one

imgModeList = []
for path in modePathList:
    img = cv2.imread(os.path.join(folderModePath, path))

    img = cv2.resize(img, (364, 673))  # Resize the right corner image
    imgModeList.append(img)

# load the encoding file
print("Loading Encode File ...")
files = open('EncodeFile.p', 'rb')
encodeListKnownWithIds = pickle.load(files)
files.close()
encodeListKnown, studentIds = encodeListKnownWithIds
# print(studentIds, "Student Ids")
print("Encode File Loaded ...")


#RUNNING PROCESS
while True:
    success, img = cap.read() # initialize or read the camera

    imgS = cv2.resize(img,(0, 0),None, 0.25, 0.25) # side image resize
    imgS = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS) # initializing the face and logically thing for the right UI images
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame) #

    imgBackground[168:168 + 480, 80:80 + 640] = img # position of the camera
    imgBackground[30:30 + 673, 836:836 + 364] = imgModeList[2]

    for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
       # print("matches", matches)
       # print("faceDis", faceDis)

        matchIndex = np.argmin(faceDis)
        # print("Match Index", matchIndex)

        if matches[matchIndex]:
            print("Face Detected")
            print(studentIds[matchIndex]) # student ID (file name[match face])
            ########cvzone.cornerRect(imgBackground, bbox,rt=0)
        else:
            print("Nothing Detected")


    # cv2.imshow("Webcam", img) #this just like a {consol.log} on jsFile
    cv2.imshow("Face Attendance", imgBackground) # background image
    cv2.waitKey(1)

