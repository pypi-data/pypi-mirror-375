#!/bin/bash
for demo in code_server custom_apt_key_dearmor jupyterlab/v4 openrefine
do
    ./demo-tests.sh $demo
    if [ ! $? == "0" ]
    then
        exit 1
    fi
done
