##########################################################################
# Copyright 2021 Deniz Iren. All Rights Reserved.
"""This module includes methods to handle file operations."""
__name__ = 'file.operations'
__author__ = 'Deniz Iren (deniziren@gmail.com)'
__version__ = '0.002'
__lastupdate__ = '07.01.2021'

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

def getFileList(directoryPath, fileType = '*'):
	"""getFileList(directoryPath, fileType='*')"""
	import os
	fileList = []
	if fileType == '*':
		for filename in os.listdir(directoryPath):
			if filename not in fileList:
				fileList.append(filename)
	else:
		for filename in os.listdir(directoryPath):
			if filename.endswith(fileType):
				if filename not in fileList:
					fileList.append(filename)
	return fileList

import string
def sanitizeFileName(badString):
    goodString = ''
    goodString = ''.join(filter(lambda x: x in string.printable, badString))
    goodString = goodString.translate(str.maketrans('', '', string.punctuation))
    goodString = goodString.translate(str.maketrans('', '', ' '))
    return goodString

