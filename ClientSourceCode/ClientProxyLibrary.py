#
# @Author: Breandan Kerin
# @Student Number: 14310166
#

from pyasn1.compat.octets import null
from socket import gethostbyname, getfqdn, socket, AF_INET, SOCK_STREAM
import os
import SharedFiles.RequestTypeToFileServer as RequestTypeToFileServer
import SharedFiles.ResponseTypeToClient as ResponseTypeToClient
from SharedFiles import SharedFileFunctions

DEFAULT_PORT_NUMBER = 12345
DEFAULT_HOST_NAME = gethostbyname(getfqdn())
MAX_NUM_BYTES = 2048
CLIENT_ID = ""
CLIENT_FILE_ROOT = 'Client/'
FILE_EXTENSION_TXT = ".txt"


# ---------------------------------------------------------------------------------------------------------------------#
#                   Functions for creating, maintaining and removing a connection to server                            #
# ---------------------------------------------------------------------------------------------------------------------#
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
                "\n1: Open file local file with gedit"
                "\n2: Create new file on server"
                "\n3: Write to file on file server"
                "\n4: Delete file from file server"
                "\n7: Download file form file server"
                "\nC: close connection"
                "\nK: kill server\n")
            running = handle_user_request_for_file_server(user_request_for_server, sock, running)
        except Exception as e:
            SharedFileFunctions.handle_errors(e, "ERROR: An error occurred when handling the user input...\n")
    print "closing connection to server...."
    sock.close()


def kill_file_server(sock):
    sock.sendall("kill")
    print "Client sent request to kill server..."


# ---------------------------------------------------------------------------------------------------------------------#
#                   Functions that provide functionality to client connected to file server                            #
# ---------------------------------------------------------------------------------------------------------------------#
def get_file_name_and_path_from_user():
    file_path = raw_input("Enter path to destination file, each folder seperated with a '/':\n")
    file_name = raw_input("Enter name of destination file, no need to include file extension, .TXT assumed:\n")
    return file_path, file_name


def check_if_file_exists_on_file_server(file_name, file_path, sock):
    message_to_file_server = str(RequestTypeToFileServer.RequestTypeToFileServer.CHECK_FOR_FILE_EXIST) + "\n" + \
                             file_path + "\n" + file_name
    print "Checking for file: " + file_path + "/" + file_name
    print "Sending " + message_to_file_server + " to file server...."
    sock.sendall(message_to_file_server)
    print "Sent request to file server to confirm if requested file exists in requested path..."
    response_from_file_server = sock.recv(MAX_NUM_BYTES)
    decode_response_from_server(response_from_file_server)


def check_if_directory_exists(file_name, file_path):
    path = CLIENT_FILE_ROOT + file_path
    if path.endswith("/") or path == "":
        full_file_path = path + file_name + FILE_EXTENSION_TXT
    else:
        full_file_path = path + "/" + file_name + FILE_EXTENSION_TXT

    print "Client wants to verify the following directory exists:\n" + full_file_path
    response_to_client = ResponseTypeToClient.ResponseTypeToClient.DIRECTORY_NOT_FOUND
    if os.path.exists(path):
        response_to_client = ResponseTypeToClient.ResponseTypeToClient.DIRECTORY_FOUND
        print "The directory exists....\nChecking for file now..."
        if os.path.isfile(full_file_path):
            print "File found in directory!"
            response_to_client = ResponseTypeToClient.ResponseTypeToClient.FILE_DOES_EXIST
        else:
            print "File not found but directory does exist..."
        return response_to_client
    print "Directory not found...."
    return response_to_client


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


def create_directory_on_server(file_path, sock):
    message_to_file_server = str(RequestTypeToFileServer.RequestTypeToFileServer.CREATE_FILE) + "\n" + \
                             file_path + "\n"
    print "Checking for file: " + file_path + "/"
    print "Sending " + message_to_file_server + " to file server...."
    sock.sendall(message_to_file_server)
    print "Sent request to file server to confirm if requested file exists in requested path..."
    response_from_file_server = sock.recv(MAX_NUM_BYTES)
    decode_response_from_server(response_from_file_server)


def delete_file_from_server(file_name, file_path, sock):
    message_to_file_server = str(RequestTypeToFileServer.RequestTypeToFileServer.DELETE_FILE) + "\n" + \
                             file_path + "\n" + file_name + "\n"
    print "Checking for file: " + file_path + "/" + file_name
    print "Sending " + message_to_file_server + " to file server...."
    sock.sendall(message_to_file_server)
    print "Sent request to file server to delete file in requested path..."
    response_from_file_server = sock.recv(MAX_NUM_BYTES)
    decode_response_from_server(response_from_file_server)


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
    if str(split_repsonse[0]) == str(ResponseTypeToClient.ResponseTypeToClient.RESPONSE_CLIENT_ID_MADE):
        CLIENT_ID = str(split_repsonse[1])
    print "Your client ID is now: " + CLIENT_ID + "..."


