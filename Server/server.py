# This is the server program capable of receiving requests, performing operations, and sending responses.
# Ali Turkman - 40111059

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

                    file_nameLength = int.from_bytes(action, 'big') - (0b00100000)  # removing GET bits
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
                    try: 
                        with open(file_path, "rb") as f:
                            file_contents = f.read()
                    except:
                        print('Client Disconected, Waiting for other TCP clients')
                        break
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
                    try:
                        with open(file_path, "wb") as f:
                            f.write(file_contents)
                    except:
                        print('Client Disconected, Waiting for other TCP clients')
                        break
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
    # create the server socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    s.bind((HOST, PORT))

    print(f"Server is awaiting connection at {HOST}:{PORT}! Make sure to turn on the client connection!")

    while True:
        data, addr = s.recvfrom(1024)
        print(f"Server has connected! Connected to {addr}!")
        opcode = data[0] >> 5

        print(f"Received opcode: {opcode}")
        if opcode == PUT:
            print("Initiate Put command.")

            filename_length = data[0] & 0b11111
            file_name = data[1:filename_length+1].decode('utf-8')

            file_size = int.from_bytes(data[filename_length+1:], 'big')

            file_contents = b""
            while len(file_contents) < file_size:
                data, addr = s.recvfrom(1024)
                file_contents += data

            file_path = os.path.join(file_dir, file_name)
            with open(file_path, "wb") as f:
                f.write(file_contents)
                print(f"File '{file_name}' ({file_size} bytes) has been uploaded by {addr}!")
                
                res_code = PUT_CHANGE_CORRECT
                filename_length = len(file_name)
                payload_byte1 = (res_code << 5) | filename_length
                res_payload = bytes([payload_byte1]) + file_name.encode('utf-8') + file_size.to_bytes(4, 'big')
                s.sendto(res_payload, addr)


        elif opcode == GET:
            print("Initiate get command")
            filename_length = data[0] & 0b11111
            file_name = data[1:filename_length+1].decode('utf-8')
            file_path = os.path.join(file_dir, file_name)

            if os.path.exists(file_path):
                rescode = GET_CORRECT
                file_name_bytes = file_name.encode('utf-8')
                filename_length = len(file_name_bytes)
                file_size = os.path.getsize(file_path)
                print(file_size)
                payload = bytes([rescode << 5 | filename_length]) + file_name_bytes + file_size.to_bytes(4, 'big')
                s.sendto(payload, addr)


                print("Now to send the contents!")
                with open(file_path, "rb") as f:
                    while True:
                        data = f.read(1024)
                        if not data:
                            break
                        s.sendto(data, addr)
                print("Finished")

            
            else :
                res_code = ERROR_FILE_NOT_FOUND
                filename_length = len(file_name)
                payload_byte1 = (res_code << 5) | filename_length
                res_payload = bytes([payload_byte1]) + file_name.encode('utf-8') 
                s.sendto(res_payload, addr)

        elif opcode == CHANGE:
            print("Initiate Change command.")
            old_filename_length = data[0] & 0b00011111
            old_file_name = data[1:old_filename_length+1].decode('utf-8')
            new_filename_length = data[old_filename_length+1]
            new_file_name = data[old_filename_length+2:old_filename_length+2+new_filename_length].decode('utf-8')

            old_file_path = os.path.join(file_dir, old_file_name)
            if not os.path.exists(old_file_path):
                res_code = ERROR_UNSUCESSFUL_CHANGE
                payload_byte1 = (res_code << 5) 
                res_payload = bytes([payload_byte1]) 
                s.sendto(res_payload, addr)
                continue

            new_file_path = os.path.join(file_dir, new_file_name)
            if os.path.exists(new_file_path):
                res_code = ERROR_UNSUCESSFUL_CHANGE
                payload_byte1 = (res_code << 5) 
                res_payload = bytes([payload_byte1]) 
                s.sendto(res_payload, addr)
                continue

            os.rename(old_file_path, new_file_path)
            res_code = PUT_CHANGE_CORRECT
            payload_byte1 = (res_code << 5) 
            res_payload = bytes([payload_byte1]) 
            s.sendto(res_payload, addr)
            

        elif opcode == HELP:
            print("Initiate Help command.")
            commands="Please use 'get filename' to download a file, 'put filename' to upload a file, 'change oldname newname' to change the name of a file, or 'bye' to exit the client program."
            help_length = len(commands)
            res_code = HELP_RESPONSE
            payload_byte1 = (res_code << 5) 
            res_payload = bytes([payload_byte1]) + commands.encode('utf-8') 
            s.sendto(res_payload, addr)

    
        else:
            res_code = ERROR_UNKNOWN_REQUEST
            error_payload = bytes([res_code << 5]) 
            s.sendto(error_payload, addr)
            print(f"Error: Unkwown request sent.")


else:
    print("Invalid choice, please choose 1 or 2.")
