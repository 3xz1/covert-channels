import sys
from scapy.all import send,sr1,IP,ICMP, UDP, TCP
import time
import random

a = "hso_c95e051d811940ec0f81cafd5b6e1596691ca5fb_" 
res = ''.join(format(ord(i), '08b') for i in a)
res += "0"
print(len(res)-1)
for i in range(0, len(res)):
	dport = random.randint(11000,40000)
	send(IP(dst="192.168.56.102", ttl=64)/UDP(dport=dport))
	if(int(res[i]) == 1):
		time.sleep(1)