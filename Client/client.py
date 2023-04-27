# Ali Turkman - 40111059
# Alexander Santelli - 40164629
# This is the client program capable of sending requests, taking commands, and receiving responses.
# We attest that this is our original work.
# Note : Change file_dir from "Server" to "./" if issues related to directory arise. 
# Note 2 : Make sure to add test files within this directory from the Tests folder.

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

# HOST = "127.0.0.1"
# PORT = 65432
# Starting argument: python3 client.py 127.0.0.1 65432 0

HOST = sys.argv[1]
PORT = int(sys.argv[2])
# Checking Debug argument
if (sys.argv[3] == '1'):
    debug = True
else:
    debug = False
protocol_choice = input("Choose 1 for TCP, or 2 for UDP: ")

file_dir = "Client/"

if protocol_choice == "1":
    print("You chose TCP!\n")

    # create the client socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # connect to the server
    s.connect((HOST, PORT))

    print(f"Connected to server at {HOST}:{PORT}!")

    while True:
        # ask the user to input the action to be taken (download or upload)
        user_input = input("myftp> ").lower().split()

        if user_input[0] == "get":
            # checking that command contains the filename after get
            if len(user_input) < 2:
                print('Error: must include file name after "get"')
            else:
                file_name = user_input[1]
                # Checking if file name is less than 31 characters, so can store as 5 bits
                if debug:
                    print('The length of the file name is ' + str(len(file_name)) + ' characters.')
                if len(file_name) > 31:
                    print('The file name cannot be greater than 31 characters')
                else:
                    byte1 = ((GET << 5) + len(file_name)).to_bytes(1, 'big')
                    byte2 = file_name.encode()
                    encodedRequestMSG = byte1 + byte2
                    if debug:
                        print('Sending encoded Header to Server. It is ' + str(encodedRequestMSG))
                    # send the Header File in the correct Byte format
                    s.send(encodedRequestMSG)
                    # Receive 1st byte to check which res-code is sent
                    response = s.recv(1)
                    serverRequest = ((int.from_bytes(response, 'big')) >> 5)
                    if debug:
                        print('Received 1 byte from Server: ' + str(response))
                        #check if correct res-code before receiving more from server
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
                        file_path = file_dir + file_name
                        with open(file_path, "wb") as f:
                            f.write(file_contents)
                        print(f"'{file_name}' has been downloaded from server")
                        if debug:
                            print(
                            f"File '{file_name}' is {file_size} bytes and saved in {file_dir}!")
                    elif serverRequest == ERROR_FILE_NOT_FOUND:
                        print(f"Could not find '{file_name}' from server")
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
                    file_path = os.path.join(file_dir, file_name)
                    #Checking if file exists
                    if not os.path.isfile(file_path):
                        print(
                            f"Error: file '{file_name}' does not exist in {file_dir}!")
                        continue

                    byte1 = ((PUT << 5) + len(file_name)).to_bytes(1, 'big')
                    byte2 = file_name.encode()
                    file_size = os.path.getsize(file_path)
                    byte3 = file_size.to_bytes(4, 'big')
                    encodedRequestMSG = byte1 + byte2 + byte3
                    if debug:
                        print('Sending encoded Header to Server. It is ' + str(encodedRequestMSG))
                    #Sending encoded Header to server
                    s.send(encodedRequestMSG)

                    with open(file_path, "rb") as f:
                        file_contents = f.read()
                    #Sending file contents
                    s.send(file_contents)
                    if debug:
                        print('Sending File contents. It is ' + str(file_size) + ' bytes.')

                    response = s.recv(1)
                    serverResponse = int.from_bytes(response, 'big') >> 5
                    #Receives header from server and compares Res-code
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
                    if debug:
                        print('Sending encoded Header to Server. It is ' + str(encodedRequestMSG))
                    #Send encoded header to server
                    s.send(encodedRequestMSG)

                    # receive response from server
                    response = s.recv(1)
                    if debug:
                        print('Received 1 byte from Server: ' + str(response))
                    serverResponse = int.from_bytes(response, 'big') >> 5

                    # check response res-code
                    if serverResponse == PUT_CHANGE_CORRECT:
                        print(
                            "Success: Changed " + old_file_name + " to " + new_file_name)
                    elif serverResponse == ERROR_UNSUCESSFUL_CHANGE:
                        print("Error: Could not change" +
                              old_file_name + " to " + new_file_name)
                    else:
                        print("Unknown Error with Change")
        elif user_input[0] == "bye":
            # Close socket connection
            s.close()
            if debug:
                print(f"Connection with Server is closed")
            print("Exiting program...")
            break
        elif user_input[0] == "help":
            if debug:
                print("Getting the commands from the server")

            encodedRequestMSG = (HELP << 5).to_bytes(1, 'big')
            s.send(encodedRequestMSG)
            if debug:
                    print('Sending encoded Header to Server. It is ' + str(encodedRequestMSG))
            # Receive and check if Res-code is correct
            response = s.recv(1)
            serverRequest = (int.from_bytes(response, 'big')) >> 5
            if serverRequest == HELP_RESPONSE:
                serverMSG = s.recv(31) 
                print(serverMSG)
            else:
                print('Could not get Help')
        else:
            encodedRequestMSG = (0b111 << 5).to_bytes(1, 'big')
            s.send(encodedRequestMSG)
            if debug:
                    print('Sending encoded Header to Server. It is ' + str(int.from_bytes(encodedRequestMSG, 'big')) + ' bytes.')
            response = s.recv(1)
            serverRequest = (int.from_bytes(response, 'big')) >> 5
            if serverRequest == ERROR_UNKNOWN_REQUEST:
                print(
                f"Invalid action '{user_input[0]}'! Please 'get' to download a file, 'put' to upload a file, or 'change' to change the name of a file : ")
            continue


