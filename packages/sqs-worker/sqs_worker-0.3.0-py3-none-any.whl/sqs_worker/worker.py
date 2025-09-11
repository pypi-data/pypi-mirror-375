import concurrent.futures
import datetime
import itertools
import json
import logging
import signal
import time
import typing

import obsv_tools.metrics.instrumentator

from . import exceptions
from . import models

import mypy_boto3_sqs.client


MAX_BATCH_SIZE = 10


class Worker:
    EXCEPTIONS_METRIC_NAME = "sqs.worker.exceptions"
    WORK_MESSAGES_METRIC_NAME = "sqs.worker.work.messages"
    WORK_LATENCY_METRIC_NAME = "sqs.worker.work.latency"

    def __init__(
        self,
        logger: logging.Logger,
        name: str,
        sqs_client: mypy_boto3_sqs.client.SQSClient,
        queue_name: str,
        payload_class: type[models.T],
        max_messages: int = MAX_BATCH_SIZE,
        metrics_instrumentator: obsv_tools.metrics.instrumentator.Instrumentator
        | None = None,
        wait_for_max_messages: datetime.timedelta = datetime.timedelta(seconds=1),
        visibility_timeout: int = 30,
        auto_ack: bool = True,
        max_retry_attempts: int = 10,
        pull_msgs_interval: datetime.timedelta = datetime.timedelta(seconds=0.5),
        idle_limit: datetime.timedelta | None = None,
    ) -> None:
        self.name = name
        self.sqs_client = sqs_client
        self.queue_name = queue_name
        self.logger = logger
        self.max_messages = max_messages
        self.wait_for_messages = wait_for_max_messages
        self.visibility_timeout = visibility_timeout
        self.active = True
        self.metrics_instrumentator = metrics_instrumentator
        self.payload_class = payload_class
        self.auto_ack = auto_ack
        self.max_retry_attempts = max_retry_attempts
        self.pull_msgs_interval = pull_msgs_interval
        self.idle_limit = idle_limit

        self.metrics_instrumentator.add_counter(
            name=self.EXCEPTIONS_METRIC_NAME,
            description="Exception Counter",
        ).add_counter(
            name=self.WORK_MESSAGES_METRIC_NAME,
            description="Number of messages processed",
        ).add_histogram(
            name=self.WORK_LATENCY_METRIC_NAME,
            description="Time spent working on message",
        )

    def start(
        self,
    ) -> None:
        self.logger.info(
            msg="Starting worker",
            extra={
                "worker_name": self.name,
            },
        )

        idle_time = 0

        while self.active:
            try:
                raw_messages: list[mypy_boto3_sqs.type_defs.MessageTypeDef] = (
                    self.pull_messages()
                )

                if not raw_messages:
                    time.sleep(self.pull_msgs_interval.total_seconds())

                    idle_time += self.pull_msgs_interval.total_seconds()
                    if self.idle_limit and idle_time >= self.idle_limit.total_seconds():
                        self.logger.info(
                            msg="Idle limit reached, stopping worker",
                            extra={
                                "worker_name": self.name,
                            },
                        )

                        self.stop()

                    continue

                messages = [
                    self.parse_message(
                        message=raw_message,
                    )
                    for raw_message in raw_messages
                ]
            except Exception:
                self.logger.exception(
                    msg="Failed to pull messages",
                )

                continue

            try:
                start_time = time.time()

                self.work(
                    messages=messages,
                )

            except exceptions.RetryLaterException:
                self.retry_later(
                    messages=messages,
                )
            except Exception as exception:
                self.logger.exception(
                    msg="Failed to process messages",
                    extra={
                        "worker_name": self.name,
                    },
                )

                self.metrics_instrumentator.increment_counter(
                    name=self.EXCEPTIONS_METRIC_NAME,
                    attributes={
                        "worker_name": self.name,
                        "error_type": type(exception).__name__,
                    },
                )

                self.on_error(
                    exception=exception,
                    messages=messages,
                )
            else:
                self.logger.info(
                    msg="Worker successfully processed messages",
                    extra={
                        "worker_name": self.name,
                    },
                )

                self.metrics_instrumentator.increment_counter(
                    name=self.WORK_MESSAGES_METRIC_NAME,
                    attributes={
                        "worker_name": self.name,
                    },
                    amount=len(messages),
                )

                self.metrics_instrumentator.record_histogram(
                    name=self.WORK_LATENCY_METRIC_NAME,
                    attributes={
                        "worker_name": self.name,
                    },
                    amount=(time.time() - start_time),
                )

                if self.auto_ack:
                    self.ack_all(
                        messages=messages,
                    )

    def stop(
        self,
    ) -> None:
        self.logger.info(
            msg="Stopping worker",
            extra={
                "worker_name": self.name,
            },
        )

        self.active = False

    def work(
        self,
        messages: list[models.Message],
    ) -> None:
        raise NotImplementedError()

    def pull_messages(
        self,
    ) -> list[mypy_boto3_sqs.type_defs.MessageTypeDef]:
        queue_url = self.get_queue_url(
            queue_name=self.queue_name,
        )

        start_time = time.time()
        wait_time_sec = 0.0

        messages: list[mypy_boto3_sqs.type_defs.MessageTypeDef] = []

        wait_for_messages_sec = int(self.wait_for_messages.total_seconds())

        while (
            len(messages) < self.max_messages and wait_time_sec <= wait_for_messages_sec
        ):
            response = self.sqs_client.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=min(10, self.max_messages - len(messages)),
                WaitTimeSeconds=max(
                    1, min(20, wait_for_messages_sec - int(wait_time_sec))
                ),
                VisibilityTimeout=self.visibility_timeout,
            )

            if "Messages" in response:
                messages.extend(response["Messages"])

            wait_time_sec = time.time() - start_time

        return messages

    def parse_message(
        self,
        message: mypy_boto3_sqs.type_defs.MessageTypeDef,
    ) -> models.Message:
        message_body = json.loads(message["Body"])

        message_body.pop("queue_name", None)
        message_body.pop("receipt_handle", None)

        payload_data = message_body.pop("payload")
        payload = self.payload_class(**payload_data)

        return models.Message(
            queue_name=self.queue_name,
            receipt_handle=message["ReceiptHandle"],
            payload=payload,
            **message_body,
        )

    def retry_later(
        self,
        messages: list[models.Message],
    ):
        retry_messages = [
            message
            for message in messages
            if message.retry_attempt <= self.max_retry_attempts
        ]

        self.logger.info(
            msg="Enqueuing retry later messages",
            extra={
                "messages_count": len(retry_messages),
            },
        )

        for message in retry_messages:
            message.retry_attempt += 1

        self.publish_messages(
            queue_name=self.queue_name,
            messages=retry_messages,
            delay_seconds=datetime.timedelta(minutes=10),
        )

        self.ack_all(
            messages=retry_messages,
        )

    def publish_message(
        self,
        queue_name: str,
        message: models.Message,
    ) -> None:
        queue_url = self.get_queue_url(
            queue_name=queue_name,
        )

        self.sqs_client.send_message(
            QueueUrl=queue_url,
            MessageBody=message.model_dump_json(),
        )

    def publish_messages(
        self,
        queue_name: str,
        messages: list[models.Message],
        delay_seconds: datetime.timedelta | None = None,
    ) -> None:
        if not messages:
            return

        queue_url = self.get_queue_url(
            queue_name=queue_name,
        )

        for i in range(0, len(messages), MAX_BATCH_SIZE):
            batch = messages[i : i + MAX_BATCH_SIZE]

            json_messages: list[
                mypy_boto3_sqs.type_defs.SendMessageBatchRequestEntryTypeDef
            ] = []

            for idx, message in enumerate(batch):
                entry = {
                    "Id": f"message-{idx}",
                    "MessageBody": message.model_dump_json(),
                }
                if delay_seconds is not None:
                    entry["DelaySeconds"] = int(delay_seconds.total_seconds())

                json_messages.append(entry)

            self.sqs_client.send_message_batch(
                QueueUrl=queue_url,
                Entries=json_messages,
            )

    def ack(
        self,
        message: models.Message,
    ) -> None:
        self.ack_all(
            messages=[
                message,
            ],
        )

    def ack_all(
        self,
        messages: list[models.Message],
    ) -> None:
        for messages_chunk in itertools.batched(messages, MAX_BATCH_SIZE):
            self.sqs_client.delete_message_batch(
                QueueUrl=self.get_queue_url(
                    queue_name=self.queue_name,
                ),
                Entries=[
                    {
                        "Id": f"message-{idx}",
                        "ReceiptHandle": message.receipt_handle,
                    }
                    for idx, message in enumerate(messages_chunk)
                    if message.receipt_handle is not None
                ],
            )

    def extend_message_visibility(
        self,
        message: models.Message,
        visibility_timeout: int,
    ):
        if message.receipt_handle is None:
            raise ValueError("Unable to extend visibility without receipt_handle")

        self.sqs_client.change_message_visibility(
            QueueUrl=self.get_queue_url(
                queue_name=self.queue_name,
            ),
            ReceiptHandle=message.receipt_handle,
            VisibilityTimeout=visibility_timeout,
        )

    def get_queue_url(
        self,
        queue_name: str,
    ) -> str:
        queue_data = self.sqs_client.get_queue_url(
            QueueName=queue_name,
        )

        return queue_data["QueueUrl"]

    def on_error(
        self,
        exception: Exception,
        messages: list[models.Message],
    ) -> None:
        pass


def single(
    worker_factory,
):
    multiple(
        worker_factory=worker_factory,
        n=1,
    )


def multiple(
    worker_factory: typing.Callable[[], Worker],
    n,
):
    pool = concurrent.futures.ThreadPoolExecutor(n)
    workers = [worker_factory() for _ in range(n)]

    def sigterm_handler(
        _signo,
        _stack_frame,
    ):
        for worker in workers:
            worker.stop()

    signal.signal(signal.SIGTERM, sigterm_handler)

    for worker in workers:
        pool.submit(worker.start)
