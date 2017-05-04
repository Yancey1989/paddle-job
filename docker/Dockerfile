FROM yancey1989/paddle:0.10.0rc4
#paddle_k8s and k8s_tools is for test,
#this will be deleted if paddle service discovery ready.
ADD ./docker/paddle_k8s /usr/bin
ADD ./docker/k8s_tools.py /root/
ADD ./python/dist/paddle_job-0.1.0-py2-none-any.whl /
ADD ./example /example/
RUN pip install /paddle_job-0.1.0-py2-none-any.whl \
      && rm /paddle_job-0.1.0-py2-none-any.whl
CMD ["paddle_k8s"]
