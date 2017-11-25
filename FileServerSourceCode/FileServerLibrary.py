#
# @Author: Breandan Kerin
# @Student Number: 14310166
#
# NOTE: for the port numbers, I will be \assuming that for the file servers, there set of port num,bers are < 45600
#      The Directory server = 45678 and the clients will be > 456700

import os
import socket

import select
from pyasn1.compat.octets import null
from socket import gethostbyname, getfqdn, socket, AF_INET, SOCK_STREAM

import SharedFiles.RequestTypeToFileServer as RequestTypeToFileServer
import SharedFiles.ResponseTypeToClient as ResponseTypeToClient
from SharedFiles import SharedFileFunctions
from SharedFiles import ThreadHelperFunctions as ThreadHelper

DEFAULT_PORT_NUMBER = 45600
MAX_NUM_BYTES = 2048
FILE_SERVER_ID = 0
HOST = ""
SERVER_FILE_ROOT = 'Server/'
IP_ADDRESS = gethostbyname(getfqdn())
SERVER_RUNNING = True
list_of_address_connected = []
num_clients = 0
FILE_EXTENSION_TXT = ".txt"


def handle_connection_as_a_client(port_number):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, port_number))
    print "Client is running on:\nPORT: %s\nIP Address: %s", port_number, IP_ADDRESS

    SharedFileFunctions.make_directory(SERVER_FILE_ROOT)

    set_server_running_value(True)
    thread_list = ThreadHelper.ListOfThreads(10, 10)

    try:
        print "Listening for requests coming from clients..."
        sock.listen(1)
        list_of_sockets = [sock]

        while get_server_running_value():
            read, _, _ = select.select(list_of_sockets, [], [], 0.1)
            for s in read:
                if s is sock:
                    connection, address = s.accept()
                    thread_list.add_task(accept_client_connection(connection, address), connection, address)

        sock.close()
        print "File Server is shutting down...."

    except Exception as e:
        SharedFileFunctions.handle_errors(e, "Exception thrown during server initialisation...")
    finally:
        print "Closing socket...."
        sock.close()


def create_connection_to_directory_server(host_name, port_number):
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


def decode_response_from_directory(response_from_file_server):
    message = "\nERROR: Invalid response from file server..."
    print "response from server: " + response_from_file_server
    if response_from_file_server == str(ResponseTypeToClient.ResponseTypeToClient.RESPONSE_CLIENT_ID_NOT_MADE):
        message = "ID assigned to Client unsuccessful..."

    elif response_from_file_server == str(ResponseTypeToClient.ResponseTypeToClient.RESPONSE_CLIENT_ID_MADE):
        message = "ID assigned to Client successful..."

    elif response_from_file_server == str(ResponseTypeToClient.ResponseTypeToClient.ERROR):
        message = "ERROR: An error occurred when creating a connection to the file server..."

    print "RESPONSE FROM FILE SERVER: " + message
    return response_from_file_server


def get_server_id(sock):
    global FILE_SERVER_ID
    print "Requesting server id for new file server in system..."
    message_to_directory_server = str(RequestTypeToFileServer.RequestTypeToFileServer.REQUEST_SERVER_ID)
    sock.sendall(message_to_directory_server)
    response_from_file_server = str(sock.recv(MAX_NUM_BYTES))
    split_repsonse = response_from_file_server.split("\n")
    print split_repsonse[0]
    decode_response_from_directory(split_repsonse[0])
    print "response from server: " + split_repsonse[0]
    if str(split_repsonse[0]) == str(ResponseTypeToClient.ResponseTypeToClient.RESPONSE_CLIENT_ID_MADE):
        FILE_SERVER_ID = str(split_repsonse[1])
    print "Your client ID is now: " + FILE_SERVER_ID + "..."


def create_and_maintain_connection_with_directory_server(port_number, host_name):
    print "In 'create_and_maintain_connection_to_server' function..."
    sock = create_connection_to_directory_server(host_name, port_number)
    running = sock is not None
    get_server_id(sock)
    while running:
        print "waiting for message from directory server..."


