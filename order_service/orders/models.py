from django.db import models

class Order(models.Model):
    user_id = models.IntegerField()  # store user_id from JWT
    product_name = models.CharField(max_length=255)
    quantity = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} by User {self.user_id}"
