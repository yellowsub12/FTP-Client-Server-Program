# app-server.py
import socket
import sys
import json
import csv
import numpy as np
# Credit for some of the code https://realpython.com/python-sockets

HOST = "127.0.0.1" 
PORT = 65432 
SERVER_DIR = "Server" 


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

    try: 
    
        s.bind((HOST, PORT)) # Values passed to bind depend on address family (AF_INET)
        s.listen() # enables server to accept connections
        print("Server is awaiting connection! Make sure to turn on the client connection!")
        conn, addr = s.accept() # blocks execution and waits for incoming connection. when a client connects, it returns a new socket object representing the connection and a tuple (host, port) holding the address of the client
        print(f"Server has connected! Connected to {addr}!")
        with conn:
            print(f"Connected by {addr}")
            while True: #infinite loop used to loop over blocking calls
                data = conn.recv(1024) #reads client data
                if not data:
                    break
                print("RFW Received! Preparing to send RFD!")
                server_request = json.loads(data.decode('utf-8'))
                ResponseForData = "Hello " + server_request
                ServerResponse = json.dumps(ResponseForData)
                conn.sendall(ServerResponse.encode('utf-8')) #sends client data back
                print("The Server's Response Has Been Sent!")
                print(ServerResponse)
                print("Awaiting for a new request!")
                #if conn.recv returns an empty bytes object, that means client closed the connection and  the loop is terminated, with statement closes the socket at the end of the block.
    except KeyboardInterrupt:
        print("Caught keyboard interrupt, exiting")

# with .send(), it's possible that you don't end up sending all the data
# with .sendall() however, this makes sure everything is sent. 
# .select() method allows to check for I/O completion on more than one socket
# asyncio does multitasking and an event loop to manage tasks
