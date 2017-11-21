#
# @Author: Breandan Kerin
# @Student Number: 14310166
#

from socket import gethostbyname, getfqdn, socket, AF_INET, SOCK_STREAM

import traceback, RequestTypeToFileServer

DEFAULT_PORT_NUMBER = 45678
DEFAULT_HOST_NAME = gethostbyname(getfqdn())


def create_connection_to_file_server(host_name, port_number):
    print "In 'create_connection_to_file_server' function..."
    sock = socket((AF_INET, SOCK_STREAM))
    sock.connect((host_name, port_number))
    if sock.getpeername:
        print "Connection to file server has been made..."
    else:
        print "ERROR: Connection to file server not made..."
        sock = None
    return sock


def get_file_name_and_path_from_user():
    file_path = raw_input("Enter path to destination file:\n")
    file_name = raw_input("Enter name of destination file:\n")
    return file_path, file_name


def check_if_file_exists_on_file_server(file_name, file_path, sock):
    # have to send request to server, who will verify if the file exists.
    message_to_file_server = str(RequestTypeToFileServer.RequestTypeToFileServer.CHECK_FOR_DIRECTORY_EXIST) + "\n" + \
                             file_path + "\n" + file_name
    print "Checking for file: " + file_path + "/" + file_name
    print "Sending " + message_to_file_server + " to file server...."
    sock.sendall(message_to_file_server)
    print "Sent request to file server to confirm if requested file exists in requested path..."

    # responce from server
    response_from_file_server = sock.recv()
    print "Response from server: \n" + response_from_file_server


def open_file_on_server(file_name, file_path, sock):
    pass


def write_file_to_server(file_name, file_path, sock):
    pass


def create_file_on_server(file_name, file_path, sock):
    pass


def kill_file_server(sock):
    pass


def handle_user_request_for_file_server(user_request_for_server, sock, running):
    if user_request_for_server == "C" or user_request_for_server == "c":
        print "User requested to close connection to file server\nclosing connection to file server..."
        running = False
    else:
        if user_request_for_server == "1":
            print "User requested to verify file is present on server..."
            file_path, file_name = get_file_name_and_path_from_user()
            check_if_file_exists_on_file_server(file_name, file_path, sock)
        elif user_request_for_server == "2":
            print "User requested to open file from server..."
            file_path, file_name = get_file_name_and_path_from_user()
            open_file_on_server(file_name, file_path, sock)
        elif user_request_for_server == "3":
            print "User requested to Write file to server..."
            file_path, file_name = get_file_name_and_path_from_user()
            write_file_to_server(file_name, file_path, sock)
        elif user_request_for_server == "4":
            print "User requested to create a new file on server..."
            file_path, file_name = get_file_name_and_path_from_user()
            create_file_on_server(file_name, file_path, sock)
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
                "\n1: Verify File is on Server"
                "\n2: Open file from server"
                "\n3: Write file to server"
                "\n4: Create new file"
                "\nC: close connection"
                "\nK: kill server")
            running = handle_user_request_for_file_server(user_request_for_server, sock, running)
        except Exception as e:
            print "ERROR: An error occurred when handling the user input...\n"
            print e.message
            print traceback.format_exc()


def main():
    running = True

    # keep client alive
    while running:
        user_request = raw_input("Select an option:\n1: Open connection to file server\nE: Shut down")

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
