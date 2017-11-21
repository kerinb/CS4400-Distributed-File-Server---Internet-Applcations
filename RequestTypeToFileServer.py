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
    CHECK_FOR_DIRECTORY_EXIST = 0
    OPEN_FILE = 1
    READ_FILE = 2
    CREATE_DIRECTORY = 3
    WRITE_TO_FILE = 4
    DELETE_FILE = 6
    REQUEST_SENT_BY_CLIENT = 7
    RESPONSE_SENT_BY_CLIENT = 8

    # server response messages to client
    FILE_DOES_EXIST_AND_NOT_LOCKED = 9
    FILE_DOES_EXIST_AND_LOCKED = 10
    FILE_DOES_NOT_EXIST = 11
    DIRECTORY_FOUND = 12

    # locking functionality
    LOCK_FILE_REQUEST = 13
    UNLOCK_FILE_REQUEST = 14
    LOCK_FILE_REQUEST_REFUSED = 13
    UNLOCK_FILE_REQUEST_REFUSED = 14
