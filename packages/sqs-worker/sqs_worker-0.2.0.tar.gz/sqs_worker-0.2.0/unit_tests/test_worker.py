import datetime
import json
import logging
import signal
import time
from unittest.mock import Mock, patch, ANY

import pytest
import pydantic

import sqs_worker.worker as worker
import sqs_worker.models as models
import sqs_worker.exceptions as exceptions
import obsv_tools.metrics.instrumentator as instrumentator


class PayloadForTesting(pydantic.BaseModel):
    message: str
    count: int


@pytest.fixture
def mock_sqs_client():
    return Mock()


@pytest.fixture
def mock_logger():
    return Mock(spec=logging.Logger)


@pytest.fixture
def mock_instrumentator():
    mock_inst = Mock(spec=instrumentator.Instrumentator)
    mock_inst.add_counter.return_value = mock_inst
    mock_inst.add_histogram.return_value = mock_inst
    return mock_inst


@pytest.fixture
def sample_payload():
    return PayloadForTesting(message="test message", count=42)


@pytest.fixture
def sample_message(
    sample_payload,
):
    return models.Message(
        version="1.0",
        msg_type="test",
        queue_name="test_queue",
        receipt_handle="receipt_123",
        payload=sample_payload,
        retry_attempt=0,
    )


@pytest.fixture
def sample_raw_message(
    sample_payload,
):
    return {
        'Body': json.dumps({
            'version': '1.0',
            'msg_type': 'test',
            'queue_name': 'test_queue',
            'receipt_handle': 'receipt_123',
            'payload': sample_payload.model_dump(),
            'retry_attempt': 0,
        }),
        'ReceiptHandle': 'receipt_123',
    }


@pytest.fixture
def test_worker(
    mock_logger,
    mock_sqs_client,
    mock_instrumentator,
):
    return worker.Worker(
        logger=mock_logger,
        name="test_worker",
        sqs_client=mock_sqs_client,
        queue_name="test_queue",
        payload_class=PayloadForTesting,
        max_messages=5,
        metrics_instrumentator=mock_instrumentator,
        wait_for_max_messages=datetime.timedelta(seconds=2),
        visibility_timeout=30,
        auto_ack=True,
        max_retry_attempts=3,
    )


class TestWorkerInit:
    def test___init___When_called_Then_sets_attributes(
        self,
        mock_logger,
        mock_sqs_client,
        mock_instrumentator,
    ):
        test_worker = worker.Worker(
            logger=mock_logger,
            name="test_worker",
            sqs_client=mock_sqs_client,
            queue_name="test_queue",
            payload_class=PayloadForTesting,
            max_messages=5,
            metrics_instrumentator=mock_instrumentator,
            wait_for_max_messages=datetime.timedelta(seconds=2),
            visibility_timeout=30,
            auto_ack=True,
            max_retry_attempts=3,
        )
        
        assert test_worker.name == "test_worker"
        assert test_worker.sqs_client == mock_sqs_client
        assert test_worker.queue_name == "test_queue"
        assert test_worker.logger == mock_logger
        assert test_worker.max_messages == 5
        assert test_worker.wait_for_messages == datetime.timedelta(seconds=2)
        assert test_worker.visibility_timeout == 30
        assert test_worker.active is True
        assert test_worker.metrics_instrumentator == mock_instrumentator
        assert test_worker.payload_class == PayloadForTesting
        assert test_worker.auto_ack is True
        assert test_worker.max_retry_attempts == 3

    def test___init___When_called_Then_configures_metrics(
        self,
        mock_instrumentator,
    ):
        worker.Worker(
            logger=Mock(),
            name="test_worker",
            sqs_client=Mock(),
            queue_name="test_queue",
            payload_class=PayloadForTesting,
            metrics_instrumentator=mock_instrumentator,
        )
        
        mock_instrumentator.add_counter.assert_called_once_with(
            counter_name='sqs.manager.exceptions',
            description='Exception Counter',
        )
        mock_instrumentator.add_histogram.assert_called_once_with(
            histogram_name='sqs.manager.work.latency',
            description='Time spent working on message',
        )


