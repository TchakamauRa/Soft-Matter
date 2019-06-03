#!/usr/bin/env python
# coding: utf-8

# In[223]:


#import av
import numpy as np
#import trackpy
#import matplotlib #for making plots inside the notebook 
import matplotlib.pyplot as plt #for maknig plots inside the notebook
import skimage
import skvideo.io


"""Currently works on a single frame. Later, will add a loop that can work on all frames."""


# In[224]:


#filename = input("What is the path to the file?\n")
filename = "C:/Users/Tchakamau/Desktop/Soft Matter/tchakamau/New_setup/45681_10Vpp_25.avi"


# In[225]:


Vid = skvideo.io.vread(filename)

fig, ax = plt.subplots(ncols=2)
ax[0].imshow(Vid[0]) # first fame of video
ax[1].imshow(Vid[-1]) #last frame of video


# In[226]:


"""Testing that the frames loaded correctly. They should be 2D matrices, in order to be used by sci-kit image programs. 
Shape of the frame colletion should hve 3 values, and shape of each frame should have 2 values.
Checking that a frame is legible as an image by displaying it."""
green = Vid[:, :, :, 2]
print(green.shape)
plt.imshow(green[500], cmap='Greys_r')

plt.hist(green[500].flatten(), bins=256, range=(0, 256))
plt.show()


# In[227]:


"""
First, we'll binarize the whole image for each frame
then find connected components and filter out all but the largest
then, for each frame, see if the largest CC has the right no. of particles (by area sounds good)
if not, then delete that frame from the list

With the resulting list, binarize agian with a diffeent threshold, to eep the transparent one out,
find connected compoents again and take the largest, 
and this time for each frame, see what shape it contains 
    keep a list of frame shapes, 
    including a shape that represents transitioning states, e.g. none-of-the-above.
"""


# In[228]:


"""All the work below is done on a single frame 
    Will be applied over all frames eventually"""


# In[229]:


"""Pt1. 
    Binarize image, 
    and then find conected components
    and then filter those for only the largest
"""


# In[230]:


"Tryign built-in thresholds for separating image and background"
from skimage.filters import try_all_threshold

img = green[906] #example image (9606 is an error!)

fig, ax = try_all_threshold(img, figsize=(10, 10), verbose=False)
#plt.show()


# In[231]:


"""Pt2. 
    Filter shapes with wrong number of balls 
        Do using area maybe
"""


# In[232]:


"Getting test frames"
test_frames = []
b_r_frames = []
b_l_frames = []
t_r_frames = []
t_l_frames = []
few_frames = []
b_m_frames = []
broken_frames = []
odd_s_frames = []

phantom_indices = {10772 : "b_r", 11130 : "broken", 11578 : "broken", 11918 : "t_r", 
                   12062 : "broken", 12133 : "b_m", 12635 : "t_r", 18009 : "b_m", 
                   21377 : "broken", 22093 : "b_l", 23813 : "b_l", 16719 : "t_l", 26394 : "4.5", 10912 : "b_r", 
                   26388 : "4.5", 26393 : "4.5", 26389 : "b_l", 26390 : "b_l", 26391 : "b_l", 26387 : "4.5", 
                   26380 : "b_l", 26379 : "4.5", 26381 : "b_l", 26383 : "4.5", 24673 : "broken", 17292 : "t_l", 
                   17289 : "t_l", 17288 : "broken", 17271 : "odd_s", 17248 : "t_l", 17249 : "4.5", 17711 : "t_r",
                   17579 : "t_r", 16766 : "odd_s", 16757 : "odd_s", 16725 : "4.5", 16333 : "odd_s", 15674 : "odd_s", 
                   15666 : "odd_s", 11990 : "odd_s", 11973 : "odd_s", 11658 : "odd_s", 10836 : "b_r", 10872 : "b_r",
                   10958 : "b_r"}
phantom_frames = {}
framesets = [b_r_frames, b_l_frames, b_m_frames, t_r_frames, t_l_frames, broken_frames, few_frames, odd_s_frames]
framesetnames = ["b_r", "b_l", "b_m", "t_r", "t_l", "broken", "few", "odd_s"]
trigger_frame = 26894 

for i in range(len(framesets)):
    if framesetnames[i] == "few":
        few_frames.extend([[green[trigger_frame - x], x] for x in phantom_indices.keys() if phantom_indices.get(x) in ["4", "4.5"]])
    else:
        framesets[i].extend([[green[trigger_frame - x], x] for x in phantom_indices.keys() if phantom_indices.get(x) == framesetnames[i]])

