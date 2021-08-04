# -*- coding: utf-8 -*-
"Sasdi module with most functions (intput/output) and Help"

import os
import sys
import tkinter as tk                    # standard library
import json                             # standard library
from tkinter import simpledialog
import cv2                              # opencv-python 4.0.0
from ffprobe import FFProbe


# NAME OF USED COLORS
COLOR_BACKGROUND = "azure"              # azure  (240, 255, 255)  #f0ffff
COLOR_MENU = "cadetblue"                # cadetblue  (95, 158, 160)  #5f9ea0
COLOR_LISTBOX = "snow"                  # snow  (255, 250, 250)  #fffafa
COLOR_BUTTON = "#D3D3D3"                # lightgray  (211, 211, 211)  #d3d3d3
COLOR_BUTTON_ACTIVE = "#87CEFA"         # lightskyblue  (135, 206, 250)  #87cefa
COLOR_BUTTON_OVER = "#40E0D0"           # turquoise  (64, 224, 208)  #40e0d0
COLOR_TEXT_LIGHT = "snow"               # snow  (255, 250, 250)  #fffafa
COLOR_TEXT_SELECT = "cyan"             # cyan  (0, 255, 255)  #00ffff

FONT_TITLE = ("Times", 20, "bold")          #font
FONT_LABEL = ("Times", 12, "bold italic")   #font
FONT_BUTTON = ("Times", 9, "bold")          #font
FONT_LISTBOX = ("Times", 11)                #font

# CUSTOM COLORS CYCLE (named for matplotlib, rgb for open cv)
MY_COLORS_NAMED = ['red', 'lime', 'DarkBlue', 'magenta', 'RebeccaPurple', 'green', 'maroon', 'orange']
MY_COLORS_RGB = [(255, 0, 0), (0, 255, 0), (0, 0, 139), (255, 0, 255), (102, 51, 153), (0, 128, 0), (128, 0, 0), (255, 165, 0)]



def color_generator(coding):
    """Generator returning custom colors,
       coding=True: output named value, ex: "blue",
       coding=False: output rgb tuple, ex: (0,0,255)
    """
    #  mycolor = sf.color_generator(False)     # starts color generator
    #  next(mycolor)    # next color from generator

    if coding:
        my_colors = MY_COLORS_NAMED
    else:
        my_colors = MY_COLORS_RGB

    for index, color in enumerate(my_colors):
        if index == len(my_colors):
            raise StopIteration
        yield color


def format_duration(duration_sec):
    "Return a duration formatted in days, h, min, s from an input duration in sec"
    time_days, remainder1 = divmod(float(duration_sec), 86400)      # return (quotient, remainder)
    time_hours, remainder2 = divmod(remainder1, 3600)
    time_mins, time_seconds = divmod(remainder2, 60)
    formatted_duration = ""
    if time_days > 0:
        formatted_duration += (str(int(time_days)) +"days ")
    if time_hours > 0:
        formatted_duration += (str(int(time_hours)) + "h ")
    if time_mins > 0:
        formatted_duration += (str(int(time_mins)) + "min ")
    formatted_duration += (str(int(time_seconds)) + "s")
    return formatted_duration

def read_parameters():
    """ INPUT sasdi directory,
        READ from parameters.json,
        RETURN Sasdi version, max acceptable fps value (int), and 2 tuples with lowercase and uppercase accepted video files extensions
    """

    params_dir = os.path.join(sys.path[0], 'params', 'parameters.json')
    if os.path.exists(params_dir):
        try:
            with open(params_dir, 'r') as filereader:
                myparams = json.load(filereader)
        except IOError as json_error:
            print(f"Error reading parameters.json: {json_error}")
            # return 100 as default fps, and 4 accepted file extensions
            return "?.?", 100, tuple(['avi', 'mp4', 'wmv', 'asf']), tuple(['AVI', 'MP4', 'WMV', 'ASF'])
        else:
            return myparams["version"], int(myparams["max_fps"]), tuple(myparams["extensions"]), tuple([x.upper() for x in myparams["extensions"]])

    else:
        print("Cannot find parameters.json, Creating a new one")
        with open(params_dir, 'w') as filewriter:
            try:
                base_params = {"version": "4.1",
                               "max_fps": "100",
                               "extensions":['avi', 'mp4', 'wmv', 'asf']
                              }
                filewriter.write(json.dumps(base_params, indent=""))
            except IOError as json_error:
                print(f"Error writing new parameters.json: {json_error}")
        # return 100 as default fps, and 4 accepted file extensions
        return base_params["version"], int(base_params["max_fps"]), tuple(base_params["extensions"]), tuple([x.upper() for x in base_params["extensions"]])


