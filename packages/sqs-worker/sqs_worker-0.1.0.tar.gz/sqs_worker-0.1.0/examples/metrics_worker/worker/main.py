import datetime
import logging
import threading
import os

import boto3
import mypy_boto3_sqs.client
import pydantic
import obsv_tools.metrics.instrumentator
import sqs_worker

import sqs_utils


logger = logging.getLogger('sqs_worker_example')

logging.basicConfig(level=logging.INFO)


class MessagePayload(
    pydantic.BaseModel,
):
    value: str


class MyWorker(
    sqs_worker.worker.Worker,
):

    def __init__(
        self,
        sqs_client: mypy_boto3_sqs.client.SQSClient,
        queue_name: str,
        metrics_instrumentator: obsv_tools.metrics.instrumentator.Instrumentator,
    ) -> None:
        super().__init__(
            logger=logger,
            name='MyWorker',
            sqs_client=sqs_client,
            queue_name=queue_name,
            metrics_instrumentator=metrics_instrumentator,
            payload_class=MessagePayload,
            max_messages=2,
            idle_limit=datetime.timedelta(seconds=2),
        )

    def work(
        self,
        messages: list[sqs_worker.models.Message[MessagePayload]],
    ) -> None:
        thread_id = threading.get_ident()
        for message in messages:
            print(f'Thread {thread_id}: Processing message with: {message.payload.value}')


def main() -> None:
    # Thread safe clients only
    metrics_instrumentator = obsv_tools.metrics.instrumentator.Instrumentator(
        server_port=9090,
    )

    sqs_client = boto3.client(
        'sqs',
        endpoint_url=os.environ['SQS_ENDPOINT_URL'],
        region_name=os.environ.get('AWS_REGION', 'us-east-1'),
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID', 'test'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY', 'test'),
    )
    queue_name = 'my-queue'
    number_of_workers = 10

    sqs_utils.ensure_queue_exists(
        sqs_client=sqs_client,
        queue_name=queue_name,
    )

    for _ in range(number_of_workers):
        sqs_utils.send_hello_message(
            sqs_client=sqs_client,
            queue_name=queue_name,
            message=sqs_worker.models.Message(
                version='1.0',
                msg_type='greeting',
                payload=MessagePayload(value='Hello, World!'),
            ),
    )

    def worker_factory():
        return MyWorker(
            sqs_client=boto3.client(
                'sqs',
                endpoint_url=os.environ['SQS_ENDPOINT_URL'],
                region_name=os.environ.get('AWS_REGION', 'us-east-1'),
                aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID', 'test'),
                aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY', 'test'),
            ),
            queue_name=queue_name,
            metrics_instrumentator=metrics_instrumentator,
        )

    sqs_worker.worker.multiple(
        worker_factory=worker_factory,
        n=10,
    )


if __name__ == '__main__':
    main()