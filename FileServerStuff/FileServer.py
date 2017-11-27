import sys
from flask import Flask, request
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)


class FileServer(Resource):
    def get(self):
        with open('test', 'r') as read_from_file:
            file_str = read_from_file.read()
        return file_str

    def post(self):
        edits_to_file = request.form['data']
        print edits_to_file
        with open('test', 'r+') as edit_file:
            edit_file.write(edits_to_file + "\n")
            print "adding {} to the file...".format(edits_to_file)
            edit_file.close()
            final_edit = open('test', 'r').read()
        return {'file': final_edit}


api.add_resource(FileServer, '/')

if __name__ == '__main__':
    app.run(debug=True, port=int(sys.argv[1] or 0))

