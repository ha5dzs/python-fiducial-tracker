from __future__ import division #I need this because I have to divide stuff
from collections import deque # This is needed for the FIFO implementation
import math # Math libs
import numpy as np # NumPy, because we can
import copy # I have mutable variables, I need to clone them.
import cv2 # OpenCV
import threading # We run the network communication stuff as a separate thread
from Queue import Queue #We use this to communicate between threads

from server_thread import tracker_server # This is the tracker server in server_thread.py
from config_file_reader import process_config_file #This is a function in config_file_reader.py


# Get the setting from the config file. These two variables are available across threads.
general_settings, markers = process_config_file('tracker_config_file.ini')

#TODO: Add freamecounter matchcounter

#Prepare the stuff to send
general_settings_to_be_shared = Queue()
markers_to_be_shared = Queue()

general_settings_to_be_shared.put(general_settings)
markers_to_be_shared.put(markers)

server_thread_handle = threading.Thread( target=tracker_server, args=(general_settings["server_udp_port"], general_settings_to_be_shared, markers_to_be_shared) )
server_thread_handle.start() #Woohoo, start the server!



#################################
# Open camera, and create camera matrix and distortion coefficients
camera = cv2.VideoCapture(general_settings["camera_id"])
    # This is the camera matrix, assembled from calibration.
camera_matrix = np.array( [[general_settings["camera_focal_length_x"], 0, general_settings["camera_center_x"]], [0, general_settings["camera_focal_length_y"], general_settings["camera_center_x"]], [0, 0, 1]], dtype = "double" )
    # Coefficients are [k1, k2, p1, p2, k3] as per OpenCV documentation
distortion_coefficients = np.array( [general_settings["camera_k1"], general_settings["camera_k2"], general_settings["camera_p1"], general_settings["camera_p2"], general_settings["camera_k3"]] )

#################################
# Detect features on the markers, compute pixel dimensions for coordinate calculation.
feature_detector = cv2.ORB_create() #Initialise the ORB feature detector.
matcher = cv2.BFMatcher(cv2.NORM_HAMMING2, crossCheck=True) #Initialise the Brute Force matcher. Change the algorithm if you think it's reasonable to do so.

    
for i in range(0, general_settings["no_of_markers"]):
    #In this loop, for each marker as defined in the config file, we:
    # 1., Load the image
    markers[i]["image_data"] = cv2.imread(markers[i]["file_name"], cv2.IMREAD_COLOR)
    # 2., Calculate pixel width and height based on specified marker dimensions
    markers[i]["height_in_px"], markers[i]["width_in_px"], _ = markers[i]["image_data"].shape
    markers[i]["pixel_width"] = markers[i]["width"] / markers[i]["width_in_px"] #Width of one pixel
    markers[i]["pixel_height"] = markers[i]["height"] / markers[i]["height_in_px"] #Height of one pixel
    # 3., Identify features (key_points and descriptors)
    markers[i]["key_points"], markers[i]["descriptors"] = feature_detector.detectAndCompute(markers[i]["image_data"], None) #Second argument is mask.
    markers[i]["matchcounter"] = 0 #this is used for the pose estimation.
    # 4., Initialise FIFOs for each marker pose data. Each FIFO length may be different.
    markers[i]["translation_fifo"] = deque(maxlen=markers[i]["fifo_length"])
    markers[i]["rotation_fifo"] = deque(maxlen=markers[i]["fifo_length"])
    markers[i]["2d_centroid_fifo"] = deque(maxlen=markers[i]["fifo_length"])

