#
# @Author: Breandan Kerin
# @Student Number: 14310166
#

import sys

from threading import Thread

import time

import RequestTypeToFileServer, traceback, socket, os, select

DEFAULT_PORT_NUMBER = 45678
HOST = ""
SERVER_FILE_ROOT = 'Server/'
IP_ADDRESS = socket.gethostbyname(socket.getfqdn())
SERVER_RUNNING = True


class MyThread(Thread):
    def __init__(self, queue_of_tasks):
        self.tasks = queue_of_tasks
        self.on = True
        Thread.__init__(self)
        self.start()  # start the thread

    def run(self):
        while self.on:
            task, args, kargs = self.tasks.get()
            self.on = task(*args, **kargs)


class ListOfThreads:
    def __init__(self, num_of_threads, size_of_queue):
        self.queue = size_of_queue
        self.num_of_threads = num_of_threads
        self.threads = []
        for i in range(0, num_of_threads):
            self.threads.append(MyThread(self.queue))

    def wait_for_thread_to_complete(self):
        self.tasks.join()

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
    pass


def open_file(split_data_received_from_client, connected_to_file_server):
    pass


def write_to_file(split_data_received_from_client, connected_to_file_server):
    pass


def create_a_new_file(split_data_received_from_client, connected_to_file_server):
    pass


def assign_id_to_client(split_data_received_from_client, connected_to_file_server):
    pass


def delete_file_from_server(split_data_received_from_client, connected_to_file_server):
    pass


def handle_client_request(data_received_from_client, connected_to_file_server):
    if data_received_from_client == "kill":
        print "Shutting down file server"
        connected_to_file_server = False
        set_server_running_value(False)
    else:
        split_data_received_from_client = data_received_from_client.split("\n")
        request_type = str(split_data_received_from_client[0])
        print "The Request made by the client is:" + request_type

        if request_type == RequestTypeToFileServer.RequestTypeToFileServer.CHECK_FOR_DIRECTORY_EXIST.value:
            print "Client requested to check if a directory exists..."
            check_if_directory_exists(split_data_received_from_client, connected_to_file_server)

        elif request_type == RequestTypeToFileServer.RequestTypeToFileServer.OPEN_FILE:
            print "Client requested to open a file..."
            open_file(split_data_received_from_client, connected_to_file_server)

        elif request_type == RequestTypeToFileServer.RequestTypeToFileServer.WRITE_TO_FILE:
            print "Client has requested to write to a file..."
            write_to_file(split_data_received_from_client, connected_to_file_server)

        elif request_type == RequestTypeToFileServer.RequestTypeToFileServer.CREATE_File:
            print "Client has requested to create a file..."
            create_a_new_file(split_data_received_from_client,connected_to_file_server)

        elif request_type == RequestTypeToFileServer.RequestTypeToFileServer.REQUEST_CLIENT_ID:
            print "Client has requested to have an ID assigned to them..."
            assign_id_to_client(split_data_received_from_client, connected_to_file_server)

        elif request_type == RequestTypeToFileServer.RequestTypeToFileServer.DELETE_FILE:
            print "Client has requested to delete a file..."
            delete_file_from_server(split_data_received_from_client, connected_to_file_server)
        else:
            print "ERROR: Invalid request was sent by the client:\nREQUEST: " + request_type
    return connected_to_file_server


def accept_client_connection(connection, address):
    print "File Server received a new connection from " + str(address)
    connected_to_file_server = True
    while connected_to_file_server:
        data_received_from_client = connection.recv()

        if not data_received_from_client:
            print "No data received..."
            continue
        else:
            connected_to_file_server = handle_client_request(data_received_from_client, connected_to_file_server)
    print "Connection closed..."
    return connected_to_file_server


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

        if not os.path.exists(SERVER_FILE_ROOT):
            print "Creating root directory 'Server/'..."
            os.makedirs(SERVER_FILE_ROOT)
            print "Created root directory 'Server/'..."
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
