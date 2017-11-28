from flask import Flask
from flask_restful import Resource, Api, reqparse

app = Flask(__name__)
api = Api(app)

# file_server_id = IP:PORT_NUM
ONLINE_FILE_SERVERS = {1: ('127.0.0.1', 5001)}
# file_server_id = number of files on file server
LOAD_ON_FILE_SERVER = {}
# file_name = file_server_id: file_id
LIST_OF_ALL_FILES = {'test': (1, 1)}


def get_file_details_if_exist(file_name):
    if file_name in LIST_OF_ALL_FILES.keys():
        file_server_id, file_id = LIST_OF_ALL_FILES[file_name]
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


api.add_resource(DirectoryServer, '/')

if __name__ == '__main__':
    app.run(debug=True)
