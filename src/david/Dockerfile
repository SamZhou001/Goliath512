# base image
FROM ubuntu:22.04

ARG PORT

# update & install python3.10 apt packages
RUN apt update && apt install -y python3 python3-pip

# setup environment variable  
ENV DockerHOME=/home/app/david
ENV PYTHONPATH=/home/app
ENV PORT=${PORT}

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

# CMD python3 david_node.py
ENTRYPOINT ["python3", "run_node.py"]
# ENTRYPOINT ["tail", "-f", "/dev/null"]