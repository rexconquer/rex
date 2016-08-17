# -*- coding:utf-8 -*-

__author__ = 'onecloud'

import subprocess
import time
import urllib
import urllib2
import urlparse
import math
import os
import sys
import logging

from config import *

try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        os.system('pip install simplejson')
#        os.system("cd /usr/local/cmdb_agent/package && tar zxvf simplejson-1.7.1.tar.gz > /dev/null 2>&1 && cd simplejson-1.7.1 && python setup.py install > /dev/null 2>&1")
        # os._exit(1)
        import simplejson as json

try:
    import cPickle as pickle
except ImportError:
    import pickle

try:
    from hashlib import sha1
except ImportError:
    import sha

    sha1 = sha.new

def build_api_key(path, **kwargs):
    keys = sorted(kwargs.keys())
    values = [kwargs.get(k) for k in keys]
    values.insert(0, CMDB_SECRET)
    values.insert(0, path)
    return sha1("".join(values)).hexdigest()


def request(url, params={}, method="POST"):
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
    if method != "GET":
        path = urlparse.urlparse(url)[2]
        params["_secret"] = build_api_key(path, **params)
        params["_key"] = CMDB_KEY

    if type(params) == dict:
        params = "&".join(["%s=%s" % (k, v)
                           for k, v in params.iteritems()])

    request = urllib2.Request(url, data=params)
    request.add_header('Content-Type', 'application/json')
    request.add_header('Accept', 'application/json')
    request.get_method = lambda: method
    resp = opener.open(request)
    return json.loads(resp.read())


def compute_ram_size(ram):
    ram_list = ram.strip().split()
    ram_list = filter(lambda x: x != "", ram_list)
    s = 0
    for r in ram_list:
        if "*" in r:
            x, y = r.split("*")
            x = x[:-2]
            z = int(math.ceil(int(x) * int(y) / 1024.0))
            s += z
        else:
            x = r.strip()
            z = int(math.ceil(int(x[:-2])/ 1024.0))
            s += z
    return str(s) + "GB"


def get_sys_info():
    try:
        p = subprocess.Popen("sh sys_info.sh", shell=True,
                             stdout=subprocess.PIPE)
        return p.stdout.read()
    except Exception, e:
        logging.error(e)
        return


def is_server():
    m = subprocess.Popen(
        """/usr/sbin/dmidecode -t 1 |
        awk -F'Manufacturer: ' '{print $2}' |awk -F'Product' '{print $1}'""",
        shell=True, stdout=subprocess.PIPE).stdout.read().strip().split()[0]
    return m == "HP" or m == "IBM" or m == "Huawei" or m == "Dell"


def wrap_device_dict(sys_info):
    values = sys_info.split(",")
    device_dict = dict()
    if is_server():
        for k in SERVER_KEYS:
            if k == "private_ip":
                device_dict[k] = filter(lambda x: x, values[
                    SERVER_KEYS.index(k)].strip().split("/"))
            else:
                device_dict[k] = values[SERVER_KEYS.index(k)].strip()
        device_dict["ci_type"] = "server"
        del device_dict["uuid"]
    else:
        for k in VSERVER_KEYS:
            if k == "private_ip":
                device_dict[k] = filter(lambda x: x, values[
                    VSERVER_KEYS.index(k)].strip().split("/"))
            else:
                device_dict[k] = values[VSERVER_KEYS.index(k)].strip()
        device_dict["ci_type"] = "vserver"
    return device_dict


