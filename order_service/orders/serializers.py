from rest_framework import serializers
from .models import Order

class OrderSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)  # Set from JWT token via header
    
    class Meta:
        model = Order
        fields = ['id', 'user_id', 'product_name', 'quantity', 'created_at']
