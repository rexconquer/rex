#! /usr/bin/env python
#coding:utf-8

from appannie_get import get_total_data
from appannie_get import open_url
from save_to_file import saveToFile
from googleanalytics_get import print_android_data
from googleanalytics_get import print_ios_data
import setting as _s

def get_appainne():
        open_url(_s.username,_s.password)
        saveToFile('------ Total ios store --------')
        saveToFile(get_total_data(_s.IOS_account_id,_s.IOS_app_id,_s.country,_s.breakdown_source,_s.oral_start_date,_s.end_date,_s.DL_chart_type))
#        saveToFile('------ Total google play --------')
#        saveToFile(get_total_data(_s.GP_account_id,_s.GP_app_id,_s.country,_s.oral_start_date,_s.end_date,_s.DL_chart_type))
        saveToFile('------ ios store --------')
        saveToFile(get_total_data(_s.IOS_account_id,_s.IOS_app_id,_s.country,_s.breakdown_country,_s.start_date,_s.end_date,_s.ALL_chart_type))
        saveToFile('------ google play --------')
        saveToFile(get_total_data(_s.GP_account_id,_s.GP_app_id,_s.country,_s.breakdown_country,_s.start_date,_s.end_date,_s.ALL_chart_type))

def get_google_analytics():
	saveToFile('------ google analystics for android --------')
	saveToFile(print_android_data())
	saveToFile('------ google analystics for IOS --------')
	saveToFile(print_ios_data())

if __name__ == '__main__':
#	get_appainne()
	get_google_analytics()