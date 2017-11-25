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


def assign_id_to_client(address):
    global list_of_connected_client_addresses, num_clients
    if not (address in list_of_connected_client_addresses):
        response_to_client = str(ResponseTypeToClient.ResponseTypeToClient.RESPONSE_CLIENT_ID_MADE) + "\n" + str(
            num_clients + 1)
        print response_to_client
        list_of_connected_client_addresses.append(address)
        print "Client ID number is: " + str(num_clients)
    else:
        response_to_client = str(ResponseTypeToClient.ResponseTypeToClient.RESPONSE_CLIENT_ID_NOT_MADE)
    return response_to_client


def broadcast_clients_request_to_file_servers(message):
    # for connected file server in my list of file servers, I want to transmit this message to you...
    print "broadcasting clients message to connected file servers\n{0}".format(message)


def handle_request(message, client_connection, address):
    # Im assuming that a client CANNOT kill the directory server...
    split_data_received_from_client = message.split("\n")
    request_type_from_client = str(split_data_received_from_client[0])

    response_to_client = ResponseTypeToClient.ResponseTypeToClient.ERROR
    print "The Request made by the client is:" + request_type_from_client
    if request_type_from_client == str(RequestTypeToFileServer.RequestTypeToFileServer.REQUEST_CLIENT_ID):
        print "Client has requested to have an ID assigned to them..."
        response_to_client = assign_id_to_client(address)

    else:
        broadcast_clients_request_to_file_servers(message)

    client_connection.sendall(response_to_client)
    return client_connection


def accept_client_connection(connection, address):
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
