from flask import Flask, request
from flask_restful import Resource, Api
import json

app = Flask(__name__)
api = Api(app)


class FileServer(Resource):
    def get(self):
        with open('test.txt', 'r') as file:
            file_str = file.read()

        return file_str

    def put(self):
        edits_to_file = request.form['data']
        with open('test.txt', 'w') as edit_file:
            print edit_file.write(edits_to_file + "\n")


api.add_resource(FileServer, '/')

if __name__ == '__main__':
    app.run(debug=True)

