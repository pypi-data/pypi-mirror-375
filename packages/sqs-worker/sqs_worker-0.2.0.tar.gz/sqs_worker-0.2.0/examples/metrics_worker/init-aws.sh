#!/bin/bash

# Wait for LocalStack to be ready
echo "Waiting for LocalStack to start..."
until awslocal sqs list-queues > /dev/null 2>&1; do
    echo "Waiting for LocalStack SQS service..."
    sleep 2
done

echo "LocalStack is ready. Creating queue and sending messages..."

# Create the queue
awslocal sqs create-queue --queue-name worker-queue

# Send test messages
awslocal sqs send-message \
    --queue-url http://localhost:4566/000000000000/worker-queue \
    --message-body '{"version": "1.0", "msg_type": "greeting", "payload": {"value": "Hello - message 1"}}'

awslocal sqs send-message \
    --queue-url http://localhost:4566/000000000000/worker-queue \
    --message-body '{"version": "1.0", "msg_type": "greeting", "payload": {"value": "Hello - message 2"}}'

awslocal sqs send-message \
    --queue-url http://localhost:4566/000000000000/worker-queue \
    --message-body '{"version": "1.0", "msg_type": "greeting", "payload": {"value": "Hello - message 3"}}'

awslocal sqs send-message \
    --queue-url http://localhost:4566/000000000000/worker-queue \
    --message-body '{"version": "1.0", "msg_type": "greeting", "payload": {"value": "Hello - message 3"}}'

echo "Queue created and messages sent successfully!"
