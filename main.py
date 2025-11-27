import cv2

cap = cv2.VideoCapture(0) # use the camera
cap.set(3, 640) #Video width Dimension
cap.set(4, 480) #Video heigh Dimension

# Read and resize the background image
imgBackground = cv2.imread("Resources/background.png")

while True:
    success, img = cap.read()
    cv2.imshow("Webcam", img)
    cv2.imshow("Face Attendance", imgBackground)
    cv2.waitKey(1)