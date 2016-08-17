#! /usr/bin/env python
#coding:utf-8

import setting as _s

def saveToFile(savedata):
	try:
		with open(_s.report_filename,'a') as data:
			data.write(savedata+'\n')
	except IOError as err:
		print('File error: ' + str(err))