def check_list_videos(videopathdir, videolist, subdir_index):
    """ INPUT current video directory, list of video filenames,
        CHECK videos by reading their fps and number of frames,
        RETURN list of videos infos:
        [0]:video filename, [1]:fps (float), [2]:nb frames (int), [3]:pathname, [4]:file index (int), [5]:status ('A', '-', 'M', 'C'), [6]:subdir index (0 if not a serie)
        RETURN statistics (int): [0]:total number, [1]:to analyze, [2]:analyzed, [3]:fps of nb frames is modified, [4]:corrupted
    """

    # Get max fps value and accepted video files extensions
    _, fps_limit, images_extensions_lower, extensions_upper = read_parameters()
    images_extensions = images_extensions_lower + extensions_upper
    list_videos = []
    stats_videos = [0, 0, 0, 0, 0]     # [0]:total number, [1]:to analyze, [2]:analyzed, [3]:fps or nb frames modified, [4]:corrupted
    index_files = 0       # 0-based index of file
    modified_fps = 0
    file_status = ""

    # Go through all video files
    for current_file in videolist:
        if current_file.endswith(images_extensions):
            file_status = ""
            stats_videos[0] += 1            # total number of videos
            try:
                # Read video header infos with opencv
                video = cv2.VideoCapture(os.path.join(videopathdir, current_file))
                nb_frames = video.get(cv2.CAP_PROP_FRAME_COUNT)
                fps = video.get(cv2.CAP_PROP_FPS)
            except cv2.error as cv2_error:   #Exclude empty video or with read error
                video.release()
                print(f"Corrupted file, cannot read with opencv: {os.path.join(videopathdir, current_file)} -> {cv2_error}")
                stats_videos[4] += 1    # corrupted file
                file_status = "C"
            else:       # video is correctly read with opencv
                video.release()
                # Check number of frames (cannot propose to user because each file will be different)
                if nb_frames < 10:
                    ffprobe_fps = 0
                    ffprobe_duration = 0
                    try:
                        # Read video header infos with ffprobe
                        metadata = FFProbe(os.path.join(videopathdir, current_file))
                        for stream in metadata.streams:
                            if stream.is_video():
                                ffprobe_fps = float(eval(stream.r_frame_rate))
                                ffprobe_duration = round(eval(stream.duration))
                    except:
                        print(f"Corrupted number of frames={nb_frames}, and cannot read video header with ffprobe: {os.path.join(videopathdir, current_file)}")
                        stats_videos[4] += 1    # corrupted file
                        file_status = "C"
                    else:
                        ffprobe_nb_frames = round(ffprobe_fps * ffprobe_duration)
                        if ffprobe_nb_frames > 10:
                           print(f"Using number of frames read with ffprobe ({ffprobe_nb_frames}): {os.path.join(videopathdir, current_file)}")
                           file_status = "M"
                           nb_frames = ffprobe_nb_frames
                        else:
                            print(f"Corrupted number of frames={nb_frames}, and cannot read video header with ffprobe: {os.path.join(videopathdir, current_file)}")
                            stats_videos[4] += 1    # corrupted file
                            file_status = "C"
                # Check fps
                if modified_fps:        # if already given by user use modified fps
                    fps = modified_fps
                    file_status = "M"
                elif (not fps or fps > fps_limit) and file_status != "C" and nb_frames > 10:
                    # Wrong fps not yet corrected by user and with a proper number of frames
                    try:
                        # Read video header infos with ffprobe
                        metadata = FFProbe(os.path.join(videopathdir, current_file))
                        for stream in metadata.streams:
                            if stream.is_video():
                                ffprobe_fps = float(eval(stream.r_frame_rate))
                    except:
                        print(f"Corrupted fps={fps}, and cannot read video header with ffprobe: {os.path.join(videopathdir, current_file)}")
                        stats_videos[4] += 1    # corrupted file
                        file_status = "C"
                    else:
                        modified_fps = simpledialog.askfloat(title=f"Wrong fps for <{current_file}>: {fps}",
                                                             prompt="For all videos, force fps to ffprobe value or enter one (float 2 digits) ?",
                                                             initialvalue=ffprobe_fps
                                                            )
                        if not modified_fps:
                            print(f"Corrupted fps not corrected by user: {os.path.join(videopathdir, current_file)}")
                            stats_videos[4] += 1
                            file_status = "C"    # corrupted file
                        else:
                            modified_fps = round(modified_fps, 2)
                            fps = modified_fps

                # fps or nb frames was modified, add to statistics
                if file_status == "M":
                    stats_videos[3] += 1
                if file_status != "C":
                   # add non corrupted video infos
                   if os.path.isfile(os.path.join(videopathdir, current_file+".csv")):
                       stats_videos[2] += 1      # file is analyzed
                       file_status = "A" + file_status
                   else:
                       stats_videos[1] += 1      # file to analyze
                       file_status = "_" + file_status
                   list_videos.append([current_file, round(fps, 2), round(nb_frames), videopathdir, index_files, file_status, subdir_index])
                  # [0]:video filename, [1]:fps, [2]:nb_frames, [3]:pathname, [4]:file index, [5]:status ('A', '-', 'M', 'C'), [6]:subdir index (0 if not a serie)
                else:
                    # add corrupted video infos
                    list_videos.append([current_file, 0, 0, videopathdir, index_files, 'C', subdir_index])
                    # [0]:video filename, [1]:fps, [2]:nb_frames, [3]:pathname, [4]:file index, [5]:status ('A', '-', 'M', 'C'), [6]:subdir index (0 if not a serie)
                index_files += 1
    return list_videos, stats_videos