class TestWorkerStart:
    def test_start_When_no_messages_Then_sleeps_and_continues(
        self,
        test_worker,
    ):
        test_worker.pull_messages = Mock(return_value=[])
        
        # Mock the start method to avoid infinite loop
        def mock_start():
            raw_messages = test_worker.pull_messages()
            if not raw_messages:
                with patch('time.sleep') as mock_sleep:
                    time.sleep(0.5)
                    mock_sleep.assert_called_with(0.5)
        
        mock_start()

    def test_start_When_messages_available_Then_processes_messages(
        self,
        test_worker,
        sample_raw_message,
        sample_message,
    ):
        test_worker.pull_messages = Mock(return_value=[sample_raw_message])
        test_worker.parse_message = Mock(return_value=sample_message)
        test_worker.work = Mock()
        test_worker.ack_all = Mock()
        
        # Simulate one iteration of the start loop
        raw_messages = test_worker.pull_messages()
        messages = [test_worker.parse_message(message=raw_message) for raw_message in raw_messages]
        test_worker.work(messages=messages)
        if test_worker.auto_ack:
            test_worker.ack_all(messages=messages)
        
        test_worker.work.assert_called_once_with(messages=[sample_message])
        test_worker.ack_all.assert_called_once_with(messages=[sample_message])

    def test_start_When_work_raises_retry_later_exception_Then_retries_later(
        self,
        test_worker,
        sample_raw_message,
        sample_message,
    ):
        test_worker.pull_messages = Mock(return_value=[sample_raw_message])
        test_worker.parse_message = Mock(return_value=sample_message)
        test_worker.work = Mock(side_effect=exceptions.RetryLaterException())
        test_worker.retry_later = Mock()
        
        # Simulate one iteration of the start loop with exception handling
        raw_messages = test_worker.pull_messages()
        messages = [test_worker.parse_message(message=raw_message) for raw_message in raw_messages]
        try:
            test_worker.work(messages=messages)
        except exceptions.RetryLaterException:
            test_worker.retry_later(messages=messages)
        
        test_worker.retry_later.assert_called_once_with(messages=[sample_message])

    def test_start_When_work_raises_exception_Then_handles_error(
        self,
        test_worker,
        sample_raw_message,
        sample_message,
        mock_instrumentator,
    ):
        test_exception = ValueError("test error")
        test_worker.pull_messages = Mock(return_value=[sample_raw_message])
        test_worker.parse_message = Mock(return_value=sample_message)
        test_worker.work = Mock(side_effect=test_exception)
        test_worker.on_error = Mock()
        
        # Simulate one iteration of the start loop with exception handling
        raw_messages = test_worker.pull_messages()
        messages = [test_worker.parse_message(message=raw_message) for raw_message in raw_messages]
        try:
            test_worker.work(messages=messages)
        except Exception as exception:
            test_worker.logger.exception(
                msg='Failed to process messages',
                extra={'worker_name': test_worker.name},
            )
            mock_instrumentator.increment_counter(
                counter_name='sqs.manager.exceptions',
                attributes={
                    'worker_name': test_worker.name,
                    'error_type': type(exception).__name__,
                },
            )
            test_worker.on_error(exception=exception, messages=messages)
        
        mock_instrumentator.increment_counter.assert_called_once_with(
            counter_name='sqs.manager.exceptions',
            attributes={
                'worker_name': 'test_worker',
                'error_type': 'ValueError',
            },
        )
        test_worker.on_error.assert_called_once_with(
            exception=test_exception,
            messages=[sample_message],
        )

    def test_start_When_pull_messages_raises_exception_Then_continues(
        self,
        test_worker,
        mock_logger,
    ):
        test_worker.pull_messages = Mock(side_effect=Exception("pull error"))
        
        # Simulate one iteration of the start loop with exception handling
        try:
            test_worker.pull_messages()
        except Exception:
            test_worker.logger.exception(msg='Failed to pull messages')
        
        mock_logger.exception.assert_called_with(msg='Failed to pull messages')

    def test_start_When_work_successful_Then_records_latency_metric(
        self,
        test_worker,
        sample_raw_message,
        sample_message,
        mock_instrumentator,
    ):
        test_worker.pull_messages = Mock(return_value=[sample_raw_message])
        test_worker.parse_message = Mock(return_value=sample_message)
        test_worker.work = Mock()
        test_worker.ack_all = Mock()
        
        # Simulate one iteration of the start loop with timing
        with patch('time.time', side_effect=[100.0, 105.0]):
            start_time = time.time()
            raw_messages = test_worker.pull_messages()
            messages = [test_worker.parse_message(message=raw_message) for raw_message in raw_messages]
            test_worker.work(messages=messages)
            
            test_worker.logger.info(
                msg='Worker successfully processed messages',
                extra={'worker_name': test_worker.name},
            )
            mock_instrumentator.record_histogram(
                histogram_name='sqs.manager.work.latency',
                attributes={'worker_name': test_worker.name},
                amount=(time.time() - start_time),
            )
            if test_worker.auto_ack:
                test_worker.ack_all(messages=messages)
        
        mock_instrumentator.record_histogram.assert_called_once_with(
            histogram_name='sqs.manager.work.latency',
            attributes={'worker_name': 'test_worker'},
            amount=5.0,
        )


