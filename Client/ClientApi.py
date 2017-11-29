import os
import requests
import SharedFileFunctions as FSL

DIRECTORY_SERVER_DETAILS = ('127.0.0.1', 5000)
LOCKING_SERVER_DETAILS = ('127.0.0.1', 12345)
NUM_CLIENTS = 0


def read_file_from_server(file_name, client_id):
    file_server_details, file_id, file_server_id = FSL.find_file_location_if_exists(file_name)

    if file_server_details is not None and file_id is not None:
        print "Trying to obtain a lock on file{} for client{}...".format(file_name, client_id)
        response_from_locking_server = requests.get(
            FSL.create_url(LOCKING_SERVER_DETAILS[0], LOCKING_SERVER_DETAILS[1]),
            json={'client_id': client_id, 'file_id': file_id,
                  'file_server_id': file_server_id}
        )
        if response_from_locking_server.json()['lock']:

            user_request = raw_input("Do you want to sync changes with the file server?\nEnter Y for yes and N for no.")

            if user_request == 'y' or user_request == 'Y':
                write_file_to_server(file_name, client_id)
                print "Syncing changes with file server..."

            elif user_request == 'n' or user_request == 'N':
                print "not syncing changes with file server..."

                response_from_directory_server = requests.get(
                    FSL.create_url(file_server_details[0], file_server_details[1]),
                    params={'file_id': file_id, 'file_server_id': file_server_id}
                )

                open_file = open(file_name + '.txt', 'w')
                open_file.write(response_from_directory_server.json()['file_str'])
                open_file.close()

                print "opening text file in gedit"
                os.system('gedit "{0}"'.format(file_name + '.txt'))
                print "handle locking here... unlock here when implemented...\n"
                response_from_locking_server = requests.get(
                    FSL.create_url(LOCKING_SERVER_DETAILS[0], LOCKING_SERVER_DETAILS[1]),
                    json={'client_id': client_id, 'file_id': file_id,
                          'file_server_id': file_server_id}
                )
                if response_from_locking_server:
                    print "The lock has been removed from file {} buy client {}".format(file_name, client_id)

            else:
                print "ERROR: Invalid request....\n"

        elif not response_from_locking_server.json()['lock']:
            print 'The file is locked on another - Try again later...'

    else:
        print "That file does not exists....\n"


def write_file_to_server(file_to_write, client_id):
    # find out if file is present on file server....
    file_server_details, file_id, file_server_id = FSL.find_file_location_if_exists(file_to_write)
    response_from_locking_server = 0

    if file_server_details is not None and file_id is not None:
        os.system('gedit "{0}"'.format(file_to_write + '.txt'))
        data_to_send = open(file_to_write + '.txt', 'r').read()
        print data_to_send

        file_server_details, file_id, file_server_id = FSL.find_file_location_if_exists(file_to_write)
        print "server details: " + str(file_server_details)
        print "file id: " + str(file_id)
        print "file server id: " + str(file_server_id)

        if file_server_details is not None and file_id is not None:
            response = requests.post(
                FSL.create_url(file_server_details[0], file_server_details[1]),
                json={'file_id': file_id, 'data': data_to_send, 'server_id': file_server_id}

            )
            print response.json()

        else:
            print "handle create file on file server here"

        print "handle locking here... unlock here when implemented...\n"
        response_from_locking_server = 0

    else:
        print "ERROR: file you entered does not exist..."


# TODO - refactor this c0de - it doesnt call the directory server just a function in it file!
def verify_file_exists(file_name, client_id):
    file_server_details, file_id, file_server_id = FSL.find_file_location_if_exists(file_name)
    if file_server_details is not None:
        print "file {0} requested by client {1} is on the file server: 'http://{2}:{3}\nAnd has id:{4}\n". \
            format(file_name, client_id, file_server_details[0], file_server_details[1], file_id)
    else:
        print "The file {0} requested by client{1} does not exist on any of our servers...\n".format(file_name,
                                                                                                     client_id)
    return file_server_details, file_id


def create_new_file(file_name, client_id):
    print "Creating a new file {0} for the client{1}\n".format(file_name, client_id)
    request_to_server = {'file_name': file_name}
    response = requests.post(
        FSL.create_url(DIRECTORY_SERVER_DETAILS[0], DIRECTORY_SERVER_DETAILS[1]),
        params=request_to_server
    )
    print response.json()
    if response.json()['message'] is True:
        print "file {0} has been created for client{1}".format(file_name, client_id)


def handle_client_request(client_req, client_id):
    if client_req == '1':
        print "client{} requested to open file to read in gedit from server....".format(client_id)
        file_name = raw_input("Enter the name of the file you want to read...\n")
        read_file_from_server(file_name, client_id)

    elif client_req == '2':
        print "client{} requested to write changes to server...".format(client_id)
        file_name = raw_input("Enter the name of the file you want to read...\n")
        write_file_to_server(file_name, client_id)

    elif client_req == '3':
        print "client{} requested to verify if a file is on a server...".format(client_id)
        file_name = raw_input("Enter the name of the file you want to verify...\n")
        verify_file_exists(file_name, client_id)

    elif client_req == '4':
        print "client{} requested to create a new file on a file server...".format(client_id)
        file_name = raw_input("Enter the name of the file you want to create...\n")
        create_new_file(file_name, client_id)
