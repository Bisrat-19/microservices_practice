import pika
import json
import os
import sys
import django
import time

# Add the parent directory to Python path so Django can find the settings module
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'notification_service.settings')
django.setup()

from notifications.models import Notification

# Get RabbitMQ host from environment variable, default to 'localhost' for local development
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')

def callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        user_id = data['user_id']
        product_name = data['product_name']
        quantity = data['quantity']

        message = f"Your order #{data['order_id']} for {quantity} x {product_name} has been created."

        Notification.objects.create(user_id=user_id, message=message)
        print(f"Notification saved for user {user_id}")
    except Exception as e:
        print(f"Error processing notification: {e}")

def connect_to_rabbitmq(max_retries=30, retry_delay=2):
    """Connect to RabbitMQ with retry logic"""
    for attempt in range(max_retries):
        try:
            print(f"Attempting to connect to RabbitMQ at {RABBITMQ_HOST} (attempt {attempt + 1}/{max_retries})...")
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=RABBITMQ_HOST,
                    connection_attempts=3,
                    retry_delay=2
                )
            )
            channel = connection.channel()
            channel.queue_declare(queue='order_created')
            print(f"Successfully connected to RabbitMQ at {RABBITMQ_HOST}")
            return connection, channel
        except pika.exceptions.AMQPConnectionError as e:
            if attempt < max_retries - 1:
                print(f"Connection failed: {e}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print(f"Failed to connect to RabbitMQ after {max_retries} attempts")
                raise
        except Exception as e:
            print(f"Unexpected error: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                raise

if __name__ == '__main__':
    try:
        # Connect to RabbitMQ with retry logic
        connection, channel = connect_to_rabbitmq()
        
        # Set up consumer
        channel.basic_consume(queue='order_created', on_message_callback=callback, auto_ack=True)
        
        print("Listening for order_created events...")
        channel.start_consuming()
    except KeyboardInterrupt:
        print("\nShutting down consumer...")
        if 'connection' in locals() and not connection.is_closed:
            connection.close()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
