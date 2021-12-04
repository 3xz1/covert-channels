from modules.frameworklogging import log
import socket, sys
from struct import *
import textwrap
from modules import config
import time
import re
from model import model
from modules.state import STATE
import traceback

def serve():
	# create an INET STREAMing socket
	try:
		conn = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(3))
	except (socket.error, msg):
		print('Socket failed')
		sys.exit()

	ttl_channel = ""
	udp_channel = ""
	time_channel = ""
	start_time = time.time()
	run_time  = start_time
	start = 0
	
	while True:
		packet = conn.recvfrom(65565)
		
		#packet string from tuple
		packet = packet[0]
		
		#parse ethernet header
		eth_length = 14
		
		eth_header = packet[:eth_length]
		eth = unpack('!6s6sH' , eth_header)
		eth_protocol = socket.ntohs(eth[2])

		#Parse IP packets, IP Protocol number = 8
		if eth_protocol == 8 :
			#Parse IP header
			#take first 20 characters for the ip header
			ip_header = packet[eth_length:20+eth_length]

			#now unpack them :)
			iph = unpack('!BBHHHBBH4s4s' , ip_header)

			version_ihl = iph[0]
			version = version_ihl >> 4
			ihl = version_ihl & 0xF

			iph_length = ihl * 4

			ttl = iph[5]
			protocol = iph[6]	
			s_addr = socket.inet_ntoa(iph[8]);
			d_addr = socket.inet_ntoa(iph[9]);				

	
			#TCP protocol
			if protocol == 6 :
				t = iph_length + eth_length
				tcp_header = packet[t:t+20]

				#now unpack them :)
				tcph = unpack('!HHLLBBHHH' , tcp_header)
				
				source_port = tcph[0]
				dest_port = tcph[1]
				sequence = tcph[2]
				acknowledgement = tcph[3]
				doff_reserved = tcph[4]
				tcph_length = doff_reserved >> 4
				
	
				h_size = eth_length + iph_length + tcph_length * 4
				data_size = len(packet) - h_size
				
				#get data from the packet
				data = packet[h_size:]
				
				#print 'Data : ' + data

			#ICMP Packets
			elif protocol == 1 :
				if d_addr == "192.168.56.102": ### Addresses for each team must be set
					team_id = 2 ### Still need to made for each team
					###
					### Hole should be turned into a function
					###
					if(len(ttl_channel) < 44):
						ttl_channel += chr(ttl)
					else:
						if(len(ttl_channel) == 44):
							ttl_channel += chr(ttl)
						else:
							ttl_channel = ttl_channel[1::] + chr(ttl)
						flag_content = ttl_channel
						if(bool(re.search('hso_[0-9a-f]{5,40}_', flag_content))):
							log.error(flag_content)
							givePoints(flag_content, team_id)

				u = iph_length + eth_length
				icmph_length = 4
				icmp_header = packet[u:u+4]

				#now unpack them :)
				icmph = unpack('!BBH' , icmp_header)
				
				icmp_type = icmph[0]
				code = icmph[1]
				checksum = icmph[2]

				h_size = eth_length + iph_length + icmph_length
				data_size = len(packet) - h_size
				
				#get data from the packet
				data = packet[h_size:]
				
				#print 'Data : ' + data

			#UDP packets
			elif protocol == 17 :
				u = iph_length + eth_length
				udph_length = 8
				udp_header = packet[u:u+8]

				#now unpack them :)
				udph = unpack('!HHHH' , udp_header)
				
				source_port = udph[0]
				dest_port = udph[1]
				length = udph[2]
				checksum = udph[3]
							
				h_size = eth_length + iph_length + udph_length
				data_size = len(packet) - h_size
				
				#get data from the packet
				data = packet[h_size:]
				if(dest_port > 9999 and dest_port < 10256):
					team_id = 2
					if d_addr == "192.168.56.102":
						if(len(udp_channel) < 44):
							udp_channel += chr(dest_port -10000)
						else:
							if(len(udp_channel) == 44):
								udp_channel += chr(dest_port - 10000)
							else:	
								udp_channel = udp_channel[1::] + chr(dest_port - 10000)
							flag_content = udp_channel
							log.error(flag_content + ' flag_content')
							if(bool(re.search('hso_[0-9a-f]{5,40}_', flag_content))):
								log.error(flag_content)
								givePoints(flag_content, team_id)

				else:
					#print(d_addr)
					if d_addr == "192.168.56.102": ### Addresses for each team must be set
						team_id = 2 ### Still need to made for each team
						###
						### Hole should be turned into a function
						###wwwwwwwwwwwwwwwwq1
						if(start_time == run_time):
							start_time = time.time()

						end_time = time.time() - start_time
						start_time = time.time()
						if(start == 1):
							if(end_time >= 1):
								time_channel += "1"
							else:
								time_channel += "0"
						else:
							start +=1

						if(len(time_channel)==360):
							flag = decode_binary_string(time_channel)
							if(bool(re.search('hso_[0-9a-f]{5,40}_', flag))):
								time_channel = ""
								start = 0
								start_time = run_time
								flag_content = flag
								givePoints(flag_content, team_id)

def decode_binary_string(s):
	return ''.join(chr(int(s[i*8:i*8+8],2)) for i in range(len(s)//8))

def givePoints(flag_content, team_id):
	try:
		session = model.open_session()
		flag = model.get_flag_by_content(session, flag_content)
		model.remove_session()
		if(len(flag) ==1):
			flag = flag[0]
			if flag.team_id == team_id:
				log.error("Flag submission")
				flag_submission = model.get_flag_submission_by_flag_id_team_id(session, flag.id, team_id)
				if(len(flag_submission)==0 and model.submit_flag(session, flag.id, team_id)):
					team = model.get_team_by_id(session, team_id)
					if(len(team) == 1):
						team[0].score = team[0].score +25
						session.commit()
					else:
						log.error("team len !=1 ")
				else:
					log.error("flag_submission != 0 or get_flag_submission_by_flag_id_team_id wrong")
			else:
				log.error("Not your own FLAG!")
	except Exception:
		log.error(traceback.format_exc())
	model.remove_session()