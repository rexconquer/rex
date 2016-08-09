#!/usr/bin/python
# -*- coding: utf-8 -*-

import redis
import datetime
import time
import os

HOSTNAME = '10.1.100.22'
REDISPORT = '6379'
REDISDB = '0'
REDISPASSWD = ''
OVERTIME = 300
DIRTARGET = '/opt/backup/redis/'
ZIP = '/usr/bin/zip'
NOWTIME = time.mktime(datetime.datetime.now().timetuple())

if not os.path.isdir(DIRTARGET):
    os.makedirs(DIRTARGET)

try:
    r = redis.StrictRedis(host=HOSTNAME, port=REDISPORT, db=REDISDB, password=REDISPASSWD)
    LTSAVE = time.mktime(r.lastsave().timetuple())
    ENABLE_AOF = r.info()['aof_enabled']
    DIRSOURCE = r.config_get()['dir'] + '/'
    DBFILENAME = r.config_get()['dbfilename']

except redis.ResponseError, e:
    print 'ResponseError: %s' % e.message
except Exception, exception:
    print exception

RDB_SOURCEFILE = DIRSOURCE + DBFILENAME
RDB_TARGETFILE = DIRTARGET + DBFILENAME + '_' + REDISPORT + '_' + time.strftime('%Y%m%d%H%M') + '.zip'
AOF_SOURCEFILE = DIRSOURCE + 'appendonly.aof'
AOF_TARGETFILE = DIRTARGET + 'appendonly.aof_' + REDISPORT + '_' + time.strftime('%Y%m%d%H%M') + '.zip'
DIFFTIME = int(NOWTIME) - int(LTSAVE)


def compressfile(sourcefile, targetfile):
    ZIPCOMMAND = ZIP + " -qr '%s' %s" % (targetfile, ' ' + sourcefile)

    if os.system(ZIPCOMMAND) == 0:
        print 'Successful backup to', targetfile
    else:
        print 'Backup FAILED'


def rdbsave(difftime, redis, overtime, rdb_sourcefile, rdb_targetfile):
    if (difftime > overtime):
        redis.bgsave()

    AFTIME = int(time.mktime(datetime.datetime.now().timetuple()))

    while not (AFTIME > OVERTIME):
        time.sleep(10)
    compressfile(sourcefile=rdb_sourcefile, targetfile=rdb_targetfile)


def aofsave(redis, aof_sourcefile, aof_targetfile):
    if (redis.bgrewriteaof()):
        compressfile(sourcefile=aof_sourcefile, targetfile=aof_targetfile)


if __name__ == '__main__':
    if (ENABLE_AOF):
        aofsave(redis=r, aof_sourcefile=AOF_SOURCEFILE, aof_targetfile=AOF_TARGETFILE)
    else:
        rdbsave(difftime=DIFFTIME, redis=r, overtime=OVERTIME, rdb_sourcefile=RDB_SOURCEFILE,
                rdb_targetfile=RDB_TARGETFILE)
