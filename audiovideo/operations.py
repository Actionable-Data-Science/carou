##########################################################################
# Copyright 2020 Deniz Iren. All Rights Reserved.

__name__ = 'file.operations'
__author__ = 'Deniz Iren (deniziren@gmail.com)'
__version__ = '0.001'
__lastupdate__ = '10.11.2019'

def version():
	return __version__
	
def lastUpdate():
	return __lastupdate__

def name():
	return __name__

def packageInfo():
	return 'Package name: ' + __name__ + ' | ' + 'Version: ' + __version__ + ' | ' + 'Author: ' + __author__
	
def getName():
	return name

## Important dependencies: 
# ffmpeg must be installed separately. 

##########################################################################

import csv
import subprocess
import math
import json
import os
import shlex
from optparse import OptionParser
import time

#ffmpeg -i example.mp4 -ss 10 -t 20 second-10-sec.mp4

def getLength(input_audio_video):
    '''Gets the URL of an audio/video file. Returns the duration of the recording in the unit of seconds.'''
    if os.path.isfile(input_audio_video):
        result = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', input_audio_video], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return float(result.stdout)
    else:
        print('File not found!') 
        return -1

def split_video_file_into_chunks(video_input, chunk_duration, split_out_dir, verbose=False):
    """Splits a given audio or video file into a number of chunks of given length. 
    The final chunk may differ in size due to the length of the original file not being a denominator of the desired chunk size
    Inputs:
    video_input: string. The path to the input audio/video file
    chunk duration: float. The desired duration of the chunks in seconds.
    split_out_dir: The target directory to save the chunks. If this directory does not exist, the method creates it.

    Returns: 
    The output directory. 
    """
    ## Check the validity of the input parameters
    
    # Check video_input
    if not os.path.isfile(video_input):
        print('File not found!') 
        return -1

    # Check if the output directory exists. If not, create it.
    if not os.path.isdir(split_out_dir):
        print('Output directory not found. Creating...')
        os.mkdir(split_out_dir)

    # Get the video length
    video_len = getLength(video_input)
    
    # Calculate the number of chunks to be created
    start = 0
    end = chunk_duration
    no_of_chunks = math.ceil(video_len / chunk_duration)

    for split_index in range(no_of_chunks):
        if (split_index+1)*chunk_duration <= video_len:
            video_output = split_out_dir + generateChunkOutputFileName(video_input, split_index)
            cmds = ['ffmpeg', '-i', video_input, '-ss', str(start), '-t', str(chunk_duration),  video_output]
            if verbose:
                print(cmds)
            subprocess.Popen(cmds)
            time.sleep(5) # this is needed. However, if the CPU is strong, you can decrease this value.
            start = end
            end = end + chunk_duration
        else:
            chunk_duration = video_len - (split_index)*chunk_duration  
            end = video_len
            video_output = split_out_dir +generateChunkOutputFileName(video_input, split_index)
            cmds = ['ffmpeg', '-i', video_input, '-ss', str(start), '-t', str(chunk_duration),  video_output]
            if verbose:
                print(cmds)
            subprocess.Popen(cmds)
    print('split into ', str(no_of_chunks), 'chunks. Output: ', split_out_dir)
    return split_out_dir

def generateChunkOutputFileName(video_input, split_index):
    """Generates a filename for a chunk of the original file, using the original file name and the chunk index.
    This method needs to be called every time when a new chunk is being created. 

    Inputs:
    video_input: string. The path to the input audio/video file
    split_index: The index of the current chunk.

    Outputs:
    the new filename for the chunk
    """
    filename, file_extension = os.path.splitext(video_input)
    return os.path.basename(filename) + '_' + str(split_index).zfill(3) + file_extension

def crop_audio_video(infile, start, duration, outfile, verbose=False):
    """
    Crops an audio/video file. 

    Inputs: 
    infile: The path to the input file to be cropped. 
    start: The start index in seconds. 
    duration: The duration of the cropped new audio/video. The output will be from the start index to start+duration. 
    outfile: The target file to write the cropped new file. 

    Outputs:
    The path to the new created file.
    """
    ## Check the validity of the input parameters
    
    # Check video_input
    if not os.path.isfile(infile):
        print('File not found!') 
        return -1
    
    cmds = ['ffmpeg', '-i', infile, '-ss', str(start), '-t', str(duration),  outfile]
    if verbose:
        print(cmds)
    subprocess.Popen(cmds)
    #subprocess.call(cmds)  ## call() is an alternative to Popen(). call() blocks the process, Popen() does not block. 
    print("File cropped: ", outfile)

def convert_audio_video(video_input, video_output):
    """
    Converts the given audio/video file. Simply specify a different file extension to make the conversion. 
    
    Inputs:
    video_input: The source audio/video file.
    video_output: Target audio/video file. 

    Returns:
    The path to the new file. 
    """
    # Check video_input
    if not os.path.isfile(video_input):
        print('File not found!') 
        return -1
    try:
        cmds = ['ffmpeg', '-i', video_input, video_output]
        
        ## this is how you specify a codec. In the future, we can make this call parametric and use something like the following. 
        #cmds = ['ffmpeg', '-i', video_input, '-ac', '1', '-ar', '16000', video_output] # we should probably make these values parametric when we need to change them. 
        
        # Note that we use sbprocess.call instead of subprocess.Popen. 
        # The reason is that .call blocks the process until the external operation (ffmpeg conversion in this case) finishes. 
        # If we do not block, then the following code which relies on the converted file will attempt to execute before the file is ready. 
        # So, block away...
        subprocess.call(cmds)
        
        print('Conversion complete: ', video_output)
        return(video_output)
    except Exception as e:
        print(e)


def check_video_integrity(video_input):
    """UNTESTED! """
    print('check_video_integrity >>> THIS IS AN UNTESTED METHOD. PLEASE MAKE SURE IT WORKS.')
    try:
        cmds = ['ffmpeg', '-v', 'error', '-i', video_input, '-f', 'null', '-', '2>test.log']
        subprocess.Popen(cmds)
        print('done')
    except Exception as e:
        print(e)