def handle_download_file_response(response_from_file_server, full_file_path, sock):
    if response_from_file_server == str(ResponseTypeToClient.ResponseTypeToClient.FILE_DOES_EXIST):
        print "File: " + full_file_path + " exists on file server..."

        print "Downloading: " + full_file_path + "..."
        f = open(full_file_path, 'w')
        connected_for_file_reading = True
        while connected_for_file_reading:
            data_from_file = sock.recv(MAX_NUM_BYTES)
            f.write(data_from_file)
            connected_for_file_reading = len(data_from_file) == MAX_NUM_BYTES
        print "file downloaded from server....\nClosing local copy..."
        f.close()
    else:
        print "File: " + full_file_path + " not downloaded... Doesnt exist..."


def download_file_from_server(file_name, file_path, sock):
    print "downloading file: " + file_name + " In: " + file_path
    message = str(RequestTypeToFileServer.RequestTypeToFileServer.DOWNLOAD_FILE_FROM_SERVER) + "\n" + file_path + \
              "\n" + file_name
    sock.sendall(message)
    if file_path.endswith("/") or file_path == "":
        full_file_path = CLIENT_FILE_ROOT + file_path + file_name + FILE_EXTENSION_TXT
    else:
        full_file_path = CLIENT_FILE_ROOT + file_path + "/" + file_name + FILE_EXTENSION_TXT
    print "Request sent to file server to open " + full_file_path
    response_from_file_server = sock.recv(MAX_NUM_BYTES)
    decode_response_from_server(response_from_file_server)
    handle_download_file_response(response_from_file_server, full_file_path, sock)


def open_file(file_name, file_path):
    print "Opening file: " + file_name + " In: " + file_path
    if file_path.endswith("/") or file_path == "":
        full_file_path = CLIENT_FILE_ROOT + file_path + file_name + FILE_EXTENSION_TXT
    else:
        full_file_path = CLIENT_FILE_ROOT + file_path + "/" + file_name + FILE_EXTENSION_TXT

    if not os.path.exists(full_file_path):
        SharedFileFunctions.create_a_new_file(file_name, file_path, CLIENT_FILE_ROOT)

    os.system('gedit "{0}"'.format(full_file_path))

    print "Local file: " + full_file_path + " has been changed - To synch with file server select option in Menu..."


def write_file_to_server(file_name, file_path, sock):
    message_to_file_server = str(RequestTypeToFileServer.RequestTypeToFileServer.WRITE_TO_FILE) + "\n" + file_path + \
                             "\n" + file_name + "\n"
    print "Writing client changes to file: " + file_name + " in directory: " + file_path
    sock.sendall(message_to_file_server)
    print "sent request to file server to write changes to file..."
    print "file: " + message_to_file_server

    if ResponseTypeToClient.ResponseTypeToClient.FILE_DOES_EXIST == check_if_directory_exists(
            file_name, file_path):

        if file_path.endswith("/") or file_path == "":
            full_file_path = CLIENT_FILE_ROOT + file_path + file_name + FILE_EXTENSION_TXT
        else:
            full_file_path = CLIENT_FILE_ROOT + file_path + "/" + file_name + FILE_EXTENSION_TXT
        print "full path to file: " + full_file_path

        f = open(full_file_path)
        print "Requested file located... Will upload to server know..."
        data_to_write = f.read(MAX_NUM_BYTES)
        print "data to write" + data_to_write
        data_in_file = True
        while data_in_file:
            sock.sendall(data_to_write)
            data_to_write = f.read(MAX_NUM_BYTES)
            print "data to write" + data_to_write
            data_in_file = data_to_write != ''
        print "Finished Transmitting file to server..."

        response_from_file_server = sock.recv(MAX_NUM_BYTES)
        decode_response_from_server(response_from_file_server)
    else:
        print "The file you are trying upload to the server doesnt exist..." \
              "Please enter a valid file_name and file_path..."


