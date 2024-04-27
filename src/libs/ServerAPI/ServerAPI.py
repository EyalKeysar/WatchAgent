from .const import *
import threading
import time
import json
from .s_socket import *


"""
For reference, this is client side code

import socket
import s_socket

def start_secure_client(host, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    print(f"Connected to {host}:{port}")

    tls_protocol = s_socket.TLSProtocol(client_socket)
    tls_protocol.client_handshake()

    while True:
        message = input("Enter message to send (type 'quit' to exit): ")
        if message == 'quit':
            break
        tls_protocol.send(message)
        decrypted_data = tls_protocol.receive()
        print("Received:", decrypted_data)

    s_socket.close(client_socket)

if __name__ == "__main__":
    HOST = '127.0.0.1'
    PORT = 12345
    start_secure_client(HOST, PORT)
"""


class ServerAPI:
    '''
        This class is used by the clients to communicate with the server.
    '''

    def __init__(self):
        host = SERVER_IP
        port = SERVER_PORT
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.connect((host, port))
        print(f"Connected to {host}:{port}")

        self.tls_protocol = TLSProtocol(self.server_socket)
        self.tls_protocol.client_handshake()




    def build_request(self, service, command, *args):
        '''
            This method is used to build the request to be sent to the server.
        '''
        if args == ():
            return f"{service}{ARGS_SEPERATOR}{command}"
        else:
            print("args: ", args)
            return f"{service}{ARGS_SEPERATOR}{command}{ARGS_SEPERATOR}" + f"{ARGS_SEPERATOR}".join(args) 


# AUTHENTICATION -----------------------------------------------------------------------------------------------------

    def login(self, email, password):
        '''
            This method is used to login to the server.
        '''
        self.tls_protocol.send(self.build_request("auth", "login", email, password))
        return self.tls_protocol.receive()
    
    def signup(self, email, password, username):
        '''
            This method is used to signup to the server.
        '''
        self.tls_protocol.send(self.build_request("auth", "signup", email, password, username))
        return self.tls_protocol.receive()
    
    def new_agent_request(self, mac_address):
        '''
            This method is used to send a new agent request to the server.
        '''
        self.tls_protocol.send(self.build_request("auth", "new_agent", mac_address))
        time.sleep(1)
        return self.tls_protocol.receive()
# ---------------------------------------------------------------------------------------------------------------------


# FETCHING INFORMATION -----------------------------------------------------------------------------------------------
    def get_info(self):
        '''
            This method is used to get the information from the server.
        '''
        self.tls_protocol.send(self.build_request("fetch", "parents"))
        return self.tls_protocol.receive()

    def get_statistics(self):
        '''
            This method is used to get the statistics from the server.
        '''
        self.tls_protocol.send(self.build_request("fetch", "statistics"))
        return self.tls_protocol.receive()
    
    def get_restrictions(self):
        '''
            This method is used to get the restrictions from the server.
        '''
        self.tls_protocol.send(self.build_request("fetch", "restrictions"))
        
        return self.tls_protocol.receive()

    def get_children(self):
        '''
            This method is used to get the children from the server.
        '''
        self.tls_protocol.send(self.build_request("fetch", "children"))
        respond = self.tls_protocol.receive()
        # parse the respond as json of list of ChildData
        print("respond (json ch)" + respond)
        self.children = json.loads(respond)
        return self.children
        

# ---------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    server = ServerAPI()
    print(server.get_info())