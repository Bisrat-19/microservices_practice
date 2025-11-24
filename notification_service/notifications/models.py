from django.db import models

class Notification(models.Model):
    user_id = models.IntegerField()  # user who will receive the notification
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for User {self.user_id}: {self.message}"
