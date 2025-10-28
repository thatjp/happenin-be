from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from .models import User, UserProfile
from .serializers import (
    UserSerializer, UserProfileSerializer, UserRegistrationSerializer,
    UserLoginSerializer, ChangePasswordSerializer
)
from .utils import success_response, error_response


class UserRegistrationView(generics.CreateAPIView):
    """API view for user registration"""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Create auth token
        token, created = Token.objects.get_or_create(user=user)
        
        return success_response(
            data={
                'user': UserSerializer(user).data,
                'token': token.key
            },
            message='User registered successfully',
            status_code=status.HTTP_201_CREATED
        )


class UserLoginView(APIView):
    """API view for user login"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        
        # Get or create auth token
        token, created = Token.objects.get_or_create(user=user)
        
        return success_response(
            data={
                'user': UserSerializer(user).data,
                'token': token.key
            },
            message='Login successful'
        )


class UserLogoutView(APIView):
    """API view for user logout"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        # Delete auth token - this is all we need for token-based auth
        try:
            if hasattr(request.user, 'auth_token') and request.user.auth_token:
                request.user.auth_token.delete()
        except Exception as e:
            # Log the error but don't fail the logout
            print(f"Token deletion error: {e}")
        
        return success_response(
            message='Logout successful'
        )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """API view for user profile"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return success_response(data=serializer.data, message='Profile updated successfully')
    
    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


class UserProfileUpdateView(generics.UpdateAPIView):
    """API view for updating user profile"""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user.profile
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return success_response(data=serializer.data, message='Profile updated successfully')
    
    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


class ChangePasswordView(APIView):
    """API view for changing password"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        # Delete old token and create new one
        try:
            user.auth_token.delete()
        except:
            pass
        token, created = Token.objects.get_or_create(user=user)
        
        return success_response(
            data={'token': token.key},
            message='Password changed successfully'
        )


class UserDashboardView(APIView):
    """API view for user dashboard"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        return success_response(
            data={
                'user': UserSerializer(user).data,
                'stats': {
                    'member_since': user.date_joined,
                    'last_login': user.last_login,
                    'is_verified': user.is_verified,
                }
            }
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_list(request):
    """API view for listing users (admin only)"""
    if not request.user.is_staff:
        return error_response('Permission denied', status_code=status.HTTP_403_FORBIDDEN)
    
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return success_response(data=serializer.data)
