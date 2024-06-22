from .const import *
import threading
import time
import json
from .s_socket import *
from .shared.SharedDTO import *
import base64

class ServerAPI:
    '''
        This class is used by the clients to communicate with the server.
    '''

    # connection needed decorator
    def connection_needed(func):
        def wrapper(self, *args, **kwargs):
            if not self.is_connected:
                raise Exception("Not connected to the server")
            return func(self, *args, **kwargs)
        return wrapper
    
    # connection exeption catcher decorator
    def connection_exception_catcher(func):
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                self.server_socket.close()
                self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.is_connected = False
                return str(e)
        return wrapper
    
    # authentication needed decorator
    def authentication_needed(func):
        def wrapper(self, *args, **kwargs):
            if not self.is_authenticated:
                raise Exception("Not authenticated")
            return func(self, *args, **kwargs)
        return wrapper


    def __init__(self):
        self.host = SERVER_IP
        self.port = SERVER_PORT
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.is_connected = False
        self.is_authenticated = False
        
    @connection_exception_catcher
    def connect(self):
        '''
            This method is used to connect to the server.
        '''
        if self.is_connected:
            return
        self.server_socket.connect((self.host, self.port))
        print(f"Connected to {self.host}:{self.port}")

        self.tls_protocol = TLSProtocol(self.server_socket)
        self.tls_protocol.client_handshake()
        self.is_connected = True

    @connection_exception_catcher
    @connection_needed
    def ping(self):
        '''
            This method is used to ping the server.
        '''
        self.tls_protocol.send("ping")
        return self.tls_protocol.receive()


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
    @connection_exception_catcher
    @connection_needed
    def login(self, email, password):
        '''
            This method is used to login to the server.
        '''
        self.tls_protocol.send(self.build_request("auth", "login", email, password))
        response = self.tls_protocol.receive()

        if response == "True":
            self.is_authenticated = True
            return True
        else:
            return response


    @connection_exception_catcher
    @connection_needed
    def signup(self, email, password, username):
        '''
            This method is used to signup to the server.
        '''
        self.tls_protocol.send(self.build_request("auth", "signup", email, password, username))
        response = self.tls_protocol.receive()

        if response == "True":
            self.is_authenticated = True
            return True
        else:
            return response


    @connection_exception_catcher
    @connection_needed
    def new_agent_request(self, mac_address):
        '''
            This method is used to send a new agent request to the server.
        '''
        self.tls_protocol.send(self.build_request("auth", "new_agent", mac_address))
        response = self.tls_protocol.receive()
        auth_str = response.split(ARGS_SEPERATOR)
        return auth_str
        

    @connection_exception_catcher
    @connection_needed
    def login_agent(self, auth_str):
        '''
            This method is used to login as an agent to the server.
        '''
        self.tls_protocol.send(self.build_request("auth", "login_agent", auth_str))
        response = self.tls_protocol.receive()
        if "True" in str(response):
            self.is_authenticated = True
            return True
        else:
            return response
# ---------------------------------------------------------------------------------------------------------------------

# RESTRICTIONS MANAGEMENT --------------------------------------------------------------------------------------------

    @authentication_needed
    @connection_exception_catcher
    @connection_needed
    def add_restriction(self, child_name, program_name, start_time, end_time, allowed_time, time_span):
        '''
            This method is used to add a restriction to the server.
        '''
        self.tls_protocol.send(self.build_request("restrict", "add_restriction", child_name, program_name, start_time, end_time, allowed_time, time_span))
        return self.tls_protocol.receive()

    @authentication_needed
    @connection_exception_catcher
    @connection_needed
    def remove_restriction(self, child_name, program_name):
        '''
            This method is used to remove a restriction from the server.
        '''
        self.tls_protocol.send(self.build_request("restrict", "remove_restriction", child_name, program_name))
        return self.tls_protocol.receive()

    @authentication_needed
    @connection_exception_catcher
    @connection_needed
    def update_known_programs(self, programs_list):
        '''
            This method is used to add a known program to the server.
        '''
        self.tls_protocol.send(self.build_request("restrict", "update_known_programs", StringListSerializer.serialize(programs_list)))
        return self.tls_protocol.receive()
    


