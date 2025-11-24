from rest_framework.routers import DefaultRouter
from .views import OrderViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r'', OrderViewSet, basename='orders')

urlpatterns = [
    path('', include(router.urls)),
]
