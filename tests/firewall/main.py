import subprocess
import socket
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

def flush_caches():
    # Define the command to flush the DNS cache
    command = 'ipconfig /flushdns'
    # Execute the command
    subprocess.run(command, shell=True)

    # Define the command to flush the ARP cache
    command = 'arp -d'
    # Execute the command
    subprocess.run(command, shell=True)

    # Define the command to flush the NetBIOS cache
    command = 'nbtstat -R'
    # Execute the command
    subprocess.run(command, shell=True)


# def get_ip_address(website):
#     # Use DNS lookup with a public DNS server (Google's DNS: 8.8.8.8)
#     result = subprocess.run(['nslookup', website, '8.8.8.8'], capture_output=True, text=True)
#     lines = result.stdout.split('\n')
#     flag = False
#     # Extract IP address from the output
#     for line in lines:
#         if 'Address' in line:
#             if flag:
#                 ip_address = line.split(': ')[1]
#                 print(ip_address)
#                 return ip_address
#             else:
#                 flag = True


def get_ip_address(domain):
    try:
        ip_address = socket.gethostbyname(domain)
        return ip_address
    except socket.gaierror:
        print(f"Unable to retrieve IP address for {domain}")
        return None

def block_website(website):
    # Get the IP address of the website
    ip_address = get_ip_address(website)
    print(ip_address)
    if ip_address:
        # Define the command to add a rule to Windows Firewall to block the website
        command = f'netsh advfirewall firewall add rule name="Block {website}" dir=out action=block protocol=any remoteip={ip_address}/32'
        # Execute the command
        subprocess.run(command, shell=True)
    else:
        print(f"Unable to retrieve IP address for {website}")
# def block_website(website):
#     # Define the command to add a rule to Windows Defender Firewall with Advanced Security to block outbound traffic to the specified domain
#     command = f'netsh advfirewall firewall add rule name="Block {website}" dir=out action=block program="%SystemDrive%\\Windows\\System32\\svchost.exe" remoteport=80,443 protocol=TCP remoteip={get_ip_address(website)}'
#     # Execute the command
#     subprocess.run(command, shell=True)



def unblock_website(website):
    # Define the command to delete the rule blocking the website
    command = f'netsh advfirewall firewall delete rule name="Block {website}"'
    # Execute the command
    subprocess.run(command, shell=True)

# flush_caches()
# print("flushed successfully")

# # Block ynet.com
# block_website('www.ynet.co.il')
print(get_ip_address('www.ynet.co.il'))

# RUN_TIME = 60
# for i in range(RUN_TIME):
#     print(f"Time remaining: {RUN_TIME - i} seconds")
#     time.sleep(1)

# Unblock ynet.com
# unblock_website('www.ynet.co.il')