def save_get_list_videos(videopathdir, videolist):
    """ INPUT current video directory, list of video filenames, for a directory or file selection 
        CHECK videos with check_list_videos(),
        SAVE valid videos infos to list_videos.json,
        RETURN list of videos infos:
        [0]:video filename, [1]:fps (float), [2]:nb frames (int), [3]:pathname, [4]:file index (int), [5]:status ('A', '-', 'M', 'C'), [6]:0
        RETURN statistics (int): [0]:total number, [1]:to analyze, [2]:analyzed, [3]:fps of nb frames is modified, [4]:corrupted
    """

    # Check video path exists
    if not videopathdir:
        return None, None
    if not os.path.exists(videopathdir):
        return None, None

    # Check all videos and get status statistics
    list_videos, stats_videos = check_list_videos(videopathdir, videolist, 0)

    # Save video infos to list_videos.json
    with open(os.path.join(sys.path[0], 'params', 'list_videos.json'), 'w') as filewriter:
        try:
            filewriter.write(json.dumps(list_videos, indent=""))
        except IOError as json_error:
            print(f"Error writing list_videos.json: {json_error}")
    return list_videos, stats_videos


def read_infos_serie():
    """ INPUT sasdi directory,
        READ infos_serie.json,
        RETURN a list with all subdirectories short name
    """
    with open(os.path.join(sys.path[0], 'params', 'infos_serie.json'), 'r') as filereader:
        try:
            infos_serie = json.load(filereader)
        except IOError as json_error:
            print(f"Error reading infos_serie.json: {json_error}")
            infos_serie = ""
    return infos_serie


def create_serie_roi():
    "Calculates ROI from first video dimensions (minus 1 pixel) for each subdirectory of serie"

    # Get accepted video files extensions
    _, _, images_extensions_lower, extensions_upper = read_parameters()
    images_extensions = images_extensions_lower + extensions_upper

    # Get main directory fullpath and subdirectory shortnames lists
    main_fullpath = read_from_lastdir()
    serie_subdir_names = read_infos_serie()

    # Initiate list of ROIs coordinates, one for each serie subdirectory
    roi_coord = [None] * len(serie_subdir_names)
    # Enumerate each subdirectory short name
    for index_subdir, current_subdir in enumerate(serie_subdir_names):
        video_width = 0
        video_height = 0
        subdir_fullpath = os.path.join(main_fullpath, current_subdir)
        # Check permissions to read and write subdirectory
        try:
            subdir_list = os.listdir(subdir_fullpath)
        except PermissionError as err:
            print(f"No read/write permission for subdir {current_subdir}: {err}")
        else:
            # Enumerate each file short name in subdirectory
            for current_file in subdir_list:
                if current_file.endswith(images_extensions):
                    # Get first valid video image dimensions for each subdirectory of the serie
                    try:
                        video = cv2.VideoCapture(os.path.join(main_fullpath, current_subdir, current_file))
                        video_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
                        video_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    except cv2.error as cv2_error:   #Exclude empty video or with read error
                        print(f"ROI calculation: error reading {current_file}: {cv2_error}")
                        video.release()
                        continue        # continue for loop
                    else:       # video is correctly read
                        video.release()
                        break           # break for loop
            if (video_width == 0 or video_height == 0):      # no valid video in subdirectory
                roi_coord[index_subdir] = [[(0, 0), (0, 0)]]
                print(f"No valid videos found in subdir {current_subdir}")
            else:                   # add first valid video full dimensions
                roi_coord[index_subdir] = [[(1, 1), (video_width-1, video_height-1)]]

    # For each subserie Save image dimensions as ROI coordinates to roi_coord.json
    save_roi_coord(roi_coord)


