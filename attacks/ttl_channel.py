import sys
from scapy.all import send,sr1,IP,ICMP
import time

a = "hso_83ed8c982460b37e3190ba25a1d8bb46db342a7c_"
for i in range(0, len(a)):
	send(IP(dst="192.168.56.102", ttl=ord(a[i]))/ICMP())
	time.sleep(0.1)