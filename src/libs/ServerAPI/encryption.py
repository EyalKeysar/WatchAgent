import socket
import hashlib
import hmac
import os

# Function to simulate key exchange (simplified)
def key_exchange():
    # Generate random shared key
    key = os.urandom(16)
    return key

# Function to simulate HMAC calculation
def calculate_hmac(key, data):
    return hmac.new(key, data, hashlib.sha256).digest()

# Function to simulate server handshake
def server_handshake(conn):
    # Server sends its public key (simplified)
    server_key = key_exchange()
    conn.send(server_key)

    # Receive client's key
    client_key = conn.recv(1024)

    # Calculate HMACs
    server_hmac = calculate_hmac(server_key, client_key)
    client_hmac = calculate_hmac(client_key, server_key)

    # Send HMACs to the client
    conn.send(server_hmac)
    conn.recv(1024)  # Wait for client's acknowledgment
    conn.send(client_hmac)

# Function to simulate client handshake
def client_handshake(conn):
    # Receive server's public key
    server_key = conn.recv(1024)

    # Client generates its own key
    client_key = key_exchange()

    # Send client's key to the server
    conn.send(client_key)

    # Calculate HMACs
    client_hmac = calculate_hmac(client_key, server_key)
    server_hmac = calculate_hmac(server_key, client_key)

    # Send HMACs to the server
    conn.send(client_hmac)
    conn.recv(1024)  # Wait for server's acknowledgment
    conn.send(server_hmac)

# Server function
def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 8080))
    server_socket.listen(1)

    while True:
        conn, addr = server_socket.accept()
        print(f"Connection from {addr}")
        
        # Perform handshake
        server_handshake(conn)

        # Close connection after handshake
        conn.close()

# Client function
def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 8080))

    # Perform handshake
    client_handshake(client_socket)

    # Close connection after handshake
    client_socket.close()

if __name__ == "__main__":
    import threading

    # Start the server in a separate thread
    server_thread = threading.Thread(target=start_server)
    server_thread.start()

    # Start the client
    start_client()
