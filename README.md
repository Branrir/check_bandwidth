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
| --- | --- | --- |
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

-------
Special thanks to Alessandro Maggio for https://github.com/alessandromaggio/quicksnmp
