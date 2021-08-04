import unittest
import os
import sys
import json
import platform
import subprocess
from pkgutil import iter_modules
# code to test
import video_analysis


class SimpleTestCase(unittest.TestCase):

    def test_packages(self):
        "Test if required packages are installed"

        def module_exists(module_name):
            return module_name in (name for loader, name, ispkg in iter_modules())

        test_passed = True
        required_packages = {
                             "cv2": "opencv-python",
                             "cycler": "cycler",
                             "ffprobe": "ffprobe",
                             "matplotlib":"matplotlib",
                             "numpy": "numpy",
                             "scipy": "scipy",
                             }

        for package_name, pip_name in required_packages.items():
            if not module_exists(package_name):
                print(f"Needed package not installed, use command >pip install {pip_name} (or conda install {pip_name} if using anaconda)")
                test_passed = False
        assert test_passed, "Needed package import error"

    def test_read_write(self):
        "Test of reading/writing to parameters.json"

        test_passed = True
        params_pathfile = os.path.join(sys.path[0], 'params', 'parameters.json')
        try:
            with open(params_pathfile, 'r') as filereader:
                myparams = json.load(filereader)
        except IOError as json_error:
            print(f"Error reading {params_pathfile}")
            test_passed = False
        if myparams:
            try:
                with open(params_pathfile, 'w') as filewriter:
                    filewriter.write(json.dumps(myparams, indent=""))
            except IOError as json_error:
                print(f"Error writing to {params_pathfile}")
                test_passed = False
        assert test_passed, "Read/Write error to params/parameters.json, check file is present and not corrupted"

    def test_video_analysis(self):
        "Test of video analysis script with defaultvideo.mp4"
        # 4 ROIs set for defaultvideo.mp4"
        roi_coord = [[[0, 0], [500, 580]], [[501, 0], [998, 580]], [[0, 585], [500, 1158]], [[503, 583], [998, 1158]]]
        # [0]:video filename, [1]:fps, [2]:nb frames, [3]:pathname, [4] roi coordinates of corresponding subdir (0 if not a serie), [5]:"to analyse" video index, [6] total number of analysed videos
        data = ["defaultvideo.mp4", 15, 300, os.path.join(sys.path[0], "params"), roi_coord, 0, 1]
        sum_intensities = video_analysis.one_video_analysis(data)
        sum_intensities = round(sum_intensities, 1)
        assert (367. < sum_intensities < 369.), f"Video analysis error, sum {sum_intensities} not in range 367-369"

    def test_vlc_video_open(self):
        "Test reading defaultvideo.mp4 with vlc"

        # Get os system ("Windows", "Linux", "Darwin" for MacOS, ...)
        current_os = platform.system()
        video_pathname = os.path.join(sys.path[0], "params", "defaultvideo.mp4")
        # linux
        if current_os == "Linux":
            mycommand = ["vlc", video_pathname]
        # windows
        if current_os == "Windows":
            vlc_path = ""
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
            mycommand = [vlc_path, "file:///" + video_pathname]
        # Mac
        if current_os == "Darwin":   # Mac TO BE CHECKED
            vlc_path = os.path.join("Applications", "VLC.app", "Contents", "MacOS", "VLC")
            mycommand = [vlc_path, video_pathname]
        # Test opening video
        if mycommand:
            try:
                proc = subprocess.Popen(mycommand)
            except:
                test_passed = False
            else:
                test_passed = True
                proc.kill()
        else:
            print("Path to VLC not found")
            test_passed = False
        assert test_passed, "Error with vlc video viewer, check vlc is installed"


if __name__ == "__main__":
    unittest.main() # run all tests