#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import csv
import json
import cv2
import os.path as path

# READ PARAMETERS CSV FORMAT
# with open('./params/version.txt', 'r') as r:
#     version = r.read()
# liste = [version]
# with open('./params/accepted_extensions.csv', newline='') as csvfile:
#     filereader = csv.reader(csvfile, delimiter=' ', quotechar='|')
#     for line in filereader:
#         liste.append("".join(line))
# SAVE JSON FORMAT
# with open('./params/parameters.json', 'w') as filewriter:
#     filewriter.write(json.dumps(liste))


# READ ROI COORD CSV FORMAT
# vecRect = []
# with open('./params/listselectedroi.csv', newline='') as csvfile:
#     filereader = csv.reader(csvfile, delimiter=' ', quotechar='|')
#     for line in filereader:
#         vecRect.append(line)
# vecRect = [[(0, 0), (1280, 720)], [(0, 0), (1280, 720)], [(0, 0), (1280, 720)]]
# SAVE ROI COORD JSON FORMAT
# with open('./params/listselectedroi.json', 'w') as filewriter:
#     filewriter.write(json.dumps(vecRect))
# READ ROI COORD JSON FORMAT
# with open('./params/listselectedroi.json', 'r') as filereader:
#     mycoord = json.load(filereader)

# print(f"0: {type(mycoord[0])}, 0:0: {type(mycoord[0][0])}")
# print(mycoord)

# READ PARAMETERS JSON FORMAT
# with open('./params/parameters.json', 'r') as filereader:
#     mylist = json.load(filereader)

# version = mylist[0]
# extension_lower = mylist[1:]
# extension_upper = [x.upper() for x in extension_lower]
# print (f"{version} : {extension_lower + extension_upper}")


# SAVE VIDEO INFOS JSON
videolist = ['short2.mp4', "short.mp4", "test.avi"]
valid_videos = []
videopathdir = "C:/python_files/test_files/video_files/various"
index = 0
for currentfile in videolist:
    try:
        video = cv2.VideoCapture(path.join(videopathdir,currentfile))
        nframes = video.get(cv2.CAP_PROP_FRAME_COUNT)
        fps = video.get(cv2.CAP_PROP_FPS)
        duration = round(nframes/fps, 1)
        fps = round (fps, 2)
    except:   #Exclude empty video or with read error
        print(f"Error with {currentfile}")
        video.release()
        continue
    else:       # video is correctly read
        # Add infos to list valid_videos
        # [0]:video filename, [1]:fps, [2]:duration, [3]:pathname, [4]:index
        valid_videos.append([currentfile, fps, duration, videopathdir, str(index)])                                
        video.release()
        index += 1
# Save video infos to listselectedvideos.json
with open('./params/listselectedvideos.json', 'w') as filewriter:
    filewriter.write(json.dumps(valid_videos))

# READ VIDEOS INFOS JSON FORMAT
with open('./params/listselectedvideos.json', 'r') as filereader:
    mylist = json.load(filereader)
print(mylist)


