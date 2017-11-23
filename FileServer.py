#
# @Author: Breandan Kerin
# @Student Number: 14310166
#

import sys
from threading import Thread

import RequestTypeToFileServer
import os
import select
import socket
import Queue as queue
import SharedFileFunctions

DEFAULT_PORT_NUMBER = 45678
MAX_NUM_BYTES = 2048
HOST = ""
SERVER_FILE_ROOT = 'Server/'
IP_ADDRESS = socket.gethostbyname(socket.getfqdn())
SERVER_RUNNING = True
list_of_address_connected = []
num_clients = 0
FILE_EXTENSION_TXT = ".txt"


class MyThread(Thread):
    def __init__(self, queue_of_tasks):
        self.tasks = queue_of_tasks
        self.on = True
        Thread.__init__(self)
        self.start()  # start the thread

    def run(self):
        while self.on:
            funcs, args, kargs = self.tasks.get()
            self.on = funcs(*args, **kargs)


class ListOfThreads:
    def __init__(self, num_of_threads, size_of_queue):
        self.queue = queue.Queue(size_of_queue)
        self.num_of_threads = num_of_threads
        self.threads = []
        for i in range(0, num_of_threads):
            self.threads.append(MyThread(self.queue))

    def wait_for_thread_to_complete(self):
        self.task.join()

    def end_threads(self):
        for i in range(0, self.num_of_threads):
            self.add_task(False)
            self.threads[i].join()

    def add_task(self, task, *args, **kargs):
        self.queue.put(task, args, kargs)


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


def open_file(message, connection):
    path = message[1]
    if path.endswith("/") or path == "":
        full_file_path = SERVER_FILE_ROOT + message[1] + message[2] + FILE_EXTENSION_TXT
    else:
        full_file_path = SERVER_FILE_ROOT + message[1] + "/" + message[2] + FILE_EXTENSION_TXT

    response_to_client = check_if_directory_exists(message)
    if response_to_client == RequestTypeToFileServer.RequestTypeToFileServer.FILE_DOES_EXIST:
        print "Requested file client wants to open exists one file directory..."
        connection.sendall(str(response_to_client))
        send_file_to_client(full_file_path, connection)
    else:
        print "File: " + full_file_path + " ---- Doesnt exist..."
        response_to_client = RequestTypeToFileServer.RequestTypeToFileServer.FILE_DOES_NOT_EXIST
        connection.sendall(str(response_to_client))


def write_to_file(message, connection):
    # Get the directory
    response_to_client = RequestTypeToFileServer.RequestTypeToFileServer.WRITE_TO_FILE_SUCCESSFUL
    if message[1].endswith("/") or message[1] == "":
        full_file_path = SERVER_FILE_ROOT + message[1] + message[2] + FILE_EXTENSION_TXT
    else:
        full_file_path = SERVER_FILE_ROOT + message[1] + "/" + message[2] + FILE_EXTENSION_TXT
    does_dir_exist = check_if_directory_exists(message)

    if not does_dir_exist == RequestTypeToFileServer.RequestTypeToFileServer.FILE_DOES_EXIST:
        create_a_new_file(message)
    print "Client wants to write to file: " + full_file_path
    try:
        # open the file for writing
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
        response_to_client = RequestTypeToFileServer.RequestTypeToFileServer.WRITE_TO_FILE_UNSUCCESSFUL
        SharedFileFunctions.handle_errors(e, "Exception thrown during server initialisation...")
    return response_to_client


# for this function - I assume that a "" file/directory means no create file/directory!
def make_file(file_to_create):
    response_to_client = RequestTypeToFileServer.RequestTypeToFileServer.FILE_NOT_MADE
    if not os.path.exists(file_to_create):
        print "Creating file: " + file_to_create + "..."
        f = open(file_to_create, 'w')
        f.close()
        response_to_client = RequestTypeToFileServer.RequestTypeToFileServer.FILE_MADE
        print "Created file: " + file_to_create + "..."
    return response_to_client


def create_a_new_file(message):
    directory = SERVER_FILE_ROOT + message[1]
    path = message[1]
    if path.endswith("/") or path == "":
        file_to_create = SERVER_FILE_ROOT + message[1] + message[2] + FILE_EXTENSION_TXT
    else:
        file_to_create = SERVER_FILE_ROOT + message[1] + "/" + message[2] + FILE_EXTENSION_TXT
    print "File to create: " + file_to_create
    print "In directory: " + directory

    # will make directory if we need....
    make_directory(directory)
    response_to_client = make_file(file_to_create)
    return response_to_client


def assign_id_to_client(address):
    global list_of_address_connected, num_clients
    if not (address in list_of_address_connected):
        response_to_client = str(RequestTypeToFileServer.RequestTypeToFileServer.RESPONSE_CLIENT_ID_MADE) + "\n" + str(
            num_clients + 1)
        list_of_address_connected.append(address)
    else:
        response_to_client = str(RequestTypeToFileServer.RequestTypeToFileServer.RESPONSE_CLIENT_ID_NOT_MADE)
    return response_to_client


