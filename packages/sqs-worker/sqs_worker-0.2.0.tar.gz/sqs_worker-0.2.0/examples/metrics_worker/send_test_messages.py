#!/usr/bin/env python3
"""
Script to send test messages to the SQS queue to generate metrics.
Run this after starting the docker-compose stack.
"""

import boto3
import json
import time
import random
import sys

def main():
    # Configure SQS client for LocalStack
    sqs_client = boto3.client(
        'sqs',
        endpoint_url='http://localhost:4566',
        region_name='us-east-1',
        aws_access_key_id='test',
        aws_secret_access_key='test',
    )
    
    queue_name = 'worker-queue'
    
    try:
        # Get queue URL
        response = sqs_client.get_queue_url(QueueName=queue_name)
        queue_url = response['QueueUrl']
        print(f"Found queue: {queue_url}")
    except Exception as e:
        print(f"Error getting queue URL: {e}")
        print("Make sure the docker-compose stack is running and the queue is created.")
        sys.exit(1)
    
    # Send test messages
    message_count = 50
    print(f"Sending {message_count} test messages...")
    
    for i in range(message_count):
        message_body = json.dumps({
            "version": "1.0",
            "msg_type": "test",
            "payload": {
                "value": f"Test message {i + 1}"
            }
        })
        
        try:
            sqs_client.send_message(
                QueueUrl=queue_url,
                MessageBody=message_body
            )
            print(f"Sent message {i + 1}/{message_count}")
            
            # Random delay between messages
            time.sleep(random.uniform(0.1, 0.5))
            
        except Exception as e:
            print(f"Error sending message {i + 1}: {e}")
    
    print("Finished sending messages!")
    print("\nYou can now check the metrics at:")
    print("- Prometheus: http://localhost:9091")
    print("- Grafana: http://localhost:3000 (admin/admin)")

if __name__ == "__main__":
    main()
