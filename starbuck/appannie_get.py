#! /usr/bin/env python
#coding:utf-8

import cookielib
import urllib2
import mechanize
import re
import setting as _s

def open_url(username,password):
	# Browser
	global br
	br = mechanize.Browser()

	# Agent setting
	br.addheaders = [ ( 'User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.152 Safari/537.36' ) ]
	# Enable cookie support for urllib2
	cookiejar = cookielib.LWPCookieJar()
	br.set_cookiejar( cookiejar )

	# Broser options
	br.set_handle_equiv(True)
	# br.set_handle_gzip(True)
	br.set_handle_redirect(True)
	br.set_handle_referer(True)
	br.set_handle_robots(False)

	br.set_handle_refresh( mechanize._http.HTTPRefreshProcessor(), max_time = 1 )

	# authenticate
	try:
		br.open('https://www.appannie.com/account/login/',timeout=3000000)
		br.select_form(nr=0)
		# these two come from the code you posted
		# where you would normally put in your username and password
		br[ "username" ] = username
		br[ "password" ] = password
		res = br.submit()
		return res
        except:
                print "login failed"

def get_total_data(account_id,app_id,country,breakdown,start_date,end_date,chart_type):
	url = 'https://www.appannie.com/dashboard/'+ account_id + '/item/' + app_id + '/downloads/export/?breakdown=' + breakdown + '&countries=' + country + '&chart_type=' + chart_type + '&start_date=' + start_date  + '&end_date=' + end_date
	url_result = br.open(url,timeout=300000)
	returnPage = url_result.read()
	if ( start_date == _s.oral_start_date ):
		return re.findall('Total.*',returnPage)[0].split(',')[2]
        else:
#		return returnPage
		result=[]
		for i in re.findall('.*,.*,.*,.*',returnPage):
			result.append(i)
		return '\n'.join(result)

if __name__ == '__main__':
	print '------ Total ios store --------'
	print get_total_data(IOS_account_id,IOS_app_id,country,breakdown_source,oral_start_date,end_date,ALL_chart_type)
#	print '------ Total google play --------'
#	print get_total_data(GP_account_id,GP_app_id,country,oral_start_date,end_date,DL_chart_type)
	print '------ ios store --------'
	print get_total_data(IOS_account_id,IOS_app_id,country,start_date,end_date,ALL_chart_type)
	print '------ google play --------'
	print get_total_data(GP_account_id,GP_app_id,country,start_date,end_date,ALL_chart_type)