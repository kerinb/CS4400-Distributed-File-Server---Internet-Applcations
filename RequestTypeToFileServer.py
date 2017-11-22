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
    READ_FILE = 3
    WRITE_TO_FILE = 4
    DELETE_FILE = 5
    CREATE_DIRECTORY = 6
    REQUEST_CLIENT_ID = 7
    RESPONSE_CLIENT_ID = 8

    # server response messages to client
    FILE_DOES_EXIST = 9
    DIRECTORY_FOUND = 10
    DIRECTORY_NOT_FOUND = 11
    FILE_MADE = 12
    FILE_NOT_MADE = 13
    FILE_DELETED = 14
    FILE_NOT_DELETED_DIRECTORY_FOUND = 15
    FILE_NOT_DELETED_DIRECTORY_NOT_FOUND = 16

    # locking functionality
    # TODO - this will be implemented later when I get around ot locking services
    #LOCK_FILE_REQUEST = 13
    #UNLOCK_FILE_REQUEST = 14
    #LOCK_FILE_REQUEST_REFUSED = 13
    #UNLOCK_FILE_REQUEST_REFUSED = 14
