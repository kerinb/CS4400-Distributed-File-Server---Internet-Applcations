import os

import datetime
import requests
import SharedFileFunctions as Fsl
import Cache

DIRECTORY_SERVER_DETAILS = ('127.0.0.1', 5000)
LOCKING_SERVER_DETAILS = ('127.0.0.1', 12345)
CACHE_DIR = ''


def get_client_num():
    try:
        path = os.getcwd()
        response_from_create_client_id = requests.get(
            Fsl.create_url(DIRECTORY_SERVER_DETAILS[0], DIRECTORY_SERVER_DETAILS[1], 'create_new_client'),
            json={'client_id': 'Y', 'path': path}
        )
        if response_from_create_client_id is not None:
            return response_from_create_client_id.json()['client_id']
    except Exception as e:
        print "ERROR: error occured when getting client id\n{}".format(e.message)


def read_file_from_server(file_name, cache):
    file_to_read = "Cache{}/".format(cache.client_id) + file_name
    file_name += '.txt'
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
            response_from_directory_server = requests.get(
                Fsl.create_url(file_server_details[0], file_server_details[1]),
                params={'file_id': file_id, 'file_server_id': file_server_id}
            )
            print response_from_directory_server.json()

    elif not os.path.exists(file_name):
        print "ERROR: file {} does not exists in cache or on the server....\n Please enter a valid file name...". \
            format(file_name)

    open_file = open(file_to_read + '.txt', 'w')
    open_file.close()
    os.system('gedit "{0}"'.format(file_to_read + '.txt'))
    data_to_cache = open(file_to_read + '.txt', 'r').read()
    cache.add_cache_entry(file_name, cache.get_version_of_file(file_name), data_to_cache)


def write_file_to_server(file_name, cache):
    key_in_cache = cache.get_key_to_file(file_name)
    is_file_in_cache = cache.get_cache_entry(file_name)
    print key_in_cache
    if key_in_cache is not None and is_file_in_cache is not None:
        # I have a file in the cache
        response_from_directory_server = requests.get(
            Fsl.create_url(DIRECTORY_SERVER_DETAILS[0], DIRECTORY_SERVER_DETAILS[1]),
            params={'file_name': file_name}
        )
        file_server_details = response_from_directory_server.json()['file_server_details']
        file_id = response_from_directory_server.json()['file_id']
        file_server_id = response_from_directory_server.json()['file_server_id']

        # get details for the server my file is on
        print "Trying to obtain a lock on file {} for client {}...".format(file_name, cache.client_id)
        # try to lokc file on server
        response_from_locking_server = requests.get(
            Fsl.create_url(DIRECTORY_SERVER_DETAILS[0], DIRECTORY_SERVER_DETAILS[1], 'lock_server'),
            json={'client_id': cache.client_id, 'file_id': file_id, 'file_server_id': file_server_id}
        )

        # if I can lock this file...
        if response_from_locking_server.json()['lock']:
            file_to_read = "Cache{}/".format(cache.client_id) + file_name

            os.system('gedit "{0}"'.format(file_to_read + '.txt'))  # last chance to edit file before synch w/ server
            data_to_send = open(file_to_read + '.txt', 'r').read()
            print "http {}\nport {}".format(file_server_details[0], file_server_details[1])
            response = requests.post(
                Fsl.create_url(file_server_details[0], file_server_details[1]),
                json={'file_id': file_id, 'data': data_to_send, 'server_id': file_server_id, 'file_name': file_name,
                      'version': str(datetime.datetime.now())}

            )
            print response.json()
            print "unlocking client{} from file .\n".format(cache.client_id, file_id)
            response_from_locking_server = requests.delete(
                Fsl.create_url(DIRECTORY_SERVER_DETAILS[0], DIRECTORY_SERVER_DETAILS[1], 'lock_server'),
                json={'client_id': cache.client_id, 'file_id': file_id,
                      'file_server_id': file_server_id}
            )
            print "unlock response: {}".format(response_from_locking_server)

        elif not response_from_locking_server.json()['lock']:
            print 'The file is locked on another - Try again later...'
    else:
        print "Data is not in cache/stored locally! - To be able to write the file to a server, first read it and" \
              " make changes"


def verify_file_exists(file_name, cache):
    try:
        response_from_directory_server = requests.get(
            Fsl.create_url(DIRECTORY_SERVER_DETAILS[0], DIRECTORY_SERVER_DETAILS[1]),
            params={'file_name': file_name}
        )
        file_server_details = response_from_directory_server.json()['file_server_details']
        file_id = response_from_directory_server.json()['file_id']

        if file_server_details is not None:
            print "file {0} requested by client {1} is on the file server: 'http://{2}:{3}\nAnd has id:{4}\n". \
                format(file_name, cache.client_id, file_server_details[0], file_server_details[1], file_id)
        elif cache.get_key_to_file(file_name) is not None:
            print "file {0} requested by client {1} is in your cache\n". \
                format(file_name, cache.client_id)
        else:
            print "The file {0} requested by client{1} does not exist on any of our servers...\n".format(file_name,
                                                                                                         cache.client_id)
        return file_server_details, file_id
    except Exception as e:
        print "ERROR: occurred when verifying if file exists\n{}".format(e.message)


def create_cache_for_client(client_id, path):
    try:
        cache = Cache.Cache(client_id)
        cache.initialise_cache(path, client_id)
        print "new cache set up for client{}".format(client_id)
        return cache
    except Exception as e:
        print "ERROR: occureed when creating a cache for the client\n{}".format(e.message)


def create_new_file(file_name, cache):
    try:
        print "Creating a new file {0} for the client{1}\n".format(file_name, cache.client_id)
        request_to_server = {'file_name': file_name, 'version': str(datetime.datetime.now())}
        response = requests.post(
            Fsl.create_url(DIRECTORY_SERVER_DETAILS[0], DIRECTORY_SERVER_DETAILS[1]),
            params=request_to_server
        )
        open_file = open(file_name + '.txt', 'w')
        open_file.write("First Time file is opened.... Edit me!")
        open_file.close()
        if response.json()['message'] is True:
            print "file {0} has been created for client{1}".format(file_name, cache.client_id)

    except Exception as e:
        print "ERROR: occurred when creating a new file\n{}".format(e.message)


def handle_client_request(client_req, client_id, cache):
    if client_req == '1':
        print "client{} requested to open file to read in gedit from server....".format(client_id)
        file_name = raw_input("Enter the name of the file you want to read...\n")
        if file_name is not '' or file_name is not None:
            read_file_from_server(file_name, cache)
        else:
            return

    elif client_req == '2':
        print "client{} requested to write changes to server...".format(client_id)
        file_name = raw_input("Enter the name of the file you want to read...\n")
        if file_name is not '':
            write_file_to_server(file_name, cache)
        else:
            return

    elif client_req == '3':
        print "client{} requested to verify if a file is on a server...".format(client_id)
        file_name = raw_input("Enter the name of the file you want to verify...\n")
        if file_name is not '':
            verify_file_exists(file_name, cache)
        else:
            return

    elif client_req == '4':
        print "client{} requested to create a new file on a file server...".format(client_id)
        file_name = raw_input("Enter the name of the file you want to create...\n")
        if file_name is not '':
            create_new_file(file_name, cache)
        else:
            return

    elif client_req == 'E' or client_req == 'e':
        print "client{} requested to leave...".format(client_id)
        return False
    return True