print(few_frames)


from skimage import measure
from skimage.filters import threshold_isodata, threshold_yen


# In[233]:


"Retreving properties for test frames with 1st hreshold"

# applies yen filter to test frames, and gets properties
# returns list of the properties
def opaque_threshold_properties(framelist):
    filtrate = []
    for framepair in framelist:
        frame = framepair[0] 
        thresh_img = frame > threshold_yen(frame) # binary image
        img_labelled = measure.label(thresh_img) # contains connected regions
        properties_list = measure.regionprops(img_labelled) # data about regions, for each connected region
        
        #----------getting maximum connected region----------
        biggest_r = properties_list[0] 
        
        for region in properties_list:
            if region.area > biggest_r.area:
                biggest_r = region
            else:
                pass
            
        filtrate.append([biggest_r, framepair[1]])#, total_threshed]) # area, frame index in phantom, binary image
    return filtrate


# In[234]:


"""Determining the area of the object"""
for i in range(0, len(framesets)):
    i_props = opaque_threshold_properties(framesets[i])
    print(framesetnames[i] + " areas :", [[i[0].area, i[1]] for i in i_props])

#with 5 spheres, area is over 1800, even with one bent out of plane; with 4 spheres it's  below 1700


# In[235]:


"""Broken objects are filtered out by their area and we then move on to identifying odd shaped objects 
    from the remaining frames"""
framesets.remove(broken_frames)
framesetnames.remove("broken")


# In[236]:


"""Srepaating out odd_shaped frames)"""
for i in range(0, len(framesets)):
    i_props = opaque_threshold_properties(framesets[i])
    print(framesetnames[i] + " inertia tensors: ", [[i[0].inertia_tensor[0, 0] + i[0].inertia_tensor[1,1], i[1]] for i in i_props])
print("\n\n")

for i in range(0, len(framesets)):
    i_props = opaque_threshold_properties(framesets[i])
    print(framesetnames[i] + " convex_areas : ", [[i[0].convex_area, i[1]] for i in i_props])
print("\n\n")


for i in range(0, len(framesets)):
    i_props = opaque_threshold_properties(framesets[i])
    print(framesetnames[i] + " major_axis_length : ", [[i[0].major_axis_length, i[1]] for i in i_props])
print("\n\n")

for i in range(0, len(framesets)):
    i_props = opaque_threshold_properties(framesets[i])
    print(framesetnames[i] + " minor_axis_length : ", [[i[0].minor_axis_length, i[1]] for i in i_props])
print("\n\n")


# In[237]:


"""Pt3. Separating variosu shapes
"""


# In[238]:


"""odd_shaped objects are filtered out by their area and we then move on to identifying the various shapes 
    in the remaining frames.
    Few are temporarily removed for comparison purposes;will be put back in in a new frameset"""
framesets.remove(odd_s_frames)
framesets.remove(few_frames)
framesetnames.remove("odd_s")
framesetnames.remove("few")


# In[239]:


"Retreving properties for test frames with 2nd threshold"

# applies isodata filter to test frames, and gets properties
# returns list of the properties
def transparent_threshold_properties(framelist):
    filtrate = []
    for framepair in framelist:
        frame = framepair[0] 
        thresh_img = frame > threshold_isodata(frame) # binary image
        img_labelled = measure.label(thresh_img) # contains connected regions
        properties_list = measure.regionprops(img_labelled) # data about regions, for each connected region
        
        #----------getting maximum connected region----------
        biggest_r_p = properties_list[0] 
        
        for region_props in properties_list:
            region = img_labelled
            if region_props.area > biggest_r_p.area:
                biggest_r_p = region_props
            else:
                pass
            
        filtrate.append([biggest_r_p, framepair[1], img_labelled])#, total_threshed]) # area, frame index in phantom, binary image
    return filtrate


# In[240]:


"Testing the new filter  - all areas should be the same, for one"

# the first function should probably produce the output for the 3rd slot in my thresholding function

# get and print areas, AND print test frames
for i in range(0, len(framesets)):
    i_props = transparent_threshold_properties(framesets[i])
    print(framesetnames[i] + " areas : ", [[i[0].area, i[1]] for i in i_props])
    fig, ax = plt.subplots(ncols=len(framesets[i]), figsize = (14, 10))
    for i in range(len(framesets[i])):
        ax[i].imshow(i_props[i][2])
print("\n\n")


# In[170]:


