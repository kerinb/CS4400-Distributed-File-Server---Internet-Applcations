from ClientApi import handle_client_request

DIRECTORY_SERVER_DETAILS = ('127.0.0.1', 5000)
LOCKING_SERVER_DETAILS = ('127.0.0.1', 12345)
NUM_CLIENTS = 0


def main():
    global NUM_CLIENTS
    NUM_CLIENTS += NUM_CLIENTS
    client_id = NUM_CLIENTS
    print "My client ID is {}".format(client_id)
    client_running = True
    while client_running:
        print "in client main!!!"

        client_req = raw_input(
            "select from list below to operate on files..."
            "\n1: Open file to read in gedit from server"
            "\n2: Write to file"
            "\n3: Verify that a file exists"
            "\n4: Create a new file on a file server\n"
        )
        handle_client_request(client_req, client_id)


main()
