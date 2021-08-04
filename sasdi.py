# -*- coding: utf-8 -*-
"Sasdi main starting script"

import os                       # standard library
import tkinter as tk            # standard library
import sys                      # standard library
# print(f"DEBUG Python version {sys.version}")
import sasdi_functions as sf

from page_select import Select
from page_detect import Detect

class SasdiContainer(tk.Tk):
    " Main class defining main_frame of all pages"

    def __init__(self):

        # Get SASDI version
        self.sasdi_version, _, _, _ = sf.read_parameters()

        # If possible rename terminal window with sasdi name and version
        try:
            sys.stdout.write("\x1b]2; SASDI v"+self.sasdi_version+"\x07")
        except:
            pass

        # Check params directory exists
        if not os.path.exists(os.path.join(sys.path[0], "params")):
            os.mkdir(os.path.join(sys.path[0], "params"))
        # Check images directory exists
        if not os.path.exists(os.path.join(sys.path[0], "images")):
            os.mkdir(os.path.join(sys.path[0], "images"))
        # Check lastdir file exists
        if not os.path.exists(os.path.join(sys.path[0], 'params', 'lastdir.txt')):
            with open(os.path.join(sys.path[0], 'params', 'lastdir.txt'), 'w') as filewriter:
                filewriter.write("c:"+os.sep)

        # Creates tkinter Main window
        tk.Tk.__init__(self)

        # Set window title
        self.title("SASDI - Semi Automatic Seizure Detection on Images")
        # Get screen dimensions in pixels
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()

        # FRAME main_frame contains all the pages on top of each others
        main_frame = tk.Frame(self,
                              width=int(self.screen_width * 0.99),
                              height=int(self.screen_height * 0.85),
                              borderwidth=0,
                              relief=tk.FLAT,
                              bg=sf.COLOR_BACKGROUND,
                              )

        main_frame.pack(side="left", expand=True, padx=5, pady=5)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        self.frames = {}        # dict containing page instances {name page: frame instance}
        for page_frame in (Select, Detect):
            page_name = page_frame.__name__
            frame = page_frame(main_frame, self)        # Pages are frame instances, placed in the main main_frame
            self.frames[page_name] = frame              # put frame instance in the dict
            frame.grid(row=0, column=0, sticky="nsew")  # all frames have the same location

        self.show_frame("Select")                     # Place Select Files page on top

#####################################
    def get_parameters(self):
        "Read and return sasdi parameters: version, accepted extensions, screen size, last used directory"

        # Get SASDI version and tuples of accepted videos extensions
        sasdi_version, _, images_extensions_lower, extensions_upper = sf.read_parameters()
        images_extensions = images_extensions_lower + extensions_upper
        # Get screen dimensions in pixels
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        # Get last used directory name
        main_fullpath = sf.read_from_lastdir()

        return sasdi_version, images_extensions_lower, images_extensions, screen_width, screen_height, main_fullpath


#####################################
    def show_frame(self, page_name):
        "Method to display page_name on top of others"

        frame = self.frames[page_name]
        frame.tkraise()              # visible page is on the top


###############################################################
# SCRIPT STARTED IN TERMINAL
if __name__ == "__main__":
    SASDI = SasdiContainer()         # instance of SasdiContainer
    SASDI.mainloop()                 # main loop to deal with events

