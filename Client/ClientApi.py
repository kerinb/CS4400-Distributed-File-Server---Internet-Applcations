import os
import requests
import SharedFileFunctions as Fsl
import Cache

DIRECTORY_SERVER_DETAILS = ('127.0.0.1', 5000)
LOCKING_SERVER_DETAILS = ('127.0.0.1', 12345)
CACHE_DIR = ''


def get_client_num():
    path = os.getcwd()
    response_from_create_client_id = requests.get(
        Fsl.create_url(DIRECTORY_SERVER_DETAILS[0], DIRECTORY_SERVER_DETAILS[1], 'create_new_client'),
        json={'client_id': 'Y', 'path': path}
    )
    if response_from_create_client_id is not None:
        return response_from_create_client_id.json()['client_id']


# TODO - I want to clean this up, and refactor this some what
def read_file_from_server(file_name, cache):
    # ask directory_server for the current version number for the file
    # check that against my cache - if the same, read from cache, else update cache and read from server
    file_to_read = "Cache{}/".format(cache.client_id)

    response_from_directory_server = requests.get(
        Fsl.create_url(DIRECTORY_SERVER_DETAILS[0], DIRECTORY_SERVER_DETAILS[1]),
        params={'file_name': file_name}
    )

    # update cache if its needed
    if cache.get_key_to_file(file_name) is None or response_from_directory_server.json()['version'] > \
            cache.get_version_of_file(file_name):
        file_server_details = response_from_directory_server.json()['file_server_details']
        file_id = response_from_directory_server.json()['file_id']
        file_server_id = response_from_directory_server.json()['file_server_id']
        # check and see if the file details are up to date - if they are ignore, else update cache
        if file_server_details is not None and file_id is not None:

            print "not syncing changes with file server..."
            response_from_directory_server = requests.get(
                Fsl.create_url(file_server_details[0], file_server_details[1]),
                params={'file_id': file_id, 'file_server_id': file_server_id}
            )
        cache.update_data_in_cache(file_name, response_from_directory_server.json()['file_str'])

    else:
        print "file does not exist..."
        return

    open_file = open(file_to_read + '.txt', 'w')
    open_file.close()
    os.system('gedit "{0}"'.format(file_to_read + '.txt'))


# TODO - I want to clean this up, and refactor this some what
def write_file_to_server(file_name, client_id, cache):
    # find out if file is present on file server....
    file_server_details, file_id, file_server_id = Fsl.find_file_location_if_exists(file_name)
    print "Trying to obtain a lock on file {} for client {}...".format(file_name, client_id)

    response_from_locking_server = requests.get(
        Fsl.create_url(LOCKING_SERVER_DETAILS[0], LOCKING_SERVER_DETAILS[1]),
        json={'client_id': client_id, 'file_id': file_id, 'file_server_id': file_server_id}
    )

    if response_from_locking_server.json()['lock']:

        if file_server_details is not None and file_id is not None:
            os.system('gedit "{0}"'.format(file_name + '.txt'))
            data_to_send = open(file_name + '.txt', 'r').read()
            print data_to_send
            print file_id

            if file_server_details is not None and file_id is not None:
                response = requests.post(
                    Fsl.create_url(file_server_details[0], file_server_details[1]),
                    json={'file_id': file_id, 'data': data_to_send, 'server_id': file_server_id, 'file_name': file_name}

                )
                print response.json()

            else:
                print "handle create file on file server here"

            print "unlocking client{} from file .\n".format(client_id, file_id)
            response_from_locking_server = requests.delete(
                Fsl.create_url(LOCKING_SERVER_DETAILS[0], LOCKING_SERVER_DETAILS[1]),
                json={'client_id': client_id, 'file_id': file_id,
                      'file_server_id': file_server_id}
            )
            print "unlock response: {}".format(response_from_locking_server)

            if response_from_locking_server:
                print "The lock has been removed from file {} buy client {}".format(file_name, client_id)

        else:
            print "ERROR: file you entered does not exist..."

    elif not response_from_locking_server.json()['lock']:
        print 'The file is locked on another - Try again later...'


# TODO - refactor this c0de - it doesnt call the directory server just a function in it file!
def verify_file_exists(file_name, client_id, cache):
    file_server_details, file_id, file_server_id = Fsl.find_file_location_if_exists(file_name)
    if file_server_details is not None:
        print "file {0} requested by client {1} is on the file server: 'http://{2}:{3}\nAnd has id:{4}\n". \
            format(file_name, client_id, file_server_details[0], file_server_details[1], file_id)
    else:
        print "The file {0} requested by client{1} does not exist on any of our servers...\n".format(file_name,
                                                                                                     client_id)
    return file_server_details, file_id


def create_cache_for_client(client_id, path):
    cache = Cache.Cache(client_id)
    cache.initialise_cache(path, client_id)
    print "new cache set up for client{}".format(client_id)
    return cache


def create_new_file(file_name, client_id, cache):
    print "Creating a new file {0} for the client{1}\n".format(file_name, client_id)
    f = open('Client' + str(client_id) + '/' + file_name, 'w')
    f.close()
    request_to_server = {'file_name': file_name, 'version': 1}
    response = requests.post(
        Fsl.create_url(DIRECTORY_SERVER_DETAILS[0], DIRECTORY_SERVER_DETAILS[1]),
        params=request_to_server
    )
    print response.json()
    if response.json()['message'] is True:
        print "file {0} has been created for client{1}".format(file_name, client_id)


def handle_client_request(client_req, client_id, cache):

    if client_req == '1':
        print "client{} requested to open file to read in gedit from server....".format(client_id)
        file_name = raw_input("Enter the name of the file you want to read...\n")
        read_file_from_server(file_name, client_id, cache)

    elif client_req == '2':
        print "client{} requested to write changes to server...".format(client_id)
        file_name = raw_input("Enter the name of the file you want to read...\n")
        write_file_to_server(file_name, client_id, cache)

    elif client_req == '3':
        print "client{} requested to verify if a file is on a server...".format(client_id)
        file_name = raw_input("Enter the name of the file you want to verify...\n")
        verify_file_exists(file_name, client_id, cache)

    elif client_req == '4':
        print "client{} requested to create a new file on a file server...".format(client_id)
        file_name = raw_input("Enter the name of the file you want to create...\n")
        create_new_file(file_name, client_id, cache)

    elif client_req == 'E' or client_req == 'e':
        print "client{} requested to leave...".format(client_id)
        return False
    return True
