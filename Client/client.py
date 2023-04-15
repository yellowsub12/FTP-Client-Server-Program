# app-client.py
import socket
import sys
import json
import uuid
# Source for lots of code and comments here https://realpython.com/python-sockets/

HOST = "127.0.0.1" # The server's hostname or IP address
PORT = 65432 # The port used by the server


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    addr = (HOST,PORT)
    print(f"Accepted connection from {addr}")
    s.connect((HOST,PORT))
    connection = True
    while connection:
        RFW = input('Give me your name : ')
        receivedRequest = json.dumps(RFW)


        s.sendall(receivedRequest.encode("utf-8"))
        
        print("\nRequest Sent!")
        print(receivedRequest)
        print("\nWaiting for Response ...\n")

        # Receive Response from Server
        # 1024 Represents Buffer Size in Bytes
        data = s.recv(1024)
        
        res = json.loads(data.decode('utf-8'))

        # Print Response
        print("Response Received!")
        print(res)
        user_input = input('Would you like to continue or end the program? Press 9 to exit! Else press 1 to continue : ')
        if user_input == '9':
            connection = False
        else:
            continue



   


    print("\nClient Socket Closed!\n")
    

print(f"Client Received back {data!r}")

#this creates a socket object
#uses .connect() to connect to the server
#uses .sendall() to send its messages
#uses .recv() to read the server's reply and then prints it.