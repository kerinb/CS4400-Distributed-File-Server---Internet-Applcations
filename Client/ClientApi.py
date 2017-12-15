import os

import datetime
from sys import platform as _platform
import requests
import sys
import subprocess as sp

CURR_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURR_DIR))
import SharedFileFunctions as Sff
import Cache

TEXT_EDITOR = None
DIRECTORY_SERVER_DETAILS = ('127.0.0.1', 5000)
CACHE_DIR = ''
LIST_OF_UNACCEPTABLE_FILE_NAMES = ['', '\n', ' ', '\t', '   ']
editor = None


def open_text_editor(file_to_read):
    global editor
    print 'platform' + _platform
    if _platform == "linux" or _platform == "linux2":
        print "OS = Linux"
        if editor is None:
            while True:
                editor = raw_input("Enter G to use gedit or N to use Nano\n")
                editor = editor.capitalize()
                if editor in ['N', 'G']:
                    break
        if editor == 'N':
            sp.call(['nano', file_to_read])
        elif editor == 'G':
            os.system('gedit "{0}"'.format(file_to_read))
    elif _platform == "win32" or "win64":
        print "OS = Windows"
        sp.Popen(['notepad.exe', file_to_read]).wait()


def get_client_num():
    try:
        path = os.getcwd()
        response_from_create_client_id = requests.get(
            Sff.create_url(DIRECTORY_SERVER_DETAILS[0], DIRECTORY_SERVER_DETAILS[1], 'create_new_client'),
            json={'client_id': 'Y', 'path': path}
        )
        if response_from_create_client_id is not None:
            return response_from_create_client_id.json()['client_id']
    except Exception as e:
        print "ERROR: error occured when getting client id\n{}".format(e.message)


def read_file_from_server(file_name, cache):
    # 1 - Check the DS, see if the file exist; get file id and file server id, and version
    response_from_directory_server = requests.get(
        Sff.create_url(DIRECTORY_SERVER_DETAILS[0], DIRECTORY_SERVER_DETAILS[1]),
        params={'file_name': file_name}, json={'client_id': cache.client_id}
    )
    not_locked = response_from_directory_server.json()['lock']
    file_server_id = response_from_directory_server.json()['file_server_id']
    print not_locked
    if not_locked and file_server_id is not None:
        file_to_read = "Cache{}/".format(cache.client_id) + file_name + '.txt'
        file_name += '.txt'
        print 'file name client has requested {}'.format(file_name)

        file_id, file_server_id, version, file_server_details = Sff.get_file_details_from_DS(
            response_from_directory_server)

        # update cache if (1) The file is not in the cache (2) the copy in the cache is out of date
        if cache.get_key_to_file(file_name) is None or version > cache.get_version_of_file(file_name):
            # getting file details
            Sff.print_file_details(file_name, file_id, file_server_id, version)

            # check and see if the file details are up to date - if they are ignore, else update cache
            if file_server_details is not None and file_id is not None:
                response_from_directory_server = requests.get(
                    Sff.create_url(file_server_details[0], file_server_details[1]),
                    params={'file_id': file_id, 'file_server_id': file_server_id}
                )
                # update cache
                print "Updating data in the cache..."
                data = response_from_directory_server.json()['file_str']
                print data
                cache.update_data_in_cache(file_to_read, data)

        if not os.path.exists(file_to_read):
            print "ERROR: file {} does not exists in cache or on the server....\n Please enter a" \
                  " valid file name or create a new file...\n".format(file_name)
            return

        open_file = open(file_to_read, 'r')
        dat = open_file.read()
        open_file.close()

        open_text_editor(file_to_read)
        data_to_cache = open(file_to_read, 'r').read()
        if dat is not data_to_cache:  # if the data in the file is updated, update the data in the cache, else continue
            print "adding data to the cache\nLocation {}".format(file_name)
            cache.add_cache_entry(file_name, cache.set_version_of_file(file_name), data_to_cache)
    else:
        print "file is locked come back later..."


