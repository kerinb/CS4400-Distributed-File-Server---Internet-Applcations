#
# @Authur: Breandan Kerin
# @Student Number: 14310166
#

#
# Enum file used to specify the type of requests that the client server can use on the file server
# Enum file used to specify the type of requests that the file server can expect and hence handle by client
#

from enum import Enum


class ResponseTypeToClient(Enum):
    def __str__(self):
        return str(self.value)

    # server response messages to client
    RESPONSE_CLIENT_ID_MADE = 50
    FILE_DOES_EXIST = 51
    DIRECTORY_FOUND = 52
    DIRECTORY_NOT_FOUND = 53
    FILE_MADE = 54
    FILE_NOT_MADE = 55
    FILE_ALREADY_EXISTS = 56
    FILE_DELETED = 57
    FILE_NOT_DELETED_DIRECTORY_FOUND = 58
    FILE_NOT_DELETED_DIRECTORY_NOT_FOUND = 59
    WRITE_TO_FILE_SUCCESSFUL = 60
    WRITE_TO_FILE_UNSUCCESSFUL = 61
    RESPONSE_CLIENT_ID_NOT_MADE = 62
    DIRECTORY_CREATED = 63
    DIRECTORY_NOT_CREATED = 64
    DOWNLOAD_SUCCESSFUL = 65
    DOWNLOAD_UNSUCCESSFUL = 66
    ERROR = 999

    # locking functionality
    # TODO - this will be implemented later when I get around ot locking services
    #LOCK_FILE_REQUEST = 13
    #UNLOCK_FILE_REQUEST = 14
    #LOCK_FILE_REQUEST_REFUSED = 13
    #UNLOCK_FILE_REQUEST_REFUSED = 14
