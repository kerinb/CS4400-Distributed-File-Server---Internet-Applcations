from flask import Flask
from flask_restful import Resource, Api, reqparse, request

app = Flask(__name__)
api = Api(app)

# file_server_id = IP:PORT_NUM
ONLINE_FILE_SERVERS = {}
# file_server_id = number of files on file server
LOAD_ON_FILE_SERVER = {}
# file_name = file_server_id: file_id
LIST_OF_ALL_FILES = {'test': (1, 0)}


def get_file_details_if_exist(file_name):
    if file_name in LIST_OF_ALL_FILES.keys():
        file_server_id, file_id = LIST_OF_ALL_FILES[file_name]
        print "file_id:" + str(file_id)
        print "server_id" + str(file_server_id)
        file_server_address = ONLINE_FILE_SERVERS[file_server_id] or None
        return file_id, file_server_address


class DirectoryServer(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('file_name')

    def get(self):
        file_name = self.parser.parse_args()['file_name']
        get_file_details_if_exist(file_name)
        file_id, file_server_details = get_file_details_if_exist(file_name)
        return {'file_id': file_id, 'file_server_id': file_server_details}

    def post(self):
        request = self.parser.parse_args()['request']
        if request == 'create':
            file_name = self.parser.parse_args()['file_name']
            file_id, file_server_details = get_file_details_if_exist(file_name)
            if file_id is not None and file_server_details is not None:
                return {'file_id': file_id, 'file_server_id': file_server_details}
            print "creating a file..."
            # come back to this when I have multiple FS's spawned...


class CreateNewFileServer(Resource):
    def post(self):
        global ONLINE_FILE_SERVERS, LOAD_ON_FILE_SERVER
        file_server_details = request.get_json()
        file_server_ip = file_server_details["new_file_server_ip_address"]
        file_server_port = file_server_details["new_file_server_port_number"]
        file_server_id = len(ONLINE_FILE_SERVERS)
        ONLINE_FILE_SERVERS[file_server_id] = (file_server_ip, file_server_port)
        LOAD_ON_FILE_SERVER[file_server_id] = 0
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


api.add_resource(DirectoryServer, '/')
api.add_resource(CreateNewFileServer, '/create_new_file_server')

if __name__ == '__main__':
    app.run(debug=True)
