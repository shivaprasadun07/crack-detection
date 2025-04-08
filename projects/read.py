import cv2 as cv 
import numpy as np

# img = cv.imread('projects/cat.jpg',0)
# img =cv.resize(img, (0, 0) ,fx=3,fy=2.75) 
# img =cv.rotate(img, cv.ROTATE_90_CLOCKWISE)

# cv.imshow('image',img)
# cv.waitKey(0)
# cv.destroyAllWindows()

cap = cv.VideoCapture(0)

      
while True:
      ret, frame =cap.read()

      # image = np.zeros(frame.shape,np.uint8)
      smaller_frame = cv.resize(frame,(0,0),fx=1,fy=1)

      cv.imshow('frame',smaller_frame)

      if cv.waitKey(1) == ord('b'):
            break
cap.release()
cv.destroyAllWindows()