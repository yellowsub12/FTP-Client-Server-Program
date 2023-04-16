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
    action = input("Enter 'get' to download a file, 'put' to upload a file, or 'change' to change the name of a file : ")

    # send the action to the server
    s.sendall(action.encode("utf-8"))

    if action.lower() == "get":
        # ask the user to input the name of the file to be downloaded
        file_name = input("Enter the name of the file to be downloaded: ")

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

    elif action.lower() == "put":
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
    elif action.lower() == "change":
            # get the old and new file names from the user
            old_file_name, new_file_name = input("Enter old and new file names separated by a space: ").split()

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
    
    elif action.lower() == "bye":
        s.sendall("Bye".encode("utf-8"))
        print("Exiting program...")
        break


    elif action.lower() == "help":
        print("Requesting list of commands from server! \n")
        response = s.recv(1024).decode("utf-8")
        command_list_len = int(response[:2])
        final_command_list = response[2:]
        print(final_command_list)

    else:
        print(f"Invalid action '{action}'! Please 'get' to download a file, 'put' to upload a file, or 'change' to change the name of a file : ")
        continue
s.close()