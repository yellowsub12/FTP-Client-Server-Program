import socket
import os
import sys


protocol_choice = input("Choose 1 for TCP, or 2 for UDP: ")

#HOST = "127.0.0.1"
#PORT = 65432

HOST = input("Please provide the IP address : ")
PORT = int(input("Please provide the port number : "))

file_dir = "Server"

if protocol_choice == "1":
    print("You chose TCP!")
    
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

                if action.lower() == "get":
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

                elif action.lower() == "put":
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
                
                elif action.lower() == "change":
                    # receive the old and new file names
                    file_names = conn.recv(1024).decode("utf-8").split()
                    
                    # check if the message contains two items
                    if len(file_names) != 2:
                        conn.sendall("-1".encode("utf-8"))
                        conn.sendall("Invalid input: please enter the old and new file names separated by a space.".encode("utf-8"))
                        continue
                    
                    old_file_name, new_file_name = file_names
                    
                    # check if the old file exists
                    old_file_path = os.path.join(file_dir, old_file_name)
                    if not os.path.exists(old_file_path):
                        conn.sendall("-1".encode("utf-8"))
                        conn.sendall(f"File '{old_file_name}' does not exist in {file_dir}!".encode("utf-8"))
                        continue

                    # check if the new file already exists
                    new_file_path = os.path.join(file_dir, new_file_name)
                    if os.path.exists(new_file_path):
                        conn.sendall("-1".encode("utf-8"))
                        conn.sendall(f"File '{new_file_name}' already exists in {file_dir}!".encode("utf-8"))
                        continue

                    # rename the file
                    os.rename(old_file_path, new_file_path)
                    conn.sendall("0".encode("utf-8"))
                    conn.sendall(f"File '{old_file_name}' has been renamed to '{new_file_name}'!".encode("utf-8"))

                # check if the client sent the "bye" command 
                elif action.lower() == "bye":
                    print("Exiting program...")
                    conn.close()
                    sys.exit()
                


                # help command to list the commands
                elif action.lower() == "help":
                    command_list = "Here's a list of commands : put filename (upload), get filename (download), change OldFileName NewFileName, help and bye"
                    command_list_len = str(len(command_list))
                    response = command_list_len + command_list
                    conn.sendall(response.encode("utf-8"))


                
                
                else:
                    conn.sendall(f"Invalid action '{action}'! Please enter 'download', 'rename', or 'upload'.".encode("utf-8"))
                    continue

elif protocol_choice == "2":
    print("You chose UDP!")

    # create the server socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # bind the socket to the host and port
    s.bind((HOST, PORT))

    print(f"Server is awaiting connection at {HOST}:{PORT}! Make sure to turn on the client connection!")

    while True:
        # receive data from client
        data, addr = s.recvfrom(1024)
        print(f"Server has connected! Connected to {addr}!")

        # decode the action to be taken (download or upload)
        action = data.decode("utf-8")

        if action.lower() == "get":
            # receive the name of the file to be sent
            data, addr = s.recvfrom(1024)
            file_name = data.decode("utf-8")

            # check if the file exists
            file_path = os.path.join(file_dir, file_name)
            if not os.path.exists(file_path):
                s.sendto("-1".encode("utf-8"), addr)
                s.sendto(f"File '{file_name}' does not exist in {file_dir}!".encode("utf-8"), addr)
                continue

            # send the size of the file to be sent
            file_size = os.path.getsize(file_path)
            s.sendto(str(file_size).encode("utf-8"), addr)

            # send the contents of the file to be sent
            with open(file_path, "rb") as f:
                while True:
                    file_contents = f.read(1024)
                    if not file_contents:
                        s.sendto(b"", addr) # indicate end of file by sending an empty datagram
                        break
                    s.sendto(file_contents, addr)

            print(f"File '{file_name}' ({file_size} bytes) has been sent to {addr}!")


        if action.lower() == "put":
            # receive the name of the file to be uploaded
            data, addr = s.recvfrom(1024)
            file_name = data.decode("utf-8")

            # receive the size of the file to be uploaded
            data, addr = s.recvfrom(1024)
            file_size = int(data.decode("utf-8"))

            # receive the contents of the file to be uploaded
            file_contents = b""
            while len(file_contents) < file_size:
                data, addr = s.recvfrom(1024)
                file_contents += data

            # save the contents of the file to disk
            file_path = os.path.join(file_dir, file_name)
            with open(file_path, "wb") as f:
                f.write(file_contents)
                print(f"File '{file_name}' ({file_size} bytes) has been uploaded by {addr}!")

                # send a response to the client
                s.sendto("OK".encode("utf-8"), addr)

        elif action.lower() == "change":
            # receive the old and new file names
            data, addr = s.recvfrom(1024)
            file_names = data.decode("utf-8").split()
            
            # check if the message contains two items
            if len(file_names) != 2:
                s.sendto("-1".encode("utf-8"), addr)
                s.sendto("Invalid input: please enter the old and new file names separated by a space.".encode("utf-8"), addr)
                continue
            
            old_file_name, new_file_name = file_names
            
            # check if the old file exists
            old_file_path = os.path.join(file_dir, old_file_name)
            if not os.path.exists(old_file_path):
                s.sendto("-1".encode("utf-8"), addr)
                s.sendto(f"File '{old_file_name}' does not exist in {file_dir}!".encode("utf-8"), addr)
                continue
        
            # check if the new file name already exists
            new_file_path = os.path.join(file_dir, new_file_name)
            if os.path.exists(new_file_path):
                s.sendto("-1".encode("utf-8"), addr)
                s.sendto(f"File '{new_file_name}' already exists in {file_dir}!".encode("utf-8"), addr)
                continue
        
            # rename the file and send success message to client
            os.rename(old_file_path, new_file_path)
            s.sendto("OK".encode("utf-8"), addr)
            
            print(f"File '{old_file_name}' has been renamed to '{new_file_name}' by {addr}!")
        
        elif action.lower() == "bye":
                # send a confirmation message to the client and close the socket
                response = "Goodbye!"
                s.sendto(response.encode("utf-8"), addr)
                s.close()
                print("Exiting program...")
                sys.exit()

        elif action.lower() == "help":
            command_list = "Here's a list of commands: put filename (upload), get filename (download), change OldFileName NewFileName, help, and bye."
            command_list_len = str(len(command_list)).zfill(4)
            response = command_list_len + command_list
            s.sendto(response.encode("utf-8"), addr)

        else:
            # send error message to client if action is invalid
            s.sendto("-1".encode("utf-8"), addr)
            s.sendto("Invalid action! Please enter 'get', 'put', or 'change'.".encode("utf-8"), addr)
            continue



else:
    print("Invalid choice, please choose 1 or 2.")

