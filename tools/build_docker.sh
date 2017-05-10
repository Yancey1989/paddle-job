#!/bin/bash
cur_path="$(cd "$(dirname "$0")" && pwd -P)"
cd "$cur_path"/../

#src trainer package
if [ ! -n "$1" ]; then
  src_trainer_package=./example
else
  src_trainer_package=$1
fi

#dest trainer package
if [ ! -n "$2" ]; then
  dest_trainer_package=/example
else
  dest_trainer_package=$2
fi

#Paddle Job base Docker image
if [ ! -n "$3" ]; then
  base_docker_image=paddlepaddle/paddle:latest
else
  base_docker_image=$3
fi

#Paddle Job runtime Docker image
if [ ! -n "$4" ]; then
  runtime_docker_image=paddlepaddle/paddle_job
else
  runtime_docker_image=$4
fi

echo "src_trainer_package": $src_trainer_package
echo "dest_trainer_package": $dest_trainer_package
echo "base_docker_image": $base_docker_image
echo "runtime_docker_image": $runtime_docker_image

#Build Python Package
docker run --rm -it -v $PWD:/paddle-job $base_docker_image \
  bash -c "cd /paddle-job/python && python setup.py bdist_wheel"

#Build Docker Image
cat > Dockerfile <<EOF
FROM ${base_docker_image}
ADD ./tools/paddle_k8s /usr/bin
ADD ./tools/k8s_tools.py /root/
ADD ./python/dist/paddle_job-0.10.0-py2-none-any.whl /
ADD ${src_trainer_package} ${dest_trainer_package}
RUN pip install -U /paddle_job-0.10.0-py2-none-any.whl \
    && pip install -U requests \
    && rm /paddle_job-0.10.0-py2-none-any.whl
CMD ["paddle_k8s"]
EOF

docker build -t $runtime_docker_image .
