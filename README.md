# Simple python fiducial tracker

This piece of code uses OpenCV to detect the position of a marker in each frame captured by the video device. Based on the physical dimensions of the marker, it does pose estimation too. For each defined marker, data is available through UDP, in the form of plain text. It returns the translation of rotation of the object with respect to the camera, and the X-Y coordinates of the 2D centroid of the object appearing on the camera's image. If a marker is not visible, the returned numbers will be a NaN.  
# Main features
* You can use **any** marker, a photo will suffice too
* Every key setting is available in a config file, which is in the standard `.ini` syntax.
* Included a camera calibration script and a .pdf file with a checkerboard. [Read on how to calibrate here.](CALIBRATION.md)
* Brutally simple network communication protocol:  
    * You can get the latest tracking data by sending ANYTHING to the port set in the config file
    * Two packets are sent back from the tracker:
        **Packet 1** is a fixed length, and contains a 16-bit integer about the packet length of...
        **Packet 2**, which contains all the configured marker information in a plain-text format.
    * You can literally dump the UDP packet as a comma separated value file.

# Quick guide to get started
You need a standard Python environment with `cv2`, and `numpy` modules available. While the code was developed using Python 2.7 and OpenCV 3.4.1 on a Mac, but it should also work with Python 3 too and other platforms too.
Here are a few steps to create a marker:
1., Take a photo of your object, and crop it. Ideally the resolution should be compatible with your camera.
2., Edit the config file, and make sure it has the following lines set:
```
[General]
```
You can leave pretty much everything the same in the general section, but you will need to calibrate your camera! [Read on how to calibrate here.](CALIBRATION.md) When adding a new marker, you will need to fine-tune the settings, so make sure that the camera's image will be visible.
```
camera_show_picture = 1
```
Otherwise, a new marker is added as a new section in the config file.  
The header is the user-friendly name of the marker
```
[My custom marker]
```
Specify the file name and the marker's physical dimensions:
```
marker_file_name = <File name in the same directory or full path>
marker_width = <Units are in mm.>
marker_height = <Units are in mm.>
```
When setting up a new marker, you will need to change the following settings:
```
marker_minimum_matching_distance = <Decrease it from 50>
marker_minimum_number_of_matches = <Set this to at least 4>
pose_estimation_running_average = <more than 1>
```
The `marker_minimum_matching_distance` is inversely proportional to the quality of the feature match between the marker image and the camera. If set too high, features outside the marker will be matched, and if set too low, no matches will be made at all.  
The `marker_minimum_number_of_matches` is required for the pose estimation. At least 4 matched points are required to calculate the `translation` coordinates and `rotation` angles. However, the more matches required for the transform, the more precise the estimation will be. If set too high, pose estimation will only work in a handful of frames.  
Lastly, the `pose_estimation_running_average` sets how many frames' position data should be averaged. Increase this number if the returned positions are too 'jerky'. However, the more frames being averaged together, the greater the lag will be.  
Furthermore, each `colour` channel can be any natural number between `0` and `255`. The `marker_feature_colour_*` items are for showing the location of the good quality matches between the marker image and the camera's image. The `marker_indicator_colour_*` settings determine the colour of a single indicator, which shows the coordinates calculated by the mean values of displayed matches. Ideally, this indicator should always be inside the marker, and is returned in the UDP packet as the `centroid`.   

```
marker_feature_colour_R = <0...255>
marker_feature_colour_G = <0...255>
marker_feature_colour_B = <0...255>
marker_indicator_colour_R = <0...255>
marker_indicator_colour_G = <0...255>
marker_indicator_colour_B = <0...255>
```
## Once everything is set up, run: `python tracker_main.py`
Good luck!

# Would you like to know more?
## [How does the tracker work?](OPERATION.md)
## [FAQ](FAQ.md)

