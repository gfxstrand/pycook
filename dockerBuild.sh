#!/bin/bash

echo "== Cleaning up previous versions of pycook Docker Images"
docker rmi pycook
echo "== Building pycook Docker image"
docker build --tag pycook .
