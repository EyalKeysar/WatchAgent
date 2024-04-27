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
