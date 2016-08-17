#!/usr/bin/python
# -*- coding: utf-8 -*-
#
import datetime

#  AppAnnie Settings

# auth useinfo
username       = 'Xin.Li@deepfocus.net'
password       = 'flipscript0502'
country        = 'CN'
IOS_account_id = '216951'
IOS_app_id     = '499819758'
GP_account_id  = '203436'
GP_app_id      = '20600003163312'
oral_start_date = '2015-07-22'
DL_chart_type   = 'downloads'
ALL_chart_type  = 'all'
breakdown_source = 'source'
breakdown_country = 'country'

# Get Date
now = datetime.datetime.now()
now_date = now.strftime('%Y-%m-%d')
start_date = (now + datetime.timedelta(days =-8)).strftime('%Y-%m-%d')
end_date   = (now + datetime.timedelta(days =-1)).strftime('%Y-%m-%d')

report_filename = "starbuck_app_weekly_report_"+ now_date + ".txt"

# Google Analystic Settings

ga_username = ''
ga_passwrod = ''
GA_ACCESS_TOKEN		= 'ya29.CjAkA5wKS_qs0qXtzGNstOAmxlx_ezfH4FLxmhAujlhZB2wEDw5EOmsTEE4i6bqe8fo'
GAANDROID_IDS   	= '85294136'
GAFT_WECHAT		= 'ga%3AeventLabel%3D~share_wechat'
GAFT_WECHAT_MOMENT	= 'ga%3AeventLabel%3D~share_wechat_moment'
GAFT_WEIBO		= 'ga%3AeventLabel%3D~share_sinaweibo'
GAFT_CHECKIN		= 'ga%3AeventLabel%3D~check_in'
GA_WECHAT		= 'share_wechat'
GA_WECHAT_MOMENT	= 'share_wechat_moment'
GA_WEIBO		= 'share_sinaweibo'
GA_CHECKIN		= 'check_in'
GAFT_ANDROID_METRICS	= 'ga%3AtotalEvents'
GAFT_ANDROID_DIMENSIONS	= 'ga%3AeventLabel'
GAFT_REGISTER_STEP2	= 'ga%3AeventCategory%3D~register_step_two'
GA_REGISTER_STEP2	= 'register_step_two'
GAFT_ADDCARD_SUCCESS	= 'ga%3AeventLabel%3D~add_card_success'
GA_ADDCARD_SUCCESS	= 'add_card_success'


GAIOS_IDS   			= '85280922'
GAFT_IOS_METRICS 		= 'ga%3AtotalEvents'
GAFT_IOS_DIMENSIONS		= 'ga%3AeventCategory%2Cga%3AeventAction'
GAFT_IOS_SHARE			= 'ga%3AeventAction%3D~Share'

GAFT_IOS_REGISTER_DIMENSIONS	= 'ga%3AeventCategory%2Cga%3AeventAction%2Cga%3AeventLabel'
GAFT_IOS_USER_REG		= 'ga%3AeventCategory%3D%3DMSR%20specific%20analytics%3Bga%3AeventAction%3D%3DUser%20register%3Bga%3AeventLabel%3D%3Dregister%20successful'
GA_IOS_USER_REG			= 'register successful'

GAFT_IOS_ADD_CARD		= 'ga%3AeventCategory%3D%3DMSR%20specific%20analytics%3Bga%3AeventAction%3D%3DAdd%20an%20additional%20card%20to%20mobile%3Bga%3AeventLabel%3D%3DAdd%20card%20successful'
GA_IOS_ADD_CARD			= 'Add card successful'

GAIOS_ALL_SESSION		= 'ga%3Asessions'
IOS_ALL_SESSION			= 'sessions'
GAANDROID_ALL_SESSION		= 'ga%3Asessions'
ANDROID_ALL_SESSION		= 'sessions'