def write_file_to_server(file_name, cache):
    file_name_ = file_name + '.txt'
    key_in_cache = cache.get_key_to_file(file_name_)
    is_file_in_cache = cache.get_cache_entry(file_name_)

    if key_in_cache is not None and is_file_in_cache is not None:
        # I have a file in the cache
        response_from_directory_server = requests.get(
            Sff.create_url(DIRECTORY_SERVER_DETAILS[0], DIRECTORY_SERVER_DETAILS[1]),
            params={'file_name': file_name}, json={'client_id': cache.client_id}
        )
        file_id, file_server_id, version, file_server_details = Sff.get_file_details_from_DS(
            response_from_directory_server)
        Sff.print_file_details(file_name, file_id, file_server_id, version)

        # get details for the server my file is on
        print "Trying to obtain a lock on file {} for client {}...".format(file_name, cache.client_id)
        # try to lock file on server
        response_from_locking_server = requests.get(
            Sff.create_url(DIRECTORY_SERVER_DETAILS[0], DIRECTORY_SERVER_DETAILS[1], 'lock_server'),
            json={'client_id': cache.client_id, 'file_id': file_id, 'file_server_id': file_server_id}
        )

        # if I can lock this file...
        if response_from_locking_server.json()['lock']:
            print "Lock has been received for client{} for file: {}".format(cache.client_id, file_name)
            file_to_read = "Cache{}/".format(cache.client_id) + file_name_
            open_file = open(file_to_read, 'r')
            dat = open_file.read()
            open_file.close()

            open_text_editor(file_to_read)
            file_ = open(file_to_read, 'r')
            data_to_send = file_.read()
            file_.close()
            if dat is not data_to_send:  # if the data in the file is updated
                # update the cache
                cache.update_data_in_cache(file_name_, data_to_send)
                # update the file on the server
                requests.post(
                    Sff.create_url(file_server_details[0], file_server_details[1]),
                    json={'file_id': file_id, 'data': data_to_send, 'server_id': file_server_id, 'file_name': file_name,
                          'version': str(datetime.datetime.now())}
                )

            print "unlocking client{} from file .\n".format(cache.client_id, file_id)
            requests.delete(
                Sff.create_url(DIRECTORY_SERVER_DETAILS[0], DIRECTORY_SERVER_DETAILS[1], 'lock_server'),
                json={'client_id': cache.client_id, 'file_id': file_id, 'file_server_id': file_server_id}
            )
            print "File has been unlocked by locking server!"

        elif not response_from_locking_server.json()['lock']:
            print 'The file is locked by another client - Try again later...'
    else:
        print "Data is not in cache/stored locally! - To be able to write the file to a server, first read it and" \
              " make changes"


def verify_file_exists(file_name, cache):
    try:
        response_from_directory_server = requests.get(
            Sff.create_url(DIRECTORY_SERVER_DETAILS[0], DIRECTORY_SERVER_DETAILS[1]),
            params={'file_name': file_name}, json={'client_id': cache.client_id}
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
            print "The file {0} requested by client{1} does not exist on any of our servers...\n". \
                format(file_name, cache.client_id)
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
        response = requests.post(
            Sff.create_url(DIRECTORY_SERVER_DETAILS[0], DIRECTORY_SERVER_DETAILS[1]),
            params={'file_name': file_name}, json={'client_id': cache.client_id}

        )
        open_file = open(file_name + '.txt', 'w')
        open_file.write("First Time file is opened.... Edit me!")
        open_file.close()
        if response.json()['message'] is True:
            print "file {0} has been created for client{1}".format(file_name, cache.client_id)

    except Exception as e:
        print "ERROR: occurred when creating a new file\n{}".format(e.message)


def check_and_remove_file_extension_if_given(file_name):
    # This list is only an example, im not bothered to go through all possible file extensions
    # If anyone wanted, you could declare a global list of file extensions and check against that
    if '.' in file_name:
        file_name = file_name.split('.', 1)[0]
    return file_name


def handle_client_request(client_req, client_id, cache):
    file_name = raw_input("Enter the name of the file without a file extension...\n")
    file_name = check_and_remove_file_extension_if_given(file_name)

    if client_req == '1':
        print "client{} requested to read a file from server....".format(client_id)
        if file_name not in LIST_OF_UNACCEPTABLE_FILE_NAMES:
            read_file_from_server(file_name, cache)
        else:
            print "ERROR: Invalid file name: {}".format(file_name)

    elif client_req == '2':
        print "client{} requested to write changes to server...".format(client_id)
        if file_name not in LIST_OF_UNACCEPTABLE_FILE_NAMES:
            write_file_to_server(file_name, cache)
        else:
            print "ERROR: Invalid file name: {}".format(file_name)

    elif client_req == '3':
        print "client{} requested to verify if a file is on a server...".format(client_id)
        if file_name not in LIST_OF_UNACCEPTABLE_FILE_NAMES:
            verify_file_exists(file_name, cache)
        else:
            print "ERROR: Invalid file name: {}".format(file_name)

    elif client_req == '4':
        print "client{} requested to create a new file on a file server...".format(client_id)
        if file_name not in LIST_OF_UNACCEPTABLE_FILE_NAMES:
            create_new_file(file_name, cache)
        else:
            print "ERROR: Invalid file name: {}".format(file_name)

    elif client_req == 'E' or client_req == 'e':
        print "client{} requested to leave...".format(client_id)
        return False
    return True
