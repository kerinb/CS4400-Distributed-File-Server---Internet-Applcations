#
# @Author: Breandan Kerin
# @Student Number: 14310166
#

import sys
import time
from threading import Thread

import RequestTypeToFileServer
import os
import select
import socket
import traceback

is_py2 = sys.version[0] == "2"
if is_py2:
    import Queue as queue
else:
    import queue as queue

DEFAULT_PORT_NUMBER = 45678
MAX_NUM_BYTES = 2048
HOST = ""
SERVER_FILE_ROOT = 'Server/'
IP_ADDRESS = socket.gethostbyname(socket.getfqdn())
SERVER_RUNNING = True
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


def check_if_directory_exists(message, connection):
    directory_to_check = SERVER_FILE_ROOT + message[1] + "/"
    full_file_path = directory_to_check + message[2]

    print "Client wants to verify the following directory exists:\n" + full_file_path
    response_to_client = RequestTypeToFileServer.RequestTypeToFileServer.DIRECTORY_NOT_FOUND
    if os.path.exists(directory_to_check):
        response_to_client = RequestTypeToFileServer.RequestTypeToFileServer.DIRECTORY_FOUND
        # we found directory
        print "The directory exists....\nChecking for file now..."
        if os.path.isfile(full_file_path):
            print "File found in directory!"
            response_to_client = RequestTypeToFileServer.RequestTypeToFileServer.FILE_DOES_EXIST
        else:
            print "File not found but directory does exist..."
        connection.sendall(str(response_to_client))
    print "Directory not found...."
    connection.sendall(str(response_to_client))


def open_file(message, connection):
    pass


def write_to_file(message, connection):
    pass


# for this function - I assume that a "" file/directory means no create file/directory!
def make_file(file_to_create):
    response_to_client = RequestTypeToFileServer.RequestTypeToFileServer.FILE_NOT_MADE
    if not os.path.exists(file_to_create):
        print "Creating file: " + file_to_create + "..."
        file = open(file_to_create, 'a')
        file.close()
        response_to_client = RequestTypeToFileServer.RequestTypeToFileServer.FILE_MADE
        print "Created file: " + file_to_create + "..."
    return response_to_client


def create_a_new_file(message, connection):
    directory = message[1]
    file_to_create = message[1] + message[2] + FILE_EXTENSION_TXT
    print "File to create: " + file_to_create
    print "In directory: " + directory

    # will make directory if we need....
    make_directory(directory)
    response_to_client = make_file(file_to_create)
    connection.sendall(str(response_to_client))


def assign_id_to_client(message, connection):
    pass


def delete_file(message, connection):
    pass  #


def handle_client_request(data_received_from_client, connection):
    if data_received_from_client == "kill":
        print "Shutting down file server"
        set_server_running_value(False)
    else:
        split_data_received_from_client = data_received_from_client.split("\n")
        request_type = str(split_data_received_from_client[0])
        print "ENUM VALUE: " + str(RequestTypeToFileServer.RequestTypeToFileServer.CHECK_FOR_FILE_EXIST.value)
        print "The Request made by the client is:" + request_type

        if request_type == str(RequestTypeToFileServer.RequestTypeToFileServer.CHECK_FOR_FILE_EXIST.value):
            print "Client requested to check if a directory exists..."
            check_if_directory_exists(split_data_received_from_client, connection)

        elif request_type == str(RequestTypeToFileServer.RequestTypeToFileServer.OPEN_FILE):
            print "Client requested to open a file..."
            open_file(split_data_received_from_client, connection)

        elif request_type == str(RequestTypeToFileServer.RequestTypeToFileServer.WRITE_TO_FILE):
            print "Client has requested to write to a file..."
            write_to_file(split_data_received_from_client, connection)

        elif request_type == str(RequestTypeToFileServer.RequestTypeToFileServer.CREATE_FILE):
            print "Client has requested to create a file..."
            create_a_new_file(split_data_received_from_client, connection)

        elif request_type == str(RequestTypeToFileServer.RequestTypeToFileServer.REQUEST_CLIENT_ID):
            print "Client has requested to have an ID assigned to them..."
            assign_id_to_client(split_data_received_from_client, connection)

        elif request_type == str(RequestTypeToFileServer.RequestTypeToFileServer.DELETE_FILE):
            print "Client has requested to delete a file..."
            delete_file_from_server(split_data_received_from_client, connection)
        else:
            print "ERROR: Invalid request was sent by the client:\nREQUEST: " + request_type
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
            connected_to_file_server = handle_client_request(data_received_from_client, connection)
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
                read, _, _, = select.select(list_of_sockets, [], [], 0.1)
                for s in read:
                    if s is sock:
                        connection, address = s.accept()
                        thread_list.add_task(accept_client_connection(connection, address), connection, address)

            sock.close()
            print "File Server is shutting down...."

        except Exception as e:
            print time.ctime(time.time()) + "Exception thrown during server initialisation..."
            print e.message
            print traceback.format_exc()
        finally:
            print "Closing socket...."
            sock.close()

    except Exception as e:
        print time.ctime(time.time()) + "Exception thrown during server initialisation..."
        print e.message
        print traceback.format_exc()


main()
