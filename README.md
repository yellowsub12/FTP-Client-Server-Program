# FTP-Client-Server-Program
A pair of client-server programs that partially simulates the file transfer protocol (FTP) using Python stream sockets. The purpose is to allow the client to download files from the server directory to the client directory and upload files from the client directory to the server directory with both TCP and UDP protocols.

#How To Run

Start the Server by entering the command "python3 servery.py" in the Server directory. Enter 1 or 2 in the terminal depending on a UDP or TCP Server.
Start the Client by entering the command "python3 client.py 127.0.0.1 65432 0". The last argument can be 0 or 1. 1 for debug mode. Then Enter the same answer (1 or 2) as entered for the Server. The UDP or TCP must match for client and server.

You can now run the get, put, change, help or bye command from the client.
