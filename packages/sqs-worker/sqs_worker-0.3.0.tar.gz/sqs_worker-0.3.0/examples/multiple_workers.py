import datetime
import logging
import threading

import boto3
import mypy_boto3_sqs.client
import pydantic
import obsv_tools.metrics.instrumentator
import sqs_worker

import sqs_utils


logger = logging.getLogger("sqs_worker_example")

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
            name="MyWorker",
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
            logger.info(
                msg=f"Thread {thread_id}: Processing message with: {message.payload.value}",
            )


def main() -> None:
    # Thread safe clients only
    metrics_instrumentator = obsv_tools.metrics.instrumentator.Instrumentator(
        server_port=9090,
    )

    sqs_client = boto3.client(
        "sqs",
        endpoint_url="http://localhost:4566",
        region_name="us-east-1",
        aws_access_key_id="test",
        aws_secret_access_key="test",
    )
    queue_name = "my-queue"
    number_of_workers = 10

    if not sqs_utils.sqs_connected(sqs_client=sqs_client):
        raise RuntimeError(
            'Cannot connect to SQS. Please ensure LocalStack is running by executing "localstack start".'
        )

    sqs_utils.ensure_queue_exists(
        sqs_client=sqs_client,
        queue_name=queue_name,
    )

    for _ in range(number_of_workers):
        sqs_utils.send_hello_message(
            sqs_client=sqs_client,
            queue_name=queue_name,
            message=sqs_worker.models.Message(
                version="1.0",
                msg_type="greeting",
                payload=MessagePayload(value="Hello, World!"),
            ),
        )

    def worker_factory():
        return MyWorker(
            sqs_client=boto3.client(
                "sqs",
                endpoint_url="http://localhost:4566",
                region_name="us-east-1",
                aws_access_key_id="test",
                aws_secret_access_key="test",
            ),
            queue_name=queue_name,
            metrics_instrumentator=metrics_instrumentator,
        )

    sqs_worker.worker.multiple(
        worker_factory=worker_factory,
        n=number_of_workers,
    )


if __name__ == "__main__":
    main()
