#!/usr/bin/python3
#
# check_bandwidth - Icinga plugin to check bandwidth usage with snmp
#

import argparse
import sys
import time
from pysnmp import hlapi


__title__ = "check_bandwidth"
__version__ = "1.0.0"

# return codes

OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3
nagiosprefixes = {
    OK: "OK",
    WARNING: "WARNING",
    CRITICAL: "CRITICAL",
    UNKNOWN: "UNKNOWN"
}

"""
Quick SNMP - https://github.com/alessandromaggio/quicksnmp/blob/master/quicksnmp.py
"""
    
def construct_object_types(list_of_oids):
    object_types = []
    for oid in list_of_oids:
        object_types.append(hlapi.ObjectType(hlapi.ObjectIdentity(oid)))
    return object_types


def construct_value_pairs(list_of_pairs):
    pairs = []
    for key, value in list_of_pairs.items():
        pairs.append(hlapi.ObjectType(hlapi.ObjectIdentity(key), value))
    return pairs


def get(target, oids, credentials, port=161, engine=hlapi.SnmpEngine(), context=hlapi.ContextData()):
    handler = hlapi.getCmd(
        engine,
        credentials,
        hlapi.UdpTransportTarget((target, port)),
        context,
        *construct_object_types(oids)
    )
    return fetch(handler, 1)[0]


def set(target, value_pairs, credentials, port=161, engine=hlapi.SnmpEngine(), context=hlapi.ContextData()):
    handler = hlapi.setCmd(
    engine,
    credentials,
    hlapi.UdpTransportTarget((target, port)),
        context,
        *construct_value_pairs(value_pairs)
    )
    return fetch(handler, 1)[0]


def get_bulk(target, oids, credentials, count, start_from=0, port=161,
            engine=hlapi.SnmpEngine(), context=hlapi.ContextData()):
    handler = hlapi.bulkCmd(
        engine,
        credentials,
        hlapi.UdpTransportTarget((target, port)),
        context,
        start_from, count,
        *construct_object_types(oids)
    )
    return fetch(handler, count)


def get_bulk_auto(target, oids, credentials, count_oid, start_from=0, port=161,
                engine=hlapi.SnmpEngine(), context=hlapi.ContextData()):
    count = get(target, [count_oid], credentials, port, engine, context)[count_oid]
    return get_bulk(target, oids, credentials, count, start_from, port, engine, context)


