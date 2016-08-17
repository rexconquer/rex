#! /usr/bin/env python
#coding:utf-8

import subprocess
import re
import dircache
import socket
import fcntl
import struct


def get_dict_value(dict,str):
    ''' retrun null , if dict has not parameters'''
    if len(dict) != 0 and dict.has_key(str):
        return dict[str]
    else:
        return ''

def uniq(lst):
    """return dict, find the count of item on list, and save item and count"""
    ulist = list(set(lst))
    rdict={}
    for item in ulist:
        rdict.update({item:lst.count(item)})
    return rdict

def itemCount_dict(dict):
    lst=[]
    for key in dict:
        lst.append(str(key)+'*'+str(dict[key]))
    return lst

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])
    except IOError:
        return ''

def hard_info_dict():
    '''return dict, the value from dmidecode'''
    dmitmp = subprocess.Popen("""/usr/sbin/dmidecode -t 1""",shell=True, stdout=subprocess.PIPE).stdout.read()
    Ddim = {}
    try:
        Ldimraw = dmitmp[dmitmp.index('System Information') + len('System Information\n'):].strip('\n').strip('\t').replace('\t', '')
        Ldim = re.split(':|\n', Ldimraw)
        for i in range(0, len(Ldim), 2):
            Ddim[Ldim[i]] = Ldim[i + 1].strip('\t').strip(' ')
    except ValueError:
        Ldimraw = ''
    return Ddim

def get_OS_Releases():
    '''get os release from issue'''
    with open('/etc/issue', 'r') as txt:
        return txt.readline().replace('\\l','').replace('\\n','').strip()

def get_kernel_ver():
    '''get kernel from uname -r'''
    kver = subprocess.Popen("""/bin/uname -r""",shell=True, stdout=subprocess.PIPE).stdout.read().strip()
    return kver

def get_hostname():
    '''get hostname from /proc/sys/kernel/hostname '''
    with open('/proc/sys/kernel/hostname','r') as txt:
        print txt.readline().strip()

def get_cpuinfo_dict():
    ''' get cpuinfo dict from /proc/cpuinfo'''
    with open('/proc/cpuinfo') as txt:
        Dcpuinfo={}
        for line in txt:
            if len(line) != 1:
                list1 = line.strip().replace('\t', '').strip(' ').split(':')
                Dcpuinfo[list1[0]] = list1[1].strip()
    return Dcpuinfo

def get_cpuinfo_count(str):
    ''' get physical id count from /proc/cpuinfo'''
    count=[]
    with open('/proc/cpuinfo') as txt:
        for line in txt:
            if re.search(str,line):
                count.append(line)
    return len(list(set(count)))

def get_phymem():
    '''return phycial memory list, the value from dmidecode'''
    dmitmp = subprocess.Popen("""/usr/sbin/dmidecode -t 17""", shell=True, stdout=subprocess.PIPE).stdout
    memlist=[]
    for line in dmitmp:
        if re.search('Size:',line) and not re.search('No Module Installed',line):
            memlist.append(line.strip().replace('Size: ',''))
        return memlist

def get_nicName():
    dclst = dircache.listdir('/sys/class/net/')
    nicNamelst=[]
    for item in dclst:
        if re.search('eth',item):
            nicNamelst.append(item)
    return nicNamelst

def get_phynic():
    lspci = subprocess.Popen("""lspci |grep -i ether| cut -d: -f 3 |awk '{print $1"-"$2"-"$3"-"$4"-"$5}'|sort -nr""",shell=True,stdout=subprocess.PIPE).stdout
    niclist=[]
    for line in lspci:
        niclist.append(line.strip())
    return niclist

def get_nic_mac():
    dclst = get_nicName()
    nicname_dic = {}
    for item in dclst:
        if re.search('eth',item):
            nicname_dic[item] = open('/sys/class/net/'+ item + '/address').read().strip()
    return nicname_dic

def get_nicip_dict():
    dclst = get_nicName()
    nicip_dic = {}
    for item in dclst:
        if re.search('eth', item):
            nicip_dic[item] = get_ip_address(item)
    return nicip_dic

def get_nicstat_dict():
    niclist=get_nicName()
    nicstat_dict={}
    for nicname in niclist:
        try:
            with open('/sys/class/net/'+ nicname +'/speed') as txt:
                with open('/sys/class/net/'+ nicname +'/duplex') as txt1:
                    duplex=txt1.read().strip()
                    speed=int(txt.read().strip())
                    if speed == 10 or speed == 100 or speed == 1000:
                        nicstat_dict[nicname] = str(speed) + ' ' + duplex
                    else:
                        nicstat_dict[nicname] = ''
        except:
            nicstat_dict[nicname]=''
    return nicstat_dict

# LG_core = int(get_dict_value(get_cpuinfo_dict(),'processor'))+1
# PHY_core = int(get_dict_value(get_cpuinfo_dict(),'cpu cores'))
# PHY_id   = int(get_cpuinfo_count('physical id'))
# Mode_name = get_dict_value(get_cpuinfo_dict(),'model name')
# HT_num = LG_core/PHY_core/PHY_id
# HT_ctl = 'enable' if HT_num==2 else 'diable'
# Ser_meminfo = itemCount_dict(uniq(get_phymem()))
# Net_info = itemCount_dict(uniq(get_phynic()))
# Net_mac  = get_nic_mac()
# ethlist = Net_mac.keys()
# Net_stat = get_nicstat_dict()
