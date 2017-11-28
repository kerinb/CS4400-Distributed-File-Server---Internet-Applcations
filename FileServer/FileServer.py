import sys

import os

import requests
from flask import Flask, request
from flask_restful import Resource, Api, reqparse
import SharedFileFunctions as SFL

app = Flask(__name__)
api = Api(app)

DIRECTORY_SERVER_DETAILS = ('127.0.0.1', 5000)


class FileServer(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('file_id')
        self.parser.add_argument('file_server_id')

    def get(self):
        file_id = self.parser.parse_args()['file_id']
        file_server_id = self.parser.parse_args()['file_server_id']
        file_name = str(file_server_id) + '/' + SFL.cast_file_id_to_file_name(file_id)
        print file_name
        with open(file_name, 'r') as read_from_file:
            file_str = read_from_file.read()
            print file_str
        return {'file_str': file_str}

    def post(self):
        file_id = request.get_json()['file_id']
        file_server_id = request.get_json()['server_id']
        print "file_id: " + str(file_id)
        edits_to_file = request.get_json()['data']
        print "edits: " + edits_to_file
        file_name = str(file_server_id) + '/' + SFL.cast_file_id_to_file_name(file_id)
        print "file name: " + file_name
        f = open(file_name, 'w')
        f.close()
        f.close()

        with open(file_name, 'r+') as edit_file:
            edit_file.write(edits_to_file)
            print "adding {} to the file...".format(edits_to_file)
            edit_file.close()
            final_edit = open(file_name, 'r').read()
        return {'file': final_edit}


class CreateNewFile(Resource):
    def post(self):
        file_id = request.get_json()['file_id']
        print "file_id: " + str(file_id)
        edits_to_file = request.get_json()['data']
        print "edits: " + edits_to_file
        file_name = SFL.cast_file_id_to_file_name(file_id)
        print "file name: " + file_name
        full_file_path = str(request.get_json()['server_id'])+'/'+file_name
        f = open(full_file_path, 'w')
        f.write('Write your text in here...')
        f.close()
        f.close()
        print "created file..."
        return {'file_id': file_id, 'message': 'created'}


api.add_resource(FileServer, '/')
api.add_resource(CreateNewFile, '/create_new_file')

if __name__ == '__main__':
    print "hello world"
    if len(sys.argv) == 3:
        if os.environ.get("WERKZEUG_RUN_MAIN") == 'true':
            print "instantiating a new instance of the file server..."
            path = os.getcwd()
            response = requests.post(
                SFL.create_url(DIRECTORY_SERVER_DETAILS[0], DIRECTORY_SERVER_DETAILS[1],
                               "create_new_file_server"),
                json={'new_file_server_ip_address': sys.argv[1], "new_file_server_port_number": sys.argv[2],
                      'path': path}
            )
            if not os.path.exists(str(response.json()['file_Server_id'])+'/'):
                print 'making directory for this machine....'
                os.mkdir(str(response.json()['file_Server_id'])+'/')
        app.run(debug=True, host=sys.argv[1], port=int(sys.argv[2]))
    else:
        print "Enter IP and Port Number for this new file server..."
