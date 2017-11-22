import os

import RequestTypeToFileServer

FILE_EXTENSION_TXT = ".txt"


def check_if_directory_exists(file_path, file_name, root):
    path = root + file_path
    if file_path.endswith("/") or file_path == "":
        full_file_path = root + file_path + file_name + FILE_EXTENSION_TXT
    else:
        full_file_path = root + file_path + "/" + file_name + FILE_EXTENSION_TXT

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
        return response_to_client
    print "Directory not found...."
    return response_to_client
