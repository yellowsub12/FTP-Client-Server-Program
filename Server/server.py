import socket
import os
import sys

PUT = 0b000
GET = 0b001
CHANGE = 0b010
HELP = 0b011

PUT_CHANGE_CORRECT = 0b010
GET_CORRECT = 0b001
ERROR_FILE_NOT_FOUND = 0b010
ERROR_UNKNOWN_REQUEST = 0b011
ERROR_UNSUCESSFUL_CHANGE = 0b101
HELP_RESPONSE = 0b110
# Ali Turkman


HOST = "127.0.0.1"
PORT = 65432
protocol_choice = input("Choose 1 for TCP, or 2 for UDP: ")

file_dir = "Server"

if protocol_choice == "1":
    print("You chose TCP!")

    # create the server socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # bind the socket to the host and port
    s.bind((HOST, PORT))

    # start listening for incoming connections
    s.listen(1)

    print(
        f"Server is awaiting connection at {HOST}:{PORT}! Make sure to turn on the client connection!")

    while True:
        # accept a new connection
        conn, addr = s.accept()
        print(f"Server has connected! Connected to {addr}!")

        with conn:
            while True:
                # receive the Res-code and check which it matches
                action = conn.recv(1)
                userRequest = (int.from_bytes(action, 'big')) >> 5

                if userRequest == GET:

                    file_nameLength = int.from_bytes(
                        action, 'big') - (0b00100000)  # removing GET bits
                    # receive the name of the file to be sent
                    file_name = conn.recv(file_nameLength).decode()

                    # check if the file exists
                    file_path = os.path.join(file_dir, file_name)
                    if not os.path.exists(file_path):
                        MSGResponse = (ERROR_FILE_NOT_FOUND <<
                                       5).to_bytes(1, 'big')
                        conn.send(MSGResponse)
                        continue

                    # send the size of the file to be sent
                    file_size = os.path.getsize(file_path)
                    byte1 = ((GET_CORRECT << 5) +
                             len(file_name)).to_bytes(1, 'big')
                    byte2 = file_name.encode()
                    byte3 = file_size.to_bytes(4, 'big')
                    MSGResponse = byte1 + byte2 + byte3
                    conn.send(MSGResponse)

                    # send the contents of the file to be sent
                    with open(file_path, "rb") as f:
                        file_contents = f.read()
                    conn.send(file_contents)

                    print(
                        f"File '{file_name}' ({file_size} bytes) has been sent to {addr}!")
                elif userRequest == PUT:
                    # receive the name of the file to be uploaded
                    file_nameLength = int.from_bytes(
                        action, 'big') - (0b00000000)  # removing PUT bits
                    # receive the name of the file to be sent
                    file_name = conn.recv(file_nameLength).decode()

                    # receive the size of the file to be uploaded
                    file_size = int.from_bytes(conn.recv(4), 'big')

                    # receive the contents of the file to be uploaded
                    file_contents = conn.recv(file_size)

                    # save the contents of the file to disk
                    file_path = os.path.join(file_dir, file_name)
                    with open(file_path, "wb") as f:
                        f.write(file_contents)

                    print(
                        f"File '{file_name}' ({file_size} bytes) has been uploaded by {addr}!")

                    # send a response to the client
                    serverResponseMSG = (
                        PUT_CHANGE_CORRECT << 5).to_bytes(1, 'big')
                    conn.send(serverResponseMSG)

                elif userRequest == CHANGE:
                    OFL_length = int.from_bytes(
                        action, 'big') - (0b01000000)  # removing CHANGE bits
                    OFL = conn.recv(OFL_length).decode()
                    NFL_length = int.from_bytes(conn.recv(1), 'big')
                    NFL = conn.recv(NFL_length).decode()

                    # check if the old file exists
                    old_file_path = os.path.join(file_dir, OFL)
                    if not os.path.exists(old_file_path):
                        conn.send(
                            (ERROR_UNSUCESSFUL_CHANGE << 5).to_bytes(1, 'big'))
                        continue

                    # check if the new file already exists
                    new_file_path = os.path.join(file_dir, NFL)
                    if os.path.exists(new_file_path):
                        conn.send(
                            (ERROR_UNSUCESSFUL_CHANGE << 5).to_bytes(1, 'big'))
                        continue

                    # rename the file
                    os.rename(old_file_path, new_file_path)
                    conn.sendall((PUT_CHANGE_CORRECT << 5).to_bytes(1, 'big'))

                # help command to list the commands
                elif userRequest == HELP:
                    command_list = "Cmds: get,put,change,help,bye"
                    byte1 = (HELP_RESPONSE << 5) + (len(command_list))
                    response = byte1.to_bytes(1, 'big') + command_list.encode()
                    conn.send(response)

                else:
                    response = (ERROR_UNKNOWN_REQUEST << 5).to_bytes(1, 'big')
                    conn.send(response)
                    continue

