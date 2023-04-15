import socket
import os

HOST = "127.0.0.1"
PORT = 65432

# set the path to the directory containing the files
file_dir = "Server"

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"Server is awaiting connection at {HOST}:{PORT}! Make sure to turn on the client connection!")
    conn, addr = s.accept()
    print(f"Server has connected! Connected to {addr}!")
    with conn:
        print(f"Connected by {addr}")
        while True:
            data = conn.recv(1024).decode("utf-8")
            if not data:
                break

            # check if the requested file exists
            file_path = os.path.join(file_dir, data)
            if not os.path.exists(file_path):
                conn.sendall("ERROR: File does not exist".encode("utf-8"))
                continue

            # open the requested file and read its contents
            with open(file_path, "rb") as f:
                file_contents = f.read()

            # send the file size to the client
            file_size = len(file_contents)
            conn.sendall(str(file_size).encode("utf-8"))

            # send the file contents to the client
            conn.sendall(file_contents)
            print(f"File '{data}' ({file_size} bytes) has been sent to the client!")
