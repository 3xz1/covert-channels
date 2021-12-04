import socket
import struct
import textwrap

def main():
    conn = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(3))
    message = ""
    
    while True:
        #print(message)
        raw_data, addr = conn.recvfrom(65535)
        dest_mac, src_mac, eth_proto, data = ethernet_frame(raw_data)
        #print('\nEthernet Frame:')
        #print('Destination: {}, Source{}, Protocol: {}'.format(dest_mac, src_mac, eth_proto))
        
        # 8 for IPv4
        if eth_proto == 8:
            (version, header_length, ttl, proto, src, target, data) = ipv4_packet(data)
            if target == "192.168.56.102":
                #print('\tIPv4 Packet:')
                #print('\t\tVersion: {}, Header Length: {}, TTL: {}'.format(version, header_length, ttl))
                #print('\t\tProtocol: {}, Source: {}, Target: {}'.format(proto, src, target))
                print(src_mac)
                if proto == 1:
                    icmp_type, code, checksum, data = icmp_packet(data)
                    message += chr(ttl)
                    print(message)
                elif proto == 6:
                    (src_port, dest_port, sequence, acknownledgment, flag_urg, flack_ack, flag_psh, flag_rst, flag_syn, flag_fin, data) = tcp_packet(data)
                    #print('\tTCP Segment:')
                    #print('\t\tSource Port:{}, Destination Port: {}'.format(src_port, dest_port))
                elif proto == 17:
                        print(src_mac, dest_mac)
                        (src_port, dest_port, size, data) = udp_packet(data)
                        if(dest_port > 10000 and dest_port < 10256):
                            message += chr(dest_port-10000) #10255
                            print(message)
                        elif(dest_port == 22222):
                            message += src_mac
                            print(bytes.fromhex(message).decode("utf-8"))
                            print(src_mac)


# Unpack ethernet frames
def ethernet_frame(data):
    dest_mac, src_mac, proto = struct.unpack('! 6s 6s H', data[:14])
    return get_mac_addr(dest_mac), get_mac_addr(src_mac), socket.htons(proto), data[14:]

# Return formatted MAC
def get_mac_addr(addr):
    #print(addr)
    return ""
def ipv4(src):
    return '.'.join(map(str, src))

# Unpack IPv4
def ipv4_packet(data):
    version_header_length = data[0]
    version = version_header_length >> 4
    header_length = (version_header_length & 15) *4
    ttl, proto, src, target = struct.unpack('! 8x B B 2x 4s 4s', data[:20])
    return version, header_length, ttl, proto, ipv4(src), ipv4(target), data[header_length:]


# Unpack ICMP
def icmp_packet(data):
    icmp_type, code, checksum = struct.unpack('! B B H', data[:4])
    return icmp_type, code, checksum, data[4:]

# Unpack TCP
def tcp_packet(data):
    (src_port, dest_port, sequence, acknownledgement, offset_reserved_flags) = struct.unpack('! H H L L H', data[:14])
    offset = (offset_reserved_flags >> 12) * 4
    flag_urg = (offset_reserved_flags & 32) >> 5
    flag_ack = (offset_reserved_flags & 16) >> 4
    flag_psh = (offset_reserved_flags &  8) >> 3
    flag_rst = (offset_reserved_flags &  4) >> 2
    flag_syn = (offset_reserved_flags &  2) >> 1
    flag_fin = offset_reserved_flags & 1
    return src_port, dest_port, sequence, acknownledgement, flag_urg, flag_ack, flag_psh, flag_rst, flag_syn, flag_fin, data[offset:]

# Unpack UDP
def udp_packet(data):
    src_port, dest_port, size = struct.unpack('! H H 2x H', data[:8])
    return src_port, dest_port, size, data[8:]

def pack_mac(packme):
    a,b,c,d,e,f = map(lambda x:int(x,16), packme.split(":"))
    return struct.pack('BBBBBB', a, b, c, d, e, f)

def unpack_mac(packed):
    mac = map(str, struct.unpack('BBBBBB', packed))
    return '.'.join(mac)

#main()
