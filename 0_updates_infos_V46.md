1/7/2021

MODIFICATIONS IN 4.6
Adapt to python version 3.13, using moviepy instead of ffprobe, display bugs in graph_results corrected

MODIFICATIONS IN 4.4
Finalising user guide, make test_sasdi script

MODIFICATIONS IN 4.3
Using FFprobe video duration if wrong fps, properly closing graph window (avoid old window to appear)

MODIFICATIONS IN 4.1
Delete sasdi-directory as argument in functions, sort file and subdir names in series,
reduce serie buttons, correct version read, add forced fps value if wrong fps

MODIFICATIONS IN 4.0

Change names to conform to PEP8
Vectorisation of most functions and code simplification
All exceptions catched properly
Modern interface with color template using constants and visible custom colors for graphs

page_select:
    Display stats on file selection, and all selected files infos
    Add ROIs selection for serie, enable/disable buttons, enhance ROI coordinates display
select_roi:
    Get and display last selection, limit selection to 8, visualise ROIs, display infos on image
page_detect:
    Analysis in multiple threads with choosen number, analysis code in a separate module, serie analysis with different ROIs
graph_results:
    Hide/show buttons according to context, enable specific ROIs plot display, enhanced serie display, OCV videoplayer with ROIs infos, time, and colors, enable sum of power display

MODIFICATIONS IN 3.6 :
PageSelect:
    Add statistics of various selected files
    Display file duration in days hours min sec
Click_mouse:
    Repair delete last ROI function
GraphResults:
    Show image ROI read video until a non null frame is found
Help:
Add scrollbar, advices

MODIFICATIONS IN 3.5 :
Main:
    Add terminal rename to sasdi version
Click_mouse:
    Image for ROI selection decreased to 70% of screen
    Image resize bug corrected
PageDetect :
    Motion calculated on L channel of LAB image
    Motion normalised as % of maximal motion (pixels x 255), ATTENTION : Valid for 8bits image only
    Height of main container decreased to 85% of screen instead of 99%
    Add update to listbox with Tk.update_idletasks()
GraphResults:
    Motion Y graph limit calculated from max without x cvalues (bug)
    Add roi drawing and Quit text for OCV video reader
