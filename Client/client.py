import socket
import os

HOST = "127.0.0.1"
PORT = 65432

# set the path to the directory where the files will be saved
file_dir = "Client"

# create the client socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connect to the server
s.connect((HOST, PORT))

print(f"Connected to server at {HOST}:{PORT}!")

while True:
    # ask the user to input the action to be taken (download or upload)
    action = input("Enter 'download' to download a file or 'upload' to upload a file: ")

    # send the action to the server
    s.sendall(action.encode("utf-8"))

    if action.lower() == "download":
        # ask the user to input the name of the file to be downloaded
        file_name = input("Enter the name of the file to be downloaded: ")

        # send the name of the file to the server
        s.sendall(file_name.encode("utf-8"))

        # receive the size of the file to be received
        file_size_bytes = s.recv(1024)
        file_size = int.from_bytes(file_size_bytes, byteorder="big")

        # receive the contents of the file to be received
        file_contents = bytearray()
        bytes_received = 0
        while bytes_received < file_size:
            chunk = s.recv(min(4096, file_size - bytes_received))
            file_contents.extend(chunk)
            bytes_received += len(chunk)

        # save the contents of the file to disk
        file_path = file_dir + "/" + file_name
        with open(file_path, "wb") as f:
            f.write(file_contents)

        print(f"File '{file_name}' ({file_size} bytes) has been downloaded and saved in {file_dir}!")

    elif action.lower() == "upload":
        # ask the user to input the name of the file to be uploaded
        file_name = input("Enter the name of the file to be uploaded: ")

        # check if the file exists
        file_path = file_dir + "/" + file_name
        if not os.path.exists(file_path):
            print(f"Error: file '{file_name}' does not exist in {file_dir}!")
            continue

        # send the name of the file to the server
        s.sendall(file_name.encode("utf-8"))

        # send the size of the file to be uploaded
        file_size = os.path.getsize(file_path)
        s.sendall(file_size.to_bytes(8, byteorder="big"))

        # send the contents of the file to be uploaded
        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(4096)
                if not chunk:
                    break
                s.sendall(chunk)

        # receive a response from the server
        response = s.recv(1024).decode("utf-8")
        if response.lower() == "ok":
            print(f"File '{file_name}' ({file_size} bytes) has been uploaded to the server!")
        else:
            print(f"Error: {response}")
    else:
        print(f"Invalid action '{action}'! Please enter 'download' or 'upload'.")
        continue

s.close()