def set_server_running_value(boolean_value):
    SERVER_RUNNING = boolean_value


def get_server_running_value():
    return SERVER_RUNNING


def send_file_to_client(full_file_path, connection):
    f = open(full_file_path)
    file_data_to_send_client = f.read(MAX_NUM_BYTES)
    while file_data_to_send_client != '':
        connection.sendall(str(file_data_to_send_client))
        print "SENDING: " + file_data_to_send_client + " ---- To Client..."
        file_data_to_send_client = f.read(MAX_NUM_BYTES)
    print "Entire file sent to client...."
    f.close()


def download_file(message, connection):
    path = message[1]
    if path.endswith("/") or path == "":
        full_file_path = SERVER_FILE_ROOT + message[1] + message[2] + FILE_EXTENSION_TXT
    else:
        full_file_path = SERVER_FILE_ROOT + message[1] + "/" + message[2] + FILE_EXTENSION_TXT

    response_to_client = SharedFileFunctions.check_if_directory_exists(message[2], message[2], SERVER_FILE_ROOT)
    if response_to_client == ResponseTypeToClient.ResponseTypeToClient.FILE_DOES_EXIST:
        print "Requested file client wants to open exists one file directory..."
        connection.sendall(str(response_to_client))
        send_file_to_client(full_file_path, connection)
    else:
        print "File: " + full_file_path + " ---- Doesnt exist..."
        response_to_client = ResponseTypeToClient.ResponseTypeToClient.FILE_DOES_NOT_EXIST
        connection.sendall(str(response_to_client))


def write_to_file(message, connection):
    response_to_client = ResponseTypeToClient.ResponseTypeToClient.WRITE_TO_FILE_SUCCESSFUL
    if message[1].endswith("/") or message[1] == "":
        full_file_path = SERVER_FILE_ROOT + message[1] + message[2] + FILE_EXTENSION_TXT
    else:
        full_file_path = SERVER_FILE_ROOT + message[1] + "/" + message[2] + FILE_EXTENSION_TXT
    does_dir_exist = SharedFileFunctions.check_if_directory_exists(message[2], message[1], SERVER_FILE_ROOT)
    if not does_dir_exist == ResponseTypeToClient.ResponseTypeToClient.FILE_DOES_EXIST:
        SharedFileFunctions.create_a_new_file(message[1], message[2], SERVER_FILE_ROOT)
    print "Client wants to write to file: " + full_file_path
    try:
        f = open(full_file_path, 'w')
        print "File opened. Beginning download from client"
        open_connection = True
        while open_connection:
            data = connection.recv(MAX_NUM_BYTES)
            f.write(data)
            print "Writing " + str(data + " to file")
            open_connection = len(data) == MAX_NUM_BYTES
        print "Write to file completed. Closing file."
        f.close()
    except Exception as e:
        response_to_client = ResponseTypeToClient.ResponseTypeToClient.WRITE_TO_FILE_UNSUCCESSFUL
        SharedFileFunctions.handle_errors(e.message, "Exception thrown during server initialisation...")
    return response_to_client


def assign_id_to_client(address):
    global list_of_address_connected, num_clients
    if not (address in list_of_address_connected):
        response_to_client = str(ResponseTypeToClient.ResponseTypeToClient.RESPONSE_CLIENT_ID_MADE) + "\n" + str(
            num_clients + 1)
        print response_to_client
        list_of_address_connected.append(address)
        print "Client ID number is: " + str(num_clients)
    else:
        response_to_client = str(ResponseTypeToClient.ResponseTypeToClient.RESPONSE_CLIENT_ID_NOT_MADE)
    return response_to_client


