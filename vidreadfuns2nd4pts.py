"""Imports"""
from __future__ import print_function, division
import matplotlib.pyplot as plt #for maknig plots inside the notebook
import skimage
import skvideo.io
from skvideo.io import vreader, ffprobe
from skimage import measure, morphology, feature
from skimage.filters import *
from skimage.morphology import *
from operator import attrgetter
import numpy as np
import math
from itertools import chain
#from functools import partial, update_wrapper
from scipy import ndimage 
from pims import pipeline, Video
from glob import glob
import seaborn as sns
from collections import OrderedDict 
#import antigravity


"""Functions"""
# apply total thresholding to each of a list of frames; filter slides with wrong number

def total_threshold_filter(frame, frame_no, transition_threshold, class_thresh,
                           broken_count, class_num, origin, last_class, last_whole, filtrate_len, 
                           sides, classes, transitions): 
    
   
    
   # ---setup image and detect blobs ----------------
    thresh_img = frame > threshold_isodata(frame)# binary image
    highlight = morphology.opening(thresh_img, square(7))
    img = np.copy(frame)
    img[highlight==0] = 0
    blobs =skimage.feature.blob_doh(img, min_sigma = 6, max_sigma = 16, threshold = 0.007, num_sigma= 15, overlap=0.8)

    num_connections = 0

    blobs = sorted(blobs, key = third_item, reverse=True)
    num_blobs = len(blobs)
    if num_blobs > 0:
        max_blob = blobs[0]
        connect_dists =connect((max_blob[1],max_blob[0]),max_rad, blobs[1::])
        cons_of_max = connect_dists[0]
        distances = connect_dists[1]        
        num_connections +=cons_of_max 
        
        length_of_transparents=0
        num_smaller_blobs = num_blobs - 1
        for i in range(num_smaller_blobs-1):
            blob = blobs[i+1]
            center_vec = (blob[1], blob[0])
            connect_dists = connect(center_vec, max_rad, blobs[i+2::])
            num_connections += connect_dists[0]
            length_of_transparents += connect_dists[1]
    
    #----------------------filter------------------------- can use actual filter
    test = (num_blobs == expected_blobs
                and num_connections == expected_connections 
               )
    if test: # keep frames that have enough paricles, and are not transitions
        side =sideify(cons_of_max, length_of_transparents )
        clas = side
        sides[side].append(frame_no)
        classes[clas].append(frame_no)
            #print(clas)
        
        if clas == 'ucf':
            #broken_count += 1
            #class_num = 0
            #print('ucf')
            pass
        else:
            if origin == 'ucf':
                origin = last_class
                #print("reset origin", origin)
            if clas == last_class:
                class_num += 1
                #print("class_num: %s" %class_num)
            else:
                class_num = 0
                #print("class_reset")
                #print("class_num: %s" %class_num)
            if class_num >= class_thresh: 
                if broken_count >= transition_threshold or clas != origin:
                    transitions[origin + "->" + clas].append((last_whole, frame_no))
                    #print(origin + "->" + clas)
                    origin = clas
                    #print("origin: %s" %origin)
                broken_count = 0
                #print("broken_count: %s" %broken_count)
                
            
                
            last_whole = frame_no
            filtrate_len += 1 
            last_class = clas
            
            
    else:
        #print("broken")
        class_num = 0
        #print("class_num: %s" %class_num)
        broken_count += 1
        #print("broken_count: %s" %broken_count)

    return [broken_count, class_num, origin, last_class, last_whole, filtrate_len]



        
# take largest isodata image region, and return aclassification
def sideify(cons_of_max, lens):    
    if cons_of_max == 3 and lens < 115 and lens > 98:
        return "c"
    elif cons_of_max == 2 and lens < 95 and lens > 80:
        return "t"
    else:
        return "ucf"

def connect(cv, radius, bloblist): # center of blob2, radius of all blobs, list of other blobs
    num_connections = 0
    length = 0
    for blob2 in bloblist:
        cv2 = (blob2[1], blob2[0]) # center of blob2
        vd = vector_dist(cv, cv2)
        length += vd
        if vd <= 2*radius: # blob centers closer than diameter of one blob
            num_connections += 1
        else:
            pass
    return (num_connections, length)

