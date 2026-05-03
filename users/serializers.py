from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model  = User
        fields = ['email', 'full_name', 'phone', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            email     = validated_data['email'],
            password  = validated_data['password'],
            full_name = validated_data['full_name'],
            phone     = validated_data.get('phone', ''),
        )
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ['id', 'email', 'full_name', 'phone', 'created_at']
        read_only_fields = ['id', 'email', 'created_at']