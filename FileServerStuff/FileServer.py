import sys
from flask import Flask, request
from flask_restful import Resource, Api, reqparse
import SharedFileFunctions as SFL

app = Flask(__name__)
api = Api(app)


class FileServer(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('file_id')

    def get(self):
        file_id = self.parser.parse_args()['file_id']
        file_name = SFL.cast_file_id_to_file_name(file_id)
        print file_name
        with open(file_name, 'r') as read_from_file:
            file_str = read_from_file.read()
            print file_str
        return file_str

    def post(self):
        file_id = request.get_json()['file_id']
        print "file_id: " + str(file_id)
        edits_to_file = request.get_json()['data']
        print "edits: " + edits_to_file
        file_name = SFL.cast_file_id_to_file_name(file_id)
        print "file name: " + file_name

        with open(file_name, 'r+') as edit_file:
            edit_file.write(edits_to_file + "\n")
            print "adding {} to the file...".format(edits_to_file)
            edit_file.close()
            final_edit = open(file_name, 'r').read()
        return {'file': final_edit}


api.add_resource(FileServer, '/')

if __name__ == '__main__':
    app.run(debug=True, port=int(sys.argv[1] or 0))

