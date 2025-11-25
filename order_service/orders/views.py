from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework import serializers
from .models import Order
from .serializers import OrderSerializer
import pika
import json
import os
import time
from django.conf import settings

# Get RabbitMQ host from environment variable, default to 'localhost' for local development
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        # Filter orders by user_id from JWT token (passed via header by API Gateway)
        user_id = self.request.headers.get('X-User-ID')
        if user_id:
            return Order.objects.filter(user_id=int(user_id))
        return Order.objects.none()

    def _publish_to_rabbitmq(self, event, max_retries=3, retry_delay=1):
        for attempt in range(max_retries):
            try:
                connection = pika.BlockingConnection(
                    pika.ConnectionParameters(
                        host=RABBITMQ_HOST,
                        connection_attempts=3,
                        retry_delay=2
                    )
                )
                channel = connection.channel()
                channel.queue_declare(queue='order_created')
                channel.basic_publish(exchange='', routing_key='order_created', body=json.dumps(event))
                connection.close()
                return True
            except pika.exceptions.AMQPConnectionError as e:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                else:
                    # Log error but don't fail the order creation
                    print(f"Failed to publish to RabbitMQ after {max_retries} attempts: {e}")
                    return False
            except Exception as e:
                print(f"Error publishing to RabbitMQ: {e}")
                return False
        return False

    def perform_create(self, serializer):
        # Extract user_id from header (set by API Gateway after JWT validation)
        user_id = self.request.headers.get('X-User-ID')
        if not user_id:
            raise serializers.ValidationError({"error": "User ID not found in request"})
        
        # Save the order with user_id from JWT
        order = serializer.save(user_id=int(user_id))

        # Publish event to RabbitMQ (with retry logic, but don't fail order creation if it fails)
        event = {
            'event': 'order_created',
            'order_id': order.id,
            'user_id': order.user_id,
            'product_name': order.product_name,
            'quantity': order.quantity
        }
        
        self._publish_to_rabbitmq(event)
