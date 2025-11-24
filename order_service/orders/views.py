from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework import serializers
from .models import Order
from .serializers import OrderSerializer
import pika
import json
from django.conf import settings

RABBITMQ_HOST = getattr(settings, 'RABBITMQ_HOST', 'localhost')

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        # Filter orders by user_id from JWT token (passed via header by API Gateway)
        user_id = self.request.headers.get('X-User-ID')
        if user_id:
            return Order.objects.filter(user_id=int(user_id))
        return Order.objects.none()

    def perform_create(self, serializer):
        # Extract user_id from header (set by API Gateway after JWT validation)
        user_id = self.request.headers.get('X-User-ID')
        if not user_id:
            raise serializers.ValidationError({"error": "User ID not found in request"})
        
        # Save the order with user_id from JWT
        order = serializer.save(user_id=int(user_id))

        # Publish event to RabbitMQ
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        channel = connection.channel()
        channel.queue_declare(queue='order_created')
        
        event = {
            'event': 'order_created',
            'order_id': order.id,
            'user_id': order.user_id,
            'product_name': order.product_name,
            'quantity': order.quantity
        }

        channel.basic_publish(exchange='',routing_key='order_created',body=json.dumps(event))
        connection.close()
