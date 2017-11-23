#
# @Author: Breandan Kerin
# @Student Number: 14310166
#

import os
from pyasn1.compat.octets import null
from socket import gethostbyname, getfqdn, socket, AF_INET, SOCK_STREAM

import SharedFiles.RequestTypeToFileServer as RequestTypeToFileServer

from SharedFiles import SharedFileFunctions

DEFAULT_PORT_NUMBER = 45678
DEFAULT_HOST_NAME = gethostbyname(getfqdn())
MAX_NUM_BYTES = 2048
CLIENT_ID = ""
CLIENT_FILE_ROOT = 'Client/'
FILE_EXTENSION_TXT = ".txt"


def create_connection_to_file_server(host_name, port_number):
    print "In 'create_connection_to_file_server' function..."
    try:
        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect((host_name, port_number))
        if sock.getpeername:
            print "Connection to file server has been made..."
        else:
            print "ERROR: Connection to file server not made..."
            sock = None
    except Exception as e:
        SharedFileFunctions.handle_errors(e, "ERROR: An error occurred when creating connection to file server...\n")
        sock = null
    return sock


def get_file_name_and_path_from_user():
    file_path = raw_input("Enter path to destination file, each folder seperated with a '/':\n")
    file_name = raw_input("Enter name of destination file, no need to include file extension, .TXT assumed:\n")
    return file_path, file_name


def decode_response_from_server(response_from_file_server):
    message = "\nERROR: Invalid response from file server..."
    print "response from server: " + response_from_file_server
    if response_from_file_server == "8":
        message = "New client has ben assigned a new unique ID..."

    elif response_from_file_server == "9":
        message = "File exists in directory specified by client..."

    elif response_from_file_server == "10":
        message = "Directory found but specified file not found..."

    elif response_from_file_server == "11":
        message = "Directory and file not found..."

    elif response_from_file_server == "12":
        message = "requested file was created..."

    elif response_from_file_server == "13":
        message = "requested file was not created..."

    elif response_from_file_server == "14":
        message = "requested file already exists..."

    elif response_from_file_server == "15":
        message = "requested file was deleted..."

    elif response_from_file_server == "16":
        message = "directory given found but file not found and deleted..."

    elif response_from_file_server == "17":
        message = "directory given not found... file not deleted..."

    elif response_from_file_server == "18":
        message = "write to given file was successful..."

    elif response_from_file_server == "19":
        message = "write to given file was unsuccessful..."

    elif response_from_file_server == "20":
        message = "ID assigned to Client unsuccessful..."

    elif response_from_file_server == "21":
        message = "Directory created..."

    elif response_from_file_server == "22":
        message = "Directory not created..."

    elif response_from_file_server == "999":
        message = "ERROR: An error occurred when creating a connection to the file server..."

    print "RESPONSE FROM FILE SERVER: " + message
    return response_from_file_server


def check_if_file_exists_on_file_server(file_name, file_path, sock):
    message_to_file_server = str(RequestTypeToFileServer.RequestTypeToFileServer.CHECK_FOR_FILE_EXIST) + "\n" + \
                             file_path + "\n" + file_name
    print "Checking for file: " + file_path + "/" + file_name
    print "Sending " + message_to_file_server + " to file server...."
    sock.sendall(message_to_file_server)
    print "Sent request to file server to confirm if requested file exists in requested path..."
    response_from_file_server = sock.recv(MAX_NUM_BYTES)
    decode_response_from_server(response_from_file_server)


def handle_open_file_response(response_from_file_server, full_file_path, sock):
    if response_from_file_server == str(RequestTypeToFileServer.RequestTypeToFileServer.FILE_DOES_EXIST):
        print "File: " + full_file_path + " exists on file server..."

        print "Opening: " + full_file_path + "..."
        f = open(full_file_path, 'w')
        connected_for_file_reading = True
        while connected_for_file_reading:
            data_from_file = sock.recv(MAX_NUM_BYTES)
            f.write(data_from_file)
            connected_for_file_reading = len(data_from_file) == MAX_NUM_BYTES
        print "file downloaded from server....\nClosing local copy..."
        f.close()
    else:
        print "File: " + full_file_path + " not opened... Doesnt exist..."


