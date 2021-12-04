import sys
from scapy.all import send,sr1,IP,UDP
import time

#a = "hso_ca4b2e2d0d2561830f3b3a33c02cab60ef82431c_"
b = "hso_8642a0c227ec8e342e1226bf122e562ace5c7f63_"
c = "hso_0c43d8d3dbf91ce0341d8ddcca9610aa148c9168_"
for i in range(0, len(b)):
	send(IP(dst="192.168.56.102")/UDP(dport=ord(b[i])+10000))
	time.sleep(0.1)
for i in range(0, len(c)):
	send(IP(dst="192.168.56.102")/UDP(dport=ord(c[i])+10000))
	time.sleep(0.1)