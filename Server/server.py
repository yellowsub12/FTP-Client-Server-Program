import socket
import os

HOST = "127.0.0.1"
PORT = 65432

# set the path to the directory where the files will be saved
file_dir = "Server"

# create the server socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# bind the socket to the host and port
s.bind((HOST, PORT))

# start listening for incoming connections
s.listen()

print(f"Server is awaiting connection at {HOST}:{PORT}! Make sure to turn on the client connection!")

while True:
    # accept a new connection
    conn, addr = s.accept()
    print(f"Server has connected! Connected to {addr}!")

    with conn:
        while True:
            # receive the action to be taken (download or upload)
            action = conn.recv(1024).decode("utf-8")

            if action.lower() == "download":
                # receive the name of the file to be sent
                file_name = conn.recv(1024).decode("utf-8")

                # check if the file exists
                file_path = os.path.join(file_dir, file_name)
                if not os.path.exists(file_path):
                    conn.sendall("-1".encode("utf-8"))
                    conn.sendall(f"File '{file_name}' does not exist in {file_dir}!".encode("utf-8"))
                    continue

                # send the size of the file to be sent
                file_size = os.path.getsize(file_path)
                conn.sendall(str(file_size).encode("utf-8"))

                # send the contents of the file to be sent
                with open(file_path, "rb") as f:
                    file_contents = f.read()
                conn.sendall(file_contents)

                print(f"File '{file_name}' ({file_size} bytes) has been sent to {addr}!")

            elif action.lower() == "upload":
                # receive the name of the file to be uploaded
                file_name = conn.recv(1024).decode("utf-8")

                # receive the size of the file to be uploaded
                file_size = int(conn.recv(1024).decode("utf-8"))

                # receive the contents of the file to be uploaded
                file_contents = conn.recv(file_size)

                # save the contents of the file to disk
                file_path = os.path.join(file_dir, file_name)
                with open(file_path, "wb") as f:
                    f.write(file_contents)

                print(f"File '{file_name}' ({file_size} bytes) has been uploaded by {addr}!")

                # send a response to the client
                conn.sendall("OK".encode("utf-8"))
            else:
                conn.sendall(f"Invalid action '{action}'! Please enter 'download' or 'upload'.".encode("utf-8"))
                continue
