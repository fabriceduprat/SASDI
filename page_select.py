# -*- coding: utf-8 -*-
"Sasdi module to display page and select video files and ROIs"

import os                   # standard library
import sys                  # standard library
import tkinter as tk        # standard library
from tkinter import filedialog, messagebox
import select_roi
import sasdi_functions as sf
import graph_results


class Select(tk.Frame):  # Class of page select
    "Class to draw page and select videos and ROIs"

    # constructor with parent tk frame = menu_frame, controller instance = SasdiContainer instance
    def __init__(self, parent, controller):

        # Get attributs from parent class
        (self.sasdi_version,
         self.images_extensions_lower,
         self.images_extensions,
         self.screen_width,
         self.screen_height,
         self.main_fullpath
         ) = controller.get_parameters()

        # INITIALISE NEW ATTRIBUTS
        self.main_fullpath = []
        self.list_videos = []
        self.stats_videos = []

        # Creates tkinter sub window
        tk.Frame.__init__(self, parent)

        ########## Buttons frames
        menu_frame = tk.Frame(self,
                              borderwidth=3,
                              width=int(0.9 * self.screen_width),
                              height=int(0.1 * self.screen_height),
                              relief=tk.RAISED,
                              background=sf.COLOR_MENU,
                             )   # Main top Frame
        menu_frame.pack(side="top", expand=True, padx=20, pady=(10, 1))
        menu_frame.pack_propagate(False)

        # MENU
        menu_btn_frame = tk.Frame(menu_frame,
                                  borderwidth=2,
                                  relief=tk.RIDGE,
                                  background=sf.COLOR_MENU,
                                 )   #frame with navigation buttons

        lbl_left = tk.Label(menu_frame,
                            text="SASDI v" + self.sasdi_version,
                            font=sf.FONT_TITLE,
                            background=sf.COLOR_MENU,
                            foreground=sf.COLOR_TEXT_LIGHT,
                            borderwidth=0,
                            relief=tk.FLAT,
                           )
        lbl_left.pack(side="left", expand=True, padx=10, pady=10)

        photoimg = tk.PhotoImage(file=os.path.join(sys.path[0], "images", "graphs.png"))
        lbl_right = tk.Label(menu_frame, image=photoimg, borderwidth=0)
        lbl_right.image = photoimg   # keep a reference
        lbl_right.pack(side="right", expand=True, padx=10, pady=10)

        # NAVIGATION BUTTONS CALLING SPECIFIED CLASS
        button1 = tk.Button(menu_btn_frame,
                            text="Select",
                            font=sf.FONT_BUTTON,
                            state="active",
                            background=sf.COLOR_BUTTON_ACTIVE,
                            activebackground=sf.COLOR_BUTTON_ACTIVE,
                            command=lambda: controller.show_frame("Select"),
                            )
        button2 = tk.Button(menu_btn_frame,
                            text="Detect",
                            font=sf.FONT_BUTTON,
                            state="normal",
                            background=sf.COLOR_BUTTON,
                            activebackground=sf.COLOR_BUTTON_ACTIVE,
                            command=lambda: controller.show_frame("Detect"),
                            )
        button3 = tk.Button(menu_btn_frame,
                            text="Results",
                            font=sf.FONT_BUTTON,
                            state="normal",
                            background=sf.COLOR_BUTTON,
                            activebackground=sf.COLOR_BUTTON_ACTIVE,
                            command=lambda: graph_results.open_graph(self.screen_width, self.screen_height),
                            )
        button4 = tk.Button(menu_btn_frame,
                            text="Help",
                            font=sf.FONT_BUTTON,
                            state="normal",
                            background=sf.COLOR_BUTTON,
                            activebackground=sf.COLOR_BUTTON_ACTIVE,
                            command=lambda: sf.user_guide(self.sasdi_version),
                            )
        button5 = tk.Button(menu_btn_frame,
                            text="Exit",
                            font=sf.FONT_BUTTON,
                            state="normal",
                            background=sf.COLOR_BUTTON,
                            activebackground=sf.COLOR_BUTTON_ACTIVE,
                            command=lambda: sf.exit_sasdi(),
                           )
        button1.pack(side="left", padx=5, pady=10)
        button2.pack(side="left", padx=5, pady=10)
        button3.pack(side="left", padx=5, pady=10)
        button4.pack(side="left", padx=5, pady=10)
        button5.pack(side="left", padx=5, pady=10)

        menu_btn_frame.pack(side="left", expand=True, padx=10, pady=10)

        # PAGE
        tools_frame = tk.Frame(self,
                               borderwidth=3,
                               width=int(0.9 * self.screen_width),
                               height=int(0.85 * self.screen_height),
                               relief=tk.RAISED,
                               background=sf.COLOR_BACKGROUND,
                              )
        tools_frame.pack(side="top", expand=True, padx=10, pady=5)
        tools_frame.pack_propagate(False)

        ##### Specific frames
        sel_file_frame = tk.Frame(tools_frame,
                                  width=0.8 * self.screen_width,
                                  height=0.35 * self.screen_height,
                                  borderwidth=0,
                                  relief=tk.FLAT,
                                  background=sf.COLOR_BACKGROUND,
                                 )
        sel_file_frame.pack(padx=50, pady=(20, 5), side="top")
        sel_file_frame.pack_propagate(False)

        # ////////////////////////////// FRAMES AND BUTTON FOR FILES SELECTION /////////
        # LABEL "Videos to analyse : "
        mytext = "Select at least one video (accepted extensions: " + ", ".join(ext for ext in self.images_extensions_lower) + ")"
        label_title = tk.Label(sel_file_frame,
                               text=mytext,
                               font=sf.FONT_LABEL,
                               background=sf.COLOR_MENU,
                               foreground=sf.COLOR_TEXT_LIGHT,
                               borderwidth=2,
                               relief=tk.RAISED,
                              )
        label_title.pack(side="top", padx=10, pady=10)

        # FRAME FOR SELECT FILES BUTTONS
        file_btn_frame = tk.Frame(sel_file_frame,
                                  borderwidth=2,
                                  relief=tk.RIDGE,
                                  background=sf.COLOR_BACKGROUND,
                                 )
        file_btn_frame.pack(side="left", padx=10, pady=10)

        #LISTBOX TO DISPLAY SELECTED FILE(S) LIST
        self.listbox_files = tk.Listbox(sel_file_frame,
                                        width=120,
                                        height=30,
                                        background=sf.COLOR_LISTBOX,
                                        selectbackground=sf.COLOR_TEXT_SELECT,
                                        borderwidth=2,
                                        relief=tk.SUNKEN,
                                        font=sf.FONT_LISTBOX,
                                        selectmode=tk.SINGLE,
                                       )
        self.listbox_files.pack(side="left", padx=10, pady=10)

        # BUTTON "Select a directory"
        self.btn_select_dir = tk.Button(file_btn_frame,
                                        text="Select a directory",
                                        font=sf.FONT_BUTTON,
                                        background=sf.COLOR_BUTTON,
                                        activebackground=sf.COLOR_BUTTON_ACTIVE,
                                        command=lambda: self.select_videos('directory'),
                                       )
        self.btn_select_dir.pack(side="top", padx=10, pady=10)

        # BUTTON "Select some Videos"
        self.btn_select_video = tk.Button(file_btn_frame,
                                          text="Select some videos",
                                          font=sf.FONT_BUTTON,
                                          background=sf.COLOR_BUTTON,
                                          activebackground=sf.COLOR_BUTTON_ACTIVE,
                                          command=lambda: self.select_videos('files'),
                                         )
        self.btn_select_video.pack(side="top", padx=10, pady=10)

        # BUTTON "Select a serie"
        self.btn_select_serie = tk.Button(file_btn_frame,
                                          text="Select a serie",
                                          font=sf.FONT_BUTTON,
                                          background=sf.COLOR_BUTTON,
                                          activebackground=sf.COLOR_BUTTON_ACTIVE,
                                          command=self.select_serie,
                                         )
        self.btn_select_serie.pack(side="top", padx=10, pady=10)

        # BUTTON "unselect a video"
        self.btn_unselect_video = tk.Button(file_btn_frame,
                                            text="Unselect a video",
                                            font=sf.FONT_BUTTON,
                                            background=sf.COLOR_BUTTON,
                                            activebackground=sf.COLOR_BUTTON_ACTIVE,
                                            command=self.unselect
                                           )
        self.btn_unselect_video.pack(side="top", padx=10, pady=10)

        # BUTTON "Refresh"
        self.btn_refresh_video = tk.Button(file_btn_frame,
                                           text="Refresh",
                                           font=sf.FONT_BUTTON,
                                           background=sf.COLOR_BUTTON,
                                           activebackground=sf.COLOR_BUTTON_ACTIVE,
                                           command=lambda: self.refresh_selected_files(newselection=0),
                                          )
        self.btn_refresh_video.pack(side="top", padx=10, pady=10)


        # //////////// FRAMES AND BUTTON FOR ROI SELECTION /////////////////////

        # GLOBAL FRAME sel_roi_frame
        sel_roi_frame = tk.Frame(tools_frame,
                                 width=int(0.8 * self.screen_width),
                                 height=int(0.35 * self.screen_height),
                                 borderwidth=0,
                                 relief=tk.FLAT,
                                 background=sf.COLOR_BACKGROUND,
                                )
        sel_roi_frame.pack(padx=50, pady=(20, 5), side="top")
        sel_roi_frame.pack_propagate(False)

        # LABEL "Please select at least one ROI..."
        label_info = tk.Label(sel_roi_frame,
                              borderwidth=2,
                              relief=tk.RAISED,
                              text="For each directory, you can select 1 to 8 ROIs (one for each animal zone)",
                              font=sf.FONT_LABEL,
                              background=sf.COLOR_MENU,
                              foreground=sf.COLOR_TEXT_LIGHT,
                             )
        label_info.pack(side="top", padx=10, pady=10)

        # FRAME FOR SELECT ROI BUTTONS
        roi_btn_frame = tk.Frame(sel_roi_frame,
                                 borderwidth=2,
                                 relief=tk.RIDGE,
                                 background=sf.COLOR_BACKGROUND,
                                )
        roi_btn_frame.pack(side="left", padx=10, pady=10)

        #LISTBOX TO DISPLAY ROI(S) LIST
        self.listbox_roi = tk.Listbox(sel_roi_frame,
                                      width=120,
                                      height=30,
                                      font=sf.FONT_LISTBOX,
                                      selectbackground=sf.COLOR_TEXT_SELECT,
                                      background=sf.COLOR_LISTBOX,
                                      borderwidth=2,
                                      relief=tk.SUNKEN,
                                      selectmode=tk.SINGLE,
                                     )
        self.listbox_roi.pack(side="left", padx=10, pady=10)

        # BUTTON "Select new ROIs"
        self.btn_select_roi = tk.Button(roi_btn_frame,
                                        text="Select new ROIs",
                                        font=sf.FONT_BUTTON,
                                        state="active",
                                        background=sf.COLOR_BUTTON,
                                        activebackground=sf.COLOR_BUTTON_ACTIVE,
                                        command=self.select_new_roi,
                                       )
        self.btn_select_roi.pack(padx=10, pady=10, side="top")

        # BUTTON "Reselect serie ROIs"
        self.btn_reselect_serie_roi = tk.Button(roi_btn_frame,
                                                text="Reselect subseries ROIs",
                                                font=sf.FONT_BUTTON,
                                                state="disable",
                                                background=sf.COLOR_BUTTON,
                                                activebackground=sf.COLOR_BUTTON_ACTIVE,
                                                command=self.reselect_serie_roi,
                                                )
        self.btn_reselect_serie_roi.pack(padx=10, pady=10, side="top")


        # VARIABLES FOR CONTROL
        # self.filename = tk.StringVar(value='results')
        # self.fps = tk.StringVar()

        # Start functions
        self.refresh_selected_files(newselection=0)   # Display last selection of video
        self.show_roi(roi_type="previous")


    #################  METHODS #############################

    def select_videos(self, input_type):
        """ INPUT input_type = 'directory' or multiple 'files',
            GET all videos shortnames,
            SAVE directory name to lastdir.txt,
            SAVE infos of valid videos to list_videos.json,
            GET infos in self.list_videos and statistics in self.stats_videos,
            Refresh display in listbox
        """

        # Delete serie file
        if os.path.isfile(os.path.join(sys.path[0], 'params', 'infos_serie.json')):
            os.remove(os.path.join(sys.path[0], 'params', 'infos_serie.json'))
        # Indicate that ROI(s) is from previous selection
        self.show_roi(roi_type="previous")

        # Clear listbox to display informations
        self.listbox_files.delete(0, "end")
        # List for selected videos short filenames
        video_files = []
        # Get serie main directory full path
        self.main_fullpath = sf.read_from_lastdir()

        if input_type == 'directory':   # Input from a directory
            #Dialog to select a directory
            self.path_dir = filedialog.askdirectory(title="Choose a directory with videos to analyse",
                                                    initialdir=self.main_fullpath
                                                    )
            if os.path.isdir(self.path_dir):
                # Normalise pathname and set it in main_fullpath
                self.main_fullpath = os.path.normpath(self.path_dir)
                self.listbox_files.insert(tk.END, "")
                self.listbox_files.insert(tk.END, f" >>>> PLEASE WAIT, ANALYSING FILES OF {self.main_fullpath} ...")
                self.update_idletasks()
                # video_files = list of all files
                video_files = os.listdir(self.main_fullpath)

        elif input_type == 'files':   # Input from multiple files
            # Format the list of accepted image extensions
            extensions = "*." + " *.".join(ext for ext in self.images_extensions)
            # Dialog to select multiple files
            inputfiles = filedialog.askopenfilenames(defaultextension='.asf',
                                                     filetypes=[("Video files", extensions), ("All files", "*.*")],
                                                     parent=self,
                                                     title="Select some video files",
                                                     multiple=True,
                                                     initialdir=self.main_fullpath
                                                    )
            #Get the path and filenames in a list
            path_filenames = list(inputfiles)
            # Start if there is at least 1 file to analyse
            if path_filenames:
                self.listbox_files.insert(tk.END, "")
                self.listbox_files.insert(tk.END, " >>> ANALYSING SELECTED VIDEO(S), PLEASE WAIT ...")
                self.update_idletasks()
                # Get pathname only
                self.main_fullpath = os.path.dirname(path_filenames[0])
                # Get filenames only without path
                for name in path_filenames:
                    video_files.append(os.path.basename(name))

        else:  # no argument passed
            self.listbox_files.delete(0, "end")
            self.listbox_files.insert(tk.END, " ************************ You have not selected any video ... ********************")
            self.update_idletasks()
            return

        # In both cases (directory and multiple files):

        # Eliminate files without accepted extension
        for index, _ in enumerate(video_files):
            if not video_files[index].endswith(self.images_extensions):
                video_files.pop(index)

        # Save the directory name
        sf.save_to_lastdir(self.main_fullpath)

        # Sort list of video short filenames
        video_files.sort()     #sort the list in ascending order
        # Save valid selected videos infos to list_videos.json
        # Get self.list_videos: [0]:video filename, [1]:fps, [2]:nb_frames, [3]:pathname, [4]:index, [5]:status ('A', '-')
        # Get self.stats_videos (int): [0]:total number, [1]:to analyse, [2]:analysed, [3]:corrupted
        self.list_videos, self.stats_videos = sf.save_get_list_videos(self.main_fullpath, video_files)

        # Refresh display in listbox
        self.refresh_selected_files(newselection=1)


    def select_serie(self):
        """ GET main directory path, first level subdirectories and all videos shortnames,
            SAVE main directory full path and then all subdirectories short name to infos_serie.json,
            SAVE directory name to lastdir.txt,
            SAVE infos of valid videos to list_videos.json,
            GET infos in self.list_videos and statistics in self.stats_videos,
            Refresh display in listbox and ROI list
        """

        # Get serie main directory full path
        self.main_fullpath = sf.read_from_lastdir()

        #Dialog to select the main serie directory
        self.listbox_files.delete(0, "end")
        self.main_fullpath = filedialog.askdirectory(title="Choose the main directory of the serie to analyse",
                                                     initialdir=self.main_fullpath
                                                     )
        if os.path.isdir(self.main_fullpath):
            self.listbox_files.insert(tk.END, "")
            self.listbox_files.insert(tk.END, " >>>> PLEASE WAIT, ANALYSING VIDEO(S) OF SELECTED SERIE FROM :")
            self.listbox_files.insert(tk.END, f" >>>> {self.main_fullpath} ...")
            self.update_idletasks()
            # Normalise parent serie path
            self.main_fullpath = os.path.normpath(self.main_fullpath)

            # Save main serie directory to lastdir.txt
            sf.save_to_lastdir(self.main_fullpath)

            # Save valid selected videos infos to list_videos.json and serie main dir and subdir to infos_serie.json
            _, _, _ = sf.update_serie()

            # By default using each subserie video dimensions as ROI coordinates
            sf.create_serie_roi()
            # Update ROIs display
            self.show_roi(roi_type="series")
            # Update videos infos in listbox
            self.refresh_selected_files(newselection=1)

        else:
            self.listbox_files.delete(0, "end")
            self.listbox_files.insert(tk.END, " ************************ You have not selected any valid serie ... ********************")


    def unselect(self):
        """ Unselect one video file and remove it from list_videos.json and displayed list
        """

        listbox_index = self.listbox_files.curselection()[0]     # Get index of selected line
        if listbox_index >= 9:
            try:
                self.listbox_files.delete(listbox_index)
                list_index = int(listbox_index) - 9                     # Index in list is minus header length
                self.list_videos.pop(list_index)
                # Save valid selected videos infos to list_videos.json
                # Get list_videos: [0]:video filename, [1]:nb frames, [2]:duration, [3]:pathname, [4]:index, [5]:status ('A', '-', 'M', 'C')
                # Get stats_videos (int): [0]:total number, [1]:to analyse, [2]:analysed, [3]:modified fps, [4] corrupted
                self.list_videos, self.stats_videos = sf.save_get_list_videos(self.main_fullpath, [info[0] for info in self.list_videos])
                self.refresh_selected_files(newselection=0)                   #refresh listbox with files
            except IndexError:
                messagebox.showwarning('WARNING', 'Please select one video file ')


    def refresh_selected_files(self, newselection):
        """Display in listbox the newly selected files (newselection=1),
           or refresh previous selection (newselection=0)
        """

        self.update_idletasks()
        # Delete listbox content
        self.listbox_files.delete(0, "end")
        # Get main directory full path
        self.main_fullpath = sf.read_from_lastdir()

        # SERIE DISPLAY: show subserie directories names and number of files
        if os.path.exists(os.path.join(sys.path[0], 'params', 'infos_serie.json')):

            # If serie choosen then disable "unselect a video", "Select new ROI", and "Delete selected ROI" buttons
            self.btn_unselect_video["state"] = "disable"
            self.btn_select_roi["state"] = "disable"
            self.btn_reselect_serie_roi["state"] = "normal"

            # Update serie infos
            self.list_videos, self.stats_videos, self.serie_subdir_names = sf.update_serie()

            # PREVIOUSLY SELECTED FILES, REFRESH INFOS, (ELSE NEW SELECTION, USE SELF INFOS)
            if newselection == 0:
                self.show_roi(roi_type="previous")
            else:
                # Refresh ROIs display
                self.show_roi(roi_type="new")

            # DISPLAY SERIE INFOS
            if (self.main_fullpath != "" and self.serie_subdir_names):
                # Display serie infos in listbox
                grand_total = 0
                self.listbox_files.insert(tk.END, f"  You have selected the serie <{self.main_fullpath}> containing the following subseries:")
                for subdir_index, subdir_name in enumerate(self.serie_subdir_names):
                    stats = self.stats_videos[subdir_index]
                    grand_total = grand_total + stats[1] + stats[2]
                    self.listbox_files.insert(tk.END, f" <{subdir_name}>: {stats[0]} total video files with:")
                    self.listbox_files.insert(tk.END, f"     {stats[1]} to analyse (_),")
                    self.listbox_files.insert(tk.END, f"     {stats[2]} already analysed (A),")
                    self.listbox_files.insert(tk.END, f"     {stats[3]} with user modified fps or number of frames (M),")
                    self.listbox_files.insert(tk.END, f"     {stats[4]} corrupted files (C)")
                self.listbox_files.insert(tk.END, f"  Legend : (status) #index = <subserie> 'filename' (fps, duration)")
                self.listbox_files.insert(tk.END, "  ==========================================================================")
                self.listbox_files.insert(tk.END, "  Note that unselecting a video is not permitted within series selection.")
                self.listbox_files.insert(tk.END, f"  List of found video files :")
                for file_info in self.list_videos:
                    if file_info[1]:
                        duration_sec = round(file_info[2] / file_info[1])
                    else:
                        duration_sec = 0
                    # [0]:video filename     [1]:fps        [2]:nb frames    [4]:video index+1      [5]:status          [6]:subdir index 
                    self.listbox_files.insert(tk.END, f"({file_info[5]}) #{file_info[4] + 1:<4}= <{self.serie_subdir_names[file_info[6]]}> '{file_info[0]}' (fps: {file_info[1]}, duration: {sf.format_duration(duration_sec)})")

            else:
                self.listbox_files.delete(0, "end")
                self.listbox_files.insert(tk.END, "  ***** No videos found in that directory, please reselect ********************")

        # NOT A SERIE DISPLAY
        else:
            # Not a serie then enable "unselect a video", "Select new ROI", and "Delete selected ROI" buttons
            self.btn_unselect_video["state"] = "normal"
            self.btn_select_roi["state"] = "normal"
            self.btn_reselect_serie_roi["state"] = "disable"

            # PREVIOUSLY SELECTED FILES, REFRESH INFOS, (ELSE NEW SELECTION, USE SELF INFOS)
            if newselection == 0:
                # Get list of videos
                # [0]:video filename, [1]:fps, [2]:duration, [3]:pathname, [4]:index, [5]:status ('A', '-')
                self.list_videos, message = sf.read_list_videos()
                print(message)
                # Get self.list_videos: [0]:video filename, [1]:fps, [2]:duration, [3]:pathname, [4]:index, [5]:status ('A', '-', 'M', 'C')
                # Get self.stats_videos (int): [0]:total number, [1]:to analyse, [2]:analysed, [3]:modified fps, [4] corrupted
                self.list_videos, self.stats_videos = sf.save_get_list_videos(self.main_fullpath, [val[0] for val in self.list_videos])
                intro = "  Previously selected videos from the directory <"
                # Refresh ROIs display
                self.show_roi(roi_type="previous")
            else:
                intro = "  Selection from the directory <"
                # Refresh ROIs display
                self.show_roi(roi_type="previous")

            # DISPLAY INFOS
            if self.list_videos:
                # Display list of videos infos in listbox
                self.listbox_files.insert(tk.END, f"{intro}{self.main_fullpath}> :")
                self.listbox_files.insert(tk.END, f"  {self.stats_videos[0]} total video files with:")
                self.listbox_files.insert(tk.END, f"      {self.stats_videos[1]} to analyse (_),")
                self.listbox_files.insert(tk.END, f"      {self.stats_videos[2]} already analysed (A),")
                self.listbox_files.insert(tk.END, f"      {self.stats_videos[3]} with user modified fps or number of frames (M),")
                self.listbox_files.insert(tk.END, f"      {self.stats_videos[4]} corrupted files (C)")
                self.listbox_files.insert(tk.END, f"  Legend : (status) #index = 'filename' (fps, duration)")
                self.listbox_files.insert(tk.END, " ==========================================================================")
                self.listbox_files.insert(tk.END, f"  List of found video files:")
                for file_info in self.list_videos:
                # [0]:video filename  [1]:fps    # [2]:nb frames [4]:video index+1  [5]:status
                    if file_info[1]:
                        duration_sec = round(file_info[2] / file_info[1])
                    else:
                        duration_sec = 0
                    self.listbox_files.insert(tk.END, f"({file_info[5]}) #{file_info[4] + 1:<4}= '{file_info[0]}' (fps: {file_info[1]}, duration: {sf.format_duration(duration_sec)})")

            else:      # No video found, NOT A SERIE DISPLAY
                self.listbox_files.delete(0, "end")
                self.listbox_files.insert(tk.END, "  ***** No valid video found, please select at least one video ********************")


    def select_new_roi(self):
        " Get first selected video, call select_roi.py to enable selection of new ROI(s), save them"
        if self.list_videos:
            # Start select_roi with first video of list
            path_video = os.path.join(self.list_videos[0][3], self.list_videos[0][0])
            # list with roi (read first element of returned list)
            roi_coord, _ = sf.read_roi_coord()
            # no previously selected roi coordinates
            if not roi_coord:
                roi_coord = [[[(100, 100), (1000, 1000)],],]
            message = ""
            selected_roi, message = select_roi.click(path_video, self.screen_width, self.screen_height, roi_coord, self.list_videos[0][0])
            # Add in a list to keep the same format as series
            selected_roi = [selected_roi]
            if message:
                # Error selecting roi
                messagebox.showwarning('WARNING', message)
            else:
                # Save selected ROI coordinates to roi_coord.json
                sf.save_roi_coord(selected_roi)
                self.show_roi(roi_type="new")
        else:
            messagebox.showwarning('WARNING', 'Please select at least one video !')


    def reselect_serie_roi(self):
        " For each serie subdirectory call select_roi.py to enable selection of new ROI(s)"

        # Get main directory fullpath and subdirectory shortnames lists
        main_fullpath = sf.read_from_lastdir()
        serie_subdir_names = sf.read_infos_serie()
        # Get current serie ROIs
        previous_roi, _ = sf.read_roi_coord()
        # From selected videos list get first video for each subdirectory
        full_serie_roi = []
        for index_subdir, subdir in enumerate(serie_subdir_names):
            # get list of video infos of current subdir
            subdir_video_info = [video_info for video_info in self.list_videos if video_info[6] == index_subdir]
            if not subdir_video_info:
                # Use previously saved one(s)
                full_serie_roi.append(previous_roi[index_subdir])
                continue
            else:
                # [0]:video filename, [1]:fps (float), [2]:duration (int), [3]:pathname, [4]:video index (int), [5]:status ('A', '-'), ++ [6]:subdir index (int)
                first_filename = subdir_video_info[0][0]
                # Start select_roi
                path_video = os.path.join(main_fullpath, subdir, first_filename)
                message = ""
                subdir_selected_rois, message = select_roi.click(path_video, self.screen_width, self.screen_height, previous_roi, subdir)
                if message:        # Error selecting roi in current subdir
                    # No ROI selected for this subdir
                    if previous_roi[index_subdir]:
                        # Use previously saved one(s)
                        full_serie_roi.append(previous_roi[index_subdir])
                        messagebox.showwarning('WARNING', f"Using previous ROI for <{subdir}> : {message}")
                    else:
                        messagebox.showwarning('WARNING', f"No ROI selected for <{subdir}> : {message}")
                else:
                    # ROI(s) were selected
                    full_serie_roi.append(subdir_selected_rois)

        # Save all ROI coordinates to roi_coord.json
        sf.save_roi_coord(full_serie_roi)
        self.show_roi(roi_type="new")

    def show_roi(self, roi_type):
        """  Get selected ROIs from roi_coord.json and display in selectbox listRoi
             Argument roi_type : "previous"=using previously saved ROI, "new"=newly selected ROI
        """
        # list with roi (read first element of returned list)
        roi_coord, message = sf.read_roi_coord()
        # Clear listbox
        self.listbox_roi.delete(0, "end")
        # Display error message
        if not message:
            self.listbox_roi.insert(tk.END, message)
        # Display if no coordinates found
        if not roi_coord:
            self.listbox_roi.insert(tk.END, "No ROI selected")
            return

        # Start display in ListBox
        # NOT A SERIE DISPLAY
        # ROIs lists are in roi_coord[0]
        if not os.path.exists(os.path.join(sys.path[0], 'params', 'infos_serie.json')):
            if roi_type == "previous":         # no new ROi selected, using saved one
                self.listbox_roi.insert(tk.END, f" Using {len(roi_coord[0])} previously saved ROI(s) :")
            else:       # using newly selected ROI
                self.listbox_roi.insert(tk.END, f" You have selected {len(roi_coord[0])} ROI(s) :")
            # In both case display list of ROIs
            self.listbox_roi.insert(tk.END, "")
            for i, _ in enumerate(roi_coord[0]):
                self.listbox_roi.insert(tk.END, f"    ROI[{i + 1}] --> {' , '.join([str(coord) for coord in roi_coord[0][i]])}")
        # SERIE DISPLAY
        # There is a ROIs list for each subdir roi_coord[0], roi_coord[1, ...]
        else:
            # Get subdirectory shortnames lists
            serie_subdir_names = sf.read_infos_serie()
            # By default using each subserie video dimensions as ROI coordinates
            self.listbox_roi.insert(tk.END, "  SERIE ANALYSIS")
            self.listbox_roi.insert(tk.END, "  Default ROIs are full size of first valid video for each subserie, standard selection is disabled")
            self.listbox_roi.insert(tk.END, "  Click 'Reselect subseries ROIs' if you need to reselect ROIs (max 8), you will be prompted for each subserie.")
            self.listbox_roi.insert(tk.END, "  Legend: **Subserie <subserie name>     ROI[roi index] ----> [x_topleft, y_topleft], [x_bottomright, y_bottomright]")
            for subdir_index, subdir_name in enumerate(serie_subdir_names):
                self.listbox_roi.insert(tk.END, f"**Subserie <{subdir_name}>")
                for roi_index, coordinates in enumerate(roi_coord[subdir_index]):
                    self.listbox_roi.insert(tk.END, f"      ROI[{roi_index + 1}] ----> {' , '.join([str(coord) for coord in coordinates])}")
