#
# @Author: Breandan Kerin
# @Student Number: 14310166
#

def open_connection_to_file_server():
    print("in 'open_connection_to_file_server' function")


def main():
    running  = True

    # keep client alive
    while running:
        user_request = raw_input("Select an option:\n1: Open connection to file server\nE: Shut down")

        if user_request == "E" or user_request == "e":
            running = False
            print("User chose to shut down server.\n SHUTTING DOWN....")
        else:
            if user_request == "1":
                print("User chose to open connection to file server")
                open_connection_to_file_server()
            else:
                print("ERROR: User Entered invalid request\nENTERED: ", user_request)


main()