def open_file_on_server(file_name, file_path, sock):
    print "Opening file: " + file_name + " In: " + file_path
    message = str(RequestTypeToFileServer.RequestTypeToFileServer.OPEN_FILE) + "\n" + file_path + "\n" + file_name
    sock.sendall(message)
    if file_path.endswith("/") or file_path == "":
        full_file_path = CLIENT_FILE_ROOT + file_path + file_name + FILE_EXTENSION_TXT
    else:
        full_file_path = CLIENT_FILE_ROOT + file_path + "/" + file_name + FILE_EXTENSION_TXT
    print "Request sent to file server to open " + full_file_path
    response_from_file_server = sock.recv(MAX_NUM_BYTES)
    decode_response_from_server(response_from_file_server)
    handle_open_file_response(response_from_file_server, full_file_path, sock)


def write_file_to_server(file_name, file_path, sock):
    message_to_file_server = str(RequestTypeToFileServer.RequestTypeToFileServer.WRITE_TO_FILE) + "\n" + file_path + \
                             "\n" + file_name + "\n"
    print "Writing client changes to file: " + file_name + " in directory: " + file_path
    sock.sendall(message_to_file_server)
    print "sent request to file server to write changes to file..."
    print "file: " + message_to_file_server

    if RequestTypeToFileServer.RequestTypeToFileServer.FILE_DOES_EXIST == check_if_directory_exists(
            file_name, file_path):

        if file_path.endswith("/") or file_path == "":
            full_file_path = CLIENT_FILE_ROOT + file_path + file_name + FILE_EXTENSION_TXT
        else:
            full_file_path = CLIENT_FILE_ROOT + file_path + "/" + file_name + FILE_EXTENSION_TXT
        print "full path to file: " + full_file_path

        f = open(full_file_path)
        print "Requested file located... Will upload to server know..."
        data_to_write = f.read(MAX_NUM_BYTES)
        data_in_file = True
        while data_in_file:
            sock.sendall(data_to_write)
            data_to_write = f.read(MAX_NUM_BYTES)
            data_in_file = data_to_write != ''
        print "Finished Transmitting file to server..."

        response_from_file_server = sock.recv(MAX_NUM_BYTES)
        decode_response_from_server(response_from_file_server)
    else:
        print "The file you are trying upload to the server doesnt exist..." \
              "Please enter a valid file_name and file_path..."


def create_file_on_server(file_name, file_path, sock):
    message_to_file_server = str(RequestTypeToFileServer.RequestTypeToFileServer.CREATE_FILE) + "\n" + \
                             file_path + "\n" + file_name + "\n"
    print "Checking for file: " + file_path + "/" + file_name
    print "Sending " + message_to_file_server + " to file server...."
    sock.sendall(message_to_file_server)
    print "Sent request to file server to confirm if requested file exists in requested path..."
    response_from_file_server = sock.recv(MAX_NUM_BYTES)
    decode_response_from_server(response_from_file_server)
    return response_from_file_server


def make_directory(directory_to_create):
    if not os.path.exists(directory_to_create):
        print "Creating root directory 'Server/'..."
        os.makedirs(directory_to_create)
        print "Created root directory 'Server/'..."


def delete_file_from_server(file_name, file_path, sock):
    message_to_file_server = str(RequestTypeToFileServer.RequestTypeToFileServer.DELETE_FILE) + "\n" + \
                             file_path + "\n" + file_name + "\n"
    print "Checking for file: " + file_path + "/" + file_name
    print "Sending " + message_to_file_server + " to file server...."
    sock.sendall(message_to_file_server)
    print "Sent request to file server to delete file in requested path..."
    response_from_file_server = sock.recv(MAX_NUM_BYTES)
    decode_response_from_server(response_from_file_server)


def kill_file_server(sock):
    sock.sendall("kill")
    print "Client sent request to kill server..."


def create_directory_on_server(file_path, sock):
    message_to_file_server = str(RequestTypeToFileServer.RequestTypeToFileServer.CREATE_FILE) + "\n" + \
                             file_path + "\n"
    print "Checking for file: " + file_path + "/"
    print "Sending " + message_to_file_server + " to file server...."
    sock.sendall(message_to_file_server)
    print "Sent request to file server to confirm if requested file exists in requested path..."
    response_from_file_server = sock.recv(MAX_NUM_BYTES)
    decode_response_from_server(response_from_file_server)