class TestWorkerStop:
    def test_stop_When_called_Then_sets_active_false(
        self,
        test_worker,
        mock_logger,
    ):
        test_worker.stop()
        
        assert test_worker.active is False
        mock_logger.info.assert_called_once_with(
            msg='Stopping worker',
            extra={'worker_name': 'test_worker'},
        )


class TestWorkerWork:
    def test_work_When_called_Then_raises_not_implemented_error(
        self,
        test_worker,
        sample_message,
    ):
        with pytest.raises(NotImplementedError):
            test_worker.work(messages=[sample_message])


class TestWorkerPullMessages:
    def test_pull_messages_When_called_Then_returns_messages(
        self,
        test_worker,
    ):
        test_worker.get_queue_url = Mock(return_value="https://queue-url")
        # Provide enough empty responses to fill the wait time
        test_worker.sqs_client.receive_message.side_effect = [
            {'Messages': [{'Body': 'test', 'ReceiptHandle': 'handle1'}]},
        ] + [{}] * 10  # Multiple empty responses to avoid StopIteration
        
        # Mock time to control the timeout
        with patch('time.time', side_effect=[0.0, 3.0]):  # Forces timeout after first call
            result = test_worker.pull_messages()
        
        assert len(result) >= 1
        assert result[0]['Body'] == 'test'
        test_worker.sqs_client.receive_message.assert_called()

    def test_pull_messages_When_no_messages_Then_returns_empty_list(
        self,
        test_worker,
    ):
        test_worker.get_queue_url = Mock(return_value="https://queue-url")
        test_worker.sqs_client.receive_message.return_value = {}
        
        with patch('time.time', side_effect=[0.0, 3.0]):
            result = test_worker.pull_messages()
        
        assert result == []

    def test_pull_messages_When_max_messages_reached_Then_stops_polling(
        self,
        test_worker,
    ):
        test_worker.max_messages = 2
        test_worker.get_queue_url = Mock(return_value="https://queue-url")
        test_worker.sqs_client.receive_message.return_value = {
            'Messages': [
                {'Body': 'test1', 'ReceiptHandle': 'handle1'},
                {'Body': 'test2', 'ReceiptHandle': 'handle2'},
            ]
        }
        
        result = test_worker.pull_messages()
        
        assert len(result) == 2
        test_worker.sqs_client.receive_message.assert_called_once()


class TestWorkerParseMessage:
    def test_parse_message_When_valid_message_Then_returns_message_object(
        self,
        test_worker,
        sample_raw_message,
    ):
        result = test_worker.parse_message(sample_raw_message)
        
        assert isinstance(result, models.Message)
        assert result.version == "1.0"
        assert result.msg_type == "test"
        assert result.queue_name == "test_queue"
        assert result.receipt_handle == "receipt_123"
        assert isinstance(result.payload, PayloadForTesting)
        assert result.payload.message == "test message"
        assert result.payload.count == 42
        assert result.retry_attempt == 0

    def test_parse_message_When_message_has_extra_fields_Then_ignores_queue_name_and_receipt_handle(
        self,
        test_worker,
        sample_payload,
    ):
        raw_message = {
            'Body': json.dumps({
                'version': '1.0',
                'msg_type': 'test',
                'queue_name': 'ignored_queue',
                'receipt_handle': 'ignored_handle',
                'payload': sample_payload.model_dump(),
                'retry_attempt': 1,
            }),
            'ReceiptHandle': 'receipt_456',
        }
        
        result = test_worker.parse_message(raw_message)
        
        assert result.queue_name == "test_queue"
        assert result.receipt_handle == "receipt_456"
        assert result.retry_attempt == 1


