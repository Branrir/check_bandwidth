# Nagios SNMP Bandwidth check

Nagios Check for measuring your Bandwidth usage.

## Example output (with performance data):

OK: Bandwidth Download: 11.67 %, Upload: 0.75 % | Download_band=1.4Mbps;10;11;0;12 | Upload_band=0.09Mbps;10;11;0;12

## For Python requirements run:

sudo pip3 install -r requirements

## Installation:

```bash
cd /usr/lib/nagios/plugins
wget https://raw.githubusercontent.com/Branrir/check_bandwidth/master/check_bandwidth.py
chmod +x check_bandwidth.py
```
## 

| Parameter | Description |
| --- | --- |
| -h, --help | Shows help |
| -H, --host | hostaddress |
| -i, --interface | Interface index in SNMP |
| -t, --time | Time in between measurements |
| -v, --verbose | Verbose mode, shows all variables (for debugging) | 
| -C, --communityName | SNMP v2c CommunityNamme |
| -d, --download | Max download bandwidth of your interface |
| -u, --upload | Max upload bandwidth of your interface |
| -w, --warning | Warning value in % of max bandwidth |
| -c, --critical | Critical value in % of max bandwidht |

Example usage:
```bash
/usr/lib/nagios/plugins/check_bandwidth.py --communityName public --critical 95 --download 12 --hostname 192.168.1.1 --interface 21 --time 10 --upload 12 --warning 90
```
Output: 
```bash
OK: Bandwidth Download: 0.08%, Upload: 0.0%;| Download_band=0.01;9;10;0;12 Upload_band=0.0;9;10;0;12
```

## How to get SNMP ID
first use snmpwalk to get all data about device. Now you can look for device description in snmpwalk output and check the last part of that oid.
You may try to use this command and look for your interface:
```bash
snmpwalk [device_ip] -c [community] -v 1 | grep "interface_description"
```
-------
Special thanks to Alessandro Maggio for https://github.com/alessandromaggio/quicksnmp
