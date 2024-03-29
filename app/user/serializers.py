from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for Users"""

    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'name')
        extra_kwargs = {'password': {'write_only': 'True', 'min_length': 4}}

    def create(self, validated_data):
        """Create user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update user password correctly and returning it"""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerialiser(serializers.Serializer):
    """Authantication Token Serializer for Objects"""
    email = serializers.CharField()
    password = serializers.CharField(
                style={'input_type': 'password'},
                trim_whitespace=False
    )

    def validate(self, attrs):
        """Validate and Authenticate the user"""
        email = attrs['email']
        password = attrs['password']

        user = authenticate(
                request=self.context.get('request'),
                email=email,
                password=password
        )

        if not user:
            msg = _("Unable to proceed with provided credentials")
            raise serializers.ValidationError(msg, code='authentication')

        attrs['user'] = user
        return attrs
