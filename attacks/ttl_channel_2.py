import socket
import time
import random
import struct

ethernet  = b'\x00\x0c\x29\xd3\xbe\xd6' # MAC Address Destination
ethernet += b'\x00\x0c\x29\xe0\xc4\xaf' # MAC Address Source
ethernet += b'\x08\x00'                 # Protocol-Type: IPv4

ip_header  = b'\x45\x00\x00\x28'            # Version, IHL, Type of Service | Total Length
ip_header += b'\xab\xcd\x00\x00'            # Identification | Flags, Fragment Offset
ip_header_ttl = b'\xff'                     # TTL
ip_header_pro = b'\x06'                     # Protocol
ip_header_checksum = b'\x00\x00'             # Header Checksum 0x0000 for calculatiom
ip_header_source = b'\xc0\xa8\x01\xc9'      # Source Address
ip_header_dest = b'\xc0\xa8\x01\xc9'        # Destination Address

tcp_header_src_port  = b'\x54\x54' # Source Port
tcp_header_dest_port = b'\x30\x39' # Destination Port
tcp_header = b'\x01\x22\x00\x00' # Sequence Number
tcp_header += b'\x00\x00\x00\x00' # Acknowledgement Number
tcp_header += b'\x50\x02\x71\x10' # Data Offset, Reserved, Flags | Window Size
tcp_header_checksum = b'\x00\x00' # Checksum  
tcp_header_urgent_pointer = b'\x00\x00' # Urgent Pointer


#
# Function to calculate ip header checksum
# Return check sum as bytes
#
def calc_ip_checksum(ip_header):
	ip_checksum = 0 
	for i in range(0, len(ip_header), 2):
		ip_checksum += int.from_bytes(ip_header[i:i+2], "big")
	if(len(hex(ip_checksum)) > 6):
		ip_checksum = 0xffff - (ip_checksum - (ip_checksum >> 16 << 16) + (ip_checksum >> 16))
		return ip_checksum.to_bytes(2, "big")
	else:
		return ip_checksum.to_bytes(2, "big")
#
# Function to calculate tcp header checksum
# Returns check sum as bytes
#
def calc_tcp_checksum(tcp_header): 
	tcp_checksum = 0
	tcp_protocol = b'\x00\x06' # IP Protocol 6 = TCP
	tcp_length = b'\x00\x14'            # Length of TCP packet
	
	# Combine all needed headers
	tcp_header = tcp_protocol + ip_header_source + ip_header_dest + tcp_length + tcp_header
	# Loop to calculate check sum 
	for i in range(0, len(tcp_header), 2):
		tcp_checksum += int.from_bytes(tcp_header[i:i+2], "big") # Get Integer from bytes and add it to check sum
	# If carry over remove, add at last spot and negation with 0xffff
	if(len(hex(tcp_checksum)) > 6):
		# tcp_check_sum >> 16 << 16 to remove carry over
		# tcp_check_sum >> 16 to add carry over
		tcp_checksum = 0xffff - (tcp_checksum - (tcp_checksum >> 16 << 16) + (tcp_checksum >> 16))
		return tcp_checksum.to_bytes(2, "big") # return tcp check sum as bytes
	else:
		return tcp_checksum.to_bytes(2, "big") 

# Send some data over ttl:
dataToSend= 'hso_f7a87448296f18a140c1810723b703aaec12eb60_'
for i in range(0, len(dataToSend)):#	len(dataToSend)):
	s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
	ip_header_ttl = b'\xff'
	#tcp_header_src_port = struct.pack('! H', 5959)
	ip_header_checksum = calc_ip_checksum(ip_header + ip_header_ttl + ip_header_pro + ip_header_checksum + ip_header_source + ip_header_dest)
	# run calculation of the checksum
	tcp_checksum = calc_tcp_checksum(tcp_header_src_port + tcp_header_dest_port +tcp_header+tcp_header_checksum + tcp_header_urgent_pointer)
	# set packet together
	tcp_header = tcp_header_src_port + tcp_header_dest_port + tcp_header + tcp_checksum + tcp_header_urgent_pointer
	ip_header = ip_header + ip_header_ttl + ip_header_pro + ip_header_checksum + ip_header_source + ip_header_dest

	packet = ip_header + tcp_header
	# send packet
	#s.setsockopt(socket.IPPROTO_ICMP, socket.IP_TTL, ord(dataToSend[i]))
	s.setsockopt(socket.SOL_IP, socket.IP_TTL, ord(dataToSend[i]))
	#s.sendto(bytes("", "UTF-8"), ('192.168.56.102', 0))
	s.sendto(packet, ('192.168.56.102', 0))
	s.close()

