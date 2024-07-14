"""
This code works for two computers on same wifi/network.
The server can find out it's IP address using the "ipconfig" command in terminal.
Make sure to use a port which is not reserved for any other process. Usually ports like 9999 or 1234 works fine.
Make sure to start the server first then the client.
"""

import socket
import threading
import random
import math
from sympy import isprime


### Creating the RSA algorithm:


def generate_keypair(
    p, q
):  # p and q are prime numbers. Large p and q means better encryption.
    if not (isprime(p) and isprime(q)):
        raise ValueError("Both numbers must be prime.")
    elif p == q:
        raise ValueError("p and q cannot be the same")
    n = p * q
    phi = (p - 1) * (q - 1)
    e = random.randrange(1, phi)
    g = math.gcd(e, phi)
    while g != 1:
        e = random.randrange(1, phi)
        g = math.gcd(e, phi)
    d = modinv(e, phi)
    return ((e, n), (d, n))


def modinv(a, m):
    m0, x0, x1 = m, 0, 1
    if m == 1:
        return 0
    while a > 1:
        q = a // m
        m, a = a % m, m
        x0, x1 = x1 - q * x0, x0
    if x1 < 0:
        x1 += m0
    return x1


# pow function with 3 arguments means - arg1 ** arg2 % arg3


def encrypt(pk, plaintext):
    key, n = pk
    cipher = [pow(ord(char), key, n) for char in plaintext]
    return cipher


def decrypt(pk, encryptext):
    key, n = pk
    plain = [chr(pow(char, key, n)) for char in encryptext]
    return "".join(plain)


### RSA algorithm completed.


def exchange_keys(c, pk):
    c.send(f"{pk[0]} {pk[1]}".encode())
    received_key = c.recv(1024).decode()
    e, n = map(
        int, received_key.split()
    )  # convert the string to int and store in e and n
    return (e, n)


choice = input("Do you want to host (1) or to connect (2): ")

if choice == "1":
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ip = input("Your IP address: ")
    port = int(input("Port: "))
    server.bind((ip, port))
    server.listen()

    client, address = server.accept()
    print("Client Connected.")

    # Generate RSA key pair for server
    public_key, private_key = generate_keypair(61, 53)
    print(f"Server Public Key: {public_key}")

    # Exchange keys with the client
    client_public_key = exchange_keys(client, public_key)
    print(f"Client Public Key: {client_public_key}")
    print("Start Chatting \n")

elif choice == "2":
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ip = input("Server IP address: ")
    port = int(input("Port: "))
    client.connect((ip, port))
    print("Connected to the server.")

    # Generate RSA key pair for client
    public_key, private_key = generate_keypair(61, 53)
    print(f"Client Public Key: {public_key}")

    # Exchange keys with the server
    server_public_key = exchange_keys(client, public_key)
    print(f"Server Public Key: {server_public_key}")
    print("Start Chatting \n")

else:
    exit()


def sending_messages(c, pk):
    while True:
        message = input("")
        encrypted_message = encrypt(pk, message)
        c.send(str(encrypted_message).encode())
        print("You: " + message)


def receiving_messages(c, pk):
    while True:
        encrypted_message = c.recv(1024).decode()
        message = decrypt(pk, eval(encrypted_message))
        print("Partner: " + message)


if choice == "1":
    threading.Thread(target=sending_messages, args=(client, client_public_key)).start()
    threading.Thread(target=receiving_messages, args=(client, private_key)).start()
elif choice == "2":
    threading.Thread(target=sending_messages, args=(client, server_public_key)).start()
    threading.Thread(target=receiving_messages, args=(client, private_key)).start()
