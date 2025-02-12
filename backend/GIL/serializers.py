from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from .models import (
    TitleTransferTypes, TitleProcess, Client,
    Surveyor, Payment, TitleDocument, User
)
class UserSerializer(serializers.ModelSerializer):
    name = serializers.CharField(write_only=True, required=True)  # Temporary field for frontend

    class Meta:
        model = User
        fields = ['id', 'name', 'username', 'email', 'password', 'first_name', 'last_name']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_name(self, value):
        """Ensure that the name field contains at least two parts."""
        name_parts = value.strip().split()
        if len(name_parts) < 2:
            raise serializers.ValidationError("Please enter both first and last name.")
        return value

    def create(self, validated_data):
        name = validated_data.pop('name')
        name_parts = name.strip().split(" ")
        validated_data['first_name'] = name_parts[0]
        validated_data['last_name'] = " ".join(name_parts[1:])  # Everything after first name

        user = User.objects.create_user(**validated_data)
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        try:
            # Get user by email
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password.")

        # Check password
        if not user.check_password(password):
            raise serializers.ValidationError("Invalid email or password.")

        # Ensure the user is active
        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")

        return {
             'email': email,
            'user': user
        }


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
