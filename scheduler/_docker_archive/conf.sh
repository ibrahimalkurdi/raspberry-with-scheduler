#!/bin/bash
docker build --no-cache -t athan .
docker rm -f athan
docker run --name athan -d -p 80:80 --restart=always athan
