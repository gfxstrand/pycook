#!/bin/bash

if [ "$1" = "pdf" ]; then
    if [ "$2" = "-s" ]; then
    docker run --rm -v $4:/cookbook -v $5:/output pycook $1 -s $3\
        /cookbook/cookbook.yaml /output/cookbook.pdf
    else
    docker run --rm -v $2:/cookbook -v $3:/output pycook $1\
        /cookbook/cookbook.yaml /output/cookbook.pdf
    fi
else
docker run --rm -v $2:/cookbook -v $3:/output pycook $1\
 /cookbook/cookbook.yaml /output
fi

