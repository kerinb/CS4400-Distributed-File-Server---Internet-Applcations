import os
import requests
import sys
from flask import Flask
from flask_restful import Resource, Api, reqparse, request
CURR_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURR_DIR))
import SharedFileFunctions as SFL

app = Flask(__name__)
api = Api(app)

# file_server_id = IP:PORT_NUM
ONLINE_FILE_SERVERS = {}
# file_server_id = number of files on file server
LOAD_ON_FILE_SERVER = {}
# file_name = file_server_id: file_id: file_version
LIST_OF_ALL_FILES_BY_NAME = {}
# file_server_port = file_server_id
ONLINE_SERVER_BY_PORT = {}
# number of clients attached to directory
NUM_CLIENTS = 0
# LIST_OF_FILE_VERSIONS[file_id] = {}
LIST_OF_FILE_VERSIONS = {}
LOCK_SERVER_ON = False

LOCKING_SERVER_DETAILS = ('127.0.0.1', 12345)


def get_file_details_if_exist(file_name):
    print LIST_OF_ALL_FILES_BY_NAME
    if file_name in LIST_OF_ALL_FILES_BY_NAME.keys():
        print "file name: " + str(file_name)
        file_id, file_server_id = LIST_OF_ALL_FILES_BY_NAME[file_name]
        print 'file ' + str(file_id) + 'server ' + str(file_server_id)
        print ONLINE_FILE_SERVERS
        file_server_address = ONLINE_FILE_SERVERS[file_server_id]
        version = LIST_OF_FILE_VERSIONS[file_name]
        print str(file_server_id)
        return file_id, file_server_address, file_server_id, version
    else:
        return None, None, None, None


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
        client_id = request.get_json()['client_id']
        print 'file name:' + file_name
        file_id, file_server_details, file_server_id, version = get_file_details_if_exist(file_name)

        resp = requests.post(
            SFL.create_url(LOCKING_SERVER_DETAILS[0], LOCKING_SERVER_DETAILS[1]),
            json={'client_id': client_id, 'file_id': file_id, 'file_server_id': file_server_id}
        )
        foo = {'lock': resp.json()['lock']}
        print foo
        requests.post(
            SFL.create_url(LOCKING_SERVER_DETAILS[0], LOCKING_SERVER_DETAILS[1]),
            json={'client_id': client_id, 'file_id': file_id, 'file_server_id': file_server_id}
        )
        print foo
        if not resp.json()['lock']:
            return {'file_id': None, 'file_server_details': None, 'file_server_id': None,
                    'version': None, 'lock': foo}
        return {'file_id': file_id, 'file_server_details': file_server_details, 'file_server_id': file_server_id,
                'version': version, 'lock': foo}

    def post(self):
        file_name = self.parser.parse_args()['file_name']
        file_id, file_server_details, file_server_id, version = get_file_details_if_exist(file_name)
        if file_name in LIST_OF_ALL_FILES_BY_NAME:
            return {'file_id': file_id, 'file_server_id': file_server_details,
                    'message': False, 'version': version}
        print "creating a file..."

        file_id = len(LIST_OF_ALL_FILES_BY_NAME)
        file_server_id = find_least_loaded_file_server()
        LIST_OF_FILE_VERSIONS[file_name] = version
        LIST_OF_ALL_FILES_BY_NAME[file_name] = (file_id, file_server_id)
        ip = ONLINE_FILE_SERVERS[file_server_id][0]
        port = ONLINE_FILE_SERVERS[file_server_id][1]

        response = requests.post(
            SFL.create_url(ip, port, 'create_new_file'),
            json={'file_id': file_id, 'file_name': file_name, 'data': '', 'server_id': file_server_id}
        )
        print response.json()
        # return Y to let client now file is created
        return {'file_id': file_id, 'file_server_id': file_server_id,
                'message': True, 'server_details': ONLINE_FILE_SERVERS[file_server_id]}


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
        num_files = 0

        path += '/' + 'Server' + str(file_server_id)
        print "creating folder: " + path
        if not os.path.exists(path):
            os.mkdir(path)
            print "made dir for server"
        else:
            print "folder already exists - getting listing in folder...."
            for f in os.listdir(path):
                num_files += 1
                print f
                LIST_OF_ALL_FILES_BY_NAME[f.replace(" ", "").rstrip(f[-5:])] = {file_server_id, f}

        print num_files
        LOAD_ON_FILE_SERVER[file_server_id] = num_files
        print "Just created a new file server...\n" \
              "FILE_SERVER_IP='{0}'\nFILE_SERVER_PORT='{1}'\nFILE_SERVER_ID='{2}'\n".format(
               file_server_ip, file_server_port, file_server_id
        )
        print "----------------------------------\n" \
              "hello world from file server {}...\n" \
              "----------------------------------\n".format(file_server_id)
        print "\n\n" \
              "Information on the current state of the directory server...\nNumber of File Servers currently online: " \
              "{0}\nLoad on the file servers: {1}".format(ONLINE_FILE_SERVERS, LOAD_ON_FILE_SERVER)
        return {'file_server_id': file_server_id}