# ---------------------------------------------------------------------------------------------------------------------#
#                              handle responses and requests to/from the file server                                   #
# ---------------------------------------------------------------------------------------------------------------------#
def decode_response_from_server(response_from_file_server):
    message = "\nERROR: Invalid response from file server..."
    print "response from server: " + response_from_file_server
    if response_from_file_server == str(ResponseTypeToClient.ResponseTypeToClient.RESPONSE_CLIENT_ID_MADE):
        message = "New client has ben assigned a new unique ID..."

    elif response_from_file_server == str(ResponseTypeToClient.ResponseTypeToClient.FILE_DOES_EXIST):
        message = "File exists in directory specified by client..."

    elif response_from_file_server == str(ResponseTypeToClient.ResponseTypeToClient.DIRECTORY_FOUND):
        message = "Directory found but specified file not found..."

    elif response_from_file_server == str(ResponseTypeToClient.ResponseTypeToClient.DIRECTORY_NOT_FOUND):
        message = "Directory and file not found..."

    elif response_from_file_server == str(ResponseTypeToClient.ResponseTypeToClient.FILE_MADE):
        message = "requested file was created..."

    elif response_from_file_server == str(ResponseTypeToClient.ResponseTypeToClient.FILE_NOT_MADE):
        message = "requested file was not created..."

    elif response_from_file_server == str(ResponseTypeToClient.ResponseTypeToClient.FILE_ALREADY_EXISTS):
        message = "requested file already exists..."

    elif response_from_file_server == str(ResponseTypeToClient.ResponseTypeToClient.FILE_DELETED):
        message = "requested file was deleted..."

    elif response_from_file_server == str(ResponseTypeToClient.ResponseTypeToClient.FILE_NOT_DELETED_DIRECTORY_FOUND):
        message = "directory given found but file not found and deleted..."

    elif response_from_file_server == str(
            ResponseTypeToClient.ResponseTypeToClient.FILE_NOT_DELETED_DIRECTORY_NOT_FOUND):
        message = "directory given not found... file not deleted..."

    elif response_from_file_server == str(ResponseTypeToClient.ResponseTypeToClient.WRITE_TO_FILE_SUCCESSFUL):
        message = "write to given file was successful..."

    elif response_from_file_server == str(ResponseTypeToClient.ResponseTypeToClient.WRITE_TO_FILE_UNSUCCESSFUL):
        message = "write to given file was unsuccessful..."

    elif response_from_file_server == str(ResponseTypeToClient.ResponseTypeToClient.RESPONSE_CLIENT_ID_NOT_MADE):
        message = "ID assigned to Client unsuccessful..."

    elif response_from_file_server == str(ResponseTypeToClient.ResponseTypeToClient.RESPONSE_CLIENT_ID_MADE):
        message = "ID assigned to Client successful..."

    elif response_from_file_server == str(ResponseTypeToClient.ResponseTypeToClient.DIRECTORY_CREATED):
        message = "Directory created..."

    elif response_from_file_server == str(ResponseTypeToClient.ResponseTypeToClient.DIRECTORY_NOT_CREATED):
        message = "Directory not created..."

    elif response_from_file_server == str(ResponseTypeToClient.ResponseTypeToClient.DOWNLOAD_SUCCESSFUL):
        message = "Downloaded file from server successful..."

    elif response_from_file_server == str(ResponseTypeToClient.ResponseTypeToClient.DOWNLOAD_UNSUCCESSFUL):
        message = "Downloaded file from server unsuccessful..."

    elif response_from_file_server == str(ResponseTypeToClient.ResponseTypeToClient.ERROR):
        message = "ERROR: An error occurred when creating a connection to the file server..."

    print "RESPONSE FROM FILE SERVER: " + message
    return response_from_file_server


def handle_user_request_for_file_server(user_request_for_server, sock, running):
    if user_request_for_server == "C" or user_request_for_server == "c":
        print "User requested to close connection to file server\nclosing connection to file server..."
        running = False
    else:
        if user_request_for_server == "0":
            print "User requested to verify file is present on server..."
            file_path, file_name = get_file_name_and_path_from_user()
            check_if_file_exists_on_file_server(file_name, file_path, sock)

        elif user_request_for_server == "1":
            print "User requested to open local file..."
            file_path, file_name = get_file_name_and_path_from_user()
            open_file(file_name, file_path)

        elif user_request_for_server == "2":
            print "User requested to create a new file on server..."
            file_path, file_name = get_file_name_and_path_from_user()
            create_file_on_server(file_name, file_path, sock)

        elif user_request_for_server == "3":
            print "User requested to Write file to server..."
            file_path, file_name = get_file_name_and_path_from_user()
            write_file_to_server(file_name, file_path, sock)

        elif user_request_for_server == "4":
            print "User requested to delete file from server..."
            file_path, file_name = get_file_name_and_path_from_user()
            delete_file_from_server(file_name, file_path, sock)

        elif user_request_for_server == "7":
            print "User requested to download file from server..."
            file_path, file_name = get_file_name_and_path_from_user()
            download_file_from_server(file_name, file_path, sock)

        elif user_request_for_server == "5":
            print "User requested to delete file from server..."
            file_path, file_name = get_file_name_and_path_from_user()
            delete_file_from_server(file_name, file_path, sock)
        else:
            if user_request_for_server == "K" or user_request_for_server == "k":
                print "User requested to kill server...\nSHUTTING DOWN SERVER..."
                kill_file_server(sock)
                running = False
            else:
                print "ERROR: Invalid input read in...\nEnter correct option to continue..."
    return running
