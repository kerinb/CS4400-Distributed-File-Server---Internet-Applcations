#!/bin/bash

echo "Launching the Locking Server on 'http://127.0.0.1:46667'"

python LockingServer/LockingServer.py "127.0.0.1" "46667"
