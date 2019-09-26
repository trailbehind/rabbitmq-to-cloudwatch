FROM python:3.7.4

RUN pip install pyrabbit boto3

ADD publish_queue_size.py /opt

CMD /opt/publish_queue_size.py
