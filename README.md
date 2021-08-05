What is SASDI ?

This package is designed for neuroscience research, but can be used in other fields.
It enables to analyse a large number of video files and performs a motion analysis and display results to ease the identification of convulsive seizures in rodents models. It goes with VASD, a package that enables to acquire video from IP cameras and to perform automatically the same motion analysis as SASDI.

INSTALLING

Copy all files in a directory called "sasdi", also copy the 2 directories ("images", "params") and their contents.
Install python environment (https://www.python.org/downloads/, or https://docs.anaconda.com/), recommended versions are 3.8 or 3.9.
Install some extra packages, use the command pip install -r requirements.txt from the sasdi directory.
Install the vlc video viewer (https://www.videolan.org/vlc/).

TESTING

After installing vlc video viewer, the required packages/modules, and Sasdi please launch the test script to check everything is properly installed:
  - open a terminal
  - switch to the main sasdi directory (/sasdi/)
  - start the test by entering: python test_sasdi.py
The script will perform the following tests using "unittest" standard library module:
  1) check the presence of all required packages
  2) check the parameters files (in sasdi/params/) can be read/write
  3) check the motion analysis gives the proper value on the sasdi/params/defaultvideo.mp4 test file
  4) test vlc video viewer can be accessed and started from python script

CONFIGURING

You can manually change the default parameters in file /sasdi/params/parameters.json.
Make sure to keep the dict structure {key1: value1, key2: value2, ...}
  - max_fps : 
  The max_fps value (string) is the threshold above which sasdi considered as abnormal the fps (frames per second) read in video file header.
  If your videos present a high frame rate increase this value above your fps.
  This is important in case of file with no fps indicated in their header, sasdi will allow you to manually enter the correct fps value.
  - extensions : 
  Make sure to keep the list structure [val1, val2, ...]
  This is the list of accepted extension by sasdi, you can add other extensions but make sure they are fully compatible with opencv module (used for video analysis).
  Note that even with the accepted extension, a video file could be incompatible with opencv if your file is encoded with an unusual codec.
  If sasdi failed to open a video file, the following script allows you to test if your video file is compatible with OpenCV.
  If it returns "True" the video file is compatible and the problem comes from another source. You can try to convert to standard:
    - import cv2
    - video_pathname = "enter/the/fullpath/to/the/video/file"
    - vidcap = cv2.VideoCapture(video_pathname)
    - vidcap.isOpened()

STARTING

To start the script, type the following command in a terminal from the sasdi directory (use cd):
python sasdi.py
OR from any directory type the full path:
python complete/path/to/sasdi/sasdi.py

USER GUIDE

Run SASDI and then click on the "Help" button to get detailed instructions.

IF YOU HAVE PROBLEM WITH THE SCRIPT:

Fabrice DUPRAT: duprat@ipmc.cnrs.fr
For python packages installation and network setting, please see your network manager.
