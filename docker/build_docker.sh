#!/bin/bash
set -xe

cur_path="$(cd "$(dirname "$0")" && pwd -P)"
cd "$cur_path"/../

#Paddle Job Docker image name
if [ ! -n "$1" ]; then
  image_name=paddlepaddle/paddle_job
else
  image_name=$1
fi

#Paddle Job Docker image tag
if [ ! -n "$2" ]; then
  image_tag=latest
else
  image_tag=$2
fi

echo "paddle_job_image:"$image_name:$image_tag

#Build Python Package
cd python && python setup.py bdist_wheel && cd ..

#Build Docker Image
docker build -t ${image_name}:${image_tag} -f docker/Dockerfile .
