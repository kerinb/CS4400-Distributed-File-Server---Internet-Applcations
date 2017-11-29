from ClientApi import handle_client_request, get_client_num

DIRECTORY_SERVER_DETAILS = ('127.0.0.1', 5000)
LOCKING_SERVER_DETAILS = ('127.0.0.1', 12345)


def main():
    client_id = get_client_num()
    print "My client ID is {}".format(client_id)
    client_running = True
    while client_running:
        print "in client main!!!"

        client_req = raw_input(
            "select from list below to operate on files..."
            "\n1: Read file from server"
            "\n2: Write to file to server"
            "\n3: Open file/Verify it exists"
            "\n4: Create a new file on a file server"
            "\nE: Exit"
        )
        client_running = handle_client_request(client_req, client_id)


main()
