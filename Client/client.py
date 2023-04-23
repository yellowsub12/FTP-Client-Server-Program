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
# Alexander Santelli - 40164629

# HOST = "127.0.0.1"
# PORT = 65432
# Starting argument: python client.py 127.0.0.1 65432 0

HOST = sys.argv[1]
PORT = int(sys.argv[2])
# Checking Debug argument
if (sys.argv[3] == '1'):
    debug = True
else:
    debug = False
protocol_choice = input("Choose 1 for TCP, or 2 for UDP: ")

file_dir = "Client"

if protocol_choice == "1":
    print("You chose TCP!\n")

    # create the client socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # connect to the server
    s.connect((HOST, PORT))

    print(f"Connected to server at {HOST}:{PORT}!")

    while True:
        # ask the user to input the action to be taken (download or upload)
        user_input = input("myftp> ").split()

        if user_input[0] == "get":
            # checking that command contains the filename after get
            if len(user_input) < 2:
                print('Error: must include file name after "get"')
            else:
                file_name = user_input[1]
                # Checking if file name is less than 31 characters, so can store as 5 bits
                if len(file_name) > 31:
                    print('The file name cannot be greater than 31 characters')
                else:
                    byte1 = ((GET << 5) + len(file_name)).to_bytes(1, 'big')
                    byte2 = file_name.encode()
                    encodedRequestMSG = byte1 + byte2

                    # send the name of the file to the server
                    s.send(encodedRequestMSG)
                    # Receive 1st byte to check which opcode is sent
                    response = s.recv(1)
                    serverRequest = ((int.from_bytes(response, 'big')) >> 5)
                    if serverRequest == GET_CORRECT:
                        # Getting length of the file Name
                        file_nameLength = int.from_bytes(
                            response, 'big') - (0b00100000)  # removing GET bits
                        serverfile_name = s.recv(file_nameLength).decode()
                        byte3 = s.recv(4)
                        file_size = (int.from_bytes(byte3, 'big'))

                        # receive the contents of the file to be received
                        file_contents = s.recv(file_size)

                        # save the contents of the file to disk
                        file_path = file_dir + "/" + file_name
                        with open(file_path, "wb") as f:
                            f.write(file_contents)

                        print(
                            f"File '{file_name}' ({file_size} bytes) has been downloaded and saved in {file_dir}!")
                    elif serverRequest == ERROR_FILE_NOT_FOUND:
                        print("Could not find " + file_name + " from server")
                    else:
                        print('Error Occured. Failed get')
        elif user_input[0] == "put":
            if len(user_input) < 2:
                print('Error: must include file name after "put"')
            else:
                file_name = user_input[1]

                # Checking if file name is less than 31 characters, so can store as 5 bits
                if len(file_name) > 31:
                    print('The file name cannot be greater than 31 characters')
                else:

                    # check if the file exists
                    file_path = file_dir + "/" + file_name
                    if not os.path.exists(file_path):
                        print(
                            f"Error: file '{file_name}' does not exist in {file_dir}!")
                        continue

                    byte1 = ((PUT << 5) + len(file_name)).to_bytes(1, 'big')
                    byte2 = file_name.encode()
                    file_size = os.path.getsize(file_path)
                    byte3 = file_size.to_bytes(4, 'big')
                    encodedRequestMSG = byte1 + byte2 + byte3
                    # send put request format
                    s.send(encodedRequestMSG)

                    # send the contents of the file to be uploaded
                    with open(file_path, "rb") as f:
                        file_contents = f.read()
                    s.send(file_contents)

                    # receive a response from the server and check if put Succeeded
                    response = s.recv(1)
                    serverResponse = int.from_bytes(response, 'big') >> 5
                    if serverResponse == PUT_CHANGE_CORRECT:
                        print(
                            f"File '{file_name}' has been uploaded to the server!")
                    else:
                        print(f"Error: Could not upload file to the server!")
        elif user_input[0] == "change":
            if len(user_input) < 3:
                print('Error: must include both file names after "change"')
            else:
                if len(user_input[1]) > 31 | len(user_input[2]) > 31:
                    print("The file names cannot be greater than 31 characters")
                else:
                    # get user input for old and new file names
                    old_file_name = user_input[1]
                    new_file_name = user_input[2]

                    byte1 = ((CHANGE << 5) + len(old_file_name)
                             ).to_bytes(1, 'big')
                    byte2 = old_file_name.encode()
                    byte3 = len(new_file_name).to_bytes(1, 'big')
                    byte4 = new_file_name.encode()

                    encodedRequestMSG = byte1 + byte2 + byte3 + byte4
                    s.send(encodedRequestMSG)

                    # receive response from server
                    response = s.recv(1)
                    serverResponse = int.from_bytes(response, 'big') >> 5

                    # check response code
                    if serverResponse == PUT_CHANGE_CORRECT:
                        print(
                            "Success: Changed " + old_file_name + " to " + new_file_name)
                    elif serverResponse == ERROR_UNSUCESSFUL_CHANGE:
                        print("Error: Could not change" +
                              old_file_name + " to " + new_file_name)
                    else:
                        print("Unknown Error with Change")
        elif user_input[0] == "bye":
            s.close()
            print("Exiting program...")
            break
        elif user_input[0] == "help":
            if debug:
                print("Getting the commands from the server")

            encodedRequestMSG = (HELP << 5).to_bytes(1, 'big')
            s.send(encodedRequestMSG)
            # Receive and check if Res-code is correct
            response = s.recv(1)
            serverRequest = (int.from_bytes(response, 'big')) >> 5
            if serverRequest == HELP_RESPONSE:
                serverMSG = s.recv(31)
                print(serverMSG)
            else:
                print('Could not get Help')
        else:
            print(
                f"Invalid action '{user_input[0]}'! Please 'get' to download a file, 'put' to upload a file, or 'change' to change the name of a file : ")
            continue


