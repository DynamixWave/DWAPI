from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from accounts.models import User

class CustomTokenObtainPairSerializer(serializers.Serializer):
    login =serializers.CharField()
    password = serializers.CharField(style={"input_type":"password"})

    def validate(self, attrs):
        login = attrs.get("login")
        password = attrs.get("password")

        user = authenticate(
            request = self.context.get("request"),
            username = login,
            password = password,
        )
        if not user:
            raise AuthenticationFailed(
                _("Invalid username/email/phone or password"), code="authorization"
            )
        if not user.is_active:
            raise AuthenticationFailed(_("Account is disabled."), code="authorization")
        
        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])
        user.refresh_from_db(fields=["last_login"])  # memory ထဲကို sync

        refresh = RefreshToken.for_user(user)
        
        return {
            "refresh": str(refresh),
            "access" : self(refresh.access_token),
            "message": "Login successful",
            "user": {
                "id"    :   user.id,
                "username" : user.username,
                "email": user.email,
                "phone": user.phone,
                "date_joined" : user.date_joined,
                "last_login" : user.last_login
            }
        }
    
class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={"input_type":"password"})
    confirm_password = serializers.CharField(write_only=True, style={"input_type":"password"})

    class Meta:
        model = User
        fields = ["username", "email", "phone", "password", "confirm_password"]

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match !"})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop("confirm_password")
        user = User.objects.create_user(
            username = validated_data["username"],
            email = validated_data["email"],
            phone = validated_data["phone"],
            password = validated_data["password"],
        )
        return user