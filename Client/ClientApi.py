import os
import requests
import SharedFileFunctions as FSL

HOME_DIRECTORY = "Client/"


def read_file_from_server():
    file_name = raw_input("Enter the name of the file you want to read...")

    file_server_details, file_id = FSL.find_file_location_if_exists(file_name)
    if file_server_details is not None and file_id is not None:

        response = requests.post(
            FSL.create_url(file_server_details[0], file_server_details[1]),
            data={'data': file_name}
        )

        open_file = open(file_name, 'w')
        open_file.write(response.json()['file'])
        print "opening text file in gedit"
        open_file.close()
        os.system('gedit "{0}"'.format(file_name))
    else:
        print "That file does not exists...."


def write_file_to_server():
    file_to_write = raw_input("Enter the name of the file you want to read...")
    # find out if file is present on file server....
    os.system('gedit "{0}"'.format(file_to_write))

    file_server_details, file_id = FSL.find_file_location_if_exists(file_to_write)

    if file_server_details is not None and file_id is not None:
        response = requests.post(
            FSL.create_url(file_server_details[0], file_server_details[1]),
            data={'data': file_to_write}
        )
        print response.json()['file']
    else:
        print "handle create file on file server here"


def handle_client_request(client_req):
    if client_req == '1':
        print "client requested to open file to read in gedit from server...."
        read_file_from_server()
    elif client_req == '2':
        print "client requested to write changes to server..."
        write_file_to_server()
    return "was in handle client"


def main():
    client_running = True
    while client_running:
        print "in client main!!!"
        client_req = raw_input(
            "select from list below to operate on files..."
            "\n1: open file to read in gedit"
            "\n2: write to file"
        )

        print handle_client_request(client_req)


main()
