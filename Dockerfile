from ubuntu:16.04

#install prerequisites
RUN apt-get -q update && \
    apt-get -q -y install python python-pip && \
    pip install pyrabbit boto3 && \
    apt-get clean && \
    rm -rf /var/lib/apt/ /var/cache/apt/ /var/cache/debconf/

ADD publish_queue_size.py /opt

CMD "/opt/publish_queue_size.py"
