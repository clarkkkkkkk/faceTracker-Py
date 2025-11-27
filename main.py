import cv2

cap = cv2.VideoCapture(0) # use the camera
cap.set(3, 640) #Video width Dimension
cap.set(4, 480) #Video height Dimension

# Read and resize the background image
imgBackground = cv2.imread("Resources/background.png")
imgBackground = cv2.resize(imgBackground, (1220, 720))

while True:
    success, img = cap.read()

    imgBackground[168:168 + 480, 80:80 + 640] = img

    cv2.imshow("Webcam", img) #this just like a {consol.log} on jsFile
    cv2.imshow("Face Attendance", imgBackground)
    cv2.waitKey(1)