elif protocol_choice == "2":
    print("You chose UDP!")

    # create the server socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # bind the socket to the host and port
    s.bind((HOST, PORT))

    print(
        f"Server is awaiting Requests from Clients")

    while True:
        # receive data from client
        data, addr = s.recvfrom(1024)
        byte1 = data[0].to_bytes(1, 'big')

        # userRequest = byte1 >> 5
        userRequest = (int.from_bytes(byte1, 'big')) >> 5
        if userRequest == GET:
            file_nameLength = int.from_bytes(
                byte1, 'big') - (0b00100000)  # removing GET bits
            # receive the name of the file to be sent
            file_name = data[1:len(data)]
            decodedFile_name = file_name.decode()

            # check if the file exists
            file_path = os.path.join(file_dir, decodedFile_name)
            if not os.path.exists(file_path):
                MSGResponse = (ERROR_FILE_NOT_FOUND <<
                               5).to_bytes(1, 'big')
                s.sendto(MSGResponse, addr)
                continue

            # send the size of the file to be sent
            file_size = os.path.getsize(file_path)
            byte1 = ((GET_CORRECT << 5) +
                     len(decodedFile_name)).to_bytes(1, 'big')
            byte2 = decodedFile_name.encode()
            byte3 = file_size.to_bytes(4, 'big')
            # send the contents of the file to be sent
            with open(file_path, "rb") as f:
                file_contents = f.read()
            # Sending Header + File Data
            MSGResponse = byte1 + byte2 + byte3 + file_contents
            s.sendto(MSGResponse, addr)

            print(
                f"File '{file_name}' ({file_size} bytes) has been sent to {addr}!")

        if userRequest == PUT:
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
                print(
                    f"File '{file_name}' ({file_size} bytes) has been uploaded by {addr}!")

                # send a response to the client
                s.sendto("OK".encode("utf-8"), addr)

        elif userRequest == CHANGE:
            # receive the old and new file names
            data, addr = s.recvfrom(1024)
            file_names = data.decode("utf-8").split()

            # check if the message contains two items
            if len(file_names) != 2:
                s.sendto("-1".encode("utf-8"), addr)
                s.sendto("Invalid input: please enter the old and new file names separated by a space.".encode(
                    "utf-8"), addr)
                continue

            old_file_name, new_file_name = file_names

            # check if the old file exists
            old_file_path = os.path.join(file_dir, old_file_name)
            if not os.path.exists(old_file_path):
                s.sendto("-1".encode("utf-8"), addr)
                s.sendto(
                    f"File '{old_file_name}' does not exist in {file_dir}!".encode("utf-8"), addr)
                continue

            # check if the new file name already exists
            new_file_path = os.path.join(file_dir, new_file_name)
            if os.path.exists(new_file_path):
                s.sendto("-1".encode("utf-8"), addr)
                s.sendto(
                    f"File '{new_file_name}' already exists in {file_dir}!".encode("utf-8"), addr)
                continue

            # rename the file and send success message to client
            os.rename(old_file_path, new_file_path)
            s.sendto("OK".encode("utf-8"), addr)

            print(
                f"File '{old_file_name}' has been renamed to '{new_file_name}' by {addr}!")

        elif userRequest == HELP:
            command_list = "Cmds: get,put,change,help,bye"
            byte1 = (HELP_RESPONSE << 5) + (len(command_list))
            response = byte1.to_bytes(1, 'big') + command_list.encode()
            s.sendto(response, addr)

        else:
            # send error message to client if action is invalid
            s.sendto("-1".encode("utf-8"), addr)
            s.sendto("Invalid action! Please enter 'get', 'put', or 'change'.".encode(
                "utf-8"), addr)
            continue


else:
    print("Invalid choice, please choose 1 or 2.")
