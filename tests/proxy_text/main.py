import os
import socket
import time
from pydivert.windivert import WinDivert
from scapy.all import DNS, IP, UDP
os.system('ipconfig /flushdns')
# allowed_ips = []  # Replace with your allowed IPs

# with WinDivert() as w:
#     for packet in w:
#         if packet.src_addr not in allowed_ips:
#             print(f"Packet dropped from {packet.src_addr}")
#         else:
#             print(f"Packet allowed from {packet.src_addr}")
#             w.send(packet)



blocked_domains = ["www.ynet.co.il", "www.globes.co.il"]
blocked_ips = []

def update_blocked_ips():
    global blocked_ips
    blocked_ips = []
    for domain in blocked_domains:
        try:
            addr_info = socket.getaddrinfo(domain, None)
            for info in addr_info:
                blocked_ips.append(info[4][0])
        except socket.gaierror:
            print(f"Failed to resolve {domain}")

update_blocked_ips()
try:
    with WinDivert() as w:
        last_update_time = time.time()
        for packet in w:
            # Update the blocked IPs every minute
            if time.time() - last_update_time > 60:
                update_blocked_ips()
                last_update_time = time.time()

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
            elif packet.dst_addr in blocked_ips:
                print(f"Blocked traffic to {packet.dst_addr}")
            else:
                w.send(packet)
except OSError as e:
    print(e)