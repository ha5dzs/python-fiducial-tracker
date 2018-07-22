% This code evaluates udp communication between the tracker and Matlab.
% The function 'udp()' is in the instrument control toolbox, so make sure it is
% accessible.
clear all
clc



host = '127.0.0.1'; %Change this to wherever
port = 8472;

udp_object = udp(host, port);


fopen(udp_object);

%Send something
fwrite(udp_object, 'Nobody cares what this text is.')

%Read out how many bytes the packet will be
length_info = fread(udp_object, 2); 

%Calculate how many bytes the info will be
length_of_packet = length_info(2)*255 + length_info(1);

%Read the next packet
raw_packet_data = fread(udp_object, length_of_packet);

%Convert the raw data to readable string. We need to rotate the matrix
readily_available_data = char(raw_packet_data')


fclose(udp_object)