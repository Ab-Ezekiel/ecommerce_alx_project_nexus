# ecommerce_nexus/accounts/serializers.py
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True, label="Confirm password")

    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "password2")
        extra_kwargs = {
            "email": {"required": True},
            "username": {"required": True},
        }

    def validate(self, attrs):
        pw = attrs.get("password")
        pw2 = attrs.pop("password2", None)
        if pw != pw2:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        # run Django validators (length, common password, numeric)
        validate_password(pw, user=get_user_model())
        return attrs

    def create(self, validated_data):
        User = get_user_model()
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
