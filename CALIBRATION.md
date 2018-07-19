# Calibration
The calibration process is pretty much like as described in the OpenCV documentation. Print out the included checkerboard, attach it to a flat and rigid surface, and start `calibrate_camera.py`. Show the checkerboard to the camera, wait until enough frames are being collected, and the new camera settings will be printed out to the console. You will need to replace the corresponding settings in the .ini file.

## Step by step instructions:
1., Print [calibration_checkerboard.pdf](calibration_checkerboard.pdf) and attach it to a rigid and flat surface, such as a clipboard
2., Run `$ python calibrate_camera.py`
3., When you see the camera's window appearing, hold the checkerboard against the camera, taking up a large piece of its field of view.
4., Wait until a sufficient number of frames are collected. When done, the camera window will disappear.
5., Copy and paste the camera settings from the console output into the config file.

# How do I know that the settings are correct?
For each calibration process, the numbers will be different. If you just use a cheap pinhole-type webcam commonly found in laptops and electronics stores, then the focal lengths should be a number around 1000. The distortion coefficients could be any number, I am generally getting values between -5 and +5.

Good luck!