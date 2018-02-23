#!/usr/bin/env python
from __future__ import with_statement, print_function

from pyrabbit.api import Client
import boto3
import os
from time import sleep

def get_queue_depths(host, username, password, vhost):
    cl = Client(host, username, password)
    if not cl.is_alive():
        raise Exception("Failed to connect to rabbitmq")
    depths = {}
    queues = [q['name'] for q in cl.get_queues(vhost=vhost)]
    for queue in queues:
        if queue == "aliveness-test":
            continue
        depths[queue] = cl.get_queue_depth(vhost, queue)
    return depths


def publish_queue_depth_to_cloudwatch(cwc, queue_name, depth, namespace):
    print("Putting metric namespace=%s name=%s unit=Count value=%i" % 
        (namespace, queue_name, depth))

    cwc.put_metric_data(
        MetricData=[
            {
                'MetricName': queue_name,
                'Unit': 'Count',
                'Value': depth
            },
        ],
        Namespace=namespace
    )


def publish_depths_to_cloudwatch(depths, namespace):
    cloudwatch = boto3.client('cloudwatch',
        region_name=os.environ.get("AWS_REGION", "us-east-1"))
    for queue in depths:
        publish_queue_depth_to_cloudwatch(cloudwatch, queue, depths[queue], namespace)


def get_queue_depths_and_publish_to_cloudwatch(host, username, password, vhost, namespace):
    depths = get_queue_depths(host, username, password, vhost)
    publish_depths_to_cloudwatch(depths, namespace)

if __name__ == "__main__":
    sleep_interval = int(os.environ.get("metric_interval", 300))
    print("Publishing metrics every %d seconds" % sleep_interval)
    while True:
        get_queue_depths_and_publish_to_cloudwatch(
            os.environ.get("rabbitmq_management_host"),
            os.environ.get("rabbitmq_management_user"),
            os.environ.get("rabbitmq_management_password"),
            "/",
            "rabbitmq_depth")
        sleep(60 * 5)
