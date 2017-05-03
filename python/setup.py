from setuptools import setup

packages=['paddle',
          'paddle.job']

setup(name='paddle_job',
      version='0.1.0',
      description="PaddlePaddle Job For Kubernetes",
      packages=packages,
      install_requires=['kubernetes']
)