def vector_dist(v1, v2): # euclidean distance between 2 points
    return math.sqrt(np.sum([(v1[i] - v2[i])**2 for i in range(len(v1))]))

def third_item(l1):
        return l1[2]   

"""Pipeline for lists of frames"""
""""""
"""Pipeline for videos:"""
# initialize frame lists
filenames = glob("./tchakamau/Trn*/*[1][0]V*[7].avi")#["./tchakamau/New_setup/45681_10Vpp_25.avi"
print(filenames)
num_top_keys = 3
num_full_keys = 3
num_tran_keys = 2
trans_threshes = np.linspace(45, 100, 12)#[30, 40, 50]#[5, 8, 10, 19, 27, 38, 52, 60]
class_threshes = np.linspace(5, 100, 20)#[15, 22, 30]
trans_runs = {}
#trans_fil = 10

ave = np.average

expected_blobs = 4
expected_connections = 5
max_rad = 15*1.35
thresholds = [expected_blobs , expected_connections, max_rad ]
params = [3, 115, 98, 2, 95, 80]
print("Number files: ", len(filenames))
index = 0
for trans_fil in trans_threshes:
    
    for class_thresh in class_threshes:
        
        Top_bottoms = np.zeros((len(filenames), num_top_keys))
        Full_classif = np.zeros((len(filenames), num_full_keys))
        N_transitions = np.zeros((len(filenames), num_tran_keys, num_tran_keys))
        num_total_frames = 0 
        filtrate_len = 0
        for vidnum in range(len(filenames)):
            print("Processing vid %s : %s" %(vidnum, filenames[vidnum]))
            #meta = ffprobe(filenames[vidnum])
            #print(meta)#['@nb_frames'])
            #print(5)
            frames = vreader(filenames[vidnum])
            #frame_vid = frames[:, :, :, 2]# making videos ino a frame list
            #print(frames)



            sides = {"t":[], "c":[], "ucf":[]}
            classes = {"t":[], "c":[], "ucf":[]}
            transitions = [("t->t",[]), ("t->c",[]),
                          ("c->t" ,[]), ("c->c",[])]

            transitions = OrderedDict(transitions)
            broken_count = 0
            class_num = 0
            origin = 'ucf'
            last_class = 'ucf'
            last_whole = 0
            for fr in frames:
                frame = fr[:, :, 2]
                num_total_frames += 1
                org = total_threshold_filter(frame, num_total_frames, trans_fil, class_thresh,
                                             broken_count, class_num, origin, last_class, last_whole, filtrate_len, 
                                             sides, classes, transitions)
                broken_count, class_num, origin, last_class, last_whole, filtrate_len = org
            filtered_len = filtrate_len
            #----------------------------------------------------------------
            trans_len = len([y for x in transitions.values() for y in x])
            skeys = list(sides.keys())
            ckeys = list(classes.keys())
            tkeys = list(transitions.keys())
            slcs = [len(sides[x]) for x in skeys]
            clcs = [len(classes[x]) for x in ckeys]
            trans = [len(transitions[x]) for x in tkeys] #num of each transition
            ucf = len(sides["ucf"])


            Top_bottoms[vidnum,:] = [slcs[i] for i in range(len(skeys))]
            Full_classif[vidnum,:] = [clcs[i] for i in range(len(ckeys))]
            N_transitions[vidnum,:] = np.reshape(trans, (num_tran_keys, num_tran_keys))
            print("T threshold: %s" %trans_fil)
            print("C threshold: %s" %class_thresh)
            print(N_transitions[vidnum,:])
            #print("finished vid %s" %vidnum)
        trans_runs[index] = [[Top_bottoms, Full_classif, N_transitions, (trans_fil, class_thresh), num_top_keys, num_full_keys,
                                 num_tran_keys, skeys, ckeys, num_tran_keys, num_total_frames], thresholds, params]
        index += 1
        #---------------------------------------------------------------------------------

#-----------------------------------------------------------------------

np.save('trans_runs_transparentd_err.npy',trans_runs)