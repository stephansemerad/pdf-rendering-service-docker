FROM ubuntu:latest

RUN apt-get update -y
RUN apt-get upgrade -y
RUN apt-get dist-upgrade -y
RUN apt-get install nano -y


RUN apt-get install --no-install-recommends -y python3.8 python3-pip python3.8-dev

RUN apt-get install libpcre3 libpcre3-dev -y
RUN apt-get install poppler-utils -y
RUN apt-get install gcc -y

# Place the application components in a dir below the root dir
COPY . /app

# Make the directory the working directory for subsequent commands
WORKDIR /app

# Install from the requirements.txt we copied above
RUN pip3 install -r requirements.txt