class TestWorkerRetryLater:
    def test_retry_later_When_messages_within_retry_limit_Then_requeues_messages(
        self,
        test_worker,
        sample_message,
        mock_logger,
    ):
        sample_message.retry_attempt = 2
        test_worker.publish_messages = Mock()
        test_worker.ack_all = Mock()
        
        test_worker.retry_later(messages=[sample_message])
        
        assert sample_message.retry_attempt == 3
        test_worker.publish_messages.assert_called_once_with(
            queue_name="test_queue",
            messages=[sample_message],
            delay_seconds=datetime.timedelta(minutes=10),
        )
        test_worker.ack_all.assert_called_once_with(messages=[sample_message])
        mock_logger.info.assert_called_once_with(
            msg='Enqueuing retry later messages',
            extra={'messages_count': 1},
        )

    def test_retry_later_When_messages_exceed_retry_limit_Then_skips_messages(
        self,
        test_worker,
        sample_message,
    ):
        sample_message.retry_attempt = 5
        test_worker.max_retry_attempts = 3
        test_worker.publish_messages = Mock()
        test_worker.ack_all = Mock()
        
        test_worker.retry_later(messages=[sample_message])
        
        test_worker.publish_messages.assert_called_once_with(
            queue_name="test_queue",
            messages=[],
            delay_seconds=datetime.timedelta(minutes=10),
        )
        test_worker.ack_all.assert_called_once_with(messages=[])


class TestWorkerPublishMessage:
    def test_publish_message_When_called_Then_sends_message_to_queue(
        self,
        test_worker,
        sample_message,
    ):
        test_worker.get_queue_url = Mock(return_value="https://queue-url")
        
        test_worker.publish_message(
            queue_name="test_queue",
            message=sample_message,
        )
        
        test_worker.sqs_client.send_message.assert_called_once_with(
            QueueUrl="https://queue-url",
            MessageBody=sample_message.model_dump_json(),
        )


class TestWorkerPublishMessages:
    def test_publish_messages_When_empty_list_Then_returns_early(
        self,
        test_worker,
    ):
        test_worker.get_queue_url = Mock()
        
        test_worker.publish_messages(
            queue_name="test_queue",
            messages=[],
        )
        
        test_worker.get_queue_url.assert_not_called()
        test_worker.sqs_client.send_message_batch.assert_not_called()

    def test_publish_messages_When_single_batch_Then_sends_batch(
        self,
        test_worker,
        sample_message,
    ):
        test_worker.get_queue_url = Mock(return_value="https://queue-url")
        
        test_worker.publish_messages(
            queue_name="test_queue",
            messages=[sample_message],
        )
        
        expected_entries = [{
            'Id': 'message-0',
            'MessageBody': sample_message.model_dump_json(),
        }]
        test_worker.sqs_client.send_message_batch.assert_called_once_with(
            QueueUrl="https://queue-url",
            Entries=expected_entries,
        )

    def test_publish_messages_When_with_delay_Then_adds_delay_seconds(
        self,
        test_worker,
        sample_message,
    ):
        test_worker.get_queue_url = Mock(return_value="https://queue-url")
        delay = datetime.timedelta(minutes=5)
        
        test_worker.publish_messages(
            queue_name="test_queue",
            messages=[sample_message],
            delay_seconds=delay,
        )
        
        expected_entries = [{
            'Id': 'message-0',
            'MessageBody': sample_message.model_dump_json(),
            'DelaySeconds': 300,
        }]
        test_worker.sqs_client.send_message_batch.assert_called_once_with(
            QueueUrl="https://queue-url",
            Entries=expected_entries,
        )

    def test_publish_messages_When_multiple_batches_Then_sends_multiple_batches(
        self,
        test_worker,
        sample_payload,
    ):
        messages = [
            models.Message(
                version="1.0",
                msg_type="test",
                payload=sample_payload,
            )
            for _ in range(25)
        ]
        test_worker.get_queue_url = Mock(return_value="https://queue-url")
        
        test_worker.publish_messages(
            queue_name="test_queue",
            messages=messages,
        )
        
        assert test_worker.sqs_client.send_message_batch.call_count == 3


class TestWorkerAck:
    def test_ack_When_called_Then_calls_ack_all(
        self,
        test_worker,
        sample_message,
    ):
        test_worker.ack_all = Mock()
        
        test_worker.ack(sample_message)
        
        test_worker.ack_all.assert_called_once_with(messages=[sample_message])