def query_device_info(ci_type, unique):
    result = dict()
    if ci_type == "vserver":
        q_url = QUERY_URI % urllib.quote("_type:vserver,uuid:%s" % unique)
        result["ci_type"] = "vserver"
    else:
        q_url = QUERY_URI % urllib.quote("_type:server,sn:%s" % unique)
        result["ci_type"] = "server"
    try:
        resp = urllib2.urlopen(q_url)
        res = resp.read()
        res = json.loads(res).get("result")
        if res and ci_type == "server":
            res = res[0]
            for k in SERVER_KEYS:
                if k not in SERVER_CHILD_KEYS:
                    result[k] = res.get(k, "")
                # special handle
            if res.get("ilo_ip") is None:
                ilo_ip = ""
            else:
                ilo_ip = res.get("ilo_ip")
            if res.get("ilo_mac") is None:
                ilo_mac = ""
            else:
                ilo_mac = res.get("ilo_mac")
            result["ilo"] = ilo_ip + "/" + ilo_mac

        elif res and ci_type == "vserver":
            res = res[0]
            for k in VSERVER_KEYS:
                result[k] = res.get(k, "")
        else:
            return dict()
    except Exception, e:
        logging.error(e)
    return result


def nic_handler(ci_id, nic_dict):
    nic_type = nic_dict.get("nic_type", "")
    if nic_type:
        nic_type = nic_type[:-2]
    _nics = nic_dict.get("nic_mac", "").split()
    _nics = filter(lambda x: x != "", _nics)
    nics = [(_nics[i], _nics[i + 1]) for i in range(0, len(_nics), 2)]
    for nic_interface, nic_mac in nics:
        _nic_dict = {"ci_type": "NIC"}
        _nic_dict["nic_interface"] = nic_interface
        _nic_dict["nic_mac"] = nic_mac
        _nic_dict["nic_type"] = nic_type
        if nic_interface == "eth0":
            _nic_dict["nic_ip"] = nic_dict.get("nic_ip", "")
        if nic_interface in nic_dict.get("nic_status", ""):
            if "Full" in nic_dict.get("nic_status", ""):
                _nic_dict["nic_status"] = "Full"
            elif "Half" in nic_dict.get("nic_status", ""):
                _nic_dict["nic_status"] = "Half"
            if "Mb/s" in nic_dict.get("nic_status", ""):
                _nic_dict["nic_speed"] = nic_dict.get(
                    "nic_status", "").split()[0].split(":")[1]
        try:
            res = request(PUT_URI, _nic_dict, method="PUT")
            nic_id = res.get("ci_id")
            add_relation(ci_id, nic_id)
        except Exception, e:
            logging.error("add nic fail, %s, %s, %s" % (ci_id, _nic_dict, str(e)))


def harddisk_handler(ci_id, hd_dict):
    _hds = hd_dict.get("harddisk", "").strip().split("/")
    _hds = filter(lambda x: x != "", _hds)
    for _hd in _hds:
        __hd = _hd.strip().split()
        _hd_dict = {"ci_type": "harddisk"}
        _hd_dict["hd_sn"] = __hd[0]
        if len(__hd) > 1:
            _hd_dict["hd_interface_type"] = __hd[1]
        if len(__hd) > 2:
            _hd_dict["hd_size"] = __hd[2]
        if len(__hd) > 3:
            _hd_dict["hd_type"] = __hd[3]
        if len(__hd) > 4:
            _hd_dict["hd_speed"] = __hd[4]
        if _hd_dict.get("hd_sn"):
            try:
                res = request(PUT_URI, _hd_dict, method="PUT")
                hd_id = res.get("ci_id")
                add_relation(ci_id, hd_id)
            except Exception, e:
                logging.error(e)


def pcie_handler(ci_id, pcie_cards):
    pcie_cards = pcie_cards.split('/')
    for pcie_card in pcie_cards:
        pcie_card = pcie_card.split(' ')
        if len(pcie_card) != 4:
            logging.error('pcie info error....')
            continue

        pcie_dict = {
            "ci_type": "pcie",
            "pcie_vender": pcie_card[0],
            "pcie_sn": pcie_card[1],
            "pcie_capacity": pcie_card[2].split('GB')[0],
            "pcie_speed": pcie_card[3]
        }
        try:
            res = request(PUT_URI, pcie_dict, method="PUT")
            pcie_id = res.get("ci_id")
            add_relation(ci_id, pcie_id)
        except Exception, e:
            logging.error(e)


