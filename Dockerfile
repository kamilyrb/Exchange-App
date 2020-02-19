FROM python:3.7
# Ensure that Python outputs everything that's printed inside 
# the application rather than buffering it
ENV PYTHONUNBUFFERED 1
# Creation of the workdir
RUN mkdir /exchange
WORKDIR /exchange
# Add requirements.txt file to container
ADD requirements.txt /exchange/
# Install requirements
RUN pip install --upgrade pip
RUN pip install -r /exchange/requirements.txt
# Add the current directory(the web folder) to Docker container
ADD . /exchange/