def handle_user_request_for_file_server(user_request_for_server, sock, running):
    if user_request_for_server == "C" or user_request_for_server == "c":
        print "User requested to close connection to file server\nclosing connection to file server..."
        running = False
    else:
        # TODO - TEST
        if user_request_for_server == "0":
            print "User requested to verify file is present on server..."
            file_path, file_name = get_file_name_and_path_from_user()
            check_if_file_exists_on_file_server(file_name, file_path, sock)

        # TODO - TEST
        elif user_request_for_server == "1":
            print "User requested to open file from server..."
            file_path, file_name = get_file_name_and_path_from_user()
            open_file_on_server(file_name, file_path, sock)

        # TODO - TEST
        elif user_request_for_server == "2":
            print "User requested to create a new file on server..."
            file_path, file_name = get_file_name_and_path_from_user()
            create_file_on_server(file_name, file_path, sock)

        # TODO - TEST
        elif user_request_for_server == "3":
            print "User requested to create new directory on server..."
            file_path, file_name = get_file_name_and_path_from_user()
            create_directory_on_server(file_path, sock)

        # TODO - TEST
        elif user_request_for_server == "4":
            print "User requested to Write file to server..."
            file_path, file_name = get_file_name_and_path_from_user()
            write_file_to_server(file_name, file_path, sock)

        # TODO - TEST
        elif user_request_for_server == "5":
            print "User requested to delete file from server..."
            file_path, file_name = get_file_name_and_path_from_user()
            delete_file_from_server(file_name, file_path, sock)

        # TODO - TEST
        else:
            if user_request_for_server == "K" or user_request_for_server == "k":
                print "User requested to kill server...\nSHUTTING DOWN SERVER..."
                kill_file_server(sock)
                running = False
            else:
                print "ERROR: Invalid input read in...\nEnter correct option to continue..."
    return running


def get_client_id(sock):
    global CLIENT_ID
    print "Requesting client id for new client in system..."
    message_to_file_server = str(RequestTypeToFileServer.RequestTypeToFileServer.REQUEST_CLIENT_ID)
    sock.sendall(message_to_file_server)
    response_from_file_server = str(sock.recv(MAX_NUM_BYTES))
    split_repsonse = response_from_file_server.split("\n")
    print split_repsonse[0]
    decode_response_from_server(split_repsonse[0])
    print "response from server: " + split_repsonse[0]
    if str(split_repsonse[0]) == str(RequestTypeToFileServer.RequestTypeToFileServer.RESPONSE_CLIENT_ID_MADE):
        CLIENT_ID = str(split_repsonse[1])
    print "Your client ID is now: " + CLIENT_ID + "..."


def check_if_directory_exists(file_name, file_path):
    path = CLIENT_FILE_ROOT + file_path
    if path.endswith("/") or path == "":
        full_file_path = path + file_name + FILE_EXTENSION_TXT
    else:
        full_file_path = path + "/" + file_name + FILE_EXTENSION_TXT

    print "Client wants to verify the following directory exists:\n" + full_file_path
    response_to_client = RequestTypeToFileServer.RequestTypeToFileServer.DIRECTORY_NOT_FOUND
    if os.path.exists(path):
        response_to_client = RequestTypeToFileServer.RequestTypeToFileServer.DIRECTORY_FOUND
        print "The directory exists....\nChecking for file now..."
        if os.path.isfile(full_file_path):
            print "File found in directory!"
            response_to_client = RequestTypeToFileServer.RequestTypeToFileServer.FILE_DOES_EXIST
        else:
            print "File not found but directory does exist..."
        return response_to_client
    print "Directory not found...."
    return response_to_client


def create_and_maintain_connection_to_server(host_name, port_number):
    print "In 'create_and_maintain_connection_to_server' function..."
    sock = create_connection_to_file_server(host_name, port_number)
    running = sock is not None
    get_client_id(sock)
    while running:
        try:
            user_request_for_server = raw_input(
                "Select an option:"
                "\n0: Verify File is on Server"
                "\n1: Open file from server"
                "\n2: Create new file on server"
                "\n3: Read File from server"
                "\n4: Write to file"
                "\n5: Delete file"
                "\n6: Create new Directory"
                "\nC: close connection"
                "\nK: kill server\n")
            running = handle_user_request_for_file_server(user_request_for_server, sock, running)
        except Exception as e:
            SharedFileFunctions.handle_errors(e, "ERROR: An error occurred when handling the user input...\n")


def main():
    running = True

    while running:
        make_directory(CLIENT_FILE_ROOT)
        user_request = raw_input("Select an option:\n1: Open connection to file server\nE: Shut down\n")

        if user_request == "E" or user_request == "e":
            running = False
            print "User chose to shut down server.\n SHUTTING DOWN...."
        else:
            if user_request == "1":
                print "Opening connection to file server"
                create_and_maintain_connection_to_server(DEFAULT_HOST_NAME, DEFAULT_PORT_NUMBER)
            else:
                print "ERROR: User Entered invalid request\nENTERED: ", user_request


main()
