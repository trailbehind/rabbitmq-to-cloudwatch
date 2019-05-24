from ubuntu:18.04
ENV DEBIAN_FRONTEND=noninteractive

#install prerequisites
RUN apt-get -q update && \
    apt-get -q -y install python3 python3-pip && \
    pip3 install pyrabbit boto3 && \
    apt-get clean && \
    rm -rf /var/lib/apt/ /var/cache/apt/ /var/cache/debconf/

ADD publish_queue_size.py /opt

CMD "/opt/publish_queue_size.py"