def update_serie():
    """ INPUT sasdi directory,
        READ main serie directory fullpath from infos_serie.json,
        CHECK all videos by reading their fps and number of frames,
        SAVE valid videos infos to list_videos.json WITH subserie index,
        SAVE main directory and non empty subdirectories list to infos_serie.json
        RETURN list of valid videos infos WITH subserie index
        [0]:video filename, [1]:fps (float), [2]:nb frames (int), [3]:pathname, [4]:video index (int), [5]:status ('A', '-', 'M', 'C'), [6]:subdir index (int)
        RETURN statistics [ [subdir1], [subdir2], ...], for each subdir:
        (int): [0]:total number, [1]:to analyze, [2]:analyzed, [3]:modified fps or nb frames, [4]:corrupted
        RETURN list of non empty subdirectories
    """

    # Get and check main serie directory fullpath
    main_fullpath = read_from_lastdir()
    if not os.path.exists(main_fullpath):
        # Delete serie file
        if os.path.isfile(os.path.join(sys.path[0], 'params', 'infos_serie.json')):
            os.remove(os.path.join(sys.path[0], 'params', 'infos_serie.json'))
        return None, None, None

    # Get all serie subdirectories names
    serie_subdir_names = []
    for sub_dir in os.listdir(main_fullpath):
        if os.path.isdir(os.path.join(main_fullpath, sub_dir)):
            # Get the list of subseries directories short names to infos_series
            serie_subdir_names.append(sub_dir)

    serie_subdir_names.sort()
   # Get accepted video files extensions
    _, fps_limit, images_extensions_lower, extensions_upper = read_parameters()
    images_extensions = images_extensions_lower + extensions_upper

    # GET STATS AND INFOS FOR ALL VALID VIDEOS
    # Initialise list of non empty subdirectories
    valid_subdir = []
    valid_subdir_index = 0
    # Initialise list of valid videos infos
    list_videos = []
    # Initialise list for stats for each serie subdirectory
    stats_videos = []

    # GO THROUGH ALL SUBDIRECTORIES short name
    for subdir_index, current_sub_dir in enumerate(serie_subdir_names):
        # Current subdirectory fullpath
        videopathdir = os.path.join(main_fullpath, current_sub_dir)
        # List of videos filenames in current subdirectory
        list_all_files = os.listdir(videopathdir)
        list_all_files.sort()
        # Check all videos and get status statistics
        infos_videos, subdir_stats = check_list_videos(videopathdir, list_all_files, valid_subdir_index)

        # If at least one video is valid: keep current subdir name and add stats and videos infos
        if len(infos_videos) > 1:
            valid_subdir_index += 1
            valid_subdir.append(current_sub_dir)
            list_videos.extend(infos_videos)
            stats_videos.append(subdir_stats)
  
    # Save video infos to list_videos.json
    with open(os.path.join(sys.path[0], 'params', 'list_videos.json'), 'w') as filewriter:
        try:
            filewriter.write(json.dumps(list_videos, indent=""))
        except IOError as json_error:
            print(f"Error writing to list_video.json: {json_error}")

    # Save main serie directory full path and valid subdirectories names to infos_serie.json
    valid_subdir.sort()
    with open(os.path.join(sys.path[0], 'params', 'infos_serie.json'), 'w') as filewriter:
        try:
            filewriter.write(json.dumps(valid_subdir, indent=""))
        except IOError as json_error:
            print(f"Error writing infos_serie.json: {json_error}")

    return list_videos, stats_videos, valid_subdir


