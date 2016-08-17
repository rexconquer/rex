#! /usr/bin/env python
# coding:utf-8

import cookielib
import urllib2
import mechanize
import json
import re
import setting as _s
import sys


def open_url_token(url):
    # Browser
    global br
    br = mechanize.Browser(factory=mechanize.RobustFactory())

    # Agent setting
    br.addheaders = [('User-agent',
                      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.152 Safari/537.36')]
    # Enable cookie support for urllib2
    cookiejar = cookielib.LWPCookieJar()
    br.set_cookiejar(cookiejar)

    # Broser options
    br.set_handle_equiv(True)
    # br.set_handle_gzip(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(False)

    br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

    # authenticate
    try:
        res = br.open(url, timeout=30000)
        return res.read()
    except:
        print "login failed"
        sys.exit(2)


def generate_url(access_token, ids, start_date, end_date, metrics, dimensions, filter):
    url = 'https://www.googleapis.com/analytics/v3/data/ga?ids=ga%3A' + ids + \
          '&start-date=' + start_date + \
          '&end-date=' + end_date + \
          '&metrics=' + metrics + \
          '&dimensions=' + dimensions + \
          '&filters=' + filter + \
          '&access_token=' + access_token
    return url


def generate_url_withoutfilter(access_token, ids, start_date, end_date, metrics):
    url = 'https://www.googleapis.com/analytics/v3/data/ga?ids=ga%3A' + ids + \
          '&start-date=' + start_date + \
          '&end-date=' + end_date + \
          '&metrics=' + metrics + \
          '&access_token=' + access_token
    return url


def get_total_data(url):
    url_result = open_url_token(url)
    json_result = json.loads(url_result)
    sum = 0
    if json_result.has_key('rows'):
        for i in json_result['rows']:
            sum += int(i[1])
        return str(sum)
    else:
        return '0'


def get_data(url):
    url_result = open_url_token(url)
    json_result = json.loads(url_result)
    str_result = ''
    for i in json_result['rows']:
        for j in i:
            str_result += j + ' '
        if len(json_result['rows']) == 1:
            str_result += ''
        else:
            str_result += '\n'
    return str_result


def print_android_data():
    android_wechat = get_total_data(
        generate_url(_s.GA_ACCESS_TOKEN, _s.GAANDROID_IDS, _s.start_date, _s.end_date, _s.GAFT_ANDROID_METRICS,
                     _s.GAFT_ANDROID_DIMENSIONS, _s.GAFT_WECHAT))
    android_wechat_moment = get_total_data(
        generate_url(_s.GA_ACCESS_TOKEN, _s.GAANDROID_IDS, _s.start_date, _s.end_date, _s.GAFT_ANDROID_METRICS,
                     _s.GAFT_ANDROID_DIMENSIONS, _s.GAFT_WECHAT_MOMENT))
    android_weibo = get_total_data(
        generate_url(_s.GA_ACCESS_TOKEN, _s.GAANDROID_IDS, _s.start_date, _s.end_date, _s.GAFT_ANDROID_METRICS,
                     _s.GAFT_ANDROID_DIMENSIONS, _s.GAFT_WEIBO))
    android_check_in = get_total_data(
        generate_url(_s.GA_ACCESS_TOKEN, _s.GAANDROID_IDS, _s.start_date, _s.end_date, _s.GAFT_ANDROID_METRICS,
                     _s.GAFT_ANDROID_DIMENSIONS, _s.GAFT_CHECKIN))
    android_register_step_two = get_total_data(
        generate_url(_s.GA_ACCESS_TOKEN, _s.GAANDROID_IDS, _s.start_date, _s.end_date, _s.GAFT_ANDROID_METRICS,
                     _s.GAFT_ANDROID_DIMENSIONS, _s.GAFT_REGISTER_STEP2))
    android_add_card_success = get_total_data(
        generate_url(_s.GA_ACCESS_TOKEN, _s.GAANDROID_IDS, _s.start_date, _s.end_date, _s.GAFT_ANDROID_METRICS,
                     _s.GAFT_ANDROID_DIMENSIONS, _s.GAFT_ADDCARD_SUCCESS))
    andorid_all_sessions = get_data(
        generate_url_withoutfilter(_s.GA_ACCESS_TOKEN, _s.GAANDROID_IDS, _s.oral_start_date, _s.end_date,
                                   _s.GAANDROID_ALL_SESSION))

    re_result = _s.GA_WECHAT + ": " + android_wechat + '\n'
    re_result += _s.GA_WECHAT_MOMENT + ": " + android_wechat_moment + '\n'
    re_result += _s.GA_WECHAT + ' - ' + _s.GA_WECHAT_MOMENT + ": " + str(
        int(android_wechat) - int(android_wechat_moment)) + '\n'
    re_result += _s.GA_WEIBO + ": " + android_weibo + '\n'
    re_result += _s.GA_CHECKIN + ": " + android_check_in + '\n'
    re_result += _s.GA_REGISTER_STEP2 + ": " + android_register_step_two + '\n'
    re_result += _s.GA_ADDCARD_SUCCESS + ": " + android_add_card_success + '\n'
    re_result += _s.ANDROID_ALL_SESSION + ": " + andorid_all_sessions + '\n'

    return re_result


def print_ios_data():
    ios_register_successful = get_data(
        generate_url(_s.GA_ACCESS_TOKEN, _s.GAIOS_IDS, _s.start_date, _s.end_date, _s.GAFT_IOS_METRICS,
                     _s.GAFT_IOS_REGISTER_DIMENSIONS, _s.GAFT_IOS_USER_REG))
    ios_add_card_success = get_data(
        generate_url(_s.GA_ACCESS_TOKEN, _s.GAIOS_IDS, _s.start_date, _s.end_date, _s.GAFT_IOS_METRICS,
                     _s.GAFT_IOS_REGISTER_DIMENSIONS, _s.GAFT_IOS_ADD_CARD))
    ios_all_sessions = get_data(
        generate_url_withoutfilter(_s.GA_ACCESS_TOKEN, _s.GAIOS_IDS, _s.oral_start_date, _s.end_date,
                                   _s.GAIOS_ALL_SESSION))

    re_result = get_data(generate_url(_s.GA_ACCESS_TOKEN, _s.GAIOS_IDS, _s.start_date, _s.end_date, _s.GAFT_IOS_METRICS,
                                      _s.GAFT_IOS_DIMENSIONS, _s.GAFT_IOS_SHARE)) + '\n'
    re_result += _s.GA_IOS_USER_REG + ": " + ios_register_successful + '\n'
    re_result += _s.GA_IOS_ADD_CARD + ": " + ios_add_card_success + '\n'
    re_result += _s.IOS_ALL_SESSION + ": " + ios_all_sessions + '\n'

    return re_result


if __name__ == '__main__':
    print_android_data()
    print_ios_data()