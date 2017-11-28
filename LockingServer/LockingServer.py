from flask import Flask, request
from flask_restful import Resource, Api, abort

app = Flask(__name__)
api = Api(app)

# Map fileID to Locked(True/False)
# FILES_WITH_LOCK[file_server_id/file_id] = client_id
FILES_WITH_LOCK = {}


class LockingServer(Resource):
    def put(self):
        file_id = request.get_json()['file_id']
        file_server_id = request.get_json()['file_id']
        client_id = request.get_json()['file_id']
        print "client {0} has requested a lock on file {1} on file server{2}".format(client_id, file_id, file_server_id)
        key = str(file_server_id) + '/' + str(file_id)
        if key in FILES_WITH_LOCK:
            # This file on this server is already taken by a client...
            return {'lock': False}
        else:
            FILES_WITH_LOCK[key] = client_id
            return {'lock': True}

    def remove(self):
        file_id = request.get_json()['file_id']
        file_server_id = request.get_json()['file_id']
        client_id = request.get_json()['file_id']
        print "client {0} has requested its lock on file {1} on file server{2} to be removed".format(client_id,
                                                                                                     file_id,
                                                                                                     file_server_id)
        key = str(file_server_id) + '/' + str(file_id)
        if FILES_WITH_LOCK[key] == client_id:
            del FILES_WITH_LOCK[key]
            return {'lock': False}
        elif FILES_WITH_LOCK[key] is None:
            return {'message': 'There is no lock on this file'}
        else:
            return {'message': 'client does not have lock on this file'}


api.add_resource(LockingServer, '/<int:file_id>')

if __name__ == '__main__':
    app.run(debug=True, port=12345)
