import os
import socket
import time
from pydivert.windivert import WinDivert
from scapy.all import DNS, IP, UDP

os.system('ipconfig /flushdns')

blocked_domains = ["www.ynet.co.il", "www.globes.co.il"]
blocked_ips = []
error_state = False  # Add a flag for the error state

def update_blocked_ips():
    global blocked_ips, error_state
    blocked_ips = []
    for domain in blocked_domains:
        try:
            addr_info = socket.getaddrinfo(domain, None)
            for info in addr_info:
                blocked_ips.append(info[4][0])
        except socket.gaierror:
            print(f"Failed to resolve {domain}")
            error_state = True  # Set the error state flag

update_blocked_ips()

while True:  # Add an infinite loop
    try:
        if time.time() - last_update_time > 60:
            update_blocked_ips()
            last_update_time = time.time()

        with WinDivert() as w:
            last_update_time = time.time()
            for packet in w:
                if error_state:  # Drop all packets if in error state
                    print("In error state, dropping all packets")
                    continue

                if packet.udp and packet.dst_port == 53:
                    scapy_packet = IP(bytes(packet.raw))
                    if scapy_packet.haslayer(DNS):
                        dns_layer = scapy_packet.getlayer(DNS)
                        for query in dns_layer.qd:
                            if query.qname.decode('utf-8') in blocked_domains:
                                print(f"Blocked DNS request for {query.qname.decode('utf-8')}")
                                break
                        else:
                            w.send(packet)
                    else:
                        w.send(packet)  # Add this line to allow non-DNS UDP packets
                elif packet.dst_addr in blocked_ips:
                    print(f"Blocked traffic to {packet.dst_addr}")
                else:
                    w.send(packet)
    except Exception as e:
        print(f"An error occurred: {e}")
        error_state = True  # Set the error state flag