#
# @Author: Breandan Kerin
# @Student Number: 14310166
#
# NOTE: for the port numbers, I will be \assuming that for the file servers, there set of port num,bers are < 45600
#      The Directory server = 45678 and the clients will be > 456700

import socket
import select

from SharedFiles import SharedFileFunctions, ResponseTypeToClient, RequestTypeToFileServer
from SharedFiles import ThreadHelperFunctions as ThreadHelper

DIRECTORY_SERVER_RUNNING = True
HOST = ""
DEFAULT_PORT_NUMBER = 45678
IP_ADDRESS = socket.gethostbyname(socket.getfqdn())
MAX_NUM_BYTES = 2048
list_of_connected_client_addresses = []
num_clients = 0
list_of_connected_file_server_addresses = []
num_file_servers = 0


def set_server_running_value(boolean_value):
    DIRECTORY_SERVER_RUNNING = boolean_value


def get_server_running_value():
    return DIRECTORY_SERVER_RUNNING


def give_id_if_new(addresses, address, num):
    if not (address in addresses):
        num += 1
        response_to_client = str(ResponseTypeToClient.ResponseTypeToClient.RESPONSE_CLIENT_ID_MADE) + "\n" + num
        print response_to_client
        list_of_connected_client_addresses.append(address)
        print "Client ID number is: " + str(num_clients)
    else:
        response_to_client = str(ResponseTypeToClient.ResponseTypeToClient.RESPONSE_CLIENT_ID_NOT_MADE)
    return response_to_client, num


def assign_id(address, request_type):
    global list_of_connected_client_addresses, num_clients, list_of_connected_file_server_addresses, num_file_servers
    if request_type == RequestTypeToFileServer.RequestTypeToFileServer.CLIENT:
        response_to_client, num = give_id_if_new(list_of_connected_client_addresses, address, num_clients)
        num_clients = num
    elif request_type == RequestTypeToFileServer.RequestTypeToFileServer.FILE_SERVER:
        response_to_client, num = give_id_if_new(list_of_connected_file_server_addresses, address, num_clients)
        num_file_servers = num
    else:
        print "deal with this properly later"
        response_to_client = str(ResponseTypeToClient.ResponseTypeToClient.ERROR)
    return response_to_client


def broadcast_clients_request_to_file_servers(message):
    # for connected file server in my list of file servers, I want to transmit this message to you...
    print "broadcasting clients message to connected file servers\n{0}".format(message)


def deal_with_request(connection, message, address):
    if message == "kill":
        print "Shutting down file server"
        set_server_running_value(False)
    else:
        split_data_received_from_client = message.split("\n")
        request_type = str(split_data_received_from_client[0])
        response_to_client = ResponseTypeToClient.ResponseTypeToClient.ERROR
        print "The Request made by the client is:" + request_type

        if request_type == str(RequestTypeToFileServer.RequestTypeToFileServer.CHECK_FOR_FILE_EXIST):
            print "Client requested to check if a directory exists..."

        elif request_type == str(RequestTypeToFileServer.RequestTypeToFileServer.WRITE_TO_FILE):
            print "Client has requested to write to a file..."
            # construct write to file message to broadcast

        elif request_type == str(RequestTypeToFileServer.RequestTypeToFileServer.CREATE_FILE):
            print "Client has requested to write to a file..."
            # construct create mesage to broadcast

        elif request_type == str(RequestTypeToFileServer.RequestTypeToFileServer.REQUEST_CLIENT_ID):
            print "Client has requested to have an ID assigned to them..."
            response_to_client = assign_id(address, )

        elif request_type == str(RequestTypeToFileServer.RequestTypeToFileServer.DELETE_FILE):
            print "Client has requested to delete a file..."
            # construct delete file message to broadcast

        elif request_type == str(RequestTypeToFileServer.RequestTypeToFileServer.DOWNLOAD_FILE_FROM_SERVER):
            print "Client has requested to delete a file..."
            # construct downlaod message to broadcast.

        else:
            print "ERROR: Invalid request was sent by the client:\nREQUEST: " + request_type
        connection.sendall(str(response_to_client))
    return connection


def handle_request(message, connection, address):
    # Im assuming that a client CANNOT kill the directory server...
    split_data_received_from_client = message.split("\n")
    request_source = str(split_data_received_from_client[3])

    print "The Request was made by:" + request_source
    deal_with_request(connection, split_data_received_from_client, address)
    return connection


def accept_connection(connection, address):
    print "File Server received a new connection from " + str(address)
    connected_to_file_server = True
    while connected_to_file_server:
        data_received_from_client = connection.recv(MAX_NUM_BYTES)

        if not data_received_from_client:
            print "No data received..."
            continue
        else:
            connected_to_file_server = handle_request(data_received_from_client, connection, address)
    print "Connection closed..."
    return connected_to_file_server
