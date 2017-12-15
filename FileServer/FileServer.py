import sys

import os

import requests
import shutil
from flask import Flask, request
from flask_restful import Resource, Api, reqparse
CURR_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURR_DIR))
import SharedFileFunctions as SFL

app = Flask(__name__)
api = Api(app)

DIRECTORY_SERVER_DETAILS = ('127.0.0.1', 46666)
LOCKING_SERVER_DETAILS = ()


class FileServer(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('file_id')
        self.parser.add_argument('file_server_id')

    def get(self):
        file_id = self.parser.parse_args()['file_id']
        file_server_id = self.parser.parse_args()['file_server_id']
        file_name = 'Server' + str(file_server_id) + '/' + SFL.cast_file_id_to_file_name(file_id)
        print file_name

        with open(file_name, 'r') as read_from_file:
            file_str = read_from_file.read()
            print file_str
        return {'file_str': file_str}

    def post(self):
        file_id = request.get_json()['file_id']
        file_name = request.get_json()['file_name']
        file_server_id = request.get_json()['server_id']
        print "file_id: " + str(file_id)
        edits_to_file = request.get_json()['data']
        print "edits: " + edits_to_file
        file_name = 'Server' + str(file_server_id) + '/' + SFL.cast_file_id_to_file_name(file_id)
        print "file name: " + file_name
        f = open(file_name, 'w')
        f.close()
        f.close()

        with open(file_name, 'r+') as edit_file:
            edit_file.write(edits_to_file)
            print "adding {} to the file...".format(edits_to_file)
            edit_file.close()
            final_edit = open(file_name, 'r').read()
        if os.path.exists(file_name):
            return {'file': True, 'final_edit': final_edit}
        else:
            return {'file': False}


class CreateNewFile(Resource):
    def post(self):
        file_id = request.get_json()['file_id']
        print "file_id: " + str(file_id)
        edits_to_file = request.get_json()['data']
        print "edits: " + edits_to_file
        full_file_path = 'Server' + str(request.get_json()['server_id']) + '/' + str(file_id) + '.txt'
        f = open(full_file_path, 'w')
        f.write('Write your text in here...')
        f.close()
        f.close()
        if os.path.exists(full_file_path):
            print "created file..."
            return {'file': True}
        else:
            return {'file': False}


api.add_resource(FileServer, '/')
api.add_resource(CreateNewFile, '/create_new_file')

if __name__ == '__main__':
    print "'hello world' said the file server"
    print "sys[1]: {}".format(str(sys.argv[1]))
    print "sys[2]: {}".format(str(sys.argv[2]))

    if len(sys.argv) == 3:
        print "registering the file server at 'http://{}:{} with the directory server...".format(str(sys.argv[1]),
                                                                                                 str(sys.argv[2]))
        path = os.getcwd()
        response = requests.post(
            SFL.create_url(DIRECTORY_SERVER_DETAILS[0], DIRECTORY_SERVER_DETAILS[1],
                           "create_new_file_server"),
            json={'new_file_server_ip_address': sys.argv[1], "new_file_server_port_number": sys.argv[2],
                  'path': path}
        )
        print "registered the file server at 'http://{}:{} with the directory server...".format(str(sys.argv[1]),
                                                                                                str(sys.argv[2]))
        if os.path.exists((path + '/' + 'Server' + str(response.json()['file_server_id']))):
            shutil.rmtree((path + '/' + 'Server' + str(response.json()['file_server_id'])))
            os.mkdir(path + '/' + 'Server' + str(response.json()['file_server_id']))
            print "made dir for server"
        app.run(debug=False, host=sys.argv[1], port=int(sys.argv[2]))
    else:
        print "Enter IP and Port Number for this new file server..."
