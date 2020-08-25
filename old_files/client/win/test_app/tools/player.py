import cv2 
import sys


playlist = sys.argv[1:]
window_name = 'Player'

for video in playlist:
	cap = cv2.VideoCapture(video)

	if cap.isOpened() == False:  
		print("Error opening video  file") 

	while cap.isOpened(): 
		ret, frame = cap.read()
		cv2.imshow(window_name, frame) 
	    # Press Q on keyboard to  exit or to move to next video
		if cv2.waitKey(25) & 0xFF == ord('q'): 
			break
		x, y, width, height = cv2.getWindowImageRect(window_name)
		if x == -1:
			sys.exit()
			
	cap.release() 
	cv2.destroyAllWindows() 
