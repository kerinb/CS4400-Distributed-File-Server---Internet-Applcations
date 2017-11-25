#
# @Authur: Breandan Kerin
# @Student Number: 14310166
#

#
# Enum file used to specify the type of requests that the client server can use on the file server
# Enum file used to specify the type of requests that the file server can expect and hence handle by client
#

from enum import Enum


class RequestTypeToFileServer(Enum):
    def __str__(self):
        return str(self.value)

    # request messages sent by the client
    CHECK_FOR_FILE_EXIST = 0
    OPEN_FILE = 1
    CREATE_FILE = 2
    WRITE_TO_FILE = 3
    DELETE_FILE = 4
    REQUEST_CLIENT_ID = 5
    DOWNLOAD_FILE_FROM_SERVER = 6
    CLIENT = 7
    FILE_SERVER = 8

    # locking functionality
    # TODO - this will be implemented later when I get around ot locking services
    #LOCK_FILE_REQUEST = 13
    #UNLOCK_FILE_REQUEST = 14
    #LOCK_FILE_REQUEST_REFUSED = 13
    #UNLOCK_FILE_REQUEST_REFUSED = 14