class CreateNewClient(Resource):
    def get(self):
        global NUM_CLIENTS

        request_from_client = request.get_json()['client_id']
        path = request.get_json()['path']
        if request_from_client == 'Y':
            resp = {'client_id': NUM_CLIENTS}
            if os.path.exists((path + '/' + str(NUM_CLIENTS))):
                os.mkdir(path + '/' + 'Client' + str(NUM_CLIENTS) + '.txt')
                print "made dir for client{}".format(NUM_CLIENTS)
            NUM_CLIENTS += 1
            return resp
        else:
            return {'client_id': None}


class CommsWithLockingServer(Resource):
    def get(self):
        global LOCK_SERVER_ON
        print "looking for lock on a file"
        message_to_locking_server = request.get_json()
        client_id = message_to_locking_server['client_id']
        file_id = message_to_locking_server['file_id']
        file_server_id = message_to_locking_server['file_server_id']
        if LOCK_SERVER_ON is True:
            resp = requests.get(
                SFL.create_url(LOCKING_SERVER_DETAILS[0], LOCKING_SERVER_DETAILS[1]),
                json={'client_id': client_id, 'file_id': file_id, 'file_server_id': file_server_id}
            )
            return {'lock': resp.json()['lock']}
        else:
            return {'lock': False, 'message': "Lock Server is not online"}

    def delete(self):
        global LOCK_SERVER_ON
        message_to_locking_server = request.get_json()
        client_id = message_to_locking_server['client_id']
        file_id = message_to_locking_server['file_id']
        file_server_id = message_to_locking_server['file_server_id']
        if LOCK_SERVER_ON is True:
            resp = requests.delete(
                SFL.create_url(LOCKING_SERVER_DETAILS[0], LOCKING_SERVER_DETAILS[1]),
                json={'client_id': client_id, 'file_id': file_id, 'file_server_id': file_server_id}
            )
            return {'lock': resp.json()['lock']}
        else:
            return {'lock': False, 'message': "Lock Server is not online"}

    def post(self):
        global LOCKING_SERVER_DETAILS
        message = request.get_json()
        address = message['address']
        port = message['port']
        LOCKING_SERVER_DETAILS = (address, port)
        print "Received Registration request from a Locking Server...."
        global LOCK_SERVER_ON
        LOCK_SERVER_ON = True
        print "Acknowledging Locking Servers Registration request...\n"
        return {'response': LOCK_SERVER_ON}


api.add_resource(DirectoryServer, '/')
api.add_resource(CreateNewFileServer, '/create_new_file_server')
api.add_resource(CreateNewClient, '/create_new_client')
api.add_resource(CommsWithLockingServer, '/lock_server')

if __name__ == '__main__':
    print "'hello world' said the directory server"
    print "sys[1]: {}".format(str(sys.argv[1]))
    print "sys[2]: {}".format(str(sys.argv[2]))
    if len(sys.argv) == 3:
        if os.environ.get("WERKZEUG_RUN_MAIN") == 'true':
            pass
        app.run(debug=False, host=sys.argv[1], port=int(sys.argv[2]))
        # except Exception as e:
        # print "ERROR: occurred when initialising the directory server\nMESSAGE: {}".format(e.message)
