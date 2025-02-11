from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    TitleTransferTypes, TitleProcess, Client,
    Surveyor, Payment, TitleDocument, User
)


class UserSerializer (serializers.ModelSerializer):
    password= serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'first_name', 'last_name')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class TitleTransferTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TitleTransferTypes
        fields = '__all__'
class TitleProcessSerializer(serializers.ModelSerializer):
    class Meta:
        model = TitleProcess
        fields = '__all__'
class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'
class SurveyorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Surveyor
        fields = '__all__'
class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
class TitleDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TitleDocument
        fields = '__all__'