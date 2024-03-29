import os
import requests
import sys
from flask import Flask, request
from flask_restful import Resource, Api

import SharedFileFunctions as SFL

app = Flask(__name__)
api = Api(app)

# Map fileID to Locked(True/False)
# FILES_WITH_LOCK[file_server_id/file_id] = client_id
FILES_WITH_LOCK = {}

DIRECTORY_SERVER_DETAILS = ('127.0.0.1', 5000)


class LockingServer(Resource):

    # get lock on file
    def get(self):
        file_id = request.get_json()['file_id']
        file_server_id = request.get_json()['file_server_id']
        client_id = request.get_json()['client_id']
        print "client {0} has requested a lock on file {1}" \
              " on file server{2}".format(client_id, file_id, file_server_id)
        key = str(file_server_id) + '/' + str(file_id)
        print key

        if key in FILES_WITH_LOCK:
            # This file on this server is already taken by a client...
            print FILES_WITH_LOCK
            print 'file is locked'
            return {'lock': False}

        else:
            FILES_WITH_LOCK[key] = client_id
            print FILES_WITH_LOCK
            print 'file is not locked'
            return {'lock': True}

    def post(self):
        file_id = request.get_json()['file_id']
        file_server_id = request.get_json()['file_server_id']
        client_id = request.get_json()['client_id']
        print "client {0} has requested a lock on file {1}" \
              " on file server{2}".format(client_id, file_id, file_server_id)
        key = str(file_server_id) + '/' + str(file_id)
        print key

        if key in FILES_WITH_LOCK:
            # This file on this server is already taken by a client...
            print FILES_WITH_LOCK
            print 'file is locked'
            return {'lock': False}

        else:
            print FILES_WITH_LOCK
            print 'file is not locked'
            return {'lock': True}

    # remove lock on file
    def delete(self):
        file_id = request.get_json()['file_id']
        file_server_id = request.get_json()['file_server_id']
        client_id = request.get_json()['client_id']
        print "client {0} has requested its lock on file {1}" \
              " on file server{2} to be removed".format(client_id, file_id, file_server_id)

        key = str(file_server_id) + '/' + str(file_id)

        if FILES_WITH_LOCK[key] == client_id:
            del FILES_WITH_LOCK[key]
            return {'lock': False}

        elif FILES_WITH_LOCK[key] is None:
            return {'message': 'There is no lock on this file'}

        else:
            return {'message': 'client does not have lock on this file'}


api.add_resource(LockingServer, '/')

if __name__ == '__main__':
    print "'hello world' said the locking server"
    print "sys[1]: {}".format(str(sys.argv[1]))
    print "sys[2]: {}".format(str(sys.argv[2]))
    if len(sys.argv) == 3:
        print "Registering with Directory Server..."
        response = requests.post(
            SFL.create_url(DIRECTORY_SERVER_DETAILS[0], DIRECTORY_SERVER_DETAILS[1],
                           "lock_server"), json={'address': str(sys.argv[1]), 'port': str(sys.argv[2])}
        )
        if response.json()['response'] is True:
            print "Registered with Directory Server..."
            app.run(debug=False, host=sys.argv[1], port=int(sys.argv[2]))
        else:
            print "ERROR: Could not connect to the directory server..."