# FETCHING INFORMATION -----------------------------------------------------------------------------------------------
    @connection_exception_catcher
    @connection_needed
    def get_info(self):
        '''
            This method is used to get the information from the server.
        '''
        self.tls_protocol.send(self.build_request("fetch", "parents"))
        return self.tls_protocol.receive()

    @authentication_needed
    @connection_exception_catcher
    @connection_needed
    def get_statistics(self):
        '''
            This method is used to get the statistics from the server.
        '''
        self.tls_protocol.send(self.build_request("fetch", "statistics"))
        return self.tls_protocol.receive()
    
    @authentication_needed
    @connection_exception_catcher
    @connection_needed
    def get_restrictions(self, child_name):
        '''
            This method is used to get the restrictions from the server.
        '''
        self.tls_protocol.send(self.build_request("fetch", "restrictions", child_name))
        
        respond = self.tls_protocol.receive()
        # parse the respond as json of list of RestrictionData
        print("respond (json res)" + respond)
        return RestrictionListSerializer.deserialize(respond)

    @authentication_needed
    @connection_exception_catcher
    @connection_needed
    def get_children(self):
        '''
            This method is used to get the children from the server.
        '''
        self.tls_protocol.send(self.build_request("fetch", "children"))
        respond = self.tls_protocol.receive()
        # parse the respond as json of list of ChildData
        print("respond (json ch)" + respond)
        self.children = ChildListSerializer.deserialize(respond)
        return self.children
    
    @authentication_needed
    @connection_exception_catcher
    @connection_needed
    def get_programs(self, child_name):
        '''
            This method is used to get the available programs from the server.
        '''
        self.tls_protocol.send(self.build_request("fetch", "programs", child_name))
        return StringListSerializer.deserialize(self.tls_protocol.receive())
        
    @authentication_needed
    @connection_exception_catcher
    @connection_needed
    def agent_get_restrictions(self):
        '''
            This method is used to get the restrictions from the server.
        '''
        self.tls_protocol.send(self.build_request("fetch", "agent_restrictions"))
        return self.tls_protocol.receive()

# ---------------------------------------------------------------------------------------------------------------------



# CHILDREN MANAGEMENT -----------------------------------------------------------------------------------------------
    @authentication_needed
    @connection_exception_catcher
    @connection_needed
    def confirm_agent(self, auth_str, child_name):
        '''
            This method is used to confirm the agent.
        '''
        self.tls_protocol.send(self.build_request("manage", "confirm_agent", auth_str, child_name))
        return self.tls_protocol.receive()


# STREAMING ---------------------------------------------------------------------------------------------------------


    @authentication_needed
    @connection_exception_catcher
    @connection_needed
    def subscribe(self, child_name, type):
        '''
            This method is used to subscribe to the server.
        '''
        self.tls_protocol.send(self.build_request("stream", "subscribe", child_name, type))
        return self.tls_protocol.receive()
    
    @authentication_needed
    @connection_exception_catcher
    @connection_needed
    def unsubscribe(self, child_name, type):
        '''
            This method is used to unsubscribe from the server.
        '''
        self.tls_protocol.send(self.build_request("stream", "unsubscribe", child_name, type))
        return self.tls_protocol.receive()
    
    @authentication_needed
    @connection_exception_catcher
    @connection_needed
    def get_frame(self, child_name, type):
        '''
            This method is used to get a frame from the server.
        '''
        self.tls_protocol.send(self.build_request("stream", "get_frame", child_name, type))

        return self.tls_protocol.receive()
        
    
    @authentication_needed
    @connection_exception_catcher
    @connection_needed
    def set_frame(self, stream_type, frame):
        '''
            This method is used to set a frame to the server.
        '''
        frame = base64.b64encode(frame).decode('utf-8')
        self.tls_protocol.send(self.build_request("stream", "set_frame", stream_type, frame))

        return self.tls_protocol.receive()

    @authentication_needed
    @connection_exception_catcher
    @connection_needed
    def update_program_usage(self, program_name, start_time):
        '''
            This method is used to update the program usage.
        '''
        self.tls_protocol.send(self.build_request("restrict", "update_program_usage", program_name, start_time))
        return self.tls_protocol.receive()


if __name__ == '__main__':
    server = ServerAPI()
    print(server.get_info())