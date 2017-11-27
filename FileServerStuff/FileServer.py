from flask import Flask, request
from flask_restful import Resource, Api
import json

app = Flask(__name__)
api = Api(app)


class FileServer(Resource):
    def get(self):
        with open('test.txt', 'r') as read_from_file:
            file_str = read_from_file.read()
        return file_str

    def post(self):
        edits_to_file = request.form['data']
        print edits_to_file
        with open('test.txt', 'r+') as edit_file:
            edit_file.write(edits_to_file + "\n")
            print "adding {} to the file...".format(edits_to_file)


api.add_resource(FileServer, '/')

if __name__ == '__main__':
    app.run(debug=True)

