##########################################################################
# Copyright 2020 Deniz Iren. All Rights Reserved.
"""This module includes methods to handle file operations."""
__name__ = 'vera.emocess'
__author__ = 'Deniz Iren (deniziren@gmail.com)'
__version__ = '0.001'
__lastupdate__ = '07.06.2020'

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

##########################################################################

from pydub import AudioSegment
import requests
import json
import matplotlib.pyplot as plt
import pandas as pd
from pydub.utils import mediainfo
from carou.audiovideo.operations import getLength, convert_audio_video
import os
from IPython.display import display, HTML

def emocess(fileToEmocess, verbose=True):
	'''This function takes the path of an audio file as an input. 
	Converts the file to MP3 if it is not already in that format. Then splits and sends the data to VERA service.
	Returns a dataframe that has emovecs for rows.
	'''
    ## Get length
	filename, file_extension = os.path.splitext(fileToEmocess)
	if verbose:
		print(filename, file_extension, getLength(fileToEmocess))
    
	## Get Media Info
	if verbose:
		print(mediainfo(fileToEmocess))

    ## CONVERSION IF NECESSARY
	if len(filename) > 4:
		if '.mp3' not in file_extension:
			print('Not an MP3 file. Converting...')
			fileToEmocessSource = fileToEmocess
			fileToEmocess = fileToEmocess.replace(file_extension, '.mp3')
			print(fileToEmocessSource, ' > ', fileToEmocess)
			convert_audio_video(fileToEmocessSource, fileToEmocess)
			print('conversion complete!')
			## Get Media Info
			print(mediainfo(fileToEmocess))
	else: 
		print('Filename too short')
    
    ## VERA EMOVEC ACQUISITION
	df = pd.DataFrame()
	audioSegmentToEmocess = AudioSegment.from_mp3(fileToEmocess)

	full_duration = getLength(fileToEmocess)
	currentDurationIndex = 0
	seconds_index = 15
	seconds_shift = 3
    #while ((currentDurationIndex/1000) + seconds_shift + seconds_index) < full_duration:
	while ((currentDurationIndex/1000) + 18) < full_duration:
		window = audioSegmentToEmocess[currentDurationIndex:currentDurationIndex+((seconds_shift + seconds_index) * 1000)]
		window = audioSegmentToEmocess[currentDurationIndex:currentDurationIndex+18000]
        # emocess
		window.export('temp.mp3', format="mp3")
		r = getVeraOutput('temp.mp3', verbose=True)
		if r.status_code == 500:
			print('Internal server error detected. Perhaps the server is overloaded. Try restarting the service.')
        #print(r)
		if r!= False:
			df1 = jsonToDataFrame(r, seconds_index, verbose=False)
			seconds_index = seconds_index + 3
			#seconds_index = seconds_index + seconds_shift
			df = df.append(df1)
			#print(df1.head())

		#currentDurationIndex = currentDurationIndex + (seconds_shift * 1000)
		currentDurationIndex = currentDurationIndex + 3000

    #print(df)    
	print('Emovec complete...')
	return(df)

def getVeraOutput(mp3_path, vera_service_url='http://13.93.109.28:8882/', verbose=False):
    try:
        if os.path.isfile(mp3_path):
            files = {'file': open(mp3_path, 'rb')}
            r =  requests.post(vera_service_url, files=files)
            if verbose:
                print(r.text)
            return r
        else:
            print('File not found >> ', mp3_path)
            return False
    except e:
        print('Exception thrown. Possibly related to server connection. >> ', e)
        return False

def jsonToDataFrame(r, index=-1, verbose=False):
    json_tuple = json.loads(r.text)
    if verbose:
        print(len(json_tuple['emotions_series']))
        print(json_tuple)
    
    dictEmovec = json_tuple['emotions_series']
    if index >= 0:
        dictEmovec[index] = dictEmovec['15']
        del dictEmovec['15']
    else:
        index = dictEmovec.keys()[0]
        
    dictEmovec[index]['stress'] = json_tuple['stress'][0][0]
    evalpd = pd.DataFrame(dictEmovec).T
    df = evalpd[['Anger/Disgust', 'Happiness', 'Surprise or Fear', 'Neutral', 'stress']]
    if verbose:
        print(df.tail())
    return df

def plotEmovec(df):
	ax = df.plot(figsize=(23,8), grid=True)
	fig = ax.get_figure()
	#fig.show()
	return fig

def showAudioAndEmovecPlot(df, filename):
	print("WARNING! THIS IS AN UNSTABLE METHOD. Make sure it works properly before using it.")
	ax = df.plot(figsize=(23,8), grid=True)
	fig = ax.get_figure()
	#ax.set_xlim(600, 1200)
	
	fig.savefig(filename + '.png')
	print(filename)

	#display(HTML('<audio src=713_DisruptBerlin2019_Nyxo_TRIM.mp3></audio>'))
	video_html_tag_text = '<audio controls alt="display local video in jupyter notebook" src="' + filename + '" style="width:100%; margin-left:-80px;">'
	html = HTML(data=video_html_tag_text)
	return html

