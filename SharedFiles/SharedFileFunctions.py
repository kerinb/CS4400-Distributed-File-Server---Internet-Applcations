import os

import time
import traceback

import ResponseTypeToClient

FILE_EXTENSION_TXT = ".txt"


def handle_errors(e, message):
    print time.ctime(time.time()) + message
    print e.message
    print traceback.format_exc()


def create_a_new_file(file_name, file_path, root):
    directory = root + file_name
    path = file_path
    if path.endswith("/") or path == "":
        file_to_create = root + file_path + file_name + FILE_EXTENSION_TXT
    else:
        file_to_create = root + file_path + "/" + file_name + FILE_EXTENSION_TXT
    print "File to create: " + file_to_create
    print "In directory: " + directory
    response_to_client = ResponseTypeToClient.ResponseTypeToClient.FILE_NOT_MADE
    if not check_if_directory_exists(file_name, file_path, root) == ResponseTypeToClient.ResponseTypeToClient.FILE_DOES_EXIST:
        make_directory(directory)
        response_to_client = make_file(file_to_create)
    elif check_if_directory_exists(file_name, file_path, root) == ResponseTypeToClient.ResponseTypeToClient.FILE_DOES_EXIST:
        response_to_client = ResponseTypeToClient.ResponseTypeToClient.FILE_ALREADY_EXISTS
    return response_to_client


def check_if_directory_exists(file_name, file_path,  root):
    path = root + file_path
    if path.endswith("/") or path == "":
        full_file_path = root + file_path + file_name + FILE_EXTENSION_TXT
    else:
        full_file_path = root + file_path + "/" + file_name + FILE_EXTENSION_TXT

    print "Client wants to verify the following directory exists:\n" + full_file_path
    response_to_client = ResponseTypeToClient.ResponseTypeToClient.DIRECTORY_NOT_FOUND
    if os.path.exists(path):
        response_to_client = ResponseTypeToClient.ResponseTypeToClient.DIRECTORY_FOUND
        print "The directory exists....\nChecking for file now..."
        if os.path.isfile(full_file_path):
            print "File found in directory!"
            response_to_client = ResponseTypeToClient.ResponseTypeToClient.FILE_DOES_EXIST
        else:
            print "File not found but directory does exist..."
    else:
        print "Directory not found...."
    return response_to_client


def make_file(file_to_create):
    response_to_client = ResponseTypeToClient.ResponseTypeToClient.FILE_NOT_MADE
    if os.path.exists(file_to_create):
        print "Creating file: " + file_to_create + "..."
        f = open(file_to_create, 'w')
        f.write(" ")
        f.close()
        response_to_client = ResponseTypeToClient.ResponseTypeToClient.FILE_MADE
        print "Created file: " + file_to_create + "..."
    return response_to_client


def make_directory(directory_to_create):
    if not os.path.exists(directory_to_create):
        print "Creating root directory 'Server/'..."
        os.makedirs(directory_to_create)
        print "Created root directory 'Server/'..."

