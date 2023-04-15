import socket
import os

HOST = "127.0.0.1"
PORT = 65432

# set the path to the directory where the files will be saved
file_dir = "Client"

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    print(f"Connected to server at {HOST}:{PORT}!")

    while True:
        # get the name of the file to be requested
        file_name = input("Enter the name of the file to be requested: ")

        # send the file name to the server
        s.sendall(file_name.encode("utf-8"))

        # receive the size of the file from the server
        file_size = int(s.recv(1024).decode("utf-8"))

        if file_size < 0:
            print(f"ERROR: {s.recv(1024).decode('utf-8')}")
            continue

        # receive the file contents from the server
        file_contents = s.recv(file_size)

        # save the file contents to disk
        file_path = os.path.join(file_dir, file_name)
        with open(file_path, "wb") as f:
            f.write(file_contents)
        print(f"File '{file_name}' ({file_size} bytes) has been saved to {file_path}!")
