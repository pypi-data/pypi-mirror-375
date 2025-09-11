import mypy_boto3_sqs.client
import sqs_worker


def sqs_connected(
    sqs_client: mypy_boto3_sqs.client.SQSClient,
) -> bool:
    try:
        sqs_client.list_queues()
        return True
    except Exception:
        return False


def ensure_queue_exists(
    sqs_client: mypy_boto3_sqs.client.SQSClient,
    queue_name: str,
) -> None:
    try:
        sqs_client.get_queue_url(QueueName=queue_name)
    except sqs_client.exceptions.QueueDoesNotExist:
        sqs_client.create_queue(QueueName=queue_name)


def send_hello_message(
    sqs_client: mypy_boto3_sqs.client.SQSClient,
    queue_name: str,
    message: sqs_worker.models.Message,
) -> None:
    queue_url = sqs_client.get_queue_url(QueueName=queue_name)["QueueUrl"]
    sqs_client.send_message(
        QueueUrl=queue_url,
        MessageBody=message.model_dump_json(),
    )
