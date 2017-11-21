#
# @Author: Breandan Kerin
# @Student Number: 14310166
#

import sys

from threading import Thread
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
    def __init__(self, num_of_threads,size_of_queue):
        self.queue = size_of_queue
        self.num_of_threads = num_of_threads
        self.threads = []
        for i in range(0, num_of_threads):
            self.threads.append(MyThread(self.queue))

    def wait_for_thread_to_complete(self):
        self.tasks.join();

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
        # TODO - Implement threading in here somewhere.... each thread corresponds to a user accessing server

        try:
            print "Listening for requests coming from clients..."
            sock.listen(1)
            list_of_sockets = [sock]

            while get_server_running_value():
                read, _, _, = select.select(list_of_sockets, [], [], 0.1)
                for s in read:
                    if s is sock:
                        connection, address = s.accept()
                        # TODO - add task to queue of tasks to be completed by ALL threads

            sock.close()
            print "File Server is shutting down...."

        except Exception as e:
            print "Exception thrown during server initialisation..."
            print e.message
            print traceback.format_exc()
        finally:
            print "Closing socket...."
            sock.close()

    except Exception as e:
        print "Exception thrown during server initialisation..."
        print e.message
        print traceback.format_exc()


main()
