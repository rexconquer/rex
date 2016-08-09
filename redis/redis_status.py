#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

HOSTNAME = '127.0.0.1'
REDISPORT = '6379'
REDISDB = '0'
REDISPASSWD = ''

# ERROR CODE
CONNECT_ERROR = "-0.9900"
ERROR_IMPORT = "-0.9901"
ERROR_PARAM = "-0.9902"
INVALID_ITEM = "-0.9903"
NO_PARAM = "-0.9904"

try:
        import redis
except ImportError:
        print(ERROR_IMPORT)
        sys.exit(2)

def get_status(r,*subparam):
        try:
                if len(subparam) > 1:
                        r_result=r.info()[subparam[0]][subparam[1]]
                else:
                        r_result=r.info()[subparam[0]]

        except KeyError:
                return INVALID_ITEM
        except redis.exceptions.ConnectionError:
                return CONNECT_ERROR
        if isinstance(r_result,dict):
                return ERROR_PARAM
        return r_result

if __name__ == '__main__':
        try:
                r = redis.StrictRedis(host=HOSTNAME, port=REDISPORT, db=REDISDB, password=REDISPASSWD)

        except redis.ResponseError, e:
                print('ResponseError: %s' % e.message)
        except Exception, exception:
                print(exception)

        if len(sys.argv) == 1:
                print(NO_PARAM)
        elif len(sys.argv) == 2:
                print(get_status(r,sys.argv[1]))
        elif len(sys.argv) == 3:
                print(get_status(r,sys.argv[1],sys.argv[2]))
