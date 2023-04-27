# FTP-Client-Server-Program
A pair of client-server programs that partially simulates the file transfer protocol (FTP) using Python stream sockets. The purpose is to allow the client to download files from the server directory to the client directory and upload files from the client directory to the server directory with both TCP and UDP protocols. The program will also allow the client to rename files within the server directory.

## How To Run

Start the Server by entering the command **python3 server.py** in the Server directory. Enter 1 or 2 in the terminal depending on a UDP or TCP Server.
Start the Client by entering the command **python3 client.py 127.0.0.1 65432 0**. The last argument can be 0 or 1. 1 for debug mode. Then Enter the same answer (1 or 2) as entered for the Server. The UDP or TCP must match for client and server.

You can now run the **get**, **put**, **change**, **help** or **bye** command from the client.

Example : <code>get photo.jpg</code> <code>put ilovetigers.jpg</code> <code>rename tigers.jpg tiger.jpg</code>

## Directory

NOTE: The program presupposes that the client and server file are initiated within the terminal from the main directory, and not from within the server and client folders. If this is not the case, then it is advised to change the <code>file_dir</code> in both server.py and client.py to "./", and this will fix the issue of the programs locating the files. 