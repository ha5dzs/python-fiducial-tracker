# This function loads the config file and processes it.
# It returns two things:
#   1., general_settings is a dict, where camera and miscellaneous settings were defined
#   2., markers is an array of dicts, which contains specific settings for the markers themselves.
import configparser as cp #This is needed for reading the config file
import numpy as np #NumPy, because we can
import copy #dicts have mutable variables, I need to clone them.

def process_config_file(config_file_name):
    configs = cp.ConfigParser()
    configs.read(config_file_name) #Read the config file as a dictionary
    config_section_names = configs.sections() #Read in the section names.
    assert config_section_names != 'General', "The 'General' section does not exist in the config file!"
    general_settings = dict()
        #Number of markers
    general_settings["no_of_markers"] = np.int_(len(configs) - 2) #The first entry is the general settings
        #Camera ID
    general_settings["camera_id"] = np.int_(configs['General']['camera_id']) #We need to know which camera to use.
        #Camera focal lengths for camera matrix
    general_settings["camera_focal_length_x"] = np.float_(configs['General']['camera_focal_length_x'])
    general_settings["camera_center_x"] = np.float_(configs['General']['camera_center_x'])
    general_settings["camera_focal_length_y"] = np.float_(configs['General']['camera_focal_length_y'])
    general_settings["camera_center_y"] = np.float_(configs['General']['camera_center_y'])
        #Camera distortion coefficients
    general_settings["camera_k1"] = np.float_(configs['General']['camera_dist_coeff_k1'])
    general_settings["camera_k2"] = np.float_(configs['General']['camera_dist_coeff_k2'])
    general_settings["camera_p1"] = np.float_(configs['General']['camera_dist_coeff_p1'])
    general_settings["camera_p2"] = np.float_(configs['General']['camera_dist_coeff_p2'])
    general_settings["camera_k3"] = np.float_(configs['General']['camera_dist_coeff_k3'])
        #Display camera image
    general_settings["camera_show_picture"] = np.int_(configs['General']['camera_show_picture'])
        #Server port, converted to an integer, not a script.
    general_settings["server_udp_port"] = np.int_(configs['General']['server_udp_port'])
        #Now load marker parameters. We can have an arbitrary amount of markers, so we have to fill up the info from the config file.
    #no_of_markers = int(general_settings["no_of_markers"]) #get this out here temporarily
    markers = [] #init array.
    marker_info = dict() #This will contain the particulars of a marker
    for i in range(0, int(general_settings["no_of_markers"])):
        #section 0 is 'General', so we won't need to worry about it.
        #marker_info.clear #clear the variable
        marker_info["name_string"] = config_section_names[i+1]
        marker_info["file_name"] = configs[marker_info["name_string"]]['marker_file_name']
        marker_info["width"] = np.int_(configs[marker_info["name_string"]]['marker_width'])
        marker_info["height"] = np.int_(configs[marker_info["name_string"]]['marker_height'])
        marker_info["minDistance"] = np.int_(configs[marker_info["name_string"]]['marker_minimum_matching_distance'])
        marker_info["minMatches"] = np.int_(configs[marker_info["name_string"]]['marker_minimum_number_of_matches'])
        #How long the running average filter should be
        marker_info["fifo_length"] = np.int_(configs[marker_info["name_string"]]['pose_estimation_running_average'])
        #Colours are are a different kettle of fish.
        marker_info["feature_colour"] = ( np.int_(configs[marker_info["name_string"]]['marker_feature_colour_B']), np.int_(configs[marker_info["name_string"]]['marker_feature_colour_G']), np.int_(configs[marker_info["name_string"]]['marker_feature_colour_R']) )
        marker_info["indicator_colour"] = ( np.int_(configs[marker_info["name_string"]]['marker_indicator_colour_B']), np.int_(configs[marker_info["name_string"]]['marker_indicator_colour_G']), np.int_(configs[marker_info["name_string"]]['marker_indicator_colour_R']) )
        #Now that we have the data, toss it to the array. This method is slow, but we only need it once.
        markers.append(copy.deepcopy(marker_info)) #If we do it this way, no entry will be overwritten.

#print "Config file read and processed."
    #Return the variables
    return general_settings, markers
