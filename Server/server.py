import socket
import sys
import json
import os

HOST = "127.0.0.1" # Standard loopback interface address (localhost), can be hostname, IP address or empty string.
PORT = 65432 # Port to listen on (non-privileged ports are > 1023)

SERVER_DIR = "Server" # Directory containing the file to be sent

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

    try:
        s.bind((HOST, PORT))
        s.listen()
        print("Server is awaiting connection! Make sure to turn on the client connection!")
        conn, addr = s.accept()
        print(f"Server has connected! Connected to {addr}!")
        with conn:
            print(f"Connected by {addr}")
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                request = json.loads(data.decode('utf-8'))
                print(f"Request received: {request}")

                if request == "hello.txt":
                    file_path = os.path.join(SERVER_DIR, request)
                    if os.path.exists(file_path):
                        with open(file_path, "rb") as f:
                            file_data = f.read()
                        conn.sendall(file_data)
                        print(f"{request} sent to client")
                    else:
                        error = f"{request} not found on the server"
                        conn.sendall(error.encode("utf-8"))
                        print(error)
                else:
                    error = f"{request} is not a valid request"
                    conn.sendall(error.encode("utf-8"))
                    print(error)

    except KeyboardInterrupt:
        print("Caught keyboard interrupt, exiting")
