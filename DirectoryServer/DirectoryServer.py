import os
import requests
from flask import Flask
from flask_restful import Resource, Api, reqparse, request
import SharedFileFunctions as SFL

app = Flask(__name__)
api = Api(app)

# file_server_id = IP:PORT_NUM
ONLINE_FILE_SERVERS = {}
# file_server_id = number of files on file server
LOAD_ON_FILE_SERVER = {}
# file_name = file_server_id: file_id
LIST_OF_ALL_FILES_BY_NAME = {}
# file_name = file_server_id: file_name
LIST_OF_ALL_FILES_BY_ID = {}
# file_server_port = file_server_id
ONLINE_SERVER_BY_PORT = {}

LOCKING_SERVER_DETAILS = ('127.0.0.1', 12345)


def get_file_details_if_exist(file_name):
    if file_name in LIST_OF_ALL_FILES_BY_NAME.keys():
        print "file name: " + str(file_name)
        file_id, file_server_id = LIST_OF_ALL_FILES_BY_NAME[str(file_name)]
        print ONLINE_FILE_SERVERS
        file_server_address = ONLINE_FILE_SERVERS[file_server_id]
        print str(file_server_id)
        return file_id, file_server_address, file_server_id

    else:
        return None, None, None


def find_least_loaded_file_server():
    file_server_id = min(LOAD_ON_FILE_SERVER, key=LOAD_ON_FILE_SERVER.get)
    LOAD_ON_FILE_SERVER[file_server_id] += 1
    return file_server_id


class DirectoryServer(Resource):

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('file_name')

    # returns the location and file number for desired file
    def get(self):
        file_name = self.parser.parse_args()['file_name']
        print 'file name:' + file_name
        get_file_details_if_exist(file_name)
        file_id, file_server_details, file_server_id = get_file_details_if_exist(file_name)
        return {'file_id': file_id, 'file_server_details': file_server_details, 'file_server_id': file_server_id}

    def post(self):
        file_name = self.parser.parse_args()['file_name']
        file_id, file_server_details, file_server_id = get_file_details_if_exist(file_name)
        if file_name in LIST_OF_ALL_FILES_BY_NAME:
            return {'file_id': file_id, 'file_server_id': file_server_details,
                    'message': 'N'}
        print "creating a file..."

        file_id = len(LIST_OF_ALL_FILES_BY_NAME)
        file_server_id = find_least_loaded_file_server()
        LIST_OF_ALL_FILES_BY_NAME[file_name] = (file_id, file_server_id)
        LIST_OF_ALL_FILES_BY_ID[file_id] = (file_server_id, file_name)
        ip = ONLINE_FILE_SERVERS[file_server_id][0]
        port = ONLINE_FILE_SERVERS[file_server_id][1]

        response = requests.post(
            SFL.create_url(ip, port, 'create_new_file'),
            json={'file_id': file_id, 'data': '', 'server_id': file_server_id}
        )
        print response.json()
        # return Y to let client now file is created
        return {'file_id': file_id, 'file_server_id': file_server_id,
                'message': 'Y', 'server_details': ONLINE_FILE_SERVERS[file_server_id]}


class CreateNewFileServer(Resource):
    def post(self):
        global ONLINE_FILE_SERVERS, LOAD_ON_FILE_SERVER
        file_server_details = request.get_json()
        file_server_ip = file_server_details["new_file_server_ip_address"]
        file_server_port = file_server_details["new_file_server_port_number"]
        path = file_server_details["path"]
        file_server_id = len(ONLINE_FILE_SERVERS)
        ONLINE_FILE_SERVERS[file_server_id] = (file_server_ip, file_server_port)
        ONLINE_SERVER_BY_PORT[file_server_port] = (file_server_id, file_server_ip)

        path += '/' + str(file_server_id)
        if not os.path.isfile(os.path.join(path)):
            os.mkdir(path)

        num_files = len([f for f in os.listdir(path)
                         if os.path.isfile(os.path.join(path, f))])
        LOAD_ON_FILE_SERVER[file_server_id] = num_files
        print "Just created a new file server...\n" \
              "FILE_SERVER_IP='{0}'\n" \
              "FILE_SERVER_PORT='{1}'\n" \
              "FILE_SERVER_ID='{2}'\n".format(
               file_server_ip, file_server_port, file_server_id
        )
        print "----------------------------------\n" \
              "hello world from file server {}...\n" \
              "----------------------------------\n".format(file_server_id)
        print "\n\n" \
              "Information on the current state of the directory server...\n" \
              "Number of File Servers currently online: {0}\n" \
              "Load on the file servers: {1}".format(ONLINE_FILE_SERVERS, LOAD_ON_FILE_SERVER)
        return {'file_Server_id': file_server_id}


api.add_resource(DirectoryServer, '/')
api.add_resource(CreateNewFileServer, '/create_new_file_server')

if __name__ == '__main__':
    app.run(debug=True)
