import json

import os
import requests

HOME_DIRECTORY = "ClientStuff/"

def read_file_from_server():
    file_to_read = raw_input("Enter the name of the file you want to read...")
    request_to_file_server = {'file_name', file_to_read}
    response = requests.get('http://127.0.0.1:5000')
    full_file_path = HOME_DIRECTORY+file_to_read+".txt"
    open_file = open(file_to_read, 'w')
    open_file.write(response.json())
    print "opening text file in gedit"
    print response.json()
    os.system('gedit "{0}"'.format(full_file_path))



def main():
    print "in client main!!!"
    print "making request to file server for a txt file"
    read_file_from_server()

main()
