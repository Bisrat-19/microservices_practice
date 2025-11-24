from rest_framework import viewsets, status
from rest_framework.response import Response
from .serializers import RegisterSerializer
from rest_framework.decorators import action
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import AllowAny

class AuthViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=['get', 'post'], permission_classes=[AllowAny])
    def validate(self, request):
        """
        JWT validation endpoint for Nginx auth_request module.
        Validates the JWT token and returns user info in response headers.
        """
        jwt_auth = JWTAuthentication()
        try:
            # Extract and validate JWT token
            header = jwt_auth.get_header(request)
            if header is None:
                return Response({"error": "No authorization header"}, status=status.HTTP_401_UNAUTHORIZED)
            
            raw_token = jwt_auth.get_raw_token(header)
            if raw_token is None:
                return Response({"error": "Invalid token format"}, status=status.HTTP_401_UNAUTHORIZED)
            
            validated_token = jwt_auth.get_validated_token(raw_token)
            user = jwt_auth.get_user(validated_token)
            
            # Return success with user info in headers
            response = Response(status=status.HTTP_200_OK)
            response['X-User-ID'] = str(user.id)
            response['X-Username'] = user.username
            return response
            
        except Exception as e:
            return Response({"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
