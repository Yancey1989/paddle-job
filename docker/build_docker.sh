#!/bin/bash
set -xe

cur_path="$(cd "$(dirname "$0")" && pwd -P)"
cd "$cur_path"/../

#Trainer package
if [ ! -n "$1" ]; then
  trainer_package_path=./example
else
  trainer_package_path=$1
fi

#Trainer package
if [ ! -n "$2" ]; then
  trainer_package_image_path=/example
else
  trainer_package_image_path=$2
fi

#Paddle Job Docker image name
if [ ! -n "$3" ]; then
  image_name=paddlepaddle/paddle_job
else
  image_name=$3
fi

#Paddle Job Docker image tag
if [ ! -n "$4" ]; then
  image_tag=latest
else
  image_tag=$4
fi

echo "paddle_job_image:"$image_name:$image_tag

#Build Python Package
cd python && python setup.py bdist_wheel && cd ..

#Build Docker Image
cat > Dockerfile <<EOF
FROM yancey1989/paddle:0.10.0rc4
#paddle_k8s and k8s_tools is for test,
#this will be deleted if paddle service discovery ready.
ADD ./docker/paddle_k8s /usr/bin
ADD ./docker/k8s_tools.py /root/
ADD ./python/dist/paddle_job-0.1.0-py2-none-any.whl /
ADD ${trainer_package_path} ${trainer_package_image_path}
RUN pip install /paddle_job-0.1.0-py2-none-any.whl \
      && rm /paddle_job-0.1.0-py2-none-any.whl
CMD ["paddle_k8s"]
EOF

docker build -t ${image_name}:${image_tag} .
