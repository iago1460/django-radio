#!/bin/bash

HOST=$1
PORT=$2

if [[ "$HOST" == "" ]]; then
    echo "wait_for: Missing host"
    exit 1
fi

if [[ "$PORT" == "" ]]; then
    echo "wait_for: Missing port"
    exit 1
fi

counter=0
echo -n "Waiting for $HOST:$PORT..."
while ! nc -z $HOST $PORT > /dev/null; do
    echo -n "."
    sleep 1
    ((counter+=1))
    if (( counter > 60 )); then
        echo " Failed"
        exit 1
    fi
done
echo " Ready"
