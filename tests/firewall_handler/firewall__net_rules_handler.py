import subprocess

class FirewallNetRulesHandler:
    @staticmethod
    def get_ip_address(website):
        # Use DNS lookup to get the IP address of the website
        result = subprocess.run(['nslookup', website], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        # Extract IP address from the output
        for line in lines:
            if 'Address' in line:
                ip_address = line.split(': ')[1]
                return ip_address

    @staticmethod
    def block_website(website):
        # Get the IP address of the website
        ip_address = FirewallNetRulesHandler.get_ip_address(website)
        if ip_address:  
            # Define the command to add a rule to Windows Firewall to block the website
            command = f'netsh advfirewall firewall add rule name="Block {website}" dir=out action=block protocol=any remoteip={ip_address}/32'
            # Execute the command
            subprocess.run(command, shell=True)
        else:
            print(f"Unable to retrieve IP address for {website}")

    def unblock_website(website):
        # Define the command to delete the rule blocking the website
        command = f'netsh advfirewall firewall delete rule name="Block {website}"'
        # Execute the command
        subprocess.run(command, shell=True)