elif protocol_choice == "2":
    print("You chose UDP!\n")
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print("Welcome to the file transfer system!")
    while True:
        user_input = input("ftp> ").lower().split()


        if user_input[0] == "get":
                if len(user_input) < 2:
                    print('Error: must include file name after "get"')
                else:
                    file_name = user_input[1]
                    if len(file_name) > 31:
                        print('The file name cannot be greater than 31 characters')
                    else:
                        opcode = GET
                        file_name_bytes = file_name.encode('utf-8')
                        filename_length = len(file_name_bytes)
                        payload = bytes([opcode << 5 | filename_length]) + file_name_bytes 

                        s.sendto(payload, (HOST, PORT))
                        data, addr = s.recvfrom(1024)
                        res_code = (data[0] & 0b11100000) >> 5
                        filename_length = data[0] & 0b00011111
                        file_name = data[1:filename_length+1].decode('utf-8')
                        if res_code == GET_CORRECT:
                            file_size = int.from_bytes(data[filename_length+1:], 'big')
                            file_contents = b""
                            while len(file_contents) < file_size:
                                data, addr = s.recvfrom(1024)
                                file_contents += data

                            s.sendto(payload, (HOST, PORT))
                            response, addr = s.recvfrom(1024)
                            res_code = (response[0] & 0b11100000) >> 5
                            filename_length = response[0] & 0b00011111
                            file_size = int.from_bytes(response[filename_length+1:], 'big')

                            file_contents = b""

                            while len(file_contents) < file_size:
                                data, addr = s.recvfrom(1024)
                                file_contents += data

                            file_path = os.path.join(file_dir, file_name)
                            with open(file_path, "wb") as f:
                                f.write(file_contents)
                            print(f"File '{file_name}' ({file_size} bytes) has been downloaded from the server!")
                                
                        else:
                            print(f"{file_name} not found on server")

        elif user_input[0] == "put":
            if debug:
                print("PUT command.")
            if len(user_input) < 2:
                    print('Error: must include file name after "get"')
            else:
                file_name = user_input[1]
                if len(file_name) > 31:
                    print('The file name cannot be greater than 31 characters')
                else:
                    file_path = os.path.join(file_dir, file_name)
                    if not os.path.exists(file_path):
                        print(f"File '{file_name}' does not exist in {file_dir}!")
                        continue

                    opcode = PUT
                    file_name_bytes = file_name.encode('utf-8')
                    filename_length = len(file_name_bytes)
                    file_size = os.path.getsize(file_path)
                    payload = bytes([opcode << 5 | filename_length]) + file_name_bytes + file_size.to_bytes(4, 'big')

                    s.sendto(payload, (HOST, PORT))

                    with open(file_path, "rb") as f:
                        while True:
                            data = f.read(1024)
                            if not data:
                                break
                            s.sendto(data, (HOST, PORT))

                    response, addr = s.recvfrom(1024)
                    res_code = (response[0] & 0b11100000) >> 5
                    filename_length = response[0] & 0b00011111

                    if res_code == PUT_CHANGE_CORRECT:
                        file_name = response[1:filename_length + 1].decode('utf-8')
                        print(f"File '{file_name}' ({file_size} bytes) has been uploaded to the server!")
                    else:
                        error_message = response[1:].decode('utf-8')
                        print(f"Failed to upload file '{file_name}' to the server: {error_message}")
        elif user_input[0] == "change":
            if debug:
                print("Change command.")
            if len(user_input) < 3:
                print('Error: must include both file names after "change"')
            else:
                old_file_name = user_input[1]
                new_file_name = user_input[2]

                opcode = CHANGE
                old_file_name_bytes = old_file_name.encode('utf-8')
                old_filename_length = len(old_file_name_bytes)
                new_file_name_bytes = new_file_name.encode('utf-8')
                new_filename_length = len(new_file_name_bytes)
                payload = bytes([opcode << 5 | old_filename_length]) + old_file_name_bytes + bytes([new_filename_length]) + new_file_name_bytes
                s.sendto(payload, (HOST, PORT))


                # receive response from server
                response, addr = s.recvfrom(1024)
                res_code = (response[0] & 0b11100000) >> 5
                filename_length = response[0] & 0b00011111

                if res_code == PUT_CHANGE_CORRECT:
                    print(f"Success: Changed " + old_file_name + " to " + new_file_name)
                elif res_code == ERROR_UNSUCESSFUL_CHANGE:
                    print("Unsuccessful change! No change was made.")
                else:
                    print("Change operation failed. Please retry.")
        elif user_input[0] == "bye":
            if debug:
                print("Will close socket and exit client.")
            s.close()
            print("Exiting program...")
            break
        elif user_input[0] == "help":
            if debug:
                print("Requesting list of commands from server! \n")

            opcode = HELP
            payload = bytes([opcode << 5 ]) 
            s.sendto(payload, (HOST, PORT))

            response, addr = s.recvfrom(1024)
            res_code = (response[0]) >> 5
            filename_length = response[0] & 0b00011111
            commands = response[1:].decode()
            if res_code == HELP_RESPONSE:
                print(commands)
            else:
                print('Could not get Help')

        else:
            response, addr = s.recvfrom(1024)
            res_code = (response[0]) >> 5
            if res_code == ERROR_UNKNOWN_REQUEST:
                print(
                f"Invalid action '{user_input[0]}'! Please use 'get' to download a file, 'put' to upload a file, or 'change' to change the name of a file : ")
            continue
    s.close()

else:
    print("Invalid choice, please choose 1 or 2.")
