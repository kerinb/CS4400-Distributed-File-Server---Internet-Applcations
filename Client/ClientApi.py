import os
import requests
import SharedFileFunctions as FSL

DIRECTORY_SERVER_IP = '127.0.0.1'
DIRECTORY_SERVER_PORT_NUMBER = 5000
HOME_DIRECTORY = "Client/"


def read_file_from_server(file_name):

    file_server_details, file_id = FSL.find_file_location_if_exists(file_name)

    if file_server_details is not None and file_id is not None:
        request_to_server = {'file_id': file_id, 'request': 'read'}
        response = requests.get(
            FSL.create_url(file_server_details[0], file_server_details[1]),
            params=request_to_server
        )
        open_file = open(file_name+'.txt', 'w')
        open_file.write(response.json())
        open_file.close()

        print "opening text file in gedit"
        os.system('gedit "{0}"'.format(file_name+'.txt'))
        user_request = raw_input("Do you want to synch changes with the file server?"
                                 "\nEnter Y for yes and N for no...")
        if user_request == 'y' or user_request == 'Y':
            print "Synching changes with file server..."
            write_file_to_server(file_name)
        elif user_request == 'n' or user_request == 'N':
            print "not synching changes with file server..."
        else:
            print "ERROR: Invalid request...."
    else:
        print "That file does not exists...."
    print "handle locking here... unlock here when implemented...\n"


def write_file_to_server(file_to_write):
    # find out if file is present on file server....
    os.system('gedit "{0}"'.format(file_to_write+'.txt'))
    data_to_send = open(file_to_write+'.txt', 'r').read()

    file_server_details, file_id = FSL.find_file_location_if_exists(file_to_write)

    if file_server_details is not None and file_id is not None:
        response = requests.post(
            FSL.create_url(file_server_details[0], file_server_details[1]),
            json={'file_id': file_id, 'data': data_to_send}

        )
        print response.json()
    else:
        print "handle create file on file server here"
    print "handle locking here... unlock here when implemented...\n"


def verify_file_exists(file_name):
    file_server_details, file_id = FSL.find_file_location_if_exists(file_name)
    if file_server_details is not None:
        print "The file you have requested is on the file server: 'http://{}:{}\nAnd has id:{}\n".\
            format(file_server_details[0], file_server_details[1], file_id)
    else:
        print "This file does not exist on any of our servers...\n"
    return file_server_details, file_id


def create_new_file(file_name):
    file_server_details, file_id = verify_file_exists(file_name)
    if file_server_details is None:
        print "file does not exists...\nWill create file now..."
        request_to_server = {'file_name': file_name, 'request': 'create'}
        response = requests.post(
            FSL.create_url(DIRECTORY_SERVER_IP, DIRECTORY_SERVER_PORT_NUMBER),
            params=request_to_server
        )
        print response.json()


def handle_client_request(client_req):
    if client_req == '1':
        print "client requested to open file to read in gedit from server...."
        file_name = raw_input("Enter the name of the file you want to read...")
        read_file_from_server(file_name)
    elif client_req == '2':
        print "client requested to write changes to server..."#
        file_name = raw_input("Enter the name of the file you want to read...")
        write_file_to_server(file_name)
    elif client_req == '3':
        print "client requested to verify if a file is on a server..."  #
        file_name = raw_input("Enter the name of the file you want to verify...")
        verify_file_exists(file_name)
    elif client_req == '4':
        print "client requested to create a new file on a file server..."  #
        file_name = raw_input("Enter the name of the file you want to create...")
        create_new_file(file_name)
    return "was in handle client"


def main():
    client_running = True
    while client_running:
        print "in client main!!!"

        client_req = raw_input(
            "select from list below to operate on files..."
            "\n1: Open file to read in gedit"
            "\n2: Write to file"
            "\n3: Verify that a file exists"
            "\n4: Create a new file on a file server"
        )

        print handle_client_request(client_req)


main()
