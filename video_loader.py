import pims #initialize pims 
import matplotlib.pyplot as plt
#from PIL import Image


# v = pims.open("C:/Users/Tchakamau/Desktop/Soft Matter/drop.avi") #might not be the same as with pims.Video(fiename) # read in a video file 
filename = input("What is the path to the file?\n")
Vid = pims.open(filename)
print(5)
Len = len(Vid) #optional
print(Len)
for i in Vid: #iterate over frames #was: range(0, len(V)):

	plt.imshow(i)

Vid
print(2)
	
"""
get filename
open video 
get num of frames # optional; might be nevessary for the loop
loop over all frames
display the frame #open it in a program, or what?
"""
