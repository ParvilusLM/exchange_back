from django.db.models import query
from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404
from .models import *
from .serializers import *
from drf_spectacular.utils import extend_schema
import random
import string
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
from rest_framework import viewsets, parsers, renderers, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.compat import coreapi, coreschema
from rest_framework.schemas import ManualSchema
from rest_framework.schemas import coreapi as coreapi_schema
from rest_framework.permissions import  IsAuthenticated, IsAdminUser
from rest_framework import filters
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.pagination import PageNumberPagination
from rest_framework.authentication import TokenAuthentication
from rest_framework import generics
from rest_framework.exceptions import NotFound
from django.db import transaction as db_transaction




# Create your views here.
class TauxDeChangeViewSet(viewsets.ViewSet):

    @extend_schema(
        responses= TauxDeChangeSerializer,
        description="Liste des taux de change",
    )
    def list(self, request):
        queryset = TauxDeChange.objects.all()
        serializer = TauxDeChangeSerializer(queryset, many=True)
        return Response(serializer.data)
    

    @extend_schema(
        responses= TauxDeChangeSerializer,
        description="Récupérer un taux de change par ID",
    )
    def retrieve(self, request, pk=None):
        queryset = TauxDeChange.objects.all()
        tauxDeChange = get_object_or_404(queryset, pk=pk)
        serializer = TauxDeChangeSerializer(tauxDeChange)
        return Response(serializer.data)
    

    @extend_schema(
            description="La creation d'un taux de change est reservée à l'administrateur via l'admin django",
            responses= TauxDeChangeSerializer,
    )
    def create(self, request):
        pass


    @extend_schema(
            description="La modification d'un taux de change est reservée à l'administrateur via l'admin django",
            responses= TauxDeChangeSerializer,
    )
    def update(self, request, pk=None):
        pass
    

    @extend_schema(
        description="La suppression d'un taux de change est reservée à l'administrateur via l'admin django",
        responses= TauxDeChangeSerializer,
    )
    def destroy(self, request, pk=None):
        pass	


    def get_permissions(self):
        if self.action == 'update' or self.action == 'destroy' or self.action == 'create':
            permission_classes = [IsAdminUser]
        else:
            permission_classes = []
        return [permission() for permission in permission_classes]


#...
class ObtainAuthToken(APIView):
    throttle_class = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_class = (renderers.JSONRenderer,)
    serializer_class = MyAuthTokenSerializer

    if coreapi_schema.is_enabled() :
        schema = ManualSchema(
            fields=[
                coreapi.Field(
                    name="email",
                    required=True,
                    location='form',
                    schema=coreschema.String(
                        title="Email",
                        description="Valid email for authentication",
                    ),
                ),
                coreapi.Field(
                    name="password",
                    required=True,
                    location='form',
                    schema=coreschema.String(
                        title="Password",
                        description="Valid password for authentication",
                    ),
                ),
            ],
            encoding="application/json",
        )

    def get_serializer_context(self):
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        }

    def get_serializer(self, *args, **kwargs):
        kwargs['context'] = self.get_serializer_context()
        return self.serializer_class(*args, **kwargs)


    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})				


obtain_auth_token = ObtainAuthToken.as_view()


