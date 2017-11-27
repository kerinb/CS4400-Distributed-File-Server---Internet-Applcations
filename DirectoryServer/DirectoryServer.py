from flask import Flask
from flask_restful import Resource, Api, reqparse

app = Flask(__name__)
api = Api(app)

ONLINE_FILE_SERVERS = {1: ('127.0.0.1', 5001)}
LIST_OF_ALL_FILES = {'test': (1, 1)}

parser = reqparse.RequestParser()
parser.add_argument('file_name')


class DirectoryServer(Resource):
    def get(self):
        file_name = parser.parse_args()['file_name']
        if file_name in LIST_OF_ALL_FILES.keys():
            file_server_id, file_id = LIST_OF_ALL_FILES[file_name]
            file_server_address = ONLINE_FILE_SERVERS[file_server_id] or None
            return {'file_id': file_id, 'file_server_id': file_server_address}


api.add_resource(DirectoryServer, '/')

if __name__ == '__main__':
    app.run(debug=True)
