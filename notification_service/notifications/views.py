from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import Notification
from .serializers import NotificationSerializer

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [AllowAny]  

    def get_queryset(self):
        user_id = self.request.headers.get('X-User-ID')
        if user_id:
            return Notification.objects.filter(user_id=int(user_id))
        return Notification.objects.none()