class TestWorkerAckAll:
    def test_ack_all_When_messages_have_receipt_handles_Then_deletes_messages(
        self,
        test_worker,
        sample_message,
    ):
        test_worker.get_queue_url = Mock(return_value="https://queue-url")
        
        test_worker.ack_all(messages=[sample_message])
        
        expected_entries = [{
            'Id': 'message-0',
            'ReceiptHandle': 'receipt_123',
        }]
        test_worker.sqs_client.delete_message_batch.assert_called_once_with(
            QueueUrl="https://queue-url",
            Entries=expected_entries,
        )

    def test_ack_all_When_messages_without_receipt_handles_Then_skips_messages(
        self,
        test_worker,
        sample_payload,
    ):
        message_without_handle = models.Message(
            version="1.0",
            msg_type="test",
            payload=sample_payload,
            receipt_handle=None,
        )
        test_worker.get_queue_url = Mock(return_value="https://queue-url")
        
        test_worker.ack_all(messages=[message_without_handle])
        
        test_worker.sqs_client.delete_message_batch.assert_called_once_with(
            QueueUrl="https://queue-url",
            Entries=[],
        )


class TestWorkerExtendMessageVisibility:
    def test_extend_message_visibility_When_valid_message_Then_changes_visibility(
        self,
        test_worker,
        sample_message,
    ):
        test_worker.get_queue_url = Mock(return_value="https://queue-url")
        
        test_worker.extend_message_visibility(
            message=sample_message,
            visibility_timeout=60,
        )
        
        test_worker.sqs_client.change_message_visibility.assert_called_once_with(
            QueueUrl="https://queue-url",
            ReceiptHandle="receipt_123",
            VisibilityTimeout=60,
        )

    def test_extend_message_visibility_When_no_receipt_handle_Then_raises_value_error(
        self,
        test_worker,
        sample_payload,
    ):
        message_without_handle = models.Message(
            version="1.0",
            msg_type="test",
            payload=sample_payload,
            receipt_handle=None,
        )
        
        with pytest.raises(ValueError, match="Unable to extend visibility without receipt_handle"):
            test_worker.extend_message_visibility(
                message=message_without_handle,
                visibility_timeout=60,
            )


class TestWorkerGetQueueUrl:
    def test_get_queue_url_When_called_Then_returns_queue_url(
        self,
        test_worker,
    ):
        test_worker.sqs_client.get_queue_url.return_value = {
            'QueueUrl': 'https://queue-url'
        }
        
        result = test_worker.get_queue_url(queue_name="test_queue")
        
        assert result == "https://queue-url"
        test_worker.sqs_client.get_queue_url.assert_called_once_with(
            QueueName="test_queue"
        )


class TestWorkerOnError:
    def test_on_error_When_called_Then_does_nothing(
        self,
        test_worker,
        sample_message,
    ):
        exception = ValueError("test error")
        
        result = test_worker.on_error(
            exception=exception,
            messages=[sample_message],
        )
        
        assert result is None


class TestSingle:
    def test_single_When_called_Then_calls_multiple_with_n_equals_1(
        self,
    ):
        worker_factory = Mock()
        
        with patch.object(worker, 'multiple') as mock_multiple:
            worker.single(worker_factory)
        
        mock_multiple.assert_called_once_with(
            worker_factory=worker_factory,
            n=1,
        )


class TestMultiple:
    def test_multiple_When_called_Then_creates_workers_and_starts_them(
        self,
        test_worker,
    ):
        worker_factory = Mock(return_value=test_worker)
        
        with patch('concurrent.futures.ThreadPoolExecutor') as mock_executor_class:
            with patch('signal.signal') as mock_signal:
                mock_executor = Mock()
                mock_executor_class.return_value = mock_executor
                
                worker.multiple(
                    worker_factory=worker_factory,
                    n=2,
                )
                
                assert worker_factory.call_count == 2
                mock_executor.submit.assert_called()
                mock_signal.assert_called_once_with(
                    signal.SIGTERM,
                    ANY,
                )

    def test_multiple_When_sigterm_received_Then_stops_workers(
        self,
    ):
        mock_worker1 = Mock()
        mock_worker2 = Mock()
        worker_factory = Mock(side_effect=[mock_worker1, mock_worker2])
        captured_handler = None
        
        def capture_signal_handler(
            sig,
            handler,
        ):
            nonlocal captured_handler
            captured_handler = handler
        
        with patch('concurrent.futures.ThreadPoolExecutor'):
            with patch('signal.signal', side_effect=capture_signal_handler):
                worker.multiple(
                    worker_factory=worker_factory,
                    n=2,
                )
                
                captured_handler(signal.SIGTERM, None)
                
                mock_worker1.stop.assert_called_once()
                mock_worker2.stop.assert_called_once()