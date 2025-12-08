import os
import pickle
from uu import encode
import numpy as np
import cvzone
import cv2
import face_recognition
from importlib.metadata import files
from PIL.ImageChops import offset

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

from dotenv import load_dotenv
load_dotenv()

from supabase import create_client, Client

# Supabase credentials
SUPABASE_URL = "https://dbxilzmejnkfcvmbsbbx.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BUCKET_NAME = "faceAttendanceProject"   # replace with your bucket name

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL': "https://faceattendanceproject-e9b0d-default-rtdb.firebaseio.com/",
})


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

modeType = 0
counter = 0
id = -1

#RUNNING PROCESS
while True:
    success, img = cap.read() # initialize or read the camera

    imgS = cv2.resize(img,(0, 0),None, 0.25, 0.25) # side image resize
    imgS = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS) # initializing the face and logically thing for the right UI images
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame) #

    imgBackground[168:168 + 480, 80:80 + 640] = img # position of the camera
    imgBackground[30:30 + 673, 836:836 + 364] = imgModeList[modeType]

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
            y1, x2, y2, x1 = faceLoc # define to {bbox from cvzone}
            y1, x2, y2, x1 = y1*1, x2*1, y2*1, x1*1 # resize square face recognition
            bbox = 55+x1, 162+y1, x2 - x1, y2 - y1 # bounding box (convert to cvzone format)
            imgBackground = cvzone.cornerRect(imgBackground, bbox,rt=0)
            id = studentIds[matchIndex]

            if counter == 0:
                counter = 1
                modeType = 2
    if counter != 0:

        if counter == 1:
            studentInfo = db.reference(f'Students/{id}').get()
            print(studentInfo)

        cv2.putText(imgBackground, str(studentInfo['total_attendance']), (900,110),
                    cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),1)

        counter +=1

    # cv2.imshow("Webcam", img) #this just like a {consol.log} on jsFile
    cv2.imshow("Face Attendance", imgBackground) # background image
    cv2.waitKey(1)
