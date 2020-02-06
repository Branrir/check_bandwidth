Nagios SNMP Bandwidth check
=======

Nagios Check for measuring your Bandwidth usage.

-------
Example output (with performance data):

OK: Bandwidth Download: 11.67 %, Upload: 0.75 % | Download_band=1.4Mbps;10;11;0;12 | Upload_band=0.09Mbps;10;11;0;12

-------
For Python requirements run:

sudo pip3 install -r requirements

---------
Installation:

cd /usr/lib/nagios/plugins
wget https://raw.githubusercontent.com/Branrir/check_bandwidth/master/check_bandwidth.py
chmod +x check_bandwidth.py








-------
Special thanks to Alessandro Maggio for https://github.com/alessandromaggio/quicksnmp
