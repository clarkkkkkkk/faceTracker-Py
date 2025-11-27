import os

import cv2

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

#RUNNING PROCESS
while True:
    success, img = cap.read() # initialize or read the camera

    imgBackground[168:168 + 480, 80:80 + 640] = img # position of the camera
    imgBackground[30:30 + 673, 836:836 + 364] = imgModeList[3]

    # cv2.imshow("Webcam", img) #this just like a {consol.log} on jsFile
    cv2.imshow("Face Attendance", imgBackground) # background image
    cv2.waitKey(1)