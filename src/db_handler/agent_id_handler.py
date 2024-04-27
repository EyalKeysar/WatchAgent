import os
import getmac


def check_agent_id(agent_id):
    # Agent id is a 32 character string that stored in a file
    # Check if the file exists
    if not os.path.exists("agent_id.txt"):
        return False
    else:
        return True
    
def get_agent_id():
    # Read the agent id from the file
    with open("agent_id.txt", "r") as file:
        agent_id = file.read().strip()
    return agent_id

def set_agent_id(agent_id):
    # Write the agent id to the file
    with open("agent_id.txt", "w") as file:
        file.write(agent_id)

def generate_agent_id(server_api):
    # Generate a new agent id
    mac_address = getmac.get_mac_address()
    print(mac_address)
    agent_id = server_api.new_agent_request(mac_address)
    return agent_id