def read_list_videos():
    """ INPUT sasdi directory,
        READ list_videos.json,
        RETURN valid videos infos as list, and message (empty string if no error)
        [0]:video filename, [1]:fps (float), [2]:nb_frames (int), [3]:pathname, [4]:index (int), [5]:status ('A', '-', 'M', 'C'), [6]:subdir index (0 if not a serie)
    """
    message = ""
    list_videos = []
    if os.path.exists(os.path.join(sys.path[0], 'params', 'list_videos.json')):
        with open(os.path.join(sys.path[0], 'params', 'list_videos.json'), 'r') as filereader:
            try:
                list_videos = json.load(filereader)
            except IOError as json_error:
                message = f"Error reading list_videos.json: {json_error}"
    else:
        message = "File list_videos.json is absent"
    return list_videos, message

def read_roi_coord():
    """ INPUT sasdi directory,
        RETURN selected list ROIs coordinates in a list (for each subdir, [0] if not a serie),[[ [[pair], [pair]] ,[[pair], [pair]] ]]
        RETURN message (empty string if no error)
    """
    boxes = []
    message = ""
    if os.path.exists(os.path.join(sys.path[0], 'params', 'roi_coord.json')):
        with open(os.path.join(sys.path[0], 'params', 'roi_coord.json'), 'r') as filereader:
            try:
                boxes = json.load(filereader)
            except IOError as json_error:
                message = f"Error reading roi_coord.json: {json_error}"
    else:
        message = 'Can you please select at least one ROI'
    return boxes, message

def save_roi_coord(boxes):
    """ INPUT sasdi directory, ROI coordinates,
        SAVE selected ROI coordinates to roi_coord.json
    """
    with open(os.path.join(sys.path[0], 'params', 'roi_coord.json'), 'w') as filewriter:
        try:
            filewriter.write(json.dumps(boxes, indent=""))
        except IOError as json_error:
            print(f"Error writing roi_coord.json: {json_error}")

def read_from_lastdir():
    """ INPUT sasdi directory
        READ and RETURN last used directory path from lastdir.txt
    """
    if os.path.exists(os.path.join(sys.path[0], 'params', 'lastdir.txt')):
        with open(os.path.join(sys.path[0], 'params', 'lastdir.txt'), 'r') as file_reader:
            try:
                directory_name = file_reader.read()
            except IOError as txt_error:
                print(f"Error reading lastdir.txt: {txt_error}")
                return sys.path[0]
            else:
                return directory_name
    else:   # file lastdir.txt does not exists
        with open(os.path.join(sys.path[0], 'params', 'lastdir.txt'), 'w') as file_writer:
            try:
                file_writer.write(sys.path[0])
            except IOError as txt_error:
                print(f"Error writing new lastdir.txt: {txt_error}")
                return sys.path[0]
            else:
                print(f"lastdir.txt created with {sys.path[0]} as default path")
                return sys.path[0]


def save_to_lastdir(directory_name):
    """ INPUT sasdi directory and directory full path,
        SAVE given directory to lastdir.txt
    """
    with open(os.path.join(sys.path[0], 'params', 'lastdir.txt'), 'w') as file_writer:
        try:
            file_writer.write(directory_name)
        except IOError as txt_error:
            print(f"Error writing to lastdir.txt: {txt_error}")


