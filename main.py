import os
import pickle
from datetime import datetime
from uu import encode
import numpy as np
import cvzone
import cv2
import face_recognition
from importlib.metadata import files
from PIL.ImageChops import offset
import numpy as np
from datetime import datetime

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

storage = supabase.storage

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
imgStudent = []

#RUNNING PROCESS
while True:
    success, img = cap.read() # initialize or read the camera

    imgS = cv2.resize(img,(0, 0),None, 0.25, 0.25) # side image resize
    imgS = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS) # initializing the face and logically thing for the right UI images
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame) #

    imgBackground[168:168 + 480, 80:80 + 640] = img # position of the camera
    imgBackground[30:30 + 673, 836:836 + 364] = imgModeList[modeType]

    if faceCurFrame:

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
                #Get data
                studentInfo = db.reference(f'Students/{id}').get()
                print(studentInfo)

                #Get data Image from the Supabase Storage
                result = supabase.storage.from_(BUCKET_NAME).download(f'Images/{id}.jpg')

                if result:
                    array = np.frombuffer(result, np.uint8)
                    imgStudent = cv2.imdecode(array, cv2.IMREAD_COLOR)
                    imgStudent = cv2.resize(imgStudent, (280, 214)) #Size of the small picture right panel

                # Updating data of attendance from Firebase - Database
                datetimeObject = datetime.strptime(studentInfo['last_attendance_time'],
                                                   "%Y-%m-%d %H:%M:%S")

                secondsElapsed = (datetime.now()-datetimeObject).total_seconds() #Current date and time minus to dateTimeObject
                print(secondsElapsed) #for testing

                if secondsElapsed > 30: # 30 seconds
                    ref = db.reference(f'Students/{id}')
                    studentInfo['total_attendance'] += 1
                    ref.child('total_attendance').set(studentInfo['total_attendance'])
                    ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) #(ref.child) is calling function from firebase, (.set) is a function to import
                else:
                    modeType = 1
                    counter = 0
                    imgBackground[30:30 + 673, 836:836 + 364] = imgModeList[modeType]  # This shows the users face is already "ALREADY MARKED"

            if modeType != 1:


                if 10<counter<20: #if counter is within 10 to 20, is true. Otherwise, false.
                    modeType = 3
                    imgBackground[30:30 + 673, 836:836 + 364] = imgModeList[modeType] # This shows if the users face is already "MARKED"

                if counter <= 10:
                    cv2.putText(imgBackground, str(studentInfo['total_attendance']), (900,110),
                                cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),1)
                    cv2.putText(imgBackground, str(studentInfo['major']), (1000,535),
                                cv2.FONT_HERSHEY_COMPLEX,0.5,(255,255,255),1)
                    cv2.putText(imgBackground, str(id), (1000,482),
                                cv2.FONT_HERSHEY_COMPLEX,0.5,(255,255,255),1)
                    cv2.putText(imgBackground, str(studentInfo['starting_year']), (1105,642),
                                cv2.FONT_HERSHEY_COMPLEX,0.5,(0,0,0),1)
                    cv2.putText(imgBackground, str(studentInfo['standing']), (1010,642),
                                cv2.FONT_HERSHEY_COMPLEX,0.5,(0,0,0),1)
                    cv2.putText(imgBackground, str(studentInfo['year']), (930,642),
                                cv2.FONT_HERSHEY_COMPLEX,0.5,(0,0,0),1)

                    (w,h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 2)
                    offset = (370-w)//2 # this 2 line of code is to off centre the text {name}
                    cv2.putText(imgBackground, str(studentInfo['name']), (830+offset,440),
                                cv2.FONT_HERSHEY_COMPLEX,1,(0,0,0),1)

                    imgBackground[178:178+214, 878:878+280] = imgStudent

                counter +=1

                if counter >= 20:
                    counter = 0
                    modeType = 0
                    studentInfo = []
                    imgStudent = [] #reset student value information
                    imgBackground[30:30 + 673, 836:836 + 364] = imgModeList[modeType] # This shows the users face is already "ACTIVE"
    else:
        modeType = 0
        counter = 0

    # cv2.imshow("Webcam", img) #this just like a {consol.log} on jsFile
    cv2.imshow("Face Attendance", imgBackground) # background image
    cv2.waitKey(1)
