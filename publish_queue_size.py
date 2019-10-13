#!/usr/bin/env python3
import os
from time import sleep

import boto3
from pyrabbit.api import Client


def get_queue_depths(host, username, password, vhost):
    cl = Client(host, username, password)
    if not cl.is_alive():
        raise Exception("Failed to connect to rabbitmq")
    depths = {}
    queues = [q["name"] for q in cl.get_queues(vhost=vhost)]
    for queue in queues:
        if queue == "aliveness-test":
            continue
        depths[queue] = cl.get_queue_depth(vhost, queue)
    return depths


def publish_queue_depth_to_cloudwatch(cwc, queue_name, depth, namespace):
    print(
        "Putting metric namespace=%s name=%s unit=Count value=%i"
        % (namespace, queue_name, depth)
    )

    cwc.put_metric_data(
        MetricData=[{"MetricName": queue_name, "Unit": "Count", "Value": depth}],
        Namespace=namespace,
    )


def publish_depths_to_cloudwatch(depths, namespace):
    cloudwatch = boto3.client(
        "cloudwatch", region_name=os.environ.get("AWS_REGION", "us-east-1")
    )
    for queue, depth in depths.items():
        publish_queue_depth_to_cloudwatch(cloudwatch, queue, depth, namespace)

    if bool(os.environ.get("publish_sum", False)):
        publish_queue_depth_to_cloudwatch(
            cloudwatch, "sum", sum(depths.values()), namespace
        )


def get_queue_depths_and_publish_to_cloudwatch(
    host, username, password, vhost, namespace, log_only=False
):
    depths = get_queue_depths(host, username, password, vhost)
    if log_only:
        for queue, depth in depths.items():
            print("Queue:%s message depth:%d" % (queue, depth))
    else:
        publish_depths_to_cloudwatch(depths, namespace)


if __name__ == "__main__":
    sleep_interval = int(os.environ.get("metric_interval", 300))
    log_only = bool(os.environ.get("log_only", False))
    rabbitmq_management_host = os.environ.get("rabbitmq_management_host")
    rabbitmq_management_user = os.environ.get("rabbitmq_management_user")
    rabbitmq_management_password = os.environ.get("rabbitmq_management_password")
    rabbitmq_vhost = os.environ.get("rabbitmq_vhost", "/")
    cloudwatch_namespace = os.environ.get("cloudwatch_namespace", "rabbitmq_depth")

    def run_metrics():
        get_queue_depths_and_publish_to_cloudwatch(
            rabbitmq_management_host,
            rabbitmq_management_user,
            rabbitmq_management_password,
            rabbitmq_vhost,
            cloudwatch_namespace,
            log_only=log_only,
        )

    if sleep_interval < 0:
        run_metrics()
    else:
        print("Publishing metrics every %d seconds" % sleep_interval)
        while True:
            run_metrics()
            sleep(sleep_interval)
