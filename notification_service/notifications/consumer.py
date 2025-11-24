import pika
import json
import os
import sys
import django

# Add the parent directory to Python path so Django can find the settings module
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'notification_service.settings')
django.setup()

from notifications.models import Notification

RABBITMQ_HOST = 'localhost' 

def callback(ch, method, properties, body):
    data = json.loads(body)
    user_id = data['user_id']
    product_name = data['product_name']
    quantity = data['quantity']

    message = f"Your order #{data['order_id']} for {quantity} x {product_name} has been created."

    Notification.objects.create(user_id=user_id, message=message)
    print(f"Notification saved for user {user_id}")

# Connect to RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
channel = connection.channel()
channel.queue_declare(queue='order_created')
channel.basic_consume(queue='order_created', on_message_callback=callback, auto_ack=True)

print("Listening for order_created events...")
channel.start_consuming()