#################################
# Fetch image from camera. For each marker, do the feature matching and pose estimation.
general_settings["framecounter"] = np.uint64(0) #This is the number of frames since the start of the program
while(True):
    # Initialise the output arrays
    translations = [] #This is going to be the final result after the averaging
    rotations = [] #This is going to be the final result after the averaging

    # Get the latest camera image 
    capture_success, output_image = camera.read() #Take a picture from the camera
    
    # Identify features on the camera's image. This needs to be done once per frame.
    cam_key_points, cam_descriptors = feature_detector.detectAndCompute(output_image, None) #Second argument is mask.

    #For each marker....
    for i in range(0, general_settings["no_of_markers"]):
        #I had problems with these being overwritten.
        marker_descriptors_to_test = copy.deepcopy(markers[i]["descriptors"])
        camera_descriptors_to_test = copy.deepcopy(cam_descriptors)
        # 1., Identify matches between the camera image and the marker image.
        markers[i]["feature_matches"] = matcher.match(camera_descriptors_to_test, marker_descriptors_to_test) #OpenCV: Query image, Training image
        # 2., Sort the matches in ascending order of distance. The lower the distance, the better match it is.
        markers[i]["feature_matches"] = sorted(markers[i]["feature_matches"], key = lambda x:x.distance)
        # 3., Keep the matches no worse than what is defined in the config file.
        markers[i]["good_matches"] = []
        for j in range(0, len(markers[i]["feature_matches"])):
            if markers[i]["feature_matches"][j].distance < markers[i]["minDistance"]: #minDistance is read from the config file
                markers[i]["good_matches"].append(markers[i]["feature_matches"][j])
            # Now that we know how many good matches we have, pre-allocate the variables for matching and for the 3D coordinates.
        markers[i]["camera_matched_coords"] = np.zeros((len(markers[i]["good_matches"]), 2))
        markers[i]["marker_matched_coords"] = np.zeros((len(markers[i]["good_matches"]), 2))
        markers[i]["marker_3d_coords"] = np.zeros((len(markers[i]["good_matches"]), 3))
        # 4., Check if we have enough matches for the user
        if len(markers[i]["good_matches"]) > markers[i]["minMatches"]:
            # 5., Convert the X-Y coordinates to 3D coordinates. Since the marker images are flat, the coordinates will be in the Z=0 plane.
                # Extract what we have to work with:
            for j in range(0, len(markers[i]["good_matches"])):
                #Populate the x-y coordinates. The coordinates are integers.
                markers[i]["camera_matched_coords"][j,:] = np.int_( cam_key_points[markers[i]["good_matches"][j].queryIdx].pt )
                markers[i]["marker_matched_coords"][j,:] = np.int_( markers[i]["key_points"][markers[i]["good_matches"][j].trainIdx].pt )
                #Add the matched dots to the output image.
                if general_settings["camera_show_picture"] == 1:
                    output_image = cv2.circle(output_image, (np.int_(markers[i]["camera_matched_coords"][j][0]), np.int_(markers[i]["camera_matched_coords"][j][1])), 2, markers[i]["feature_colour"], 1)

                #Calculate the marker's 3D coordinates, which are the matched pixel coordinates on the marker image, on the Z=0 plane.
                markers[i]["marker_3d_coords"][j, :] = np.float_([ (markers[i]["marker_matched_coords"][j][0]) * markers[i]["pixel_width"], (markers[i]["marker_matched_coords"][j][1]) * markers[i]["pixel_height"], 0])

            #Shove the marker 2D centroid coordinate to the fifo
            markers[i]["2d_centroid_fifo"].append( np.mean( markers[i]["camera_matched_coords"], 0) )

            # 6., Now that we have the good quality common coordinates, we now can do the pose estimation.
            markers[i]["pose_found"], markers[i]["latest_translation"], markers[i]["latest_rotation"] = cv2.solvePnP(markers[i]["marker_3d_coords"], markers[i]["camera_matched_coords"], camera_matrix, distortion_coefficients)
            if markers[i]["pose_found"]:
                # If we got here, we found the marker location on the image.
                # Increase match counter for this marker
                markers[i]["matchcounter"] += 1
                # 7., Apply running average filter, by shoving the pose data into the FIFO, and taking the mean when we have enough data.
                markers[i]["translation_fifo"].append(markers[i]["latest_translation"])
                markers[i]["rotation_fifo"].append(markers[i]["latest_rotation"])

                #################################
                # These three variables are to be returned
                temp_mean_translation  = np.mean(np.asarray(markers[i]["translation_fifo"]), 0) #Convert the deque fifo object to an array
                    #I need to reshape this array to a format that can be shoved into a string.
                markers[i]["mean_translation"] = [ np.float_(temp_mean_translation[0]), np.float_(temp_mean_translation[1]), np.float_(temp_mean_translation[2]) ]
                temp_mean_rotation = np.mean(np.asarray(markers[i]["rotation_fifo"]), 0) #Convert the deque fifo object to an array
                markers[i]["mean_rotation"] = [ np.float_(temp_mean_rotation[0]), np.float_(temp_mean_rotation[1]), np.float_(temp_mean_rotation[2]) ]
                two_d_centroid_mean = np.mean(np.asarray(markers[i]["2d_centroid_fifo"]), 0)
                markers[i]["2d_centroid_mean"] = [ np.float_(two_d_centroid_mean[0]), np.float_(two_d_centroid_mean[1]) ]

                # Show the indicator on the screen, if required:
                if general_settings["camera_show_picture"] == 1:
                    output_image = cv2.circle(output_image, (np.int_(markers[i]["2d_centroid_mean"][0]), np.int_(markers[i]["2d_centroid_mean"][1])), 10, markers[i]["indicator_colour"], 10)



            
            else:
                #If solvePNP hasn't found the marker, we need to reset the matchcounter
                markers[i]["matchcounter"] = 0
                #....and we also need to clear the appropriate FIFO too.
                # This has to be done in two stages so the number of entries will be 0 when starting again:
                markers[i]["translation_fifo"].clear()
                markers[i]["rotation_fifo"].clear()
                markers[i]["2d_centroid_fifo"].clear()
                #Also, fill markers[i]["mean_translation"] and markers[i]["mean_rotation"] with NaNs.
                markers[i]["mean_translation"] = [np.nan, np.nan, np.nan]
                markers[i]["mean_rotation"] = [np.nan, np.nan, np.nan]
                markers[i]["2d_centroid_mean"] = [np.nan, np.nan]
        

        else:
            #Extra safety: if the marker is off the screen, reset the matchcounter too.
            markers[i]["matchcounter"] = 0
            #Clear the 2D centroid FIFO
            markers[i]["2d_centroid_fifo"].clear()
            markers[i]["mean_translation"] = [np.nan, np.nan, np.nan]
            markers[i]["mean_rotation"] = [np.nan, np.nan, np.nan]
            markers[i]["2d_centroid_mean"] = [np.nan, np.nan]


    general_settings["framecounter"] += 1 #Increment the framecounter value

    #Update the marker data, so the server thread can read it.
    markers_to_be_shared.put(markers)
    #Put this in too, so the server thread can read it continuously.
    general_settings_to_be_shared.put(general_settings)
    
    #Show whatever is in the output, if the config file says so.
    if general_settings["camera_show_picture"] == 1:
        #print output_image.shape
        cv2.imshow('Press ''q'' to quit.', output_image)
        #Check for escape character
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break #This breaks the render loop.

print "Quitting now."
#Clean up after ourselves.
cv2.destroyAllWindows() #close all OpenCV-based windows
print "Stopping server...."
#Signal the server thread to close, by changing the port it's supposed to listen in. This is our killswitch.
general_settings["server_udp_port"] = 0
general_settings_to_be_shared.put(general_settings)
server_thread_handle.join() #Stop the server
print "Letting go of the capture device..."
camera.release() #Let go of camera