def delete_file(message):
    response_to_client = ResponseTypeToClient.ResponseTypeToClient.FILE_NOT_DELETED_DIRECTORY_NOT_FOUND
    directory = SERVER_FILE_ROOT + message[1]
    file_to_delete = SERVER_FILE_ROOT + message[1] + "/" + message[2] + FILE_EXTENSION_TXT
    print "file to delete: " + file_to_delete
    if not os.path.exists(directory):
        print "Directory does not exist...\ncan't delete file..."
    else:
        if not os.path.exists(file_to_delete):
            print "file does not exist is directory..."
            response_to_client = ResponseTypeToClient.ResponseTypeToClient.FILE_NOT_DELETED_DIRECTORY_FOUND
        else:
            print "file will be deleted..."
            os.remove(file_to_delete)
            response_to_client = ResponseTypeToClient.ResponseTypeToClient.FILE_DELETED
            print "file has been deleted..."
    return response_to_client


def create_new_directory(split_data_received_from_client):
    response_to_client = ResponseTypeToClient.ResponseTypeToClient.DIRECTORY_NOT_CREATED
    if not SharedFileFunctions.check_if_directory_exists(split_data_received_from_client[2],
                                                         split_data_received_from_client[1],
                                                         SERVER_FILE_ROOT) == ResponseTypeToClient.ResponseTypeToClient.FILE_DOES_EXIST:
        directory_to_create = SERVER_FILE_ROOT + split_data_received_from_client[1]
        SharedFileFunctions.make_directory(directory_to_create)
        response_to_client = ResponseTypeToClient.ResponseTypeToClient.DIRECTORY_CREATED

    return response_to_client


def handle_client_request(message, connection, address):
    if message == "kill":
        print "Shutting down file server"
        set_server_running_value(False)
    else:
        split_data_received_from_client = message.split("\n")
        request_type = str(split_data_received_from_client[0])
        response_to_client = ResponseTypeToClient.ResponseTypeToClient.ERROR
        print "The Request made by the client is:" + request_type

        # TODO - TEST
        if request_type == str(RequestTypeToFileServer.RequestTypeToFileServer.CHECK_FOR_FILE_EXIST):
            print "Client requested to check if a directory exists..."
            response_to_client = SharedFileFunctions.check_if_directory_exists(split_data_received_from_client[2],
                                                                               split_data_received_from_client[1],
                                                                               SERVER_FILE_ROOT)

        # TODO - TEST
        elif request_type == str(RequestTypeToFileServer.RequestTypeToFileServer.WRITE_TO_FILE):
            print "Client has requested to write to a file..."
            response_to_client = write_to_file(split_data_received_from_client, connection)

        # TODO - TEST
        elif request_type == str(RequestTypeToFileServer.RequestTypeToFileServer.CREATE_FILE):
            print "Client has requested to write to a file..."
            response_to_client = create_new_directory(split_data_received_from_client)

        # TODO - TEST
        elif request_type == str(RequestTypeToFileServer.RequestTypeToFileServer.REQUEST_CLIENT_ID):
            print "Client has requested to have an ID assigned to them..."
            response_to_client = assign_id_to_client(address)

        # TODO - TEST
        elif request_type == str(RequestTypeToFileServer.RequestTypeToFileServer.DELETE_FILE):
            print "Client has requested to delete a file..."
            response_to_client = delete_file(split_data_received_from_client)

        # TODO - TEST
        elif request_type == str(RequestTypeToFileServer.RequestTypeToFileServer.DOWNLOAD_FILE_FROM_SERVER):
            print "Client has requested to delete a file..."
            download_file(split_data_received_from_client, connection)

        else:
            print "ERROR: Invalid request was sent by the client:\nREQUEST: " + request_type
        connection.sendall(str(response_to_client))
    return connection


def accept_client_connection(connection, address):
    print "File Server received a new connection from " + str(address)
    connected_to_file_server = True
    while connected_to_file_server:
        data_received_from_client = connection.recv(MAX_NUM_BYTES)

        if not data_received_from_client:
            print "No data received..."
            continue
        else:
            connected_to_file_server = handle_client_request(data_received_from_client, connection, address)
    print "Connection closed..."
    return connected_to_file_server
