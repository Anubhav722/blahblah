# Django Imports
from django.contrib.auth.models import User
from rest_framework.throttling import UserRateThrottle
# App Imports
from .serializers import UserSerializer
from jarvis.core.rest.permissions import IsAuthenticated

# DRF Imports
from rest_framework.response import Response
from rest_framework import status, generics


class UserView(generics.GenericAPIView):
    # throttle_classes = (UserRateThrottle,)
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            instance.profile.client = request.client
            instance.profile.save()
            response_data = {
                'label': instance.profile.label,
                'token': instance.auth_token.key
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
