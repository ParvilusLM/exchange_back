from rest_framework import serializers
from django.db.models import fields
from .models import *
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _


#...
class MyAuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField(
        label=_("Email"),
        write_only= True
        )
    password = serializers.CharField(
        label=_("Password",),
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only= True
    )

    token = serializers.CharField(
        label = _("Token"),
        read_only=True
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'),
                                email=email, password=password)

            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)
            if not user:
                msg = _('Unable to log in with provided credentials. Oupss')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "username" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


#
class ConversionDeDeviseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConversionDeDevise
        fields = '__all__'

#...
class HistoriqueTauxDeChangeSerializer(serializers.ModelSerializer):
    conversions = ConversionDeDeviseSerializer(many=True, read_only=True)

    class Meta:
        model = HistoriqueTauxDeChange
        fields = ['id', 'utilisateur_id', 'cree_le', 'conversions']

#...
class UserSerializer(serializers.ModelSerializer):
    historique = HistoriqueTauxDeChangeSerializer(many=False, read_only=True)

    class Meta:
        model = Utilisateur
        fields = ['id','email', 'pseudo', 'password', 'cree_le', 'historique']
        extra_kwargs = {'password': {'write_only': True, 'required': True}}

    def create(self, validated_data):
        user = Utilisateur.objects.create_user(**validated_data)
        Token.objects.create(user=user)
        return user 



#...
class TauxDeChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TauxDeChange
        fields = '__all__'


