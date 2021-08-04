# -*- coding: utf-8 -*
"SASDI module to perform motion analysis on input video"

import os                               # standard library
import csv                              # standard library
import cv2                              # opencv-python 4.0.0
from ffprobe import FFProbe
import sasdi_functions as sf

# SASDI.frames['Detect'].update_listbox(0, 200, 0)  COMMENT ACCEDER ???


def one_video_analysis(arg):
    """ INPUT 1 tuple with 
        # [0]:video filename, [1]:fps, [2]:nb frames, [3]:pathname, [4] roi coordinates of corresponding subdir (0 if not a serie), [5]:"to analyse" video index, [6] total number of analysed videos
        Perform video analysis
        OUTPUT results in csv file (video pathname + .csv)
    """

    # Parse arguments
    video_filename, fps, nb_frames, video_path, roi_coord, video_rank,  video_total_nb = arg
    # add full path and filename
    current_video_fullpath = os.path.normpath(os.path.join(video_path, video_filename))
    # Get max fps value
    _, fps_limit, _, _ = sf.read_parameters()

    # Print videorank, nbvideos, videoname
    print(f"{video_rank+1} / {video_total_nb}: analysing {current_video_fullpath}")

    nb_roi = len(roi_coord)
    # get each ROI(s) number of pixels in list roi_sizes
    roi_size = []
    for index_roi in range(0, nb_roi):
        # (y1-y2) * (x1-x2)
        roi_size.append(abs((roi_coord[index_roi][0][1] - roi_coord[index_roi][1][1]) * (roi_coord[index_roi][0][0] - roi_coord[index_roi][1][0])))

    # Initialise capture and get video infos
    vidcap = None
    try:
        # Capture current video
        vidcap = cv2.VideoCapture(current_video_fullpath)
        # nb_frames = number of frames in the currently analysed video file
        #nb_frames = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
        # Get frame per second value of current video
        #cv2_fps = round(float(vidcap.get(cv2.CAP_PROP_FPS)), 2)
    except cv2.error as cv2_error:
        print(f"Error reading informations from {video_filename}: {cv2_error}")
        return
    # Use FFprobe parameters if wrong fps or wrong frame number or fps read with cv2 is different from saved fps
    error_string = ""
    if fps > fps_limit:
        error_string = f"fps>{fps_limit}: {fps}"
    if nb_frames < 10:
        error_string += f" frame number<10: {nb_frames}"
    if error_string != "":
        print(f"File analysis canceled wrong parameters: fps = {fps} (limit is: {fps_limit}), number of frames = {nb_frames} for {current_video_fullpath}")
        return

    # Get first frame
    index_frame = 0
    nb_error = 0
    first_frame = None
    list_error = []
    ret = False
    while not ret:
        try:
            # Increment frame counter
            index_frame += 1
            ret, first_frame = vidcap.read()
        except cv2.error as cv2_error:
            print(f"Error reading first frame (index {index_frame}) from {video_filename}: {cv2_error}")
            nb_error += 1
            list_error.append(index_frame)
            if index_frame > nb_frames:
                return      # Stop function if all frames are corrupted


    # Creates CLAHE object for Contrast Limited Adaptive Histogram Equalization
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))      # threshold and size of grid

    # FULL FRAME PROCESSING
    # Converting image to LAB Color model
    # L=lightness (black 0 to white 255), a (green 0 to red 255), and b (blue 0 to yellow 255)
    first_frame = cv2.cvtColor(first_frame, cv2.COLOR_BGR2LAB)
    # Applying CLAHE to L-channel of first image
    first_frame = clahe.apply(first_frame[..., 0])

    # Initialise
    intensity = []           # list for calculated values
    intensity_total = 0

    while index_frame < nb_frames:
    # while True:
        # Increment frame counter
        index_frame += 1
        # Get next frame
        ret, second_frame = vidcap.read()
        if ret:     # there is a valid image to analyse
            # temporary list for values
            row = []
            # FULL FRAME PROCESSING as above
            second_frame = cv2.cvtColor(second_frame, cv2.COLOR_BGR2LAB)
            second_frame = clahe.apply(second_frame[..., 0])
            # DIFFERENCES BETWEEN 2 CONSECUTIVE FRAMES
            # Calculates current and previous images difference
            diff_images = cv2.absdiff(first_frame, second_frame)
            # Apply median bluring 3x3 px
            diff_images = cv2.medianBlur(src=diff_images, ksize=3)
            # Apply threshold
            diff_images = cv2.threshold(src=diff_images, thresh=25, maxval=255, type=cv2.THRESH_BINARY)[1]
            # append CALCULATED TIME of current image to current row, first column
            row.append(index_frame / fps)

            # Get a CROPPED FRAME for each ROI
            for roi_index in range(nb_roi):
                # crop image with coordinates of each ROI: [ Ytopleft:Ybottomright , Xtopleft:Xbottomright)]
                cropped_image = diff_images[int(roi_coord[roi_index][0][1]):int(roi_coord[roi_index][1][1]),
                                            int(roi_coord[roi_index][0][0]):int(roi_coord[roi_index][1][0])
                                           ]
                # calculated motion = sum of all differences as percentage of max value (number of pixels * 255)
                motion = (100 * cv2.sumElems(cropped_image)[0]) / (roi_size[roi_index] * 255)
                row.append(motion)
                intensity_total += motion
            # Keep second frame for next calculation
            first_frame = second_frame
            intensity.append(row)   # append row with time, valueROI1, valueROI2, ... (current frame) to intensity list
        else: # frame error or end of video file
            # list_error.append(index_frame)
            nb_error += 1

    # print(f"DEBUG, {video_filename} last frame {index_frame:_} / total {nb_frames:_} with {nb_error:_} errors and {fps} fps")
    # print(f"DEBUG, errors: {list_error}")
    if intensity_total:
        # Save ROI coordinates (first row) and then all calculated values into videoname.ext.csv file
        with open(os.path.join(video_path, video_filename + '.csv'), "w", newline='') as csvfile:
            # print(f"DEBUG, roi coord: {roi_coord}")
            filewriter = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            filewriter.writerow(roi_coord)
            filewriter.writerows(intensity)

    return intensity_total
