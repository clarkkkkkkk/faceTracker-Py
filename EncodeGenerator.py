import cv2
import pickle
import face_recognition
import os

#import firebase_admin
#from firebase_admin import  credentials
#from firebase_admin import  db
#from firebase_admin storage

from supabase import create_client, Client

# Supabase credentials ------------------- to be continue this production
SUPABASE_URL = "https://dbxilzmejnkfcvmbsbbx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRieGlsem1lam5rZmN2bWJzYmJ4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ3NDY5MzgsImV4cCI6MjA4MDMyMjkzOH0.VbfvwBkenNJfoPxWP4pweDv1boxsXKhQwjWGUe6KzoA"
BUCKET_NAME = "faceAttendanceProject"   # replace with your bucket name

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


#cred = credentials.Certificate("serviceAccountKey.json")
#firebase_admin.initialize_app(cred,{
#    'databaseURL': "https://faceattendanceproject-e9b0d-default-rtdb.firebaseio.com/",
#    'storageBucket': "{give me a guide where i can find similar like this ->(link folder path of the storage from firebase for example)}",
#})

# Importing the students images
folderPath = 'Images'
pathList = os.listdir(folderPath) # purpose of "os.listdir" is to call inside the folder one by one
print(pathList) # to print the pathname inside in the "Images" folder

imgList = []
studentIds = []
for path in pathList:
    imgList.append(cv2.imread(os.path.join(folderPath,path)))
    studentIds.append(os.path.splitext(path)[0]) #to select the first array container name "(00123), .png"

    # SUPABASE UPLOAD CODE
    fileName = f'{folderPath}/{path}'

    with open(fileName, 'rb') as f:
        supabase.storage.from_(BUCKET_NAME).upload(
            path=f'Images/{path}',  # <--- folder path here
            file=f,
            file_options={"content-type": "image/jpeg"}
        )

    #fileName = f'{folderPath}/{path}'
    #bucket = storage.bucket()
    #blob = bucket.blob(fileName)
    #blob.upload_from_filename(fileName)

    # print(os.path.splitext(path)[0])
print(studentIds)

def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB) # translate the image from GRB to RGB to read on face_recognition library
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)

    return  encodeList

print("Encoding started")
encodeListKnown = findEncodings(imgList)
encodeListKnownWithIds = [encodeListKnown, studentIds]
print("Encoding completed")

file = open("EncodeFile.p", 'wb')
pickle.dump(encodeListKnownWithIds, file)
file.close()
print("File Saved")

