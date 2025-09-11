import datetime
import logging
import random
import threading
import os
import time

import boto3
import pydantic
import obsv_tools.metrics.instrumentator
import sqs_worker


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
        sqs_client,
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
            idle_limit=datetime.timedelta(minutes=10),
        )

    def work(
        self,
        messages: list[sqs_worker.models.Message[MessagePayload]],
    ) -> None:
        thread_id = threading.get_ident()
        for message in messages:
            wait_time = random.uniform(0.1, 9.5)
            time.sleep(wait_time)

            logger.info(
                msg=f'Thread {thread_id}: Finished processing message with: {message.payload.value}',
            )


def wait_for_sqs_queue(
    sqs_client,
    queue_name: str,
) -> None:
    max_retries = 30
    for i in range(max_retries):
        try:
            sqs_client.list_queues()

            sqs_client.get_queue_url(QueueName=queue_name)
            logger.info(f'Queue {queue_name} is available')

            return
        except sqs_client.exceptions.QueueDoesNotExist:
            logger.info(
                msg=f'Queue {queue_name} does not exist yet, waiting...',
                extra={
                    'queue_name': queue_name,
                    'attempt': i + 1,
                    'max_retries': max_retries,
                },
            )
            time.sleep(2)
        except Exception:
            logger.info(
                msg='Waiting for SQS service...',
                extra={
                    'queue_name': queue_name,
                    'attempt': i + 1,
                    'max_retries': max_retries,
                },
            )
            time.sleep(2)

    raise Exception(f'Queue {queue_name} is not available after waiting')


def main() -> None:
    # Thread safe clients only
    metrics_instrumentator = obsv_tools.metrics.instrumentator.Instrumentator(
        server_port=8000,
    )

    sqs_client = boto3.client(
        'sqs',
        endpoint_url=os.environ['SQS_ENDPOINT_URL'],
        region_name=os.environ.get('AWS_REGION', 'us-east-1'),
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID', 'test'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY', 'test'),
    )
    wait_for_sqs_queue(
        sqs_client=sqs_client,
        queue_name=os.environ['SQS_QUEUE_NAME'],
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
            queue_name=os.environ['SQS_QUEUE_NAME'],
            metrics_instrumentator=metrics_instrumentator,
        )

    sqs_worker.worker.multiple(
        worker_factory=worker_factory,
        n=1,
    )


if __name__ == '__main__':
    main()