#!/bin/sh

echo "Testing image $1"
cd $1
NAME=`echo "$1" | sed -e "s#/#_#g"`
ou-container-builder build --tag $NAME:latest
podman run -p 8888:8888 --name $NAME $NAME:latest &
status=$(curl --silent --output /dev/stderr -L --write-out "%{http_code}" "http://localhost:8888/?token=test")
countdown=6
while [ $status -ne 200 ]
do
    sleep 2
    status=$(curl --silent --output /dev/stderr -L --write-out "%{http_code}" "http://localhost:8888/?token=test")
    countdown=$(expr $countdown - 1)
    if [ $countdown -lt 0 ]
    then
        break
    fi
done
podman stop $NAME
podman rm $NAME
podman rmi $NAME:latest
if [ $status -eq 200 ]
then
    exit 0
else
    exit 1
fi
