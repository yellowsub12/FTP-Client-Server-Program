import socket
import os
import sys

# Ali Turkman 

protocol_choice = input("Choose 1 for TCP, or 2 for UDP: ")

#HOST = "127.0.0.1"
#PORT = 65432

HOST = input("Please provide the IP address : ")
PORT = int(input("Please provide the port number : "))

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
        user_input = input("Enter a command please : ").lower().split()

        # send the action to the server
        s.sendall(user_input[0].encode("utf-8"))

        if user_input[0] == "get":
            # ask the user to input the name of the file to be downloaded
            file_name = user_input[1]

            # send the name of the file to the server
            s.sendall(file_name.encode("utf-8"))

            # receive the size of the file to be received
            file_size = int(s.recv(1024).decode("utf-8"))

            # receive the contents of the file to be received
            file_contents = s.recv(file_size)

            # save the contents of the file to disk
            file_path = file_dir + "/" + file_name
            with open(file_path, "wb") as f:
                f.write(file_contents)

            print(f"File '{file_name}' ({file_size} bytes) has been downloaded and saved in {file_dir}!")

        elif user_input[0] == "put":
            # ask the user to input the name of the file to be uploaded
            file_name = user_input[1]

            # check if the file exists
            file_path = file_dir + "/" + file_name
            if not os.path.exists(file_path):
                print(f"Error: file '{file_name}' does not exist in {file_dir}!")
                continue

            # send the name of the file to the server
            s.sendall(file_name.encode("utf-8"))

            # send the size of the file to be uploaded
            file_size = os.path.getsize(file_path)
            s.sendall(str(file_size).encode("utf-8"))

            # send the contents of the file to be uploaded
            with open(file_path, "rb") as f:
                file_contents = f.read()
            s.sendall(file_contents)

            # receive a response from the server
            response = s.recv(1024).decode("utf-8")
            if response.lower() == "ok":
                print(f"File '{file_name}' ({file_size} bytes) has been uploaded to the server!")
            else:
                print(f"Error: {response}")
        elif user_input[0] == "change":
                # get user input for old and new file names
                old_file_name = user_input[1]
                new_file_name = user_input[2]

                # send the old and new file names to server
                s.sendall(f"{old_file_name} {new_file_name}".encode("utf-8"))

                # receive response from server
                response_code = s.recv(1024).decode("utf-8")

                # check response code
                if response_code == "-1":
                    error_msg = s.recv(1024).decode("utf-8")
                    print(error_msg)
                elif response_code == "0":
                    success_msg = s.recv(1024).decode("utf-8")
                    print(success_msg)
        
        elif user_input[0] == "bye":
            s.sendall("Bye".encode("utf-8"))
            print("Exiting program...")
            break


        elif user_input[0] == "help":
            print("Requesting list of commands from server! \n")
            response = s.recv(1024).decode("utf-8")
            command_list_len = int(response[:2])
            final_command_list = response[2:]
            print(final_command_list)

        else:
            print(f"Invalid action '{user_input[0]}'! Please 'get' to download a file, 'put' to upload a file, or 'change' to change the name of a file : ")
            continue
    s.close()

elif protocol_choice == "2":
    print("You chose UDP!\n")
    # create the client socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print("Welcome to the file transfer system!")
    while True:
        # ask the user to input the action to be taken (download or upload)
        user_input = input("Enter a command please : ").lower().split()

        # send the action to the server
        s.sendto(user_input[0].encode("utf-8"), (HOST, PORT))

        if user_input[0] == "get":
            # get filename from user input
            file_name = user_input[1]

            # send the filename to the server
            s.sendto(file_name.encode("utf-8"), (HOST, PORT))

            # receive the size of the file to be received
            data, addr = s.recvfrom(1024)
            file_size = int(data.decode("utf-8"))

            # receive the contents of the file to be received
            file_contents = b''
            while True:
                data, addr = s.recvfrom(1024)
                if not data:
                    break
                file_contents += data

            # save the contents of the file to disk
            file_path = os.path.join(file_dir, file_name)
            with open(file_path, "wb") as f:
                f.write(file_contents)
                print(f"File '{file_name}' ({file_size} bytes) has been downloaded to {file_dir}!")

        elif user_input[0] == "put":
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
                print(f"File '{file_name}' ({file_size} bytes) has been uploaded to the server!")
            else:
                print(f"Failed to upload file '{file_name}' to the server: {response}")




        elif user_input[0] == "change":
            # get user input for old and new file names
            old_file_name = user_input[1]
            new_file_name = user_input[2]

            # send the old and new file names to the server
            s.sendto(f"{old_file_name} {new_file_name}".encode("utf-8"), (HOST, PORT))

            # receive response from server
            data, addr = s.recvfrom(1024)
            response = data.decode("utf-8")
            if response == "OK":
                print(f"File '{old_file_name}' has been renamed to '{new_file_name}' on the server!")
            else:
                print(f"Failed to rename file '{old_file_name}' to '{new_file_name}' on the server: {response}")

        elif user_input[0] == "bye":
                # send the "bye" command to the server and close the socket
                s.sendto("bye".encode("utf-8"), (HOST, PORT))
                s.close()
                print("Exiting program...")
                break

        elif user_input[0] == "help":
            print("Requesting list of commands from server!\n")
            data, addr = s.recvfrom(1024)
            command_list_len = int(data[:4])
            final_command_list = data[4:].decode("utf-8")
            print(final_command_list)

        else:
            print(f"Invalid action '{user_input[0]}'! Please 'get' to download a file, 'put' to upload a file, or 'change' to change the name of a file : ")
            continue
    s.close()

else:
    print("Invalid choice, please choose 1 or 2.")