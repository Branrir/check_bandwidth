#!/usr/bin/python3
#
# check_bandwidth - Icinga plugin to check bandwidth usage with snmp
#

import argparse
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

class qsnmp(object):
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

# Get arguments

parser = argparse.ArgumentParser()
parser.add_argument(
    '-h', '--hostname', help='hostname'
)
parser.add_argument(
    '-i', '--interface', help='InterfaceID'
)
parser.add_argument(
    '-c', '--critical',default=95, help='critical value %'
)
parser.add_argument(
    '-w', '--warning', default= 80, help='warning value in %'
)
