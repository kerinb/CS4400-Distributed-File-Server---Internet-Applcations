#
# @Author: Breandan Kerin
# @Student Number: 14310166
#
import time
from pyasn1.compat.octets import null

import RequestTypeToFileServer
import traceback
from socket import gethostbyname, getfqdn, socket, AF_INET, SOCK_STREAM

DEFAULT_PORT_NUMBER = 45678
DEFAULT_HOST_NAME = gethostbyname(getfqdn())
MAX_NUM_BYTES = 2048
CLIENT_DEFAULT_ID = ""
SERVER_FILE_ROOT = 'Server/'


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
        print time.ctime(time.time()) + "ERROR: An error occurred when creating connection to file server...\n"
        print e.message
        print traceback.format_exc()
        sock = null

    return sock


def get_file_name_and_path_from_user():
    file_path = raw_input("Enter path to destination file, each folder seperated with a '/':\n")
    file_name = raw_input("Enter name of destination file, no need to include file extension, .TXT assumed:\n")
    return file_path, file_name


def decode_response_from_server(response_from_file_server):
    if response_from_file_server == "9":
        print "RESPONSE FROM FILE SERVER: File exists in directory specified by client..."

    if response_from_file_server == "10":
        print "RESPONSE FROM FILE SERVER: Directory found but specified file not found..."

    if response_from_file_server == "11":
        print "RESPONSE FROM FILE SERVER: Directory and file not found..."

    if response_from_file_server == "12":
        print "RESPONSE FROM FILE SERVER: requested file was created..."

    if response_from_file_server == "13":
        print "RESPONSE FROM FILE SERVER:  requested file was not created..."

    if response_from_file_server == "14":
        print "RESPONSE FROM FILE SERVER:  requested file already exists..."

    if response_from_file_server == "15":
        print "RESPONSE FROM FILE SERVER:  requested file was deleted..."

    if response_from_file_server == "16":
        print "RESPONSE FROM FILE SERVER:  directory given found but file not found and deleted..."

    if response_from_file_server == "17":
        print "RESPONSE FROM FILE SERVER:  directory given not found... file not deleted..."


def check_if_file_exists_on_file_server(file_name, file_path, sock):
    # have to send request to server, who will verify if the file exists.
    message_to_file_server = str(RequestTypeToFileServer.RequestTypeToFileServer.CHECK_FOR_FILE_EXIST) + "\n" + \
                             file_path + "\n" + file_name
    print "Checking for file: " + file_path + "/" + file_name
    print "Sending " + message_to_file_server + " to file server...."
    sock.sendall(message_to_file_server)
    print "Sent request to file server to confirm if requested file exists in requested path..."

    # response from server
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


# TODO - May have to integrate this with some form caching later...
def open_file_on_server(file_name, file_path, sock):
    print "Opening file: " + file_name + " In: " + file_path
    message = str(RequestTypeToFileServer.RequestTypeToFileServer.OPEN_FILE) + "\n" + file_path + "\n" + file_name
    sock.sendall(message)
    full_file_path = SERVER_FILE_ROOT + file_path + "/" + file_name
    print "Request sent to file server to open " + full_file_path
    response_from_file_server = sock.recv(MAX_NUM_BYTES)
    decode_response_from_server(response_from_file_server)
    handle_open_file_response(response_from_file_server, full_file_path, sock)


def write_file_to_server(file_name, file_path, sock):
    pass


def create_file_on_server(file_name, file_path, sock):
    message_to_file_server = str(RequestTypeToFileServer.RequestTypeToFileServer.CREATE_FILE) + "\n" + \
                             file_path + "\n" + file_name + "\n"
    print "Checking for file: " + file_path + "/" + file_name
    print "Sending " + message_to_file_server + " to file server...."
    sock.sendall(message_to_file_server)
    print "Sent request to file server to confirm if requested file exists in requested path..."

    # response from server
    response_from_file_server = sock.recv(MAX_NUM_BYTES)
    decode_response_from_server(response_from_file_server)


def delete_file_from_server(file_name, file_path, sock):
    message_to_file_server = str(RequestTypeToFileServer.RequestTypeToFileServer.DELETE_FILE) + "\n" + \
                             file_path + "\n" + file_name + "\n"
    print "Checking for file: " + file_path + "/" + file_name
    print "Sending " + message_to_file_server + " to file server...."
    sock.sendall(message_to_file_server)
    print "Sent request to file server to delete file in requested path..."

    # response from server
    response_from_file_server = sock.recv(MAX_NUM_BYTES)
    decode_response_from_server(response_from_file_server)


def kill_file_server(sock):
    pass


def read_file_from_server(file_name, file_path, sock):
    pass


def create_directory_on_server(file_name, file_path, sock):
    pass


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
            print "User requested to open file from server..."
            file_path, file_name = get_file_name_and_path_from_user()
            open_file_on_server(file_name, file_path, sock)

        elif user_request_for_server == "2":
            print "User requested to create a new file on server..."
            file_path, file_name = get_file_name_and_path_from_user()
            create_file_on_server(file_name, file_path, sock)

        elif user_request_for_server == "3":
            print "User requested to read file from server..."
            file_path, file_name = get_file_name_and_path_from_user()
            read_file_from_server(file_name, file_path, sock)

        elif user_request_for_server == "4":
            print "User requested to Write file to server..."
            file_path, file_name = get_file_name_and_path_from_user()
            write_file_to_server(file_name, file_path, sock)

        elif user_request_for_server == "5":
            print "User requested to delete file from server..."
            file_path, file_name = get_file_name_and_path_from_user()
            delete_file_from_server(file_name, file_path, sock)

        elif user_request_for_server == "6":
            print "User requested to create new directory on server..."
            file_path, file_name = get_file_name_and_path_from_user()
            create_directory_on_server(file_name, file_path, sock)

        else:
            if user_request_for_server == "K" or user_request_for_server == "k":
                print "User requested to kill server...\nSHUTTING DOWN SERVER..."
                kill_file_server(sock)
                running = False
            else:
                print "ERROR: Invalid input read in...\nEnter correct option to continue..."
    return running


def create_and_maintain_connection_to_server(host_name, port_number):
    print "In 'create_and_maintain_connection_to_server' function..."
    sock = create_connection_to_file_server(host_name, port_number)
    running = sock is not None
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
                "\nK: kill server")
            running = handle_user_request_for_file_server(user_request_for_server, sock, running)
        except Exception as e:
            print time.ctime(time.time()) + "ERROR: An error occurred when handling the user input...\n"
            print e.message
            print traceback.format_exc()


def main():
    running = True

    # keep client alive
    while running:
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
