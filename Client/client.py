import socket
import sys
import json
import os

HOST = "127.0.0.1" # The server's hostname or IP address
PORT = 65432 # The port used by the server

CLIENT_DIR = "Client" # Directory where the file will be saved

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    addr = (HOST,PORT)
    print(f"Accepted connection from {addr}")
    s.connect((HOST,PORT))
    connection = True
    while connection:
        request = input("Enter the name of the file you want to request from the server (e.g. hello.txt): ")
        s.sendall(json.dumps(request).encode("utf-8"))

        data = s.recv(1024)

        if data.startswith(b"Error:"):
            error = data.decode("utf-8").strip()
            print(error)
        else:
            file_path = os.path.join(CLIENT_DIR, request)
            with open(file_path, "wb") as f:
                f.write(data)
            print(f"{request} received and saved in {CLIENT_DIR}")

        user_input = input('Would you like to continue or end the program? Press 9 to exit! Else press 1 to continue : ')
        if user_input == '9':
            connection = False
        else:
            continue

    print("\nClient Socket Closed!\n")
