FROM python:3.9

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Copy local code to the container image.
#ENV APP_HOME /app
#WORKDIR $APP_HOME
#COPY . ./

ENV PORT 8080
ENV HOST 0.0.0.0

EXPOSE 8080

WORKDIR /app

ARG DEBIAN_FRONTEND=noninteractive
# Install production deps.
RUN apt-get update
RUN apt-get install -y apt-utils
RUN apt-get install -y curl
RUN apt-get install -y graphviz
RUN apt-get install -y python3-tk
RUN apt install -y libblas-dev
RUN apt install -y liblapack-dev
RUN apt install -y libsuitesparse-dev
RUN apt-get install -y python3-pip
RUN pip3 install flask matplotlib ruptures pm4py

COPY . /app

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
# Timeout is set to 0 to disable the timeouts of the workers to allow Cloud Run to handle instance scaling.
ENTRYPOINT ["python3", "run.py"]
