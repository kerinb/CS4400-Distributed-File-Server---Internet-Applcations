import os

import shutil

from ClientApi import handle_client_request, get_client_num, create_cache_for_client


def main():
    client_id = get_client_num()
    print "'Hello World' said client{}".format(client_id)

    print "Creating cache{} now...".format(client_id)
    cache_path = "Cache{}".format(client_id) + '/'
    if os.path.exists(cache_path):
        shutil.rmtree(cache_path)
        os.mkdir(cache_path)
        print "made dir for cache{}".format(client_id)

    cache = create_cache_for_client(client_id, cache_path)
    client_running = True
    while client_running:
        client_req = raw_input(
            "select an option from the list below to operate on your files..."
            "\n1: Read file from server"
            "\n2: Write to file to server"
            "\n3: Open file/Verify it exists"
            "\n4: Create a new file on a file server"
            "\nE: Exit\n"
        )
        client_running = handle_client_request(client_req, client_id, cache)


main()