#################################################
def user_guide(sasdi_version):
    """ INPUT sasdi version,
        DISPLAY the user guide informations
    """

    message = []
    message.append('')
    message.append('Semi Automatic Seizure Detection on Images')
    message.append('')
    message.append('  ADVICES FOR RECORDING VIDEOS BEFORE MOTION DETECTION BY VASD OR SASDI:')
    message.append('      - To avoid observed size of mice changes upon position, videos shot from above are better than from aside,')
    message.append('      - To enhance contrast, use a dark background with light-colored animal, and vice-versa,')
    message.append('      - To avoid misplaced ROIs always keep the analyzed cage in the same place (add marks to repositioned precisely),')
    message.append('      - For the same reason, be careful not to swap position of any elements when changing cages for example (bib, food dispenser, ...),')
    message.append('      - For better animal detection, use a homogenous illumination, not blinking, and with minimal shades, during both days and nights,')
    message.append('      - For the same reason, check there is no reflection on cages both during night and day illuminations, and that the camera is not producing artifacts at the chosen acquisition rate,')
    message.append('      - To properly detect seizure, the best configuration is 1 animal per zone (use a separator with holes to keep social interactions).')
    message.append('      - To avoid errors, do not use space and special characters (except -) in all directories and file names.')
    message.append('')
    message.append('  __________________________________________________________________________________________________________________________')
    message.append('')
    message.append('  HOW TO USE SASDI INTERFACE FOR MOTION DETECTION ON MULTIPLE VIDEO FILES ?')
    message.append('  __________________________________________________________________________________________________________________________')
    message.append('  STEP 1: SELECT tab')
    message.append('')
    message.append('  BEWARE, analyzed directories should not contain csv files other than those generated by VASD or SASDI.')
    message.append('')
    message.append('  TO VISUALISE RESULTS OF VIDEO FILES PREVIOUSLY ANALYSED WITH VASD OR SASDI :')
    message.append('    * Select files as described below, ignore ROI selection and go directly to Step 3.')
    message.append('')
    message.append('  TO ANALYSE VIDEO FILE(S) :')
    message.append('    * Select files and select ROI(s) to be used for analysis, as described below:')
    message.append('')
    message.append('  SELECTING VIDEO FILES :')
    message.append('    * Select a full directory, a selection of video files, a serie, or keep the previous displayed selection.')
    message.append('          A serie is a directory containing sub-directories (or "subseries") containing video files (sub-sub-directories will not be considered),')
    message.append('    * The list of video files is shown with their fps (frame per seconds) and durations, with the following indications:')
    message.append('        (-) Video file is not analyzed.')
    message.append('        (A) Already analyzed video file (csv file present).')
    message.append('    * You can click on video names in the list and unselect them one by one using the "Unselect a video" button.')
    message.append('')
    message.append('  SELECTING ROI (Region Of Interest) :')
    message.append('')
    message.append('    * If not analyzing a serie, select at least one ROI corresponding to the zone(s) to be analyzed, or keep previous ROI(s) if corrects.')
    message.append('          Click "Select new ROIs", the first valid image of the first video is shown, draw ROIs of same size for each animal zone,')
    message.append('          press R to record each ROI, D to discard last ROI, and S to save selection.')
    message.append('    * The list of selected ROIs is displayed, you can modify the list by clicking again on "Select New ROIs".')
    message.append('    * All selected ROI(s) will be used on all the selected videos, make sure this is correct otherwise select a subset of videos corresponding to the ROI(s).')
    message.append('  ')
    message.append('    * If analyzing a serie, by default the dimensions of each subserie ROI are set automatically ')
    message.append('          to the size of the first video of each sub-directory,')
    message.append('    * You can edit the ROIs used for each subdirectory by clicking on "Reselect serie ROIs",')
    message.append('          you will then be prompted for EACH subdirectory to edit the ROI(s) as above, just press S to keep existing ROI.')
    message.append('          The same set of ROIs will be used for all videos within each subdirectory.')
    message.append('')
    message.append('  __________________________________________________________________________________________________________________________')
    message.append('  STEP 2: DETECT tab')
    message.append('')
    message.append('    * You can adjust the number of threads to be use for analysis.')
    message.append('          By default, it is set to 80% of total number of threads (to keep the computer running normally),')
    message.append('          with a maximum of 1 thread per video file to analyze (more is useless and decreases the performance).')
    message.append('')
    message.append('    * Click on "Start detection" button to start analyzing all selected files.')
    message.append('    * Optionally, check "Allow reanalyze" to force analysis of all videos,')
    message.append('          (already analyzed videos, with existing csv file in the same directory, are normally not analyzed again).')
    message.append('    * Wait for a message indicating end of analysis,')
    message.append('          depending on computer SASDI analyzed roughly 100 fps (1 hour of video at 15 fps is analyzed in 9 minutes).')
    message.append('    * When analysis is finished, go to Step 3...')
    message.append('')
    message.append('  __________________________________________________________________________________________________________________________')
    message.append('  STEP 3: RESULTS')
    message.append('')
    message.append('    * Click on "Results" button, a new window opens.')
    message.append('')
    message.append('    * The BOTTOM GRAPH is showing the motion analysis in percent of max motion, color coded for each ROI.')
    message.append('    * The ROI limits, color code, and index are displayed at the bottom right on top of an image from the current video.')
    message.append('')
    message.append('    * In the center following information are shown, index of current video / total number of videos, name of current video file.')
    message.append('    * The complete path to the current video file is indicated in the top.')
    message.append('    * If a serie is visualized, the index of current subserie / total number of subseries is also shown.')
    message.append('')
    message.append('    * The TOP GRAPH, is empty by default ("None" option is ticked).')
    message.append('')
    message.append('    * Tick "Power" to display the sum of power spectra of all frequencies, calculated from the motion values.')
    message.append('      This graph is very informative to spot seizures where a high power of motion is observed.')
    message.append('      Nevertheless, this graph is calculated on the fly for each displayed motion analysis file, it can take some time depending on the used computer.')
    message.append('')
    message.append('    * Tick "Audio", to display the audio stream, if available in the video file (only first audio stream is displayed).')
    message.append('    * This can be usefull if your animal model emits a sound upon seizure.')
    message.append('      If it is the first use of audio display for the current video file, SASDI is generating a wav audio file (named videofilename.ext.wav) using FFmpeg.')
    message.append('      FFmpeg is able to convert most video formats but it may not work if you are using an unusual format. ')
    message.append('      Be also aware that created audio files can be large, check the available disk space, and it is wise to generate it only for video files of interest.')
    message.append('')
    message.append('    * Many BUTTONS are available to control the graphs display:')
    message.append('      - MOTION Y AXIS SCALE:  Increase, decrease, or set automatically with buttons on the left or using keyboard (up and down arrows, ! keys),')
    message.append('      - POWER or AUDIO Y AXIS SCALE:  Increase, decrease, or set automatically with buttons on the left or using keyboard (+ and -, * keys),')
    message.append('      - X AXIS SCALE (shared by both graphs):  Increase, decrease, or reset to full time with buttons or using keyboard (I or D keys, space bar).')
    message.append('        If time range is not full time, move display window backward or forward in time with buttons or using keyboard (B and F keys).')
    message.append('      - If visualizing a SERIE, change display to previous or next subseries with buttons or using keyboard (P and N keys).')
    message.append('      - CURRENT VIDEO within files list: Change display to previous or next analyzed video file using buttons or using keyboard (left and right arrows),')
    message.append('        or go directly to desired video file by clicking on the slider.')
    message.append('')
    message.append('    * To VISUALIZE THE VIDEO at a specific time (to check observed motion peak is indeed a seizure), left click on a point on the motion graph, video will open at the clicked time. ')
    message.append('      Default video player is VLC which enable to navigate easily and quickly in opened video.')
    message.append('      The second video player is coded with opencv (OCV), it can be used in case VLC cannot open the video and enables to see ROIs on top of video if needed.')
    message.append('')
    message.append('    * CLOSE results window with the "Close" button.')
    message.append('    * Note that you can open more than one result window and watch at the same time the results for different videos from the same selection list.')
    message.append('')
    message.append('  __________________________________________________________________________________________________________________________')
    message.append('EXIT SASDI USING THE "Exit" button')
    message.append('  __________________________________________________________________________________________________________________________')
    message.append('If you get a permission error (ex: you have selected a system directory) you will not be able to open Sasdi anymore, in sasdi/params directory delete all files except params.json')
    message.append('')
    message.append('  __________________________________________________________________________________________________________________________')
    message.append('Dr Fabrice DUPRAT, duprat@ipmc.cnrs.fr, july 2021')

    # Define the tkinter window and its title
    master = tk.Tk()
    master.title("SASDI v"+sasdi_version)
    # Define vertical and horizontal scrollbars
    y_defil_bar = tk.Scrollbar(master, orient='vertical')
    y_defil_bar.grid(row=0, column=1, sticky='ns')
    x_defil_bar = tk.Scrollbar(master, orient='horizontal')
    x_defil_bar.grid(row=1, column=0, sticky='ew')
    # Define the listbox to display help
    myparams = tk.Listbox(master,
                          width=150,                             # in characters
                          height=30,                             # in lines
                          font=FONT_LISTBOX,
                          background=COLOR_LISTBOX,
                          selectbackground=COLOR_TEXT_SELECT,
                          borderwidth=2,
                          relief=tk.SUNKEN,
                          xscrollcommand=x_defil_bar.set,
                          yscrollcommand=y_defil_bar.set,
                         )
    for line in message:
        myparams.insert(tk.END, line)
    myparams.grid(row=0, column=0, sticky='nsew')
    x_defil_bar['command'] = myparams.xview
    y_defil_bar['command'] = myparams.yview


def exit_sasdi():
    """ Exit SASDI
    """

    sys.exit(0)
    # os._exit(1)