def delete_file(message):
    response_to_client = RequestTypeToFileServer.RequestTypeToFileServer.FILE_NOT_DELETED_DIRECTORY_NOT_FOUND
    directory = SERVER_FILE_ROOT + message[1]
    file_to_delete = SERVER_FILE_ROOT + message[1] + "/" + message[2] + FILE_EXTENSION_TXT
    print "file to delete: " + file_to_delete
    if not os.path.exists(directory):
        print "Directory does not exist...\ncan't delete file..."
    else:
        if not os.path.exists(file_to_delete):
            print "file does not exist is directory..."
            response_to_client = RequestTypeToFileServer.RequestTypeToFileServer.FILE_NOT_DELETED_DIRECTORY_FOUND
        else:
            print "file will be deleted..."
            os.remove(file_to_delete)
            response_to_client = RequestTypeToFileServer.RequestTypeToFileServer.FILE_DELETED
            print "file has been deleted..."
    return response_to_client


def check_if_directory_exists(message):
    path = SERVER_FILE_ROOT + message[1]
    if path.endswith("/") or path == "":
        full_file_path = SERVER_FILE_ROOT + message[1] + message[2] + FILE_EXTENSION_TXT
    else:
        full_file_path = SERVER_FILE_ROOT + message[1] + "/" + message[2] + FILE_EXTENSION_TXT

    print "Client wants to verify the following directory exists:\n" + full_file_path
    response_to_client = RequestTypeToFileServer.RequestTypeToFileServer.DIRECTORY_NOT_FOUND
    if os.path.exists(path):
        response_to_client = RequestTypeToFileServer.RequestTypeToFileServer.DIRECTORY_FOUND
        # we found directory
        print "The directory exists....\nChecking for file now..."
        if os.path.isfile(full_file_path):
            print "File found in directory!"
            response_to_client = RequestTypeToFileServer.RequestTypeToFileServer.FILE_DOES_EXIST
        else:
            print "File not found but directory does exist..."
    else:
        print "Directory not found...."
    return response_to_client


def handle_client_request(message, connection, address):
    if message == "kill":
        print "Shutting down file server"
        set_server_running_value(False)
    else:
        split_data_received_from_client = message.split("\n")
        request_type = str(split_data_received_from_client[0])
        response_to_client = RequestTypeToFileServer.RequestTypeToFileServer.ERROR
        print "The Request made by the client is:" + request_type

        # TODO - TEST
        if request_type == str(RequestTypeToFileServer.RequestTypeToFileServer.CHECK_FOR_FILE_EXIST.value):
            print "Client requested to check if a directory exists..."
            response_to_client = check_if_directory_exists(split_data_received_from_client)

        # TODO - TEST
        elif request_type == str(RequestTypeToFileServer.RequestTypeToFileServer.OPEN_FILE):
            print "Client requested to open a file..."
            open_file(split_data_received_from_client, connection)

        # TODO - TEST
        elif request_type == str(RequestTypeToFileServer.RequestTypeToFileServer.WRITE_TO_FILE):
            print "Client has requested to write to a file..."
            response_to_client = write_to_file(split_data_received_from_client, connection)

        # TODO - TEST
        elif str(RequestTypeToFileServer.RequestTypeToFileServer.CREATE_FILE) == request_type:
            print "Client has requested to create a file..."
            response_to_client = create_a_new_file(split_data_received_from_client)

        # TODO - TEST
        elif request_type == str(RequestTypeToFileServer.RequestTypeToFileServer.REQUEST_CLIENT_ID):
            print "Client has requested to have an ID assigned to them..."
            response_to_client = assign_id_to_client(address)

        # TODO - TEST
        elif request_type == str(RequestTypeToFileServer.RequestTypeToFileServer.DELETE_FILE):
            print "Client has requested to delete a file..."
            response_to_client = delete_file(split_data_received_from_client)
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


def make_directory(directory_to_create):
    if not os.path.exists(directory_to_create):
        print "Creating root directory 'Server/'..."
        os.makedirs(directory_to_create)
        print "Created root directory 'Server/'..."


def main():
    global IP_ADDRESS, SERVER_FILE_ROOT
    try:
        print "Initialising file server..."
        if len(sys.argv) < 2:
            port_number = int(sys.argv[0])
        else:
            port_number = DEFAULT_PORT_NUMBER
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((HOST, port_number))
        print "Server is running on:\nPORT: %s\nIP Address: %s", port_number, IP_ADDRESS

        make_directory(SERVER_FILE_ROOT)

        set_server_running_value(True)
        thread_list = ListOfThreads(10, 10)

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

    except Exception as e:
        SharedFileFunctions.handle_errors(e, "Exception thrown during server initialisation...")


main()
