# Operation

The code pretty much follows tutorials available in the OpenCV documentation.  
So, let's follow what happens when you run `tracker_main.py`:  
## 1., Read the config file using `process_config_file()` from `config_file_reader.py`
`process_config_file()` is an implementation of `ConfigParser`, and I am assembling the corresponding sections of the specified `.ini` file to a `dict()` and an `array` of `dict`s. `general_settings` contains information set in the `[General]` section, and `markers` has the same dict defined in each section for each marker. These values are returned when the function is called. 

##  2., Prepare inter-thread communication, and start the server thread
Inter-thread communication is done via `Queue()` objects. The server will bind to a port specified in the config file, and `tracker_server()` from `server_thread.py` is started as a separate thread. Within the thread, there is a loop that constantly waits for an incoming packet.  
Once a packet **containing anything** is received, the latest state of the `markers` array will be read out from the main thread. After converting the values to plain text, the response packet payload is assembled. Once the payload is known, two packets are being sent back to the address the query packet:  
**Packet 1** contains a 16-bit number, which is the length of the next datagramm packet in bytes.  
**Packet 2** is the latest tracker data, in plain-text format. You can dump this packet, and save it as a .csv file.  
Furthermore, there is a killswitch in the loop: if the port specified in `general_settings["server_udp_port"]` becomes a different number than the port the server was started at, the server thread will terminate. Since `recvfrom()` for UDP is blocking (as in, it hangs the loop until it received data), a packet might need to be sent to the server for it to terminate.

## 3., Initialise camera, load the markers and extract features
The camera matrix and the distortion coefficients are being generated from the specified options in the config file. [Read about calibration here.](CALIBRATION.md) Afterwards, the feature detector `ORB` is initialised, as well as the `BFmatcher` feature matcher algorithm.  
Then, for each marker, the features (key points and descriptors) are being calculated.

## 4., For each frame...
And lastly, for each frame, the following sequence is executed:
* Identify feature matches between the camera's image and the marker's image.
* Keep the good quality matches only, as specified by `marker_minimum_matching_distance` in the config file
* Copy the mean value of the coordinates of the matches to a `deque()` object used as a FIFO, and calculate the running average by taking the mean value of the numbers in the FIFO. Pass these 2D centroid coordinates over to the server thread.
* If there are enough matches (as per `marker_minimum_number_of_matches` in the config file), calculate the coordinates of the matches in the marker, with respect to its dimensions. Since a marker a 2D images, all 3D points will be on the Z=0 plane.
* If there are enough matches, calculate the `translation` coordinates and the `rotation` angles using SolvePNP. If successful, shove the latest data into a `deque()` object used as a FIFO.
* Calculate the running average by taking the mean value of the contents of the FIFO, and send the data over to the server thread.
* If the marker in question is not visible, or could the pose estimation failed, send NaNs to the server thread, and clear contents the `deque()` objects holding the translation, rotation and 2D centroid data.
* If set in the config file (by setting `camera_show_picture` to 1), show the matches and 2D centroid to the user.

# I want to know more...
There are lots of comments in the code itself. Also, have you checked the [FAQ?](FAQ.md)