"""Getting properties to separate frames by shape"""
for i in range(0, len(framesets)):
    i_props = transparent_threshold_properties(framesets[i])
    print(framesetnames[i] + " inertia tensors: ", [[i[0].inertia_tensor[0, 0] + i[0].inertia_tensor[1,1], i[1]] for i in i_props])
print("\n\n")

for i in range(0, len(framesets)):
    i_props = transparent_threshold_properties(framesets[i])
    print(framesetnames[i] + " perimeters : ", [[i[0].perimeter, i[1]] for i in i_props])
print("\n\n")

for i in range(0, len(framesets)):
    i_props = transparent_threshold_properties(framesets[i])
    print(framesetnames[i] + " extents : ", [[i[0].extent, i[1]] for i in i_props])
print("\n\n")


# In[ ]:


"""Separating the frames which are similar otherwise by use of coordinate systems"""


# In[222]:


def region_selector(labeled_image, label):
    #print(label)
    x = labeled_image == label
    #plt.imshow(x)
    return x

# make a function that takes a set of labeled regions, and then  returns a boolean array containing only the largest
def largest_region_extractor(labeled_regions_set):
    props_lists = measure.regionprops(labeled_regions_set)
    #print(len(labeled_regions_set), len(props_lists))
    biggest_r_p = props_lists[0]
    for i in range(0, len(props_lists)):
        pli = props_lists[i]
        if pli.area > biggest_r_p.area:
            biggest_r_p = pli
            biggest_r_label = pli.label
        else:
            pass
    return region_selector(labeled_regions_set, biggest_r_label)

#xor the results of both filters
i_threshed  = green[506] > threshold_isodata(green[506])
y_threshed  = green[506] > threshold_yen(green[506])
full = largest_region_extractor(measure.label(y_threshed))
four = largest_region_extractor(measure.label(i_threshed))
one_and_some = full^four
one = largest_region_extractor(measure.label(one_and_some))

fig, ax = plt.subplots(ncols = 2)
ax[0].imshow(one_and_some)
ax[1].imshow(one)
print(one_and_some)
print(one)
plt.show()


# In[ ]:





# In[ ]:


"New frames, as few need  to be given their shapes"

phantom_indices = {10772 : "b_r", 11130 : "broken", 11578 : "broken", 11918 : "t_r", 
                   12062 : "broken", 12133 : "b_m", 12635 : "t_r", 18009 : "b_m", 
                   21377 : "broken", 22093 : "b_l", 23813 : "b_l", 16719 : "t_l", 26394 : "4.5", 10912 : "b_r", 
                   26388 : "4.5", 26393 : "4.5", 26389 : "b_l", 26390 : "b_l", 26391 : "b_l", 26387 : "4.5", 
                   26380 : "b_l", 26379 : "4.5", 26381 : "b_l", 26383 : "4.5", 24673 : "broken", 17292 : "t_l", 
                   17289 : "t_l", 17288 : "broken", 17271 : "odd_s", 17248 : "t_l", 17249 : "4.5", 17711 : "t_r",
                   17579 : "t_r", 16766 : "odd_s", 16757 : "odd_s", 16725 : "4.5", 16333 : "odd_s", 15674 : "odd_s", 
                   15666 : "odd_s", 11990 : "odd_s", 11973 : "odd_s", 11658 : "odd_s", 10836 : "b_r", 10872 : "b_r",
                   10958 : "b_r"}

test_frames.extend([[green[trigger_frame - phantom_index], phantom_index] for phantom_index in phantom_indices.keys()])
b_r_frames.extend([[green[trigger_frame - x], x] for x in phantom_indices.keys() if phantom_indices.get(x) == "b_r" ])
b_l_frames.extend([[green[trigger_frame - x], x] for x in phantom_indices.keys() if phantom_indices.get(x) == "b_l" ])
t_r_frames.extend([[green[trigger_frame - x], x] for x in phantom_indices.keys() if phantom_indices.get(x) == "t_r" ])
t_l_frames.extend([[green[trigger_frame - x], x] for x in phantom_indices.keys() if phantom_indices.get(x) == "t_l" ])
b_m_frames.extend([[green[trigger_frame - x], x] for x in phantom_indices.keys() if phantom_indices.get(x) == "b_m" ])
print(b_r_frames)


framesets = [b_r_frames, b_l_frames, t_r_frames, t_l_frames, b_m_frames]
framesetnames = ["b_r", "b_l", "t_r", "t_l", "b_m"]


# In[ ]:




