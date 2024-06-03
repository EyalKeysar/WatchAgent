import socket
import threading
import hashlib
import random
from Crypto.Cipher import AES
import os
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from Crypto.Util.py3compat import *


# Diffie-Hellman Key Exchange
class DiffieHellman:
    def __init__(self, prime, base):
        self.prime = prime
        self.base = base
        self.private_key = random.randint(1, prime - 1)
        self.public_key = pow(base, self.private_key, prime)
        self.shared_secret = None

    def compute_shared_secret(self, other_public_key):
        print(f"pow({other_public_key}, {self.private_key}, {self.prime})")
        self.shared_secret = pow(other_public_key, self.private_key, self.prime)


class AESCipher:
    def __init__(self, key):
        self.key = key
        self.block_size = AES.block_size
    
    def encrypt(self, plaintext):
        iv = get_random_bytes(self.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        ciphertext = cipher.encrypt(pad(plaintext.encode(), self.block_size))
        return iv + ciphertext

    def decrypt(self, ciphertext):
        if len(ciphertext) < self.block_size:
            raise ValueError("Invalid ciphertext")
        
        iv = ciphertext[:self.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        plaintext = unpad(cipher.decrypt(ciphertext[self.block_size:]), self.block_size)
        return plaintext.decode()

# TLSProtocol
class TLSProtocol:
    def __init__(self, socket):
        self.socket = socket
        self.client_public_key = None
        self.server_public_key = None
        self.shared_secret = None
        self.aes_cipher = None

    def client_handshake(self):
        print("\n\n -- client handshake --")
        prime = 9973
        base = 1567

        diffie_hellman = DiffieHellman(prime, base)  # Example prime and base values
        self.client_public_key = diffie_hellman.public_key
        print(f"public key: {self.client_public_key}\nprivate key: {diffie_hellman.private_key}\nprime: {prime}\nbase: {base}\n\n")

        # Send ClientHello with client's public key
        client_hello = f"ClientHello:{self.client_public_key}"
        self.socket.send(client_hello.encode())

        # Receive ServerHello with server's public key
        server_hello = self.socket.recv(1024)
        self.server_public_key = int(server_hello.split(b":")[1])
        print("received server hello public key: ", self.server_public_key)

        # Compute shared secret using Diffie-Hellman
        diffie_hellman.compute_shared_secret(self.server_public_key)
        self.shared_secret = diffie_hellman.shared_secret

        # Initialize AES cipher with shared secret
        hash_object = hashlib.sha256()
        hash_object.update(str(self.shared_secret).encode('utf-8'))
        hashed_key = hash_object.digest()
        self.aes_cipher = AESCipher(hashed_key)

        print(f"handshake complete, shared secret: {self.shared_secret}\n\n")

    def server_handshake(self):
        """
        Performs server-side TLS handshake.
        """
        print("\n\n -- server handshake --")
        # Receive ClientHello with client's public key
        print("waiting for client hello")
        print("self socket: ", self.socket)
        client_hello = self.socket.recv(1024)
        client_public_key = int(client_hello.split(b":")[1])
        self.client_public_key = client_public_key
        print("received client hello public key: ", client_public_key)

        # Generate server's Diffie-Hellman parameters
        diffie_hellman = DiffieHellman(9973, 1567)  # Example prime and base values
        self.server_public_key = diffie_hellman.public_key
        print("server public key: ", self.server_public_key, "private key: ", diffie_hellman.private_key, "\n\n")

        # Send ServerHello with server's public key
        server_hello = f"ServerHello:{self.server_public_key}"
        self.socket.send(server_hello.encode())

        # Compute shared secret using Diffie-Hellman
        diffie_hellman.compute_shared_secret(self.client_public_key)
        self.shared_secret = diffie_hellman.shared_secret

        # Initialize AES cipher with shared secret
        hash_object = hashlib.sha256()
        hash_object.update(str(self.shared_secret).encode('utf-8'))
        hashed_key = hash_object.digest()
        self.aes_cipher = AESCipher(hashed_key)

        print(f"handshake complete, shared secret: {self.shared_secret}\n\n")


    def send(self, data):
        if self.aes_cipher is None:
            raise Exception("AES cipher is not initialized.")
        encrypted_data = self.aes_cipher.encrypt(data)

        send(self.socket,encrypted_data)

    def receive(self):
        if self.aes_cipher is None:
            raise Exception("AES cipher is not initialized.")
        encrypted_data = receive(self.socket)
        if not encrypted_data:
            return None
        decrypted_data = self.aes_cipher.decrypt(encrypted_data)
        return decrypted_data

LENGTH_PREFIX_SIZE = 10

def add_length_prefix(data):
    length = len(data)
    return length.to_bytes(LENGTH_PREFIX_SIZE, byteorder='big') + data

def send(socket, data):
    data = add_length_prefix(data)
    socket.send(data)

def receive(socket):
    length_prefix = socket.recv(LENGTH_PREFIX_SIZE)
    length = int.from_bytes(length_prefix, byteorder='big')
    print("length: ", length)
    data = socket.recv(length)
    # make sure all data is received
    while len(data) < length:
        data += socket.recv(length - len(data))
    return data


def close(socket):
    socket.close()