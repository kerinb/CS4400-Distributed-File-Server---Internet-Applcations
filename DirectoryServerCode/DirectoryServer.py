#
# @Author: Breandan Kerin
# @Student Number: 14310166
#

import select
import socket
import sys
import DirectoryServerLibrary as DSL
import SharedFiles.ThreadHelperFunctions as ThreadHelper

from SharedFiles import SharedFileFunctions

DEFAULT_PORT_NUMBER = 12348
MAX_NUM_BYTES = 2048
HOST = ""
SERVER_FILE_ROOT = 'Server/'
IP_ADDRESS = socket.gethostbyname(socket.getfqdn())
SERVER_RUNNING = True
list_of_address_connected = []
num_clients = 0


def handle_socket_connection(sock, port_number):
    print "Server is running on:\nPORT: %s\nIP Address: %s", port_number, IP_ADDRESS

    SharedFileFunctions.make_directory(SERVER_FILE_ROOT)

    DSL.set_server_running_value(True)
    thread_list = ThreadHelper.ListOfThreads(10, 10)

    try:
        print "Listening for requests coming from clients..."
        sock.listen(1)
        list_of_sockets = [sock]

        while DSL.get_server_running_value():
            read, _, _ = select.select(list_of_sockets, [], [], 0.1)
            for s in read:
                if s is sock:
                    connection, address = s.accept()
                    thread_list.add_task(DSL.accept_connection, connection, address)

    except Exception as e:
        SharedFileFunctions.handle_errors(e, "Exception thrown during server initialisation...")
    finally:
        print "Closing socket...."
        sock.close()
        thread_list.end_threads()
        sys.exit(0)


def main():
    global IP_ADDRESS, SERVER_FILE_ROOT

    try:
        print "Initialising file server..."
        if len(sys.argv) < 2:
            port_number = int(sys.argv[0])
        else:
            port_number = DEFAULT_PORT_NUMBER

        if port_number == 12345:
            client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_sock.bind((HOST, port_number))
            handle_socket_connection(client_sock, port_number)
        elif port_number == 45678:
            file_server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            file_server_sock.bind((HOST, port_number))
            handle_socket_connection(file_server_sock, port_number)
    except Exception as e:
        SharedFileFunctions.handle_errors(e, "Exception thrown during server initialisation...")


main()
