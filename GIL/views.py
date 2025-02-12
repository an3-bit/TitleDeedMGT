from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from django.utils.decorators import method_decorator
from .models import (
    TitleTransferTypes, TitleProcess, Client,
    Surveyor, Payment, TitleDocument, User
)
from .serializers import (
    TitleTransferTypesSerializer, TitleProcessSerializer,
    ClientSerializer, SurveyorSerializer,
    PaymentSerializer, TitleDocumentSerializer, UserSerializer, LoginSerializer
)

class UserRegistrationView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            # Get the validated user object
            user = serializer.validated_data['user']
            
            # Generate tokens for the user
            refresh = RefreshToken.for_user(user)
            update_last_login(None, user)  # Update last login timestamp

            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TitleTransferTypesViewSet(viewsets.ModelViewSet):
    queryset = TitleTransferTypes.objects.all()
    serializer_class = TitleTransferTypesSerializer
    permission_classes = [permissions.IsAuthenticated]

class TitleProcessViewSet(viewsets.ModelViewSet):
    queryset = TitleProcess.objects.all()
    serializer_class = TitleProcessSerializer
    permission_classes = [permissions.IsAuthenticated]

class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['get'])
    def documents(self, request, pk=None):
        client = self.get_object()
        documents = TitleDocument.objects.filter(client=client)
        serializer = TitleDocumentSerializer(documents, many=True)
        return Response(serializer.data)

class SurveyorViewSet(viewsets.ModelViewSet):
    queryset = Surveyor.objects.all()
    serializer_class = SurveyorSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def toggle_status(self, request, pk=None):
        surveyor = self.get_object()
        surveyor.is_serving = not surveyor.is_serving
        surveyor.status = "active" if surveyor.is_serving else "inactive"
        surveyor.save()
        return Response({'status': surveyor.status})

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

class TitleDocumentViewSet(viewsets.ModelViewSet):
    queryset = TitleDocument.objects.all()
    serializer_class = TitleDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
