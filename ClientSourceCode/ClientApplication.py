#
# @Author: Breandan Kerin
# @Student Number: 14310166
#

import ClientProxyLibrary as CPL

from socket import gethostbyname, getfqdn

DEFAULT_PORT_NUMBER = 45678
DEFAULT_HOST_NAME = gethostbyname(getfqdn())
CLIENT_FILE_ROOT = 'Client/'


def main():
    running = True
    print "THIS IS THE CLIENT APPLICATION!!!"

    while running:
        CPL.make_directory(CLIENT_FILE_ROOT)
        user_request = raw_input("Select an option:\n1: Open connection to file server\nE: Shut down\n")

        if user_request == "E" or user_request == "e":
            running = False
            print "User chose to shut down server.\n SHUTTING DOWN...."
        else:
            if user_request == "1":
                print "Opening connection to file server"
                CPL.create_and_maintain_connection_to_server(DEFAULT_HOST_NAME, DEFAULT_PORT_NUMBER)
            else:
                print "ERROR: User Entered invalid request\nENTERED: ", user_request


main()
