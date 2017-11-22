import os

import time
import traceback

import RequestTypeToFileServer

FILE_EXTENSION_TXT = ".txt"

def handle_errors(e, message):
    print time.ctime(time.time()) + message
    print e.message
    print traceback.format_exc()