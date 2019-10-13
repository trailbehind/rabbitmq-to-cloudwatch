# rabbitmq-to-cloudwatch

Publish number of messages in a RabbitMQ queue as AWS Cloudwatch metrics. Can also be configured to just log, and not publish to cloudwatch.

# Configuration

All configuration is through environment variables.

- `metric_interval` - Number of seconds to sleep between publishing metrics, default is `300`. Use `-1` for run only once and exit
- `log_only` - Only log, don't publish to cloudwatch. To enable set this to 1 or `true`
- `rabbitmq_management_host` - RabbitMQ host, format is `hostname:port`
- `rabbitmq_management_user` - RabbitMQ username
- `rabbitmq_management_password` - RabbitMQ password
- `rabbitmq_vhost` - RabbitMQ vhost, default is `/`
- `AWS_REGION` - AWS region to use, default is us-east-1
- `cloudwatch_namespace` - Cloudwatch namespace
- `publish_sum` - publish an additional metric that is the sum of depths of all queues. This is only useful if you have more than 1 queue.
