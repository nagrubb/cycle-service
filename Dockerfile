FROM ubuntu:18.04
MAINTAINER Nathan Grubb "nate@nathangrubb.io"

# Install System Dependencies
RUN apt-get update -y
RUN apt-get install -y python3-pip

# Create Service Directory
RUN mkdir -p /opt/cycle/
WORKDIR /opt/cycle

# Install Service Dependencies
COPY requirements.txt /opt/cycle
RUN pip3 install -r requirements.txt
COPY cycle.py /opt/cycle

# Run Service
ENTRYPOINT ["python3"]
CMD ["-u", "cycle.py"]
