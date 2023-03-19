# base image
FROM ubuntu:20.04

# update & install python3.10 apt packages
RUN apt-get update && apt-get install -y python3.10 python3.10-dev python3.10-venv

# setup environment variable  
ENV DockerHOME=/home/app/david

# set work directory  
RUN mkdir -p $DockerHOME

# where your code lives  
WORKDIR $DockerHOME

# set environment variables  
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1 

# copy src files
COPY . $DockerHOME

# install dependencies  
RUN pip install --upgrade pip

# run this command to install all dependencies
RUN pip install -r requirements.txt

# port where david bootstrap node runs
EXPOSE 8000

CMD python david_node.py