elif protocol_choice == "2":
    print("You chose UDP!\n")
    # create the client socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        # ask the user to input the action to be taken (download or upload)
        user_input = input("ftp> ").split()

        if user_input[0] == "get":
         # checking that command contains the filename after get
            if len(user_input) < 2:
                print('Error: must include file name after "get"')
            else:
                file_name = user_input[1]
                # Checking if file name is less than 31 characters, so can store as 5 bits
                if len(file_name) > 31:
                    print('The file name cannot be greater than 31 characters')
                else:
                    byte1 = ((GET << 5) + len(file_name)).to_bytes(1, 'big')
                    byte2 = file_name.encode()
                    encodedRequestMSG = byte1 + byte2

                    # send the name of the file to the server
                    s.sendto(encodedRequestMSG, (HOST, PORT))
                    response, addr = s.recvfrom(1024)
                    responsebyte1 = response[0].to_bytes(1, 'big')
                    length = len(response)

                    serverRequest = (
                        (int.from_bytes(responsebyte1, 'big')) >> 5)
                    # Getting length of the file Name
                    file_nameLength = int.from_bytes(
                        responsebyte1, 'big') - (0b00100000)  # removing GET bits
                    if serverRequest == GET_CORRECT:
                        serverfile_name = response[1:
                                                   file_nameLength + 1]
                        byte3 = (response[file_nameLength +
                                          2: file_nameLength + 5])
                        file_size = int.from_bytes(byte3, 'big')

                        # receive the contents of the file to be received
                        file_contents = response[file_nameLength + 5: length]

                        # save the contents of the file to disk
                        file_path = file_dir + "/" + file_name
                        with open(file_path, "wb") as f:
                            f.write(file_contents)
                        print(
                            f"File '{file_name}' ({file_size} bytes) has been downloaded and saved in {file_dir}!")
                    elif serverRequest == ERROR_FILE_NOT_FOUND:
                        print("Could not find " + file_name + " from server")
                    else:
                        print('Error Occured. Fail get')

        elif user_input[0] == "put":
            if len(user_input) < 2:
                print('Error: must include file name after "put"')
            else:
                # get user input for file name
                file_name = user_input[1]

                # check if the file exists
                file_path = os.path.join(file_dir, file_name)
                if not os.path.exists(file_path):
                    print(f"File '{file_name}' does not exist in {file_dir}!")
                    continue

                # send the file name to the server
                s.sendto(file_name.encode("utf-8"), (HOST, PORT))

                # send the size of the file to be uploaded
                file_size = os.path.getsize(file_path)
                s.sendto(str(file_size).encode("utf-8"), (HOST, PORT))

                # send the contents of the file to be uploaded
                with open(file_path, "rb") as f:
                    while True:
                        data = f.read(1024)
                        if not data:
                            break
                        s.sendto(data, (HOST, PORT))

                # receive response from server
                data, addr = s.recvfrom(1024)
                response = data.decode("utf-8")
                if response == "OK":
                    print(
                        f"File '{file_name}' ({file_size} bytes) has been uploaded to the server!")
                else:
                    print(
                        f"Failed to upload file '{file_name}' to the server: {response}")

        elif user_input[0] == "change":
            if len(user_input) < 3:
                print('Error: must include both file names after "change"')
            else:
                # get user input for old and new file names
                old_file_name = user_input[1]
                new_file_name = user_input[2]

                # send the old and new file names to the server
                s.sendto(f"{old_file_name} {new_file_name}".encode(
                    "utf-8"), (HOST, PORT))

                # receive response from server
                data, addr = s.recvfrom(1024)
                response = data.decode("utf-8")
                if response == "OK":
                    print(
                        f"File '{old_file_name}' has been renamed to '{new_file_name}' on the server!")
                else:
                    print(
                        f"Failed to rename file '{old_file_name}' to '{new_file_name}' on the server: {response}")

        elif user_input[0] == "bye":
            # send the "bye" command to the server and close the socket
            s.sendto("bye".encode("utf-8"), (HOST, PORT))
            s.close()
            print("Exiting program...")
            break

        elif user_input[0] == "help":
            if debug:
                print("Requesting list of commands from server! \n")

            encodedRequestMSG = (HELP << 5).to_bytes(1, 'big')
            s.sendto(encodedRequestMSG, (HOST, PORT))
            response, addr = s.recvfrom(1)

            serverRequest = (int.from_bytes(response, 'big')) >> 5
            if serverRequest == HELP_RESPONSE:
                serverMSG, addr = s.recvfrom(31)
                print(serverMSG)
            else:
                print('Could not get Help')

        else:
            print(
                f"Invalid action '{user_input[0]}'! Please 'get' to download a file, 'put' to upload a file, or 'change' to change the name of a file : ")
            continue
    s.close()

else:
    print("Invalid choice, please choose 1 or 2.")
