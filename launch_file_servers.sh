#!/bin/bash

declare -i PORT_NUM

HOST_ADDR = "127.0.0.1"
PORT_NUM = 5002


for i in $( seq 2 $1 )
do
    python FileServer/FileServer.py $HOST_ADDR "$PORT_NUM" &
    echo "Launching a file Server on 'http://127.0.0.1:"$PORT_NUM"'"
    PORT_NUM = PORT_NUM +1
done

python FileServer/FileServer.py $HOST_ADDR "$PORT_NUM"
