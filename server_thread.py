# This is the server thread. It listens on a UDP port, and processes a few global variables when receives a packet.
import time # We need this for delay
import socket # We need this for the network functionality
import numpy as np # We need this to handle weird floating-point values, such as NaNs.
import StringIO # We need this for constructing a plain text packet payload.
import threading # We run the network communication stuff as a separate thread
from Queue import Queue #We use this to communicate between threads


# The tracker server runs as a function.
def tracker_server(port, shared_general_settings, shared_markers):
    # We need to make sure the camera and everything else is running
    time.sleep(1) #delay is one second.

    # Link variables from the main thread. This way, we can overwrite values and not do harm.
    general_settings = [] #init empty array
    general_settings = shared_general_settings.get() #get the objects from the queue
    markers = []
    markers = shared_markers.get()
    
    ip_address = "127.0.0.1" # Run on this machine
    # This line initialises the socket.
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Bind to socket, so we can receive packets
    udp_socket.bind( (ip_address, port) )

    # We need to assemble this to a string. Effectively, it will be done via CSV values.
    data_to_send = StringIO.StringIO() # Create the buffer

    server_to_run = 1

    while(server_to_run):
        # Do we have a packet?
        data, sender_address = udp_socket.recvfrom(512) #this blocks code execution while waiting.
        if data:
            # If we have data, we should assemble the packet as plain text, like in a .csv file.
            data_to_send.write("Marker name,Translation coordinates,Rotation angles,Marker centroid coordinates on the camera image,Matchcounter,Framecounter\n")
            for i in range(0, general_settings["no_of_markers"]):
                #Update to the latest marker data.
                markers = shared_markers.get() # Get the latest marker data created by the main thread
                general_settings = shared_general_settings.get() # We need this for the latest framecounter value
                
                #For each marker, we add to the string.
                data_to_send.write(markers[i]["name_string"]) # This is specified as the section header in the config file
                data_to_send.write(",")
                data_to_send.write(markers[i]["mean_translation"]) # Translation coordinates
                data_to_send.write(",")
                data_to_send.write(markers[i]["mean_rotation"]) # Rotation angles
                data_to_send.write(",")
                data_to_send.write(markers[i]["2d_centroid_mean"]) # Where the feature centroid is on the image
                data_to_send.write(",")
                #We need to convert these integers to strings first.
                data_to_send.write(str(markers[i]["matchcounter"])) # This informs that how many data points the mean is calculated from
                data_to_send.write(",")
                data_to_send.write(str(general_settings["framecounter"])) # A global framecounter, counting up
                data_to_send.write("\n")

            #Once the data has been gathered, send it back via the network.
            # Packet 1 is length. We use 16-bit integers
            packet_length = np.uint16(len(data_to_send.getvalue()))
            udp_socket.sendto(packet_length, sender_address)
            #print "The packet is ", packet_length, "bytes long."
            #packet 2 is the data.
            #print "Data is:\n", data_to_send.getvalue()
            udp_socket.sendto(data_to_send.getvalue(), sender_address)
            #Once the data has been sent, clear the data buffer.
            data_to_send.truncate(0)

        #Check if the thread should still work:
        general_settings = shared_general_settings.get() #get the objects from the queue
        if int(general_settings["server_udp_port"]) != port:
            #if we got here, it means that the main thread changed the port to listen to. This is our killswitch.
            server_to_run = 0
