import cv2
import pickle
import face_recognition
import os

# Importing the students images
folderPath = 'Images'
pathList = os.listdir(folderPath) # purpose of "os.listdir" is to call inside the folder one by one
print(pathList) # to print the pathname inside in the "Images" folder

imgList = []
studentIds = []
for path in pathList:
    imgList.append(cv2.imread(os.path.join(folderPath,path)))
    studentIds.append(os.path.splitext(path)[0]) #to select the first array container name "(00123), .png"
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

