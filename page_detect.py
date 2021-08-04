# -*- coding: utf-8 -*
"Sasdi module to display page and start video analysis"

import os                               # standard library
import sys                              # standard library
import tkinter as tk                    # standard library
import tkinter.ttk as ttk
import time                             # standard library
import multiprocessing

import graph_results
import video_analysis
import sasdi_functions as sf


class Detect(tk.Frame):
    "Class with seizure detection and analysis page, inherit from parents classes tk.Frame"

    # constructor with parent tk frame = main_frame, controller instance = SasdiContainer instance
    def __init__(self, parent, controller):

        # Creates tkinter sub window
        tk.Frame.__init__(self, parent)

        # Get infos from parent class
        (self.sasdi_version,
         self.images_extensions_lower,
         self.images_extensions,
         self.screen_width,
         self.screen_height,
         self.last_dir) = controller.get_parameters()

        # INITIALISE NEW ATTRIBUTS
        self.list_videos = []

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
                            text="SASDI v"+self.sasdi_version,
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
                            state="normal",
                            background=sf.COLOR_BUTTON,
                            activebackground=sf.COLOR_BUTTON_ACTIVE,
                            command=lambda: controller.show_frame("Select"),
                            )
        button2 = tk.Button(menu_btn_frame,
                            text="Detect",
                            font=sf.FONT_BUTTON,
                            state="active",
                            background=sf.COLOR_BUTTON_ACTIVE,
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

        #LABEL
        label_title = tk.Label(tools_frame,
                               text="Start motion detection on selected videos with selected ROIs",
                               font=sf.FONT_LABEL,
                               background=sf.COLOR_MENU,
                               foreground=sf.COLOR_TEXT_LIGHT,
                               borderwidth=2,
                               relief=tk.RAISED,
                              )
        label_title.pack(side="top", padx=10, pady=20)

    #############  FRAME FOR ANALYSIS #########
        #Subframe with progress bar and button start
        self.frame_start = tk.Frame(tools_frame,
                                    width=int(0.2 * self.screen_width),
                                    height=int(0.2 * self.screen_height),
                                    borderwidth=2,
                                    relief=tk.RIDGE,
                                    background=sf.COLOR_BACKGROUND,
                                   )
        self.frame_start.pack(side="left", expand=True, padx=5, pady=5)
        self.frame_start.pack_propagate(False)


        #BUTTON START
        self.btn_start = tk.Button(self.frame_start,
                                   height=4,
                                   width=10,
                                   text="Start detection",
                                   state="normal",
                                   font=sf.FONT_BUTTON,
                                   background=sf.COLOR_BUTTON,
                                   activebackground=sf.COLOR_BUTTON_ACTIVE,
                                   command=self.start_analysis,
                                  )
        self.btn_start.pack(side="top", pady=10, padx=10)

        # CHECK BUTTON FOR REANALYSING
        self.check_reanalyse = tk.IntVar()
        self.check_btn_reanalyse = tk.Checkbutton(self.frame_start,
                                                  text="Allow reanalyse",
                                                  variable=self.check_reanalyse,
                                                  onvalue=1,
                                                  offvalue=0,
                                                  font=sf.FONT_BUTTON,
                                                  background=sf.COLOR_BUTTON,
                                                  activebackground=sf.COLOR_BUTTON_ACTIVE,
                                                 )
        self.check_btn_reanalyse.pack(side="top", padx=10, pady=10)

        #Subframe for thread choice
        self.frame_threads = tk.Frame(tools_frame,
                                      width=int(0.2 * self.screen_width),
                                      height=int(0.2 * self.screen_height),
                                      borderwidth=2,
                                      relief=tk.RIDGE,
                                      background=sf.COLOR_BACKGROUND,
                                      )
        self.frame_threads.pack(side="left", expand=True, padx=5, pady=5)
        self.frame_threads.pack_propagate(False)

        self.max_number_threads = multiprocessing.cpu_count()

        # LABEL1 OF THREAD CHOICE
        label_threads1 = tk.Label(self.frame_threads,
                                  text=f"Number of threads to use (total={self.max_number_threads})",
                                  font=sf.FONT_LABEL,
                                  background=sf.COLOR_MENU,
                                  foreground=sf.COLOR_TEXT_LIGHT,
                                  borderwidth=2,
                                  relief=tk.RAISED,
                                  )
        label_threads1.pack(side="top", padx=10, pady=20)

        # COMBOBOX TO CHOOSE NUMBER OF THREADS
        thread_nb_choice = ["auto"] + list(range(1, self.max_number_threads + 1))
        self.combo_choice_number_process = ttk.Combobox(self.frame_threads,
                                                        values=thread_nb_choice,
                                                        justify='center',
                                                        width=6,
                                                        state='normal'
                                                        )
        self.combo_choice_number_process.pack(side="top", padx=10, pady=10)
        self.combo_choice_number_process.current(0)   # Set current value to first

        # LABEL2 OF THREAD CHOICE
        self.label_threads2 = tk.Label(self.frame_threads,
                                       text=f"auto={round(self.max_number_threads * 0.8)} (80%) with max 1 thread/video",
                                       font=sf.FONT_LABEL,
                                       background=sf.COLOR_MENU,
                                       foreground=sf.COLOR_TEXT_LIGHT,
                                       borderwidth=2,
                                       relief=tk.RAISED,
                                       )
        self.label_threads2.pack(side="top", padx=10, pady=20)

        ################################# LOWER RIGHT FRAME FOR MESSAGE BOX (LISTBOX) ########################################
        self.frame_infos = tk.Frame(tools_frame,
                                    width=int(0.3 * self.screen_width),
                                    height=int(0.2 * self.screen_height),
                                    borderwidth=2,
                                    relief=tk.RIDGE,
                                    background=sf.COLOR_BACKGROUND,
                                    )
        self.frame_infos.pack(side="left", expand=True, padx=5, pady=5)
        self.frame_infos.pack_propagate(False)
        #LISTBOX = MESSAGEBOX
        self.listbox_infos = tk.Listbox(self.frame_infos,
                                        width=120,
                                        height=30,
                                        font=sf.FONT_LISTBOX,
                                        selectbackground=sf.COLOR_TEXT_SELECT,
                                        background=sf.COLOR_LISTBOX,
                                        borderwidth=2,
                                        relief=tk.SUNKEN,
                                        selectmode=tk.SINGLE,
                                        )
        self.listbox_infos.pack(side="bottom", padx=10, pady=10)



    #############################################################################################################
    ############################################# METHODS OF CLASS DETECT #######################################
    #############################################################################################################

    def update_listbox(self, videorank, nbvideos, time_analysis):
        " Updating listbox, arguments videorank (int), nbvideos (int), time_analysis (float))"

        if videorank == 0:
            self.listbox_infos.delete(0, "end")
            self.listbox_infos.insert(tk.END, " ")
            self.listbox_infos.insert(tk.END, f" Starting analysing {nbvideos} video(s)...")
            self.listbox_infos.insert(tk.END, " See terminal for more informations")
        if videorank == nbvideos:
            self.listbox_infos.delete(0, "end")
            self.listbox_infos.insert(tk.END, " ")
            self.listbox_infos.insert(tk.END, "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ")
            self.listbox_infos.insert(tk.END, f"   ANALYSIS OF {nbvideos} VIDEO(S) COMPLETED IN {sf.format_duration(int(time_analysis))}")
            self.listbox_infos.insert(tk.END, "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ")
            self.listbox_infos.insert(tk.END, " ")
        self.update_idletasks()


    def start_analysis(self):
        "Initialisation for videos analysis, started with BUTTON START"

        # Get selected ROIs coordinates in roi_coord
        roi_coord, message = sf.read_roi_coord()
        if message != "":
            tk.messagebox.showwarning(message)

        # Get list of videos
        self.list_videos, message = sf.read_list_videos()
        if message != "":
            print(message)

        # If videos and ROI coordinates present then start analysis
        if not self.list_videos:
            tk.messagebox.showwarning('WARNING', 'Please select at least one video to analyse')
        elif not roi_coord:
            tk.messagebox.showwarning('WARNING', 'Please select at least one ROI')
        else:
            # Number of videos to analyse
            nb_videos = 0
            list_videos_to_analyse = []
            for video_infos in self.list_videos:
                # for info: [0]:video filename, [1]:fps, [2]:nb frames, [3]:pathname, [4]:file index, [5]:status ('A', '-', 'M', 'C'), [6]:subdir index
                if video_infos[5] != 'C':
                    #csv_fullpathname = os.path.join(video_infos[3], video_infos[0] + ".csv")
                    #if self.check_reanalyse.get() == 0 and os.path.exists(csv_fullpathname):
                    if self.check_reanalyse.get() == 0 and video_infos[5] == 'A':
                        # reanalyse not asked and file already analysed
                        continue
                    else:
                        # For each video file, generate a list with specific infos needed for analysis
                        list_videos_to_analyse.append([video_infos[0], video_infos[1], video_infos[2], video_infos[3], roi_coord[video_infos[6]], nb_videos])
                        nb_videos += 1
            # Add total number of videos to analyse to each video list infos
            # [0]:video filename, [1]:fps, [2]:nb frames, [3]:pathname, [4] roi coordinates of corresponding subdir (0 if not a serie), [5]:"to analyse" video index, [6] total number of analysed videos
            list_videos_to_analyse = [infos + [nb_videos] for infos in list_videos_to_analyse]

            if not list_videos_to_analyse and self.list_videos:
                tk.messagebox.showwarning('WARNING', 'All videos are already analysed, please tick "Allow reanalyse"')
            else:
                # Get present time
                process_start_time = time.time()
                # Update listbox
                self.update_listbox(0, nb_videos, 0)
                choice_number_process = self.combo_choice_number_process.get()
                if choice_number_process == "auto":
                    # Update auto value
                    number_process = int(self.max_number_threads * 0.8)   # 80% of available threads
                    number_process = min(len(list_videos_to_analyse), number_process)   # Max 1 thread / video to analyse
                    print(f" Auto = {number_process} thread(s)")
                else:
                    number_process = int(choice_number_process)
                with multiprocessing.Pool(processes=number_process) as pool:
                    # Analyse each video in one process
                    pool.map(func=video_analysis.one_video_analysis,
                             iterable=list_videos_to_analyse
                            )

                print("Exiting Main Thread. ANALYSIS FINISHED")
                #Calculate process duration in sec and display it
                fullprocessduration = time.time() - process_start_time
                # Update listbox
                self.update_listbox(nb_videos, nb_videos, fullprocessduration)