def add_relation(first_ci, second_ci):
    url = RELATION_URI % (first_ci, second_ci)
    try:
        request(url, params={}, method="POST")
    except Exception, e:
        logging.error("add relation error...., %d, %d, %s" % (first_ci, second_ci, e))


def send_server_info(device_dict):
    params = device_dict
    nic_dict = {"nic_ip": params.get("nic_ip", ""),
                "nic_status": params.get("nic_status", ""),
                "nic_type": params.get("nic_type", ""),
                "nic_mac": params.get("nic_mac", "")}

    hd_dict = {"harddisk": params.get("harddisk", "")}

    ilo = params.get("ilo", "")
    if len(ilo.strip().split("/")) == 2:
        params["ilo_ip"] = ilo.strip().split("/")[0]
        params["ilo_mac"] = ilo.strip().split("/")[1]
    if ilo:
        del params["ilo"]
    if params.get("nic_ip"):
        del params['nic_ip']
    if params.get("nic_status"):
        del params['nic_status']
    if params.get("nic_type"):
        del params["nic_type"]
    if params.get("nic_mac"):
        del params["nic_mac"]
    if params.get("harddisk"):
        del params["harddisk"]
    try:
        res = request(PUT_URI, params, method="PUT")
        ci_id = res.get("ci_id")

        nic_handler(ci_id, nic_dict)
        harddisk_handler(ci_id, hd_dict)
        if params.get("pcie_card") and params['pcie_card'].strip():
            pcie_handler(ci_id, params['pcie_card'].strip())
    except Exception, e:
        logging.error('%s, %s' % (device_dict.get("private_ip"), e))


def send_sys_info(dump_file, debug=False):
    sys_info = get_sys_info()
    device_dict = wrap_device_dict(sys_info)
    has_dump_file = False
    if not debug:
        sleep = int(sha1(device_dict.get("private_ip")[0]).hexdigest(), 16) % 3600
        time.sleep(sleep)

    if is_server():
        request(HEARTBEAT_URI % ("server", device_dict.get("sn")),
                method="POST")
    else:
        request(HEARTBEAT_URI % ("vserver", device_dict.get("uuid")),
                method="POST")

    if not debug:
        try:
            d = open(dump_file)
            old_device = pickle.load(d)
            d.close()
            has_dump_file = True
        except Exception, e:
            ci_type = device_dict.get("ci_type")
            if ci_type == "vserver":
                unique = device_dict.get("uuid")
            else:
                unique = device_dict.get("sn")
            old_device = query_device_info(device_dict.get("ci_type"), unique)

        if has_dump_file and old_device and \
                        old_device == device_dict:
            logging.info("not change.......")
            return

        try:
            d = open(dump_file, "w")
            pickle.dump(device_dict, d)
            d.close()
        except Exception, e:
            pass
    else:
        print device_dict

    try:
        private_ip = ",".join(device_dict.get("private_ip"))
        device_dict["private_ip"] = private_ip
        if device_dict.get("ram"):
            try:
                ram_size = compute_ram_size(device_dict.get("ram"))
            except:
                ram_size = None
            if ram_size is not None:
                device_dict["ram_size"] = ram_size
        del device_dict['hostname']
        if device_dict.get("ci_type") == "vserver":
            res = request(PUT_URI, device_dict, method="PUT")
            logging.info("post ci......", res)
        else:
            send_server_info(device_dict)
    except Exception, e:
        logging.error(e)


if __name__ == "__main__":
    debug = True if 'debug' in sys.argv else False
    logging_args = {
        'level': logging.INFO,
        'format': '%(asctime)s - %(levelname)s - %(filename)s - %(lineno)d: %(message)s',
    }
    if debug:
        logging_args['stream'] = sys.stdout
    else:
        logging_args['filename'] = LOG_FILE
    logging.basicConfig(**logging_args)

    send_sys_info("./dump.bin", debug)