def cast(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        try:
            return float(value)
        except (ValueError, TypeError):
            try:
                return str(value)
            except (ValueError, TypeError):
                pass
    return value


def fetch(handler, count):
    result = []
    for i in range(count):
        try:
            error_indication, error_status, error_index, var_binds = next(handler)
            if not error_indication and not error_status:
                items = {}
                for var_bind in var_binds:
                    items[str(var_bind[0])] = cast(var_bind[1])
                result.append(items)
            else:
                raise RuntimeError('Got SNMP error: {0}'.format(error_indication))
        except StopIteration:
            break
    return result

"""
End of Quicksnmp
"""

# Get arguments

parser = argparse.ArgumentParser()
parser.add_argument(
    '-H', '--hostname', help='hostname', required=True, type=str
)
parser.add_argument(
    '-i', '--interface', help='InterfaceID', required=True
)
parser.add_argument(
    '-c', '--critical', default=95, help='critical value in percent', type=float
)
parser.add_argument(
    '-w', '--warning', default= 80, help='warning value in percent', type=float
)
parser.add_argument(
    '-C', '--communityName', default= 'public', help='SNMP Community name' ,type=str
)
parser.add_argument(
    '-t', '--time', default=10, help='Time beetween measurements'
)
parser.add_argument(
    '-d', '--download', help='Bandwith to compare to (Download)', required=True, type=int
)
parser.add_argument(
    '-u', '--upload', help='Bandwith to compare to (Download)', required=True, type=int
)
parser.add_argument(
    '-v', '--verbose', help='Debugging mode', action='store_true'
)
args = parser.parse_args()

# Variables
delta_t = args.time
oid_down = '1.3.6.1.2.1.2.2.1.10.{0}'.format(args.interface)
oid_up = '1.3.6.1.2.1.2.2.1.16.{0}'.format(args.interface)
download_max = args.download
upload_max = args.upload
crit = args.critical
warn = args.warning

# if verbose
if args.verbose:
    print (oid_down)
    print (oid_up)


# get octets
try:
    # get octets in (Download)
    oktets_in_t0 = get(args.hostname, [oid_down], hlapi.CommunityData(args.communityName)).get(oid_down)
    time.sleep(delta_t)
    oktets_in_t1 = get(args.hostname, [oid_down], hlapi.CommunityData(args.communityName)).get(oid_down)
    # get octets out (Upload)
    oktets_out_t0 = get(args.hostname, [oid_up], hlapi.CommunityData(args.communityName)).get(oid_up)
    time.sleep(delta_t)
    oktets_out_t1 = get(args.hostname, [oid_up], hlapi.CommunityData(args.communityName)).get(oid_up)
except Exception as e:
    print("UNKNOWN: Error getting SNMP Values {0}".format(e))

# octets in mbits conversion
usage_down = round(((oktets_in_t1 - oktets_in_t0) / delta_t) * 8 / 1048576, 2)
usage_up = round(((oktets_out_t1 - oktets_out_t0) / delta_t) * 8 / 1048576, 2)
if args.verbose:
    print ("Bandwidth Download Usage : {0} Mbps".format(usage_down))
    print ("Bandwidth Upload Usage: {0}".format(usage_up))

# Usage in %

usage_down_percent = round(usage_down / download_max * 100, 2)
usage_up_percent =  round(usage_up / upload_max * 100, 2)


# if verbose
if args.verbose:
    print ("Usage Down:{0}".format(usage_down_percent))
    print ("Usage UP:{0}".format(usage_up_percent))

# Critical, Warning , OK
# perfdata: 'label'=value[UOM];[warn];[crit];[min];[max]
if usage_down_percent > crit:
    print ("CRITICAL: Bandwidth usage (Download): {0}%".format(usage_down_percent)+
        " | Download_band={0}Mbps;{1};{2};{3};{4}".format(usage_down, int(download_max/100*warn), int(download_max/100*crit), 0, download_max ) + 
        " | Upload_band={0}Mbps;{1};{2};{3};{4}".format(usage_up, int(upload_max/100*warn), int(upload_max/100*crit), 0, upload_max ))
    sys.exit(CRITICAL)
if usage_up_percent > crit:
    print ("CRITICAL: Bandwidth usage (Upload): {0}%".format(usage_up_percent)+
        " | Download_band={0}Mbps;{1};{2};{3};{4}".format(usage_down, int(download_max/100*warn), int(download_max/100*crit), 0, download_max ) + 
        " | Upload_band={0}Mbps;{1};{2};{3};{4}".format(usage_up, int(upload_max/100*warn), int(upload_max/100*crit), 0, upload_max ))
    sys.exit(CRITICAL)
if usage_down_percent > warn and usage_down_percent < crit:
    print ("WARNING: Bandwidth usage (Download): {0}%".format(usage_down_percent)+
        " | Download_band={0}Mbps;{1};{2};{3};{4}".format(usage_down, int(download_max/100*warn), int(download_max/100*crit), 0, download_max ) + 
        " | Upload_band={0}Mbps;{1};{2};{3};{4}".format(usage_up, int(upload_max/100*warn), int(upload_max/100*crit), 0, upload_max ))
    sys.exit(WARNING)
if usage_up_percent > warn and usage_up_percent < crit:
    print ("WARNING: Bandwidth usage (Upload): {0}%".format(usage_up_percent)+
        " | Download_band={0}Mbps;{1};{2};{3};{4}".format(usage_down, int(download_max/100*warn), int(download_max/100*crit), 0, download_max ) + 
        " | Upload_band={0}Mbps;{1};{2};{3};{4}".format(usage_up, int(upload_max/100*warn), int(upload_max/100*crit), 0, upload_max ))
    sys.exit(WARNING)
if usage_up_percent > warn and usage_up_percent < crit and usage_down_percent > warn and usage_down_percent < crit:
    print ("WARNING: Bandwidth usage Upload: {0} %, Download: {1}".format(usage_up_percent, usage_down_percent)+
        " | Download_band={0}Mbps;{1};{2};{3};{4}".format(usage_down, int(download_max/100*warn), int(download_max/100*crit), 0, download_max ) + 
        " | Upload_band={0}Mbps;{1};{2};{3};{4}".format(usage_up, int(upload_max/100*warn), int(upload_max/100*crit), 0, upload_max ))
    sys.exit(WARNING)
if usage_up_percent > crit and usage_down_percent > crit:
    print ("CRITICAL: Bandwidth usage Upload: {0} %, Download: {1}".format(usage_up_percent, usage_down_percent)+
        " | Download_band={0}Mbps;{1};{2};{3};{4}".format(usage_down, int(download_max/100*warn), int(download_max/100*crit), 0, download_max ) + 
        " | Upload_band={0}Mbps;{1};{2};{3};{4}".format(usage_up, int(upload_max/100*warn), int(upload_max/100*crit), 0, upload_max ))
    sys.exit(CRITICAL)
else:
    print ("OK: Bandwidth Download: {0} %, Upload: {1} %".format(usage_down_percent, usage_up_percent) +
        " | Download_band={0}Mbps;{1};{2};{3};{4}".format(usage_down, int(download_max/100*warn), int(download_max/100*crit), 0, download_max ) + 
        " | Upload_band={0}Mbps;{1};{2};{3};{4}".format(usage_up, int(upload_max/100*warn), int(upload_max/100*crit), 0, upload_max ))