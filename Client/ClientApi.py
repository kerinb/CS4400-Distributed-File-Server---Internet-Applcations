import json

import os
import requests
import SharedFileFunctions

HOME_DIRECTORY = "Client/"


def read_file_from_server():
    file_to_read = raw_input("Enter the name of the file you want to read...")
    request_to_file_server = {'file_name', file_to_read}
    response = requests.get('http://127.0.0.1:5000')
    full_file_path = file_to_read + ".txt"
    open_file = open(file_to_read, 'w')
    open_file.write(response.json())
    print "opening text file in gedit"
    print response.json()
    os.system('gedit "{0}"'.format(full_file_path))


def write_file_to_server():
    file_to_write = raw_input("Enter the name of the file you want to read...")
    # find out if file is present on file server.....
    response = SharedFileFunctions.get_file_id_num_if_exists(file_to_write)
    print response


def handle_client_request(client_req):
    if client_req == 1:
        print "client requested to open file to read in gedit from server...."
        read_file_from_server()
    elif client_req == 2:
        print "client requested to write changes to server..."
        write_file_to_server()


def main():
    client_running = True
    while client_running:
        print "in client main!!!"
        client_req = raw_input("select from list below to operate on files..."
                  "\n1: open file to read in gedit"
                  "\n2: write to file")
        handle_client_request(client_req)
        print "making request to file server for a txt file"
        read_file_from_server()


main()
