# -*- coding: utf-8 -*-
"Sasdi module to display motion analysis results and play videos"

import platform                             # standard library
import os
import sys                                  # standard library
import csv                                  # standard library
import subprocess
import tkinter as tk                        # standard library
from copy import deepcopy
import ast
import matplotlib.pyplot as plt             # standard library
import matplotlib.image as mpl_img          # standard library
import matplotlib.ticker as mpl_ticker      # standard library
import matplotlib.widgets as mpl_wg         # standard library
import cv2                                  # opencv-python 4.0.0
from scipy.io import wavfile
from scipy import signal
import numpy as np                          # standard library
from cycler import cycler                   # Matplotlib project

import sasdi_functions as sf


class Index():
    "Class for graphing values (callback on itself)"

    def set_roi_checkbuttons_properties(self, label):
        "Display each ROI line plot according to checkbuttons status"
        # input checkbutton label ('roi1', 'roi2', ... 1-based)
        index = int(label[3:]) - 1
        if index < len(self.motion_plots):
            # reverse the visibility status (True or False)
            self.motion_plots[index].set_visible(not self.motion_plots[index].get_visible())
            if self.radiobutton_audio_power.value_selected != "None":
                self.audio_power_plots[index].set_visible(not self.audio_power_plots[index].get_visible())
            plt.draw()

    def show_photo_roi(self):
        "Display first video frame with drawn ROI"

        #Get filename of video
        video_name = os.path.join(self.videos_infos[self.videos_current_index][3], self.videos_infos[self.videos_current_index][0])   #add path + filename
        self.nb_frames = 0
        if os.path.exists(video_name):
            # Reset color cycle
            plt.gca().set_prop_cycle(None)
            # Create image from second frame
            vidcap = cv2.VideoCapture(video_name)
            self.nb_frames = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
            # vidcap.set(1, 2)      #  0-based index of the frame to be captured next (flag 1 = CV_CAP_PROP_POS_FRAMES)
            sum_image = [0]
            # Read image from video and exclude black image
            while sum_image[0] == 0:
                try:
                    success, frame_from_video = vidcap.read()
                except cv2.error as cv2_error:
                    print(f"Error reading {video_name}: {cv2_error}")
                if not success:     # could not read image
                    break
                sum_image = cv2.sumElems(frame_from_video)   # sum of all values of first channel
            if success:
                mycolor = sf.color_generator(False)     # starts color generator
                for index, coord in enumerate(self.roi_coord):
                    roi_color = next(mycolor)    # next color from generator
                    # Draw ROI(s)
                    # image, topleft, bottomright, color from matplotlib cycle, thickness
                    cv2.rectangle(img=frame_from_video,
                                  pt1=coord[0],
                                  pt2=coord[1],
                                  color=roi_color,
                                  thickness=7,
                                  )
                    # calculates center X coordinates of ROI (Xright-Xleft)
                    x_center = int(coord[0][0] + (coord[1][0] - coord[0][0]) / 2)
                    y_center = int(coord[0][1] + (coord[1][1] - coord[0][1]) / 2)           # same for Y
                    # Write ROI(s) index
                    cv2.putText(img=frame_from_video,
                                text=str(index + 1),
                                org=(x_center, y_center),
                                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                                fontScale=3,
                                color=roi_color,
                                thickness=12,
                                )
                # Resize image to 300 x 168 px (height/width ratio of 0.56)
                height, width = frame_from_video.shape[:2]
                ratio = height / 168
                # (width, height)
                frame_from_video = cv2.resize(frame_from_video, (int(width / ratio), 168), interpolation=cv2.INTER_AREA)
            vidcap.release()    # close capturing device
        else:
            # or display default one
            frame_from_video = mpl_img.imread(os.path.join(sys.path[0], 'images', 'defaultimage.png'))

        self.frame_from_video = self.ax_frame_from_video.imshow(frame_from_video, aspect='equal')
        self.frame_from_video.autoscale()
        self.frame_from_video.axes.figure.canvas.draw()
        del frame_from_video


    def open_csv_file(self, file_pathname):
        """ INPUT full pathname of current CSV file containing sasdi analysis results,
            READ,
            RETURN ROI coordinates from first row (list), and all motion analysis values (numpy array)
        """

        #Get all ROI values in list motion_time_sec and ROI coordinates in all_roi_coord
        motion_time_sec = []
        all_roi_coord = []
        firstrow = True
        line = 0
        if os.path.exists(file_pathname):
            with open(file_pathname, newline='') as csvfile:
                filereader = csv.reader(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                for row in filereader:
                    if firstrow:    # first row is list of list with ROI coordinates
                        firstrow = False
                        if isinstance(row, list):
                            if len(row) == 2 and isinstance(ast.literal_eval(row[0])[0], int):   # patch for former vasd version with 2 tuples only
                                one_roi_coord = []
                                # convert ['(val1, val2)', '(val3, val4)'] to [(val1, val2), (val3, val4)]
                                for pair_of_int in row:
                                    one_roi_coord.append(tuple(ast.literal_eval(pair_of_int)))
                                all_roi_coord.append(one_roi_coord)
                            else:
                                for pair_of_pair in row:
                                    one_roi_coord = []
                                    # convert list from string format and to list of 2 tuples for each ROI
                                    for pair_of_int in ast.literal_eval(pair_of_pair):
                                        one_roi_coord.append(tuple(pair_of_int))
                                    all_roi_coord.append(one_roi_coord)
                        else:   # if error creates a list with tiny coordinates
                            all_roi_coord = [[(1, 1), (2, 2)]]
                            print(f"{file_pathname} error with coordinates reading")

                    else:
                        line += 1
                        floatline = [float(val.replace('/0', '')) for val in row]
                        motion_time_sec.append(floatline)  #Append as float full row = time, valueROI1, valueROI2, ...
        else:   # if empty creates list to avoid error
            all_roi_coord = [[(1, 1), (2, 2)]]
            motion_time_sec = [[0, 0], [0, 0], [0, 0], [0, 0]]
            print(f"{file_pathname} does not exists")

        return all_roi_coord, np.array(motion_time_sec, dtype=np.float32)


    def __init__(self, screen_width, screen_height):
        "Init method for Index class"

        # print(f"DEBUG Inside the __init__ method of id {id(self)}.")
        # Get screen dimensions in pixels
        self.screen_width = screen_width
        self.screen_height = screen_height
        # Get main directory
        self.main_fullpath = sf.read_from_lastdir()
        # Get SASDI version
        self.sasdi_version, _, _, _ = sf.read_parameters()
        # Get os system ("Windows", "Linux", "Darwin" for MacOS, ...)
        self.current_os = platform.system()

        # Initialise new attribut
        self.nb_frames = 0
        self.serie_subdir_names = []
        self.autoscale_audio_power = True
        self.subdir_current_index = 0

        # Set X axes range as full for default
        self.full_xindex_range = True

        # Get list of all selected videos from list_videos.json:
        # [0]:video filename, [1]:fps (float), [2]:nb_frames (int), [3]:pathname, [4]:index (int), [5]:status ('A', '-', 'M', 'C'), [6]:subdir index (0 if not a serie)
        videos_infos_all, message = sf.read_list_videos()
        if message != '':
            tk.messagebox.showwarning('WARNING', message)

        self.subdir_nb_videos = []
        # Check if a serie is currently analysed
        self.serie_analysis = False
        if os.path.exists(os.path.join(sys.path[0], 'params', 'infos_serie.json')):
            # List with main directory full path and then all subdirectories short name
            self.serie_subdir_names = sf.read_infos_serie()
            self.serie_analysis = True
            self.subdir_nb_videos = [0] * len(self.serie_subdir_names)
        else:
            self.subdir_nb_videos = [0]

        first_subdir_found = False      # Use to memorise the first subdir with a valid video (in case first subdir is empty)
        # Keep only analysed videos
        self.videos_infos = []
        for infos in videos_infos_all:
            #Check that corresponding analysis csv file exists
            if os.path.exists(os.path.join(infos[3], infos[0] + ".csv")):
                self.videos_infos.append(infos)
                # Get number of videos for each directory (1 if not a serie)
                self.subdir_nb_videos[infos[6]] += 1
                if not first_subdir_found:
                    self.subdir_current_index = infos[6]
                    first_subdir_found = True
        #Total number of analysed videos
        self.videos_total_nb = sum(self.subdir_nb_videos)
        if self.videos_total_nb == 0:
            tk.messagebox.showwarning('WARNING', 'No analysis file found, please select already analysed videos or start analysis')
            return

        ### ALL ANALYSIS
        # Dictionnaries of videoplayers commands and starting options
        vlc_path = "vlc"
        # if self.current_os == "Linux":
        #     # vlc_path = os.path.join("usr", "bin", "vlc")
        #     vlc_path = "vlc"
        if self.current_os == "Windows":
            pathvlc1 = os.path.join("C:" + os.sep, "Program Files (x86)", "VLC", "vlc.exe")
            pathvlc2 = os.path.join("C:" + os.sep, "Program Files (x86)", "VideoLAN", "VLC", "vlc.exe")
            pathvlc3 = os.path.join("C:" + os.sep, "Program Files", "VLC", "vlc.exe")
            pathvlc4 = os.path.join("C:" + os.sep, "Program Files", "VideoLAN", "VLC", "vlc.exe")
            if os.path.isfile(pathvlc1):
                vlc_path = pathvlc1
            elif os.path.isfile(pathvlc2):
                vlc_path = pathvlc2
            elif os.path.isfile(pathvlc3):
                vlc_path = pathvlc3
            elif os.path.isfile(pathvlc4):
                vlc_path = pathvlc4
        if self.current_os == "Darwin":   # Mac TO BE CHECKED
            vlc_path = os.path.join("Applications", "VLC.app", "Contents", "MacOS", "VLC")
        if vlc_path == "":
            print("Path to VLC not found")
        self.commanddict = {'VLC player':vlc_path,
                            'OCV player':"",     # OpenCV
                           }
        self.optiondict = {'VLC player':"--start-time=",
                           'OCV player':"",
                          }
        # Set default values to first videoplayer
        self.video_player_command = self.commanddict['VLC player']
        self.video_player_option = self.optiondict['VLC player']

        #Initialise index of current video
        self.videos_current_index = 0

        #Get all ROI values of first video in numpy array self.timesec_motion and ROI coordinates from first row
        self.roi_coord, self.timesec_motion = self.open_csv_file(os.path.join(self.videos_infos[self.videos_current_index][3], self.videos_infos[self.videos_current_index][0] + ".csv"))

        # Get time (in sec) from first column of self.timesec_motion and change in min
        # self.timemin = [c[0]/60.0 for c in self.timesec_motion]
        self.timemin = self.timesec_motion[:, 0] / 60

        #SamplingFrequency (Hz)
        self.sampling_frequency = 1 / (60 * (self.timemin[2] - self.timemin[1]))

        # Initialise display limits self.motion_index_left_limit and self.motion_index_right_limit (points index of self.timemin and self.valuesY) to 0 and last point
        self.motion_index_left_limit = 0
        self.motion_index_right_limit = len(self.timesec_motion) - 1

        # Initialise display limits self.timemin_left_limit and self.timemin_right_limit (in min)
        self.timemin_left_limit = 0.
        self.timemin_right_limit = self.timemin[-1]

        # Initialise autoscale of XY graph
        self.autoscale_motion = True
        #Initialise Y limit of Motion XY graph
        self.motion_upper_limit = np.amax(self.timesec_motion[:, 1:])

        #Initialise Y limit of Audio /Power XY graph
        self.axe_audio_power_graph_upper_limit = 0
        self.axe1_graph_lower_limit = 0


        #Remove toolbar of pyplot window
        plt.rcParams['toolbar'] = 'None'
        #creates subplot of main plot plt (nrows, ncols, index in virtual grid), return self.main_fig and axes objects
        #nrows=1, ncols=1, sharex=False, sharey=False
        # Two subplots (axe1 unused), the axes array is 1-d
        self.main_fig, (self.axe_audio_power, self.axe_motion) = plt.subplots(nrows=2, ncols=1, sharex=True)

        # Set custom color for matplotlib cycler
        custom_cycler = (cycler(color=sf.MY_COLORS_NAMED))
        plt.rc('axes', prop_cycle=custom_cycler)

        # Add AUDIO / POWER XY plot (empty)
        self.audio_power_x_values = [0]
        self.axe1_y_values = [0]
        self.audio_power_plots = self.axe_audio_power.plot(self.audio_power_x_values, self.axe1_y_values, '-b', linewidth=0.5)

        # Add MOTION XY plot
        # x=self.timemin, y= all columns except the first of self.timesec_motion from display range with line, default colors from matplotlib return line2D object
        self.motion_plots = self.axe_motion.plot(self.timemin[self.motion_index_left_limit:self.motion_index_right_limit], self.timesec_motion[self.motion_index_left_limit:self.motion_index_right_limit, 1:], linewidth=0.5)
        # Set whole figure color
        self.main_fig.set_facecolor(sf.COLOR_BACKGROUND)

        # Set audio/power XY plot display options
        self.axe_audio_power.tick_params(axis='both',
                                         which='both',
                                         bottom=True,
                                         left=True,
                                         labelbottom=False,
                                        )
        self.axe_audio_power.grid(b=True,
                                  which='major',
                                  axis='x',
                                  color='0.1',
                                  linestyle=':',
                                  linewidth=1.5,
                                  )
        self.axe_audio_power.grid(b=True,
                                  which='major',
                                  axis='y',
                                  color='0.1',
                                  linestyle=':',
                                  linewidth=1,
                                  )
        self.axe_audio_power.grid(b=True,
                                  which='minor',
                                  axis='both',
                                  color='0.1',
                                  linestyle=':',
                                  linewidth=1,
                                  )

        # Set motion XY graph display options
        self.axe_motion.xaxis.set_minor_locator(mpl_ticker.AutoMinorLocator(5))      #minor ticks divide major division in 5 minor divisions
        self.axe_motion.xaxis.set_minor_formatter(mpl_ticker.ScalarFormatter(useOffset=True))
        self.axe_motion.xaxis.set_major_formatter(mpl_ticker.ScalarFormatter())
        self.axe_motion.tick_params(axis='x',
                                    which='major',
                                    pad=12,
                                    labelsize=12
                                    )
        self.axe_motion.tick_params(axis='x',
                                    which='minor',
                                    labelsize=10
                                    )
        self.axe_motion.grid(b=True,
                             which='major',
                             axis='x',
                             color='0.1',
                             linestyle=':',
                             linewidth=1.5,
                             )
        self.axe_motion.grid(b=True,
                             which='major',
                             axis='y',
                             color='0.1',
                             linestyle=':',
                             linewidth=1,
                             )
        self.axe_motion.grid(b=True,
                             which='minor',
                             axis='both',
                             color='0.1',
                             linestyle=':',
                             linewidth=1,
                             )
        self.axe_motion.set_ylabel('Image motion (% of maximum)')
        self.axe_motion.set_xlabel('Time (min)')

        #Autoscale XY plot
        self.axe_motion.set_xlim(self.timemin_left_limit, self.timemin_right_limit)     # set video graphs display x limits (in min)
        self.axe_motion.set_ylim(0, self.motion_upper_limit)                # set video graphs display y limits
        self.axe_audio_power.set_xlim(self.timemin_left_limit, self.timemin_right_limit)     # set audio graphs display x limits
        if self.axe_audio_power_graph_upper_limit != 0:
            self.axe_audio_power.set_ylim(0, self.axe_audio_power_graph_upper_limit)                      # set audio graphs display y limits
        serie_display = ""
        if self.serie_analysis:
            self.subdir_current_name = self.serie_subdir_names[self.subdir_current_index]
            serie_display = f"- Subserie {1}/{len(self.serie_subdir_names)} <{self.subdir_current_name}>"

        # Adjust subplots borders and add title and text
        self.main_fig.subplots_adjust(left=0.15, bottom=0.28, right=0.98, top=0.9, wspace=None, hspace=0.4)     #adjust the subplot margins in main window
        videoname = self.videos_infos[self.videos_current_index][0]
        title_motion = f"Video 1/{self.videos_total_nb} : {videoname}   {serie_display}"     #index of video/total + filename without .csv
        self.axe_motion.set_title(label=title_motion,
                                  fontsize=14,
                                  color=sf.COLOR_TEXT_LIGHT,
                                  backgroundcolor=sf.COLOR_MENU,
                                  pad=15,
                                 )
        videopath = self.videos_infos[self.videos_current_index][3]
        self.axe_audio_power.set_title(label=videopath,
                                       fontsize=14,
                                       color=sf.COLOR_TEXT_LIGHT,
                                       backgroundcolor=sf.COLOR_MENU,
                                       pad=15,
                                      )

        # First draw of main figure with image and eventually audio analysis
        self.main_fig.canvas.draw()

        # Maximise window size
        self.fig_manager = plt.get_current_fig_manager()
        self.fig_manager.resize(0.8 * self.screen_width, 0.8 * self.screen_height)
        self.fig_manager.set_window_title("SASDI v" + self.sasdi_version + ' - Graphs of analysis results')  # Window Title

        # CREATION OF MATPLOTLIB WIDGETS GRAPHICAL ELEMENTS (not tkinter)
        # (positions of axes [left, bottom, width, height] containing elements)

        ## RADIO BUTTON FOR AUDIO OR POWER DISPLAY
        self.ax_audio_power = plt.axes([0.005, 0.9, 0.1, 0.1],
                                       frame_on=False,     # border visible or not
                                       )
        self.ax_audio_power.set_facecolor(sf.COLOR_BACKGROUND)
        self.radiobutton_audio_power = mpl_wg.RadioButtons(self.ax_audio_power, ('None', 'Power', 'Audio'))
        self.radiobutton_audio_power.set_active(0)      #set first choice active
        self.radiobutton_audio_power.circles[0].set_radius(0.05)

        ## BUTTON INCREASE AUDIO/POWER Y AXIS
        self.ax_audio_power_plus = plt.axes([0.005, 0.82, 0.045, 0.04])
        self.btn_audio_power_y_plus = mpl_wg.Button(self.ax_audio_power_plus,
                                                    label=' + ',
                                                    color=sf.COLOR_BUTTON,
                                                    hovercolor=sf.COLOR_BUTTON_OVER,
                                                    )

        ## BUTTON AUTOSCALE AUDIO/POWER Y AXIS
        self.ax_audio_power_auto_y = plt.axes([0.005, 0.75, 0.045, 0.04])
        self.btn_audio_power_y_auto = mpl_wg.Button(self.ax_audio_power_auto_y,
                                                    label='(*) Auto ',
                                                    color=sf.COLOR_BUTTON_ACTIVE,
                                                    hovercolor=sf.COLOR_BUTTON_OVER,
                                                    )

        ## BUTTON DECREASE AUDIO Y AXIS
        self.ax_audio_power_minus = plt.axes([0.005, 0.68, 0.045, 0.04])
        self.btn_audio_power_y_minus = mpl_wg.Button(self.ax_audio_power_minus,
                                                     label=' - ',
                                                     color=sf.COLOR_BUTTON,
                                                     hovercolor=sf.COLOR_BUTTON_OVER,
                                                     )
        # Audio buttons are only visible if audio is checked by user
        self.ax_audio_power_plus.set_visible(False)
        self.ax_audio_power_auto_y.set_visible(False)
        self.ax_audio_power_minus.set_visible(False)

        ## BUTTON INCREASE MOTION Y AXIS
        self.ax_motion_plus = plt.axes([0.005, 0.47, 0.045, 0.04])
        self.btn_motion_y_plus = mpl_wg.Button(self.ax_motion_plus,
                                               label=' ^ ',
                                               color=sf.COLOR_BUTTON,
                                               hovercolor=sf.COLOR_BUTTON_OVER,
                                               )

        ## BUTTON AUTOSCALE MOTION Y AXIS
        self.ax_motion_auto_y = plt.axes([0.005, 0.4, 0.045, 0.04])
        self.btn_motion_y_auto = mpl_wg.Button(self.ax_motion_auto_y,
                                               label='(!) Auto ',
                                               color=sf.COLOR_BUTTON_ACTIVE,
                                               hovercolor=sf.COLOR_BUTTON_OVER,
                                               )

        ## BUTTON DECREASE Y MOTION AXIS
        self.ax_motion_minus = plt.axes([0.005, 0.33, 0.045, 0.04])
        self.btn_motion_minus = mpl_wg.Button(self.ax_motion_minus,
                                              label=' v ',
                                              color=sf.COLOR_BUTTON,
                                              hovercolor=sf.COLOR_BUTTON_OVER,
                                              )

        ## CHECK BUTTON FOR ROI DISPLAY
        self.ax_roi = plt.axes([0.06, 0.31, 0.07, 0.2],     # space given to checkbuttons
                               frame_on=False,     # border
                               )
        # Labels roi1, roi2, ...
        check_roi_labels = ["roi" + str(i) for i in range(1, 9)]
        # Default value is checked
        check_roi_active = [True] * 8
        # Creates 8 ROI checkbuttons
        self.check_roi = mpl_wg.CheckButtons(self.ax_roi,
                                             labels=check_roi_labels,
                                             actives=check_roi_active,
                                             )
        # Define properties of checkbuttons rectangles
        self.ax_roi.set_prop_cycle(None)    # Reset color cycle
        for index, rect_prop in enumerate(self.check_roi.rectangles):
            rect_prop.set_width(0.07)
            rect_prop.set_height(0.07)
            rect_prop.set_alpha(0)      # all invisible
            rect_prop.set_edgecolor(f"C{index}")
        # Define properties of checkbuttons text
        self.ax_roi.set_prop_cycle(None)    # Reset color cycle
        for index, text_prop in enumerate(self.check_roi.labels):
            text_prop.set_color(f"C{index}")
            # text_prop.set_fontproperties('bold')
            text_prop.set_alpha(0)      # all invisible
        # Set the 2 lines forming the 8 checks to invisible
        for d_lines in self.check_roi.lines:
            for s_line in d_lines:
                s_line.set_alpha(0)
        # checkbuttons are shown (alpha=1) or not in replot

        ## BUTTON PREVIOUS SERIE
        self.ax_serie_previous = plt.axes([0.005, 0.1, 0.08, 0.055])
        self.btn_serie_previous = mpl_wg.Button(self.ax_serie_previous,
                                                label='(P)rev subserie',
                                                color=sf.COLOR_BUTTON,
                                                hovercolor=sf.COLOR_BUTTON_OVER,
                                                )
        # Hide button previous serie at starts
        self.ax_serie_previous.set_visible(False)

        ## BUTTON NEXT SERIE
        self.ax_serie_next = plt.axes([0.09, 0.1, 0.08, 0.055])
        self.btn_serie_next = mpl_wg.Button(self.ax_serie_next,
                                            label='(N)ext subserie',
                                            color=sf.COLOR_BUTTON,
                                            hovercolor=sf.COLOR_BUTTON_OVER,
                                            )

        ## Display button next serie only if a serie is selected and contains more than 2 subdir
        if self.serie_analysis and len(self.serie_subdir_names) > 1:
            self.ax_serie_next.set_visible(True)
        else:
            self.ax_serie_next.set_visible(False)

        ## BUTTON PREVIOUS VIDEO
        self.ax_video_previous = plt.axes([0.175, 0.1, 0.07, 0.07])
        self.btn_video_previous = mpl_wg.Button(self.ax_video_previous,
                                                label='< Prev video',
                                                color=sf.COLOR_BUTTON,
                                                hovercolor=sf.COLOR_BUTTON_OVER,
                                                )
        # Hide button "Previous" at starts
        self.ax_video_previous.set_visible(False)

        ## BUTTON NEXT VIDEO
        self.ax_video_next = plt.axes([0.251, 0.1, 0.075, 0.07])
        self.btn_video_next = mpl_wg.Button(self.ax_video_next,
                                            label='> Next video',
                                            color=sf.COLOR_BUTTON,
                                            hovercolor=sf.COLOR_BUTTON_OVER,
                                            )
        # Show button "Next" only if more than 1 video
        if self.videos_total_nb > 1:
            self.ax_video_next.set_visible(True)

        ## SLIDER FOR FILES
        self.ax_file_slider = plt.axes([0.005, 0.01, 0.321, 0.06])
        self.file_slider = mpl_wg.Slider(ax=self.ax_file_slider,
                                         label='',
                                         valmin=0.,
                                         valmax=float(self.videos_total_nb),
                                         valstep=1.,
                                         valinit=1.,
                                         color=sf.COLOR_BUTTON_ACTIVE,
                                         )    #range from 1 to number of videos
        self.ax_file_slider.tick_params(axis='x',
                                        which='major',
                                        bottom=True,
                                        )
        self.file_slider.valtext.set_visible(False)

        ## BUTTON BACKWARD TIME
        self.ax_time_backward = plt.axes([0.437, 0.1, 0.075, 0.06])
        self.btn_time_backward = mpl_wg.Button(self.ax_time_backward,
                                               label='(B)ackward',
                                               color=sf.COLOR_BUTTON,
                                               hovercolor=sf.COLOR_BUTTON_OVER,
                                               )

        ## BUTTON FORWARD TIME
        self.ax_time_forward = plt.axes([0.517, 0.1, 0.075, 0.06])
        self.btn_time_forward = mpl_wg.Button(self.ax_time_forward,
                                              label='(F)orward',
                                              color=sf.COLOR_BUTTON,
                                              hovercolor=sf.COLOR_BUTTON_OVER,
                                              )
        # At starts hide Backward and Forward buttons
        self.ax_time_backward.set_visible(False)
        self.ax_time_forward.set_visible(False)

        ## BUTTON DECREASE TIME SCALE
        self.ax_time_decrease = plt.axes([0.395, 0.01, 0.075, 0.06])
        self.btn_time_decrease_scale = mpl_wg.Button(self.ax_time_decrease,
                                                     label='(D)ecrease ',
                                                     color=sf.COLOR_BUTTON,
                                                     hovercolor=sf.COLOR_BUTTON_OVER,
                                                     )

        ## BUTTON TIME TO FULL SCALE
        self.ax_time_fullscale = plt.axes([0.477, 0.01, 0.075, 0.06])
        self.btn_time_fullscale = mpl_wg.Button(self.ax_time_fullscale,
                                                label='( ) Full ',
                                                color=sf.COLOR_BUTTON,
                                                hovercolor=sf.COLOR_BUTTON_OVER,
                                                )

        ## BUTTON INCREASE TIME SCALE
        self.ax_time_increase = plt.axes([0.559, 0.01, 0.075, 0.06])
        self.btn_time_increase_scale = mpl_wg.Button(self.ax_time_increase,
                                                     label='(I)ncrease ',
                                                     color=sf.COLOR_BUTTON,
                                                     hovercolor=sf.COLOR_BUTTON_OVER,
                                                     )

        ## FRAME WITH ROI
        self.ax_frame_from_video = plt.axes([0.62, 0.01, 0.35, 0.21])
        plt.axis("off")
        image = mpl_img.imread(os.path.join(sys.path[0], 'images', 'defaultimage.png'))     # default image
        self.frame_from_video = self.ax_frame_from_video.imshow(image, aspect='equal')
        self.show_photo_roi()

        ## RADIOBUTTONS VIDEO PLAYERS
        self.ax_videoplayers = plt.axes([0.89, 0.1, 0.15, 0.15],
                                        facecolor=sf.COLOR_BACKGROUND,
                                        frame_on=False,     # border visible or not
                                        )
        # self.ax_videoplayers.set_xlabel('Video player')
        self.radio_videoplayers = mpl_wg.RadioButtons(self.ax_videoplayers, ('VLC player', 'OCV player'))
        self.radio_videoplayers.set_active(0)      #set first choice active
        self.radio_videoplayers.circles[0].set_radius(0.05)

        ## CLOSE BUTTON
        self.ax_close = plt.axes([0.92, 0.01, 0.05, 0.05],
                                 facecolor=sf.COLOR_BACKGROUND,
                                 )

        self.btn_close = mpl_wg.Button(self.ax_close,
                                       label='CLOSE',
                                       color=sf.COLOR_BUTTON,
                                       hovercolor=sf.COLOR_BUTTON_OVER,
                                       )
        #Replot the graphs
        self.replot()


    ###################################
    def onclick(self, event):
        "Method to open corresponding video (left click) at the clicked time after a click on the graph"

        # Calculate the graph coordinates within full matplotlib figure
        # get the motion XY graph position [[XLeft x0, YBottom y0, XRight x1, YTop y1] in ratio to max pixels value (0=first pixel, 1=last pixel)
        video_pos = self.axe_motion.get_position()
        # get the audio XY graph position [[XLeft x0, YBottom y0, XRight x1, YTop y1] in ratio to max pixels value (0=first pixel, 1=last pixel)
        # audio_pos = self.axe_audio_power.get_position()
        # get a tuple with size of full figure in pixels (width, height)
        size = self.main_fig.get_size_inches() * self.main_fig.dpi
        # calculate the motion XY graph positions in pixels [XLeft, YBottom, XRight, YTop] (X from 0 left to max right) (Y from 0 bottom to max top)
        video_xy = [video_pos.x0 * size[0], video_pos.y0 * size[1], video_pos.x1 * size[0], video_pos.y1 * size[1]]
        # calculate the audio XY graph positions in pixels [XLeft, YBottom, XRight, YTop] (X from 0 left to max right) (Y from 0 bottom to max top)
        # audio_XY = [audio_pos.x0*size[0], audio_pos.y0*size[1], audio_pos.x1*size[0], audio_pos.y1*size[1]]

        # get mouse click point (in pixels)
        click_x, click_y = event.x, event.y
        # within_video = False
        # within_audio = False

        # Check if click is within the motion graph
        if (click_x > video_xy[0] and click_x < video_xy[2] and click_y > video_xy[1] and click_y < video_xy[3]):
            #calculate time (min) per pixel on XY graph (range in min / graph width in pixels)
            time_per_pixel = (self.timemin_right_limit - self.timemin_left_limit) / (size[0] * video_pos.width)
            #calculate time of click in min = time at X axis start + ( clicked pixel X position relative to axis origin) * time per pixel
            click_time_min = self.timemin_left_limit + (click_x - video_xy[0]) * time_per_pixel
            #make sure it is within display range
            click_time_min = min(click_time_min, self.timemin[-1])
            click_time_min = max(click_time_min, self.timemin_left_limit)
            click_time_sec = int(click_time_min * 60)
            video_name = os.path.join(self.videos_infos[self.videos_current_index][3], self.videos_infos[self.videos_current_index][0])
            video_name = os.path.normpath(video_name)     # normalise separator
            # LEFT CLICK FOR VIDEO DISPLAY at click Time in seconds
            if event.button == 1:
                # If opencv is selected use it
                if self.radio_videoplayers.value_selected == 'OCV player':
                    self.show_video(video_name, click_time_sec)
                else:   # otherwise use selected videoplayer
                    # print("VLC COMMAND: "+self.video_player_command, f"file:///{video_name} {self.video_player_option} {click_time_sec}")
                    if self.current_os == "Windows":
                        mycommand = [self.video_player_command, "file:///" + video_name, self.video_player_option+str(click_time_sec)]
                    elif self.current_os == "Linux":
                        mycommand = [self.video_player_command, video_name, self.video_player_option+str(click_time_sec)]
                    print(f"VLC COMMAND: {' '.join(mycommand)}")
                    subprocess.Popen(mycommand)

    ########################################################################################################
    ########################################################################################################
    def replot(self):
        "Method to replot XY graphs"

        # Set audio/power graph values to zero
        self.axe1_x_values_sec = [0]
        self.axe1_y_values = [0]

        # Reset line object(s) and color cycle for AUDIO/POWER AXE1 plots
        self.axe_audio_power.lines = []
        self.axe_audio_power.set_prop_cycle(None)

        # UPPER AXE = AUDIO DISPLAY
        if self.radiobutton_audio_power.value_selected == "Audio":
            # Show buttons
            self.ax_audio_power_plus.set_visible(True)
            self.ax_audio_power_auto_y.set_visible(True)
            self.ax_audio_power_minus.set_visible(True)
            # AUDIO XY plot
            self.axe_audio_power.set_ylabel('Audio intensity (AU)')
            input_file = os.path.join(self.main_fullpath, self.videos_infos[self.videos_current_index][0])
            output_file = input_file[:-3] + "wav"
            if not os.path.isfile(output_file):   # audio file does not exist
                try:
                    self.axe_audio_power.set_title(label='Generating wav file ...',
                                                   fontdict={'fontsize':10},
                                                   loc='center',
                                                   )
                    # try extracting audio from current video and save to wav file
                    subprocess.check_call("ffmpeg -i " + input_file + " -map 0:a:0? -ac 1 -ar 2205 -y " + output_file, shell=False)
                except subprocess.CalledProcessError as error:     # error extracting audio
                    print(f"{output_file} file wav creation error: {error}")
                else:
                    print(f"wav created: {output_file}")

            if os.path.isfile(output_file):   # if audio file exists, read audio values and generate time values
                # Delete message in title
                videopath = self.videos_infos[self.videos_current_index][3]
                self.axe_audio_power.set_title(label=videopath,
                                               fontsize=14,
                                               color=sf.COLOR_TEXT_LIGHT,
                                               backgroundcolor=sf.COLOR_MENU,
                                               pad=15,
                                              )
                rate, self.axe1_y_values = wavfile.read(output_file)
                self.axe1_x_values_sec = np.linspace(0, self.axe1_y_values.size / rate, num=self.axe1_y_values.size)
                # ADD AUDIO PLOT
                self.axe1_x_values_min = self.axe1_x_values_sec / 60
                # Convert index of left and right limits from index of motion time into index of audio time (higher frequency)
                left_time_min = self.timemin[self.motion_index_left_limit]
                right_time_min = self.timemin[self.motion_index_right_limit]
                audio_index_left_limit = np.nonzero(self.axe1_x_values_min >= left_time_min)[0][0]         # first value >= left limit
                audio_index_right_limit = np.nonzero(self.axe1_x_values_min <= right_time_min)[0][-1]      # last value <=right limit
                self.audio_power_plots = self.axe_audio_power.plot(self.axe1_x_values_min[audio_index_left_limit:audio_index_right_limit],
                                                                   self.axe1_y_values[audio_index_left_limit:audio_index_right_limit],
                                                                   linewidth=0.5
                                                                   )
                # Recalculate graph limits if auto is selected
                if self.autoscale_audio_power:
                    self.axe_audio_power_graph_upper_limit = np.amax(np.abs(self.axe1_y_values[audio_index_left_limit:audio_index_right_limit]))
                    # self.axe_audio_power_graph_upper_limit = np.quantile(np.abs(self.axe1_y_values), 0.999)
                    self.axe1_graph_lower_limit = -self.axe_audio_power_graph_upper_limit
                    self.axe_audio_power.set_ylim(self.axe1_graph_lower_limit, self.axe_audio_power_graph_upper_limit)
            else:       # no audio file
                self.axe_audio_power.set_title(label='No audio stream',
                                               fontdict={'fontsize':10},
                                               loc='center',
                                              )
                # Hide buttons
                self.ax_audio_power_plus.set_visible(False)
                self.ax_audio_power_auto_y.set_visible(False)
                self.ax_audio_power_minus.set_visible(False)
                # Delete y axis label
                self.axe_audio_power.set_ylabel('')

        # UPPER AXE = POWER DISPLAY
        elif self.radiobutton_audio_power.value_selected == "Power":
            # Show buttons
            self.ax_audio_power_plus.set_visible(True)
            self.ax_audio_power_auto_y.set_visible(True)
            self.ax_audio_power_minus.set_visible(True)
            self.axe_audio_power.set_ylabel('Total power')
            # GET SPECTROGRAMS VALUES
            self.axe_audio_power.set_title(label='Calculating power values...',
                                           fontdict={'fontsize':10},
                                           loc='center',
                                           )
            power_values = []
            sampling_frequency_int = int(round(self.sampling_frequency, 0))
            for roi_values in self.timesec_motion.T[1:, :]:
            # return sample frequencies, segment times (indices), spectrogram
                _, time_val, spectro_val = signal.spectrogram(x=roi_values,
                                                              noverlap=0,
                                                              nperseg=sampling_frequency_int,
                                                             )
                power_values.append(np.sum(spectro_val, axis=0))
            self.axe1_y_values = np.transpose(np.array(power_values, dtype=np.float32))
            self.axe1_x_values_sec = np.array(time_val, dtype=np.float32) / sampling_frequency_int
            # ADD POWER PLOTS
            self.axe1_x_values_min = self.axe1_x_values_sec / 60
            # Convert index of left and right limits from index of motion time into index of power time (1 value/second)
            left_time_min = self.timemin[self.motion_index_left_limit]
            right_time_min = self.timemin[self.motion_index_right_limit]
            power_index_left_limit = np.nonzero(self.axe1_x_values_min >= left_time_min)[0][0]         # first value >= left limit
            power_index_right_limit = np.nonzero(self.axe1_x_values_min <= right_time_min)[0][-1]      # last value <=right limit
            self.audio_power_plots = self.axe_audio_power.plot(self.axe1_x_values_min[power_index_left_limit:power_index_right_limit],
                                                               self.axe1_y_values[power_index_left_limit:power_index_right_limit, :],
                                                               linewidth=0.5
                                                               )
            # Delete display title
            videopath = self.videos_infos[self.videos_current_index][3]
            self.axe_audio_power.set_title(label=videopath,
                                           fontsize=14,
                                           color=sf.COLOR_TEXT_LIGHT,
                                           backgroundcolor=sf.COLOR_MENU,
                                           pad=15,
                                          )
            # Recalculate graph limits if auto is selected
            if self.autoscale_audio_power:
                # self.axe_audio_power_graph_upper_limit = np.quantile(self.axe1_y_values, 0.99)
                self.axe_audio_power_graph_upper_limit = np.amax(self.axe1_y_values[power_index_left_limit:power_index_right_limit, :])
                self.axe1_graph_lower_limit = 0
                self.axe_audio_power.set_ylim(self.axe1_graph_lower_limit, self.axe_audio_power_graph_upper_limit)

        # UPPER AXE = NO DISPLAY
        else:
            # Hide buttons
            self.ax_audio_power_plus.set_visible(False)
            self.ax_audio_power_auto_y.set_visible(False)
            self.ax_audio_power_minus.set_visible(False)
            # Delete y axis label
            self.axe_audio_power.set_ylabel('')
            # Delete display title
            videopath = self.videos_infos[self.videos_current_index][3]
            self.axe_audio_power.set_title(label=videopath,
                                           fontsize=14,
                                           color=sf.COLOR_TEXT_LIGHT,
                                           backgroundcolor=sf.COLOR_MENU,
                                           pad=15,
                                          )

        # Reset line object(s) and color cycle for MOTION AXE0 plots
        self.axe_motion.lines = []
        self.axe_motion.set_prop_cycle(None)

        # Apply the choosen X axes range (full or limited range)
        if self.full_xindex_range:
            # Set full X axis
            self.motion_index_left_limit = 0
            self.motion_index_right_limit = len(self.timemin) - 1   #new self.motion_index_right_limit limit in points
            #Set Full axis button color to inactive
            self.btn_time_fullscale.color = sf.COLOR_BUTTON_ACTIVE
            #Calculates new limits (in min)
            self.timemin_left_limit = 0                    #set display min time value (in min)

        self.timemin_left_limit = ((self.motion_index_left_limit) / self.sampling_frequency) / 60    #set display min time value (in min)
        self.timemin_right_limit = ((self.motion_index_right_limit + 1) / self.sampling_frequency) / 60    #set display max time value (in min)
        # set graphs display x limits (in min)
        self.axe_motion.set_xlim(self.timemin_left_limit, self.timemin_right_limit)

        # LOWER AXE = MOTION XY plot from list time in minutes and last columns of timesec_motion
        self.motion_plots = self.axe_motion.plot(self.timemin[self.motion_index_left_limit:self.motion_index_right_limit],
                                                 self.timesec_motion[self.motion_index_left_limit:self.motion_index_right_limit, 1:],
                                                 linewidth=0.5
                                                 )

        # Display (alpha=1) the existing roi checkbuttons
        nb_roi = len(self.motion_plots)
        existing_roi = [1] * nb_roi + [0] * (8 - nb_roi)        # if 3 ROIs [1,1,1,0,0,0,0,0]
        for index, val in enumerate(existing_roi):
            self.check_roi.lines[index][0].set_alpha(val)
            self.check_roi.lines[index][1].set_alpha(val)
            self.check_roi.labels[index].set_alpha(val)
            self.check_roi.rectangles[index].set_alpha(val)
        # Display or not each plot of video analysis according to present checkbuttons status
        checkbuttons_status = self.check_roi.get_status()
        for index_0, lineplot_0 in enumerate(self.motion_plots):
            lineplot_0.set_visible(checkbuttons_status[index_0])
        for index_1, lineplot_1 in enumerate(self.audio_power_plots):
            lineplot_1.set_visible(checkbuttons_status[index_1])

        if self.autoscale_motion:
            self.motion_upper_limit = np.amax(self.timesec_motion[self.motion_index_left_limit:self.motion_index_right_limit, 1:])   # calculate graphs display y upper limit according to max value
        self.axe_motion.set_ylim(0, self.motion_upper_limit)   # set graphs display y limits

        # If serie analysis
        serie_display = ""
        if self.serie_analysis:
            # Update subdir index
            self.subdir_current_index = self.videos_infos[self.videos_current_index][6]
            # Prepare display
            self.subdir_current_name = self.serie_subdir_names[self.subdir_current_index]
            serie_display = f"- Subserie {self.subdir_current_index + 1}/{len(self.serie_subdir_names)} <{self.subdir_current_name}>"

        # Adjust borders and add window title
        self.main_fig.subplots_adjust(left=0.15, bottom=0.28, right=0.98, top=0.9, wspace=None, hspace=0.4)     #adjust the subplot margins in main window
        videoname = self.videos_infos[self.videos_current_index][0]
        title_motion = f"Video {self.videos_current_index + 1}/{self.videos_total_nb} : {videoname}   {serie_display}"     # video index(0-based)/total + filename without .csv
        self.axe_motion.set_title(label=title_motion,
                                  fontsize=14,
                                  color=sf.COLOR_TEXT_LIGHT,
                                  backgroundcolor=sf.COLOR_MENU,
                                  pad=15,
                                 )
        videopath = self.videos_infos[self.videos_current_index][3]
        self.axe_audio_power.set_title(label=videopath,
                                       fontsize=14,
                                       color=sf.COLOR_TEXT_LIGHT,
                                       backgroundcolor=sf.COLOR_MENU,
                                       pad=15,
                                      )

        #Show photo with ROIs of current video
        self.show_photo_roi()

        # ReDraw whole figure self.main_fig
        self.main_fig.canvas.draw()


        #####################################################
    def onkey(self, event):
        "Method to start methods from keyboard and not from button"

        switcher = {"+": "self.plus_y_axis_audio(event)",
                    "*": "self.auto_y_axis_audio(event)",
                    "-": "self.minus_y_axis_audio(event)",
                    "up": "self.plus_y_axis_motion(event)",
                    "!": "self.auto_y_axis_motion(event)",
                    "down": "self.minus_y_axis_motion(event)",
                    "B": "self.time_backward(event)",
                    "b": "self.time_backward(event)",
                    "F": "self.time_forward(event)",
                    "f": "self.time_forward(event)",
                    " ": "self.time_fullscale(event)",
                    "I": "self.time_increase_scale(event)",
                    "i": "self.time_increase_scale(event)",
                    "D": "self.time_decrease_scale(event)",
                    "d": "self.time_decrease_scale(event)",
                    "left": "self.previous_video(event)",
                    "right": "self.next_video(event)",
                    "p": "self.previous_serie(event)",
                    "n": "self.next_serie(event)"
                   }

        if event.key in switcher:
            #Execute the corresponding method
            eval(switcher[event.key])

    ######################################
    def refresh_buttons(self):
        " Refresh the display of 'Next' and 'Previous' serie and video buttons"

        # Show buttons "Next serie" if more than 1 serie and not last one
        if len(self.serie_subdir_names) > 1 and self.subdir_current_index + 1 < len(self.serie_subdir_names):
            self.ax_serie_next.set_visible(True)
        else:
            self.ax_serie_next.set_visible(False)
        # Show button "Previous serie" if more than 1 serie and not first one
        if len(self.serie_subdir_names) > 1 and self.subdir_current_index > 0:
            self.ax_serie_previous.set_visible(True)
        else:
            self.ax_serie_previous.set_visible(False)
        # Show button "Next video" if more than 1 video and not last one
        if self.videos_total_nb > 1 and self.videos_current_index + 1 < self.videos_total_nb:
            self.ax_video_next.set_visible(True)
        else:
            self.ax_video_next.set_visible(False)
        # Show button "Previous video" if more than 1 video and not first one
        if self.videos_total_nb > 1 and self.videos_current_index > 0:
            self.ax_video_previous.set_visible(True)
        else:
            self.ax_video_previous.set_visible(False)

    ######################################
    def update_serie(self, _):
        "Method to update displayed informations when changing current subserie"

        #Get all values of csv file in np array self.timesec_motion
        self.roi_coord, self.timesec_motion = self.open_csv_file(os.path.join(self.videos_infos[self.videos_current_index][3], self.videos_infos[self.videos_current_index][0] + ".csv"))

        #Get time (in min) in list self.timemin from first column of self.timesec_motion
        self.timemin = self.timesec_motion[:, 0] / 60

        #SamplingFrequency (Hz)
        self.sampling_frequency = 1 / (60 * (self.timemin[2] - self.timemin[1]))

        # Initialise display limits self.motion_index_left_limit and self.motion_index_right_limit (points index of self.timemin and self.timesec_motion) to 0 and last point
        self.motion_index_left_limit = 0
        self.motion_index_right_limit = len(self.timesec_motion) - 1

        # Initialise display limits self.timemin_left_limit and self.timemin_right_limit (in min)
        self.timemin_left_limit = 0.
        self.timemin_right_limit = self.timemin[-1]

        # Initialise autoscale of XY graph
        self.autoscale_motion = True
        #Initialise Y limit of XY graph
        self.motion_upper_limit = np.amax(self.timesec_motion[:, 1:])

        # Refresh the display of buttons for serie
        self.refresh_buttons()

        #Replot the graphs
        self.replot()

    ######################################
    def previous_serie(self, _):
        "Method to go to previous subdirectory within a serie"

        if self.subdir_current_index > 0:
            # Go to next non empty subdirectory
            current_subdir = self.subdir_current_index
            current_subdir -= 1
            while not self.subdir_nb_videos[current_subdir]:
                current_subdir -= 1
                if current_subdir == 0:
                    # If no videos available in previous subdirectories then keep current
                    current_subdir = self.subdir_current_index
                    break
            self.subdir_current_index = current_subdir
            self.subdir_current_name = self.serie_subdir_names[self.subdir_current_index]
            # Current video index is sum af all videos in previous subdurectories
            self.videos_current_index = sum(self.subdir_nb_videos[:current_subdir])
            #Refresh File slider value
            self.file_slider.set_val(float(self.videos_current_index + 1))
            self.update_serie(1)     # 1 unused but function is not called without it !


    ######################################
    def next_serie(self, _):
        "Method to go to next subdirectory within a serie"

        if self.subdir_current_index + 1 < len(self.serie_subdir_names):
            # Go to next non empty subdirectory
            current_subdir = self.subdir_current_index
            current_subdir += 1
            while not self.subdir_nb_videos[current_subdir]:
                current_subdir += 1
                if current_subdir + 1 == len(self.serie_subdir_names):
                    # If no videos available in next subdirectories then keep current
                    current_subdir = self.subdir_current_index
                    break
            self.subdir_current_index = current_subdir
            self.subdir_current_name = self.serie_subdir_names[self.subdir_current_index]
        # Current video index is sum af all videos in previous subdirectories
        self.videos_current_index = sum(self.subdir_nb_videos[:self.subdir_current_index])
        #Refresh File slider value
        self.file_slider.set_val(float(self.videos_current_index + 1))
        self.update_serie(1)     # 1 unused but function is not called without it !


    ######################################
    def previous_video(self, event):
        "Method to go to previous video from button"

        #Calculates current display range (in number of points)
        xindex_range = self.motion_index_right_limit - self.motion_index_left_limit

        if self.videos_current_index:    # previous video exists
            self.videos_current_index -= 1
            #Refresh File slider value
            self.file_slider.set_val(float(self.videos_current_index + 1))

            #Get all values of csv file in np array self.timesec_motion
            self.roi_coord, self.timesec_motion = self.open_csv_file(os.path.join(self.videos_infos[self.videos_current_index][3], self.videos_infos[self.videos_current_index][0] + ".csv"))
            #Get time in list self.timemin
            self.timemin = self.timesec_motion[:, 0] / 60

            # If method is called from time_backward method, display the end of file ...
            if event == 999:
                self.motion_index_right_limit = len(self.timemin)
                if xindex_range <= len(self.timemin):
                    self.motion_index_left_limit = len(self.timemin) - xindex_range
                else:
                    self.motion_index_left_limit = 0
            # ... otherwise display from beginning of file
            else:
                self.motion_index_left_limit = 0
                if xindex_range < len(self.timemin):
                    self.motion_index_right_limit = deepcopy(xindex_range)
                else:   #if > data size
                    self.motion_index_right_limit = len(self.timemin) - 1

            # Refresh the display of buttons for serie
            self.refresh_buttons()

            #Replot the graphs
            self.replot()


    ##########################################
    def next_video(self, _):
        "Method to go to next video file from button"

        #Calculates current choosen display range (in number of points)
        xindex_range = self.motion_index_right_limit - self.motion_index_left_limit

        if self.videos_current_index + 1 < self.videos_total_nb:    # next video exists
            self.videos_current_index += 1
            #Refresh File slider value and get all values of csv file in np array self.timesec_motion
            self.file_slider.set_val(float(self.videos_current_index + 1))
            #Get all values of csv file in np array self.timesec_motion
            # self.roi_coord, self.timesec_motion = self.open_csv_file(os.path.join(self.videos_infos[self.videos_current_index][3], self.videos_infos[self.videos_current_index][0]+".csv"))
            #Get time (in min) in list self.timemin from first column of self.timesec_motion
            self.timemin = self.timesec_motion[:, 0] / 60
            # Display from beginning of file
            self.motion_index_left_limit = 0
            if xindex_range < len(self.timemin):
                self.motion_index_right_limit = deepcopy(xindex_range)
            else:
                self.motion_index_right_limit = len(self.timemin) - 1

            # Refresh the display of buttons for serie
            self.refresh_buttons()

            #Replot the graphs
            self.replot()


        ################################################
    def time_backward(self, _):
        "Method to display previous xindex_range of values along X axis, with choosen xindex_range"

        # Show forward button
        self.ax_time_forward.set_visible(True)
        # Indicate that X axes range is limited by user
        self.full_xindex_range = False
        #Calculates current display range (in number of points)
        xindex_range = self.motion_index_right_limit - self.motion_index_left_limit
        # If left X limit is reached try to go to previous video
        if self.motion_index_left_limit == 0:
            self.previous_video(999)
            return
        # Otherwise calculate new limits (in number of points)
        self.motion_index_left_limit -= xindex_range
        self.motion_index_right_limit -= xindex_range
        if self.motion_index_left_limit < 0:    # left limit reached
            self.motion_index_left_limit = 0
            self.motion_index_right_limit = deepcopy(xindex_range)
            # Hide backward button
            self.ax_time_backward.set_visible(False)
        # Calculate new limits (in min)
        self.timemin_left_limit = ((self.motion_index_left_limit + 1)/self.sampling_frequency) / 60    #set display min time value (in min)
        self.timemin_right_limit = ((self.motion_index_right_limit + 1)/self.sampling_frequency) / 60    #set display max time value (in min)
        #Replot the graphs
        self.replot()


        #######################################
    def time_forward(self, _):
        "Method to display next xindex_range of values along X axis, with choosen xindex_range"

        # Show backward button
        self.ax_time_backward.set_visible(True)
        # Indicate that X axes range is limited by user
        self.full_xindex_range = False
        #Calculates current display range (in number of points)
        xindex_range = self.motion_index_right_limit - self.motion_index_left_limit
        # If right X limit is reached try to go to next video
        if self.motion_index_right_limit == len(self.timesec_motion) - 1:
            self.next_video(None)      # call next_video with empty argument
            return
        # Otherwise calculate new limits (in number of points)
        self.motion_index_left_limit += xindex_range
        self.motion_index_right_limit += xindex_range
        if self.motion_index_right_limit > len(self.timesec_motion) - 1:   # reaching right limit
            self.motion_index_left_limit = len(self.timesec_motion) - 1 - xindex_range
            self.motion_index_right_limit = len(self.timesec_motion) - 1
            # Hide forward button
            self.ax_time_forward.set_visible(False)
        # Calculate new limits (in min)
        self.timemin_right_limit = ((self.motion_index_right_limit + 1) / self.sampling_frequency) / 60    #set display max time value (in min)
        self.timemin_left_limit = ((self.motion_index_left_limit + 1) / self.sampling_frequency) / 60    #set display min time value (in min)
        # Make sure left limit is not negative
        self.timemin_left_limit = max(self.timemin_left_limit, 0)
        #Replot the graphs
        self.replot()


    ######################################
    def time_fullscale(self, _):
        "Method to set X axis slider to full value"


        # Indicated that X axes range is full
        self.full_xindex_range = True
        # Initialise display limits self.motion_index_left_limit and self.motion_index_right_limit (index of self.timemin and self.valuesY) to 0 and full
        self.motion_index_left_limit = 0
        self.motion_index_right_limit = len(self.timemin) - 1
        # Set full axis button color to active
        self.btn_time_fullscale.color = sf.COLOR_BUTTON_ACTIVE
        # Hide Backward and Forward buttons
        self.ax_time_backward.set_visible(False)
        self.ax_time_forward.set_visible(False)
        #Replot the graphs
        self.replot()

    ######################################
    def time_increase_scale(self, _):
        "Method to increase X axis scale"

        # Indicated that X axes range is not full
        self.full_xindex_range = False
        # Initialise display limits self.motion_index_left_limit and self.motion_index_right_limit (index of self.timemin and self.valuesY) to 0 and full
        self.motion_index_left_limit = 0
        self.motion_index_right_limit = int(self.motion_index_right_limit / 2)
        # Set full axis button color to normal
        self.btn_time_fullscale.color = sf.COLOR_BUTTON
        # Show Backward and Forward buttons
        self.ax_time_backward.set_visible(True)
        self.ax_time_forward.set_visible(True)
        #Replot the graphs
        self.replot()

    ######################################
    def time_decrease_scale(self, _):
        "Method to decrease X axis scale"

        # Indicated that X axes range is not full
        self.full_xindex_range = False
        # Initialise display limits self.motion_index_left_limit and self.motion_index_right_limit (index of self.timemin and self.valuesY) to 0 and full
        self.motion_index_left_limit = 0
        self.motion_index_right_limit = int(self.motion_index_right_limit * 2)
        if self.motion_index_right_limit >= len(self.timemin):
            self.motion_index_right_limit = len(self.timemin) - 1
        #Set full axis button color to normal
        self.btn_time_fullscale.color = sf.COLOR_BUTTON
        # Show Backward and Forward buttons
        self.ax_time_backward.set_visible(True)
        self.ax_time_forward.set_visible(True)
        #Replot the graphs
        self.replot()


    ######################################
    def update_file(self, event):
        """Method to update displayed File from Fileslider usage
        """

        #Calculates current display range (in number of points)
        xindex_range = self.motion_index_right_limit - self.motion_index_left_limit

        #Get current video index from slider value (1-based)
        # makes sure slider value is 1-based
        if event < 1:
            event = 1.
            self.file_slider.set_val(1.)
        self.videos_current_index = int(event) - 1

        #Get all values of csv file in np array self.timesec_motion
        self.roi_coord, self.timesec_motion = self.open_csv_file(os.path.join(self.videos_infos[self.videos_current_index][3], self.videos_infos[self.videos_current_index][0] + ".csv"))

        #Get time (in min) in list self.timemin from first column of self.timesec_motion
        self.timemin = self.timesec_motion[:, 0] / 60

        # Initialise values to display limits self.motion_index_left_limit to 0 and self.motion_index_right_limit according to current xindex_range (if<max number of values)
        self.motion_index_left_limit = 0
        if xindex_range < len(self.timemin):
            self.motion_index_right_limit = xindex_range
        else:   #if > data size
            self.motion_index_right_limit = len(self.timemin) - 1
        # Refresh the display of buttons for serie
        self.refresh_buttons()
        #Replot the graphs
        self.replot()

    #####################################
    def audio_power_display(self, _):
        "Method called when modifying checkbox to display or not audio/power"

        # Set autoscale on
        self.autoscale_audio_power = True
        self.btn_audio_power_y_auto.color = sf.COLOR_BUTTON_ACTIVE
        #Replot the graphs
        self.replot()

    #####################################
    def plus_y_axis_audio_power(self, _):
        "Method to increase Y axis of Audio XY graph"

        self.autoscale_audio_power = False
        self.axe_audio_power_graph_upper_limit = self.axe_audio_power_graph_upper_limit / 2
        self.axe1_graph_lower_limit = 0
        if self.radiobutton_audio_power.value_selected == "Audio":     # verify if display audio is on
            self.axe1_graph_lower_limit = -self.axe_audio_power_graph_upper_limit
        self.axe_audio_power.set_ylim(self.axe1_graph_lower_limit, self.axe_audio_power_graph_upper_limit)
        self.btn_audio_power_y_auto.color = sf.COLOR_BUTTON
        self.replot()

    ##########################################
    def auto_y_axis_audio_power(self, _):
        "Method to self.autoscale Y axis of Audio XY graph"

        self.autoscale_audio_power = True
        self.axe_audio_power_graph_upper_limit = np.amax(np.abs(self.axe1_y_values))
        # self.axe_audio_power_graph_upper_limit = np.quantile(np.abs(self.axe1_y_values), 0.999)
        self.axe1_graph_lower_limit = 0
        if self.radiobutton_audio_power.value_selected == "Audio":     # verify if display audio is on
            self.axe1_graph_lower_limit = -self.axe_audio_power_graph_upper_limit
        self.axe_audio_power.set_ylim(self.axe1_graph_lower_limit, self.axe_audio_power_graph_upper_limit)
        self.btn_audio_power_y_auto.color = sf.COLOR_BUTTON_ACTIVE
        # self.main_fig.canvas.draw()
        self.replot()

    #####################################
    def minus_y_axis_audio_power(self, _):
        "Method to decrease Y axis of Audio XY graph"

        self.autoscale_audio_power = False
        self.axe_audio_power_graph_upper_limit = self.axe_audio_power_graph_upper_limit * 2
        self.axe1_graph_lower_limit = 0
        if self.radiobutton_audio_power.value_selected == "Audio":     # verify if display audio is on
            self.axe1_graph_lower_limit = -self.axe_audio_power_graph_upper_limit
        self.axe_audio_power.set_ylim(self.axe1_graph_lower_limit, self.axe_audio_power_graph_upper_limit)
        self.btn_audio_power_y_auto.color = sf.COLOR_BUTTON
        self.replot()

    ##########################################
    def auto_y_axis_motion(self, _):
        "Method to self.autoscale Y axis of Motion XY graph"

        self.autoscale_motion = True
        self.motion_upper_limit = np.amax(self.timesec_motion[self.motion_index_left_limit:self.motion_index_right_limit])
        self.axe_motion.set_ylim(0, self.motion_upper_limit)
        self.btn_motion_y_auto.color = sf.COLOR_BUTTON_ACTIVE
        self.replot()

    #####################################
    def plus_y_axis_motion(self, _):
        "Method to increase Y axis of Motion XY graph"

        self.autoscale_motion = False
        self.motion_upper_limit = self.motion_upper_limit / 2
        self.axe_motion.set_ylim(0, self.motion_upper_limit)
        self.btn_motion_y_auto.color = sf.COLOR_BUTTON
        self.replot()

    #########################################
    def minus_y_axis_motion(self, _):
        "Method to increase Y axis of Motion XY graph"

        self.autoscale_motion = False
        self.motion_upper_limit = self.motion_upper_limit * 2
        self.axe_motion.set_ylim(0, self.motion_upper_limit)
        self.btn_motion_y_auto.color = sf.COLOR_BUTTON
        self.replot()

    ########################################
    def video_players(self, _):
        "Method to select which video player to use"

        #Get which command to be used from radiobutton choice and the list of players
        self.video_player_command = self.commanddict[self.radio_videoplayers.value_selected]
        self.video_player_option = self.optiondict[self.radio_videoplayers.value_selected]


    ########################################
    def show_video(self, video_name, click_time_sec):
        """ OpenCV viewer to show selected video and ROIs starting from a specific time
        """
        # Period (delay) between first 2 consecutive frames
        period_sec = self.timesec_motion[1][0] - self.timesec_motion[0][0]
        period_milli_sec = int(round(period_sec * 1000, 0))
        period_min = period_sec / 60
        # setup video capture
        videocap = cv2.VideoCapture(video_name)
        # set reading of video at click_time_sec
        videocap.set(cv2.CAP_PROP_POS_MSEC, click_time_sec * 1000)
        # Get first image to retrieve its dimensions
        ret, frame = videocap.read()
        ratio = 0.8
        if ret:
            # Get height, width, channels of image (pixels, pixels, nb channels)
            image_height, image_width, _ = frame.shape
            # Check that image is smaller than screen or set a ratio to be around 70% of screen size
            ratio_width = 1
            ratio_height = 1
            if image_width > self.screen_width * 0.8:
                ratio_width = round(self.screen_width / (image_width * 1.2), 1)
            if image_height > self.screen_height * 0.8:
                ratio_height = round(self.screen_height / (image_height * 1.2), 1)
            # Keep the smallest ratio for both dimensions
            ratio = min(ratio_height, ratio_width)
        # New resized image dimensions
        dim_images = (int(image_width * ratio), int(image_height * ratio))
        cv2.resize(frame, dim_images, interpolation=cv2.INTER_AREA)      # image, (width,height), interpolation
        # New ROI coordinates after resize
        newcoord = []
        for coord in self.roi_coord:
            newcoord.append([(int(coord[0][0] * ratio), int(coord[0][1] * ratio)), (int(coord[1][0] * ratio), int(coord[1][1] * ratio))])
        # Creates window to display image as a video
        cv2.imshow('OpenCV video display', frame)
        cv2.moveWindow('OpenCV video display', 10, 10)
        # cv2.resizeWindow('OpenCV video display', dim_images[0], dim_images[1])

        # Creates an image with legend, ROIs rectangles and index
        legend_image = np.zeros((dim_images[1], dim_images[0], 3), np.uint8)
        mycolor = sf.color_generator(False)     # starts color generator
        for index, coord in enumerate(newcoord):
            roi_color_rgb = next(mycolor)
            # Reverse RGB color to BGR for opencv
            roi_color = (roi_color_rgb[2], roi_color_rgb[1], roi_color_rgb[0])
            # Draw ROI(s)
            cv2.rectangle(img=legend_image,
                          pt1=coord[0],
                          pt2=coord[1],
                          color=roi_color,
                          thickness=1,
                          )
            x_text = int(coord[0][0] + (coord[1][0] - coord[0][0]) / 10)           # calculates first sixth X coordinates of ROI (Xright-Xleft)
            y_text = int(coord[0][1] + (coord[1][1] - coord[0][1]) / 6)           # same for Y
            # Write ROI(s) index
            cv2.putText(img=legend_image,
                        text=str(index + 1),
                        org=(x_text, y_text),
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=0.8,
                        color=roi_color,
                        thickness=2,
                        )
        # Add legend
        # Calculates size in pixels of "Quit" text to display at 10 pixels from borders
        quit_text_size, _ = cv2.getTextSize(text="(Q)uit",
                                            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                                            fontScale=0.6,
                                            thickness=2,
                                            )
        cv2.putText(img=legend_image,
                    text="(Q)uit",
                    org=(10, quit_text_size[1] + 10),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=0.6,
                    color=(0, 255, 0),
                    thickness=2,
                    )
        # Create mask to broadcast on each video frame
        sum_image = np.sum(legend_image, axis=2)
        mask_image = sum_image[:, :] > 0

        key = -1
        # Calculates size in pixels of time display text
        time_text_size, _ = cv2.getTextSize(text="11.11 min",
                                            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                                            fontScale=0.8,
                                            thickness=2,
                                            )
        # Calculate 50% of resized image width minus text width (make sure it is positive)
        display_x_coordinates_50_percent = max(int((dim_images[0] - time_text_size[0]) / 2), 0)
        # Set tuple of coordinates
        display_time_coordinates = (display_x_coordinates_50_percent, time_text_size[1] + 10)
        # Set time in min of first displayed frame
        frame_time_min = click_time_sec / 60 - period_min
        # Loop through all video frames
        while key < 0:
            ret, frame0 = videocap.read()
            frame_time_min += period_min
            if ret:
                frame = cv2.resize(frame0, dim_images, interpolation=cv2.INTER_AREA)
                # Add legend
                frame[mask_image, :] = legend_image[mask_image, :]
                # Add time in min
                cv2.putText(img=frame,
                            text=f"{frame_time_min:.2f} min",
                            org=display_time_coordinates,
                            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                            fontScale=0.8,
                            color=(0, 255, 0),
                            thickness=2,
                            )
                cv2.imshow('OpenCV video display', frame)
            key = cv2.waitKey(period_milli_sec)

        # End of video display
        videocap.release()  # release capture
        cv2.destroyAllWindows()

        return


    ########################################
    def close_window(self, _):
        "Method to close the Graph result window"

        plt.close()


################## STARTING FUNCTION ###############################################################
def open_graph(screen_width, screen_height):
    "Starting function"

    ############### CREATION OF INSTANCE OF CLASS INDEX TO START THE GRAPH PAGE
    # Call the Index class and pass arguments
    callback = Index(screen_width, screen_height)

    #MOUSE CLICK ANYWHERE ON THE FIGURE
    callback.main_fig.canvas.mpl_connect('button_press_event', callback.onclick)

    #BUTTON DISPLAY AUDIO OR POWER
    callback.radiobutton_audio_power.on_clicked(callback.audio_power_display)

    #BUTTON INCREASE AUDIO Y AXIS
    callback.btn_audio_power_y_plus.on_clicked(callback.plus_y_axis_audio_power)

    #BUTTON AUTOSCALE AUDIO Y AXIS
    callback.btn_audio_power_y_auto.on_clicked(callback.auto_y_axis_audio_power)

    #BUTTON DECREASE AUDIO Y AXIS
    callback.btn_audio_power_y_minus.on_clicked(callback.minus_y_axis_audio_power)

    #BUTTON INCREASE MOTION Y AXIS
    callback.btn_motion_y_plus.on_clicked(callback.plus_y_axis_motion)

    #BUTTON AUTOSCALE MOTION Y AXIS
    callback.btn_motion_y_auto.on_clicked(callback.auto_y_axis_motion)

    #BUTTON DECREASE MOTION Y AXIS
    callback.btn_motion_minus.on_clicked(callback.minus_y_axis_motion)

    #CHECK BUTTONS TO DISPLAY PLOTS
    callback.check_roi.on_clicked(callback.set_roi_checkbuttons_properties)

    #BUTTON PREVIOUS VIDEO
    callback.btn_video_previous.on_clicked(callback.previous_video)

    #BUTTON NEXT VIDEO
    callback.btn_video_next.on_clicked(callback.next_video)

    #BUTTON PREVIOUS SERIE
    callback.btn_serie_previous.on_clicked(callback.previous_serie)

    #BUTTON NEXT SERIE
    callback.btn_serie_next.on_clicked(callback.next_serie)

    #RADIOBUTTONS VIDEO PLAYERS
    callback.radio_videoplayers.on_clicked(callback.video_players)

    #BUTTON BACKWARD
    callback.btn_time_backward.on_clicked(callback.time_backward)

    #BUTTON FORWARD
    callback.btn_time_forward.on_clicked(callback.time_forward)

    #BUTTON TIME TO FULL SCALE
    callback.btn_time_fullscale.on_clicked(callback.time_fullscale)

    #BUTTON INCREASE TIME SCALE
    callback.btn_time_increase_scale.on_clicked(callback.time_increase_scale)

    #BUTTON INCREASE TIME SCALE
    callback.btn_time_decrease_scale.on_clicked(callback.time_decrease_scale)

    #SLIDER FOR FILES
    callback.file_slider.on_changed(callback.update_file)

    #KEYBOARD USAGE
    callback.main_fig.canvas.mpl_connect('key_press_event', callback.onkey)

    #CLOSE WINDOW
    callback.btn_close.on_clicked(callback.close_window)

    plt.show()

###############################################################
# FOR DEBUG, SCRIPT STARTED IN TERMINAL
if __name__ == '__main__':
    open_graph(1800, 800)