#...
class UserViewSet(viewsets.ViewSet):
    
    
    @extend_schema(
        responses= UserSerializer,
        description="Liste des utilisateurs",
    ) 
    def list(self, request):
        queryset = Utilisateur.objects.all()
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        responses= UserSerializer,
        description="Récupérer un utilisateur par ID",
    )
    def retrieve(self, request, pk=None):
        if pk == 'me':
            user = request.user
            serializer = UserSerializer(user)
            return Response(serializer.data)
        else:
            queryset = Utilisateur.objects.all()
            user = get_object_or_404(queryset, pk=pk)
            serializer = UserSerializer(user)
            return Response(serializer.data) 
        
    
    @extend_schema(
        responses= UserSerializer,
        description="Créer un utilisateur",
    )
    def create(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)	

    
    @extend_schema(
        responses= UserSerializer,
        description="Modifier un utilisateur par ID",
    )
    def update(self, request, pk=None):
        try:
            utilisateur = Utilisateur.objects.get(pk=pk)
        except Utilisateur.DoesNotExist:
            return Response({'response': 'Aucun utilisateur'},status= status.HTTP_404_NOT_FOUND)
        
        if utilisateur != request.user:
            return Response({'response': 'Ce compte ne vous appartient pas donc vous ne pouvez pas le modifier'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserSerializer(utilisateur, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
    @extend_schema(
        responses= UserSerializer,
        description="Supprimer un utilisateur par ID",
    )
    def destroy(self, request, pk=None):
        try:
            utilisateur = Utilisateur.objects.get(pk=pk)
        except Utilisateur.DoesNotExist:
            return Response({'response': 'Aucun utilisateur'},status= status.HTTP_404_NOT_FOUND)

        user = request.user
        if utilisateur != user:
            return Response({'response': 'Ce compte ne vous appartient pas donc vous pouvez pas le supprimer'}, status=status.HTTP_400_BAD_REQUEST)

            
        operation = utilisateur.delete()
        data = {}
        if operation:
            data["success"] = "suppression reussie"
        else:
            data["faillure"] = "suppression echouee"
        return Response(data=data)	
                 

    def get_permissions(self):
        if self.action== 'retrieve' or self.action == 'update' or self.action == 'destroy':
            permission_classes = [IsAuthenticated]
        elif self.action == 'list':
            permission_classes = [IsAdminUser]
        else:
            permission_classes = []
        return [permission() for permission in permission_classes]



#...
class HistoriqueTauxDeChangeViewSet(viewsets.ViewSet):
    
    @extend_schema(
        responses= HistoriqueTauxDeChangeSerializer,
        description="Liste des historiques de taux de change",
    )
    def list(self, request):
        queryset = HistoriqueTauxDeChange.objects.all()
        serializer = HistoriqueTauxDeChangeSerializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        responses= HistoriqueTauxDeChangeSerializer,
        description="Récupérer un historique de taux de change par ID",
    )
    def retrieve(self, request, pk=None):
        queryset = HistoriqueTauxDeChange.objects.all()
        historique = get_object_or_404(queryset, pk=pk)
        serializer = HistoriqueTauxDeChangeSerializer(historique)
        return Response(serializer.data)
    

    @extend_schema(
        responses= HistoriqueTauxDeChangeSerializer,
        description="L'historique est créé automatiquement lors de la création d'un utilisateur",
    )
    def create(self, request):
        pass

    @extend_schema(
        responses= HistoriqueTauxDeChangeSerializer,
        description="La modification d'un historique de taux de change est réservée à l'administrateur via l'admin django",
    )
    def update(self, request, pk=None):
        pass

    @extend_schema(
        responses= HistoriqueTauxDeChangeSerializer,
        description="La suppression d'un historique de taux de change est réservée à l'administrateur via l'admin django",
    )
    def destroy(self, request, pk=None):
        pass

    def get_permissions(self):
        if self.action== 'retrieve' or self.action == 'update' or self.action == 'destroy':
            permission_classes = [IsAuthenticated]
        elif self.action == 'list':
            permission_classes = [IsAdminUser]
        else:
            permission_classes = []
        return [permission() for permission in permission_classes]


#...
class ConversionDeDeviseViewSet(viewsets.ViewSet):
    
    @extend_schema(
        responses= ConversionDeDeviseSerializer,
        description="Liste des conversions de devise",
    )
    def list(self, request):
        queryset = ConversionDeDevise.objects.all()
        serializer = ConversionDeDeviseSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        responses= ConversionDeDeviseSerializer,
        description="Récupérer une conversion de devise par ID",
    )
    def retrieve(self, request, pk=None):
        queryset = ConversionDeDevise.objects.all()
        conversion = get_object_or_404(queryset, pk=pk)
        serializer = ConversionDeDeviseSerializer(conversion)
        return Response(serializer.data)
    

    @extend_schema(
        responses= ConversionDeDeviseSerializer,
        description="Créer une conversion de devise",
    )
    def create(self, request):
        # Vérification de l'utilisateur authentifié
        user = request.user
        if not user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Vérification de l'historique de l'utilisateur
        historique = HistoriqueTauxDeChange.objects.filter(utilisateur_id=user.id).first()
        if not historique:
            return Response({'error': 'Aucune historique trouvé'}, status=status.HTTP_404_NOT_FOUND)
        
        # Verifier si l'utilisateur possede l'historique de la requete
        historique_id = request.data.get('historique_id')
        if historique_id != historique.id:
            return Response({'error': 'Cet historique ne vous appartient pas'}, status=status.HTTP_403_FORBIDDEN)



        serializer = ConversionDeDeviseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @extend_schema(
        responses= ConversionDeDeviseSerializer,
        description="La modification d'une conversion de devise est réservée à l'administrateur via l'admin django",
    )
    def update(self, request, pk=None):
        pass

    @extend_schema(
        responses= ConversionDeDeviseSerializer,
        description="Supprimer une conversion de devise par ID",
    )
    def destroy(self, request, pk=None):
        try:
            conversion = ConversionDeDevise.objects.get(pk=pk)
        except ConversionDeDevise.DoesNotExist:
            return Response({'response': 'Aucune conversion'},status= status.HTTP_404_NOT_FOUND)

        user = request.user
        if conversion.historique_id.utilisateur_id.id != user.id:
            return Response({'response': 'Cette conversion ne vous appartient pas donc vous ne pouvez pas la supprimer'}, status=status.HTTP_400_BAD_REQUEST)

            
        operation = conversion.delete()
        data = {}
        if operation:
            data["success"] = "suppression reussie"
        else:
            data["faillure"] = "suppression echouee"
        return Response(data=data)


    def get_permissions(self):
        if self.action== 'retrieve' or self.action == 'update' or self.action == 'destroy':
            permission_classes = [IsAuthenticated]
        elif self.action == 'list':
            permission_classes = [IsAdminUser]
        else:
            permission_classes = []
        return [permission() for permission in permission_classes]