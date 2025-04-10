from django.db.models.deletion import CASCADE
from django.db.models.signals import pre_save, pre_delete, post_save, post_delete
from django.conf import settings
from django.db import models, transaction as db_transaction
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, Group, Permission, PermissionsMixin, BaseUserManager
from django.contrib.postgres.fields import ArrayField
from django.utils.crypto import get_random_string
from django.core.validators import RegexValidator
import string
import random
from django.dispatch import receiver
from django.utils.text import slugify
import secrets
import uuid
from django.db.models import Sum
from rest_framework import serializers
from datetime import timedelta
import logging

# Configure logger
logger = logging.getLogger(__name__)



def generate_slug(instance, new_slug=None, modele=None):
    slug = slugify(instance.nom)
    if new_slug is not None:
        slug = new_slug
    qs = modele.objects.filter(slug=slug).order_by("-id")
    exists = qs.exists()
    if exists:
        new_slug = f"{slug}-{qs.first().id}"
        return generate_slug(instance, new_slug=new_slug, modele=modele)
    return slug


def generate_slug_2(slug='', new_slug=None, modele=None):
    slug_t = slugify(slug)
    if new_slug is not None:
        slug_t = new_slug
    qs = modele.objects.filter(slug=slug_t).order_by("-id")
    exists = qs.exists()
    if exists:
        new_slug = f"{slug_t}-{qs.first().id}"
        return generate_slug(slug='', new_slug=new_slug, modele=modele)
    return slug_t



#
class TauxDeChange(models.Model):
    monnaie_locale = models.CharField(max_length=20)
    monnaie_etrangere = models.CharField(max_length=20)
    taux_du_jour = models.DecimalField(max_digits=5, decimal_places=2)
    est_reference = models.BooleanField(default=False)
    modifie_le = models.DateTimeField(auto_now=True, editable=False)
    slug = models.SlugField(max_length=25, unique=True, allow_unicode=False, editable=False) ## a generer automatiquement

    class Meta:
        verbose_name = 'Taux de change'
        verbose_name_plural = 'Taux de changes'

    def __str__(self):
        return f"Taux de change: {self.monnaie_etrangere} -> {self.monnaie_locale} : {self.taux_du_jour}"


@receiver(pre_save, sender=TauxDeChange)
def tauxDeChange_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = generate_slug_2(slug=instance.monnaie_etrangere, modele=TauxDeChange)




#...
class CustomAccountManager(BaseUserManager):

    def create_superuser(self, email, pseudo, password, **other_fields):

        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)

        if other_fields.get('is_staff') is not True:
            raise ValueError('is_staff doit etre egal a True dans Superuser')

        if other_fields.get('is_superuser') is not True:
            raise ValueError('is_superuser doit etre egal a True dans Superuser')	

        return self.create_user(email, pseudo, password, **other_fields)	

    def create_user(self, email, pseudo, password, **other_fields):
        if not email:
            raise ValueError('email incorrect')

        email = self.normalize_email(email)
        user = self.model(email=email,pseudo=pseudo, **other_fields)
        user.set_password(password)	
        user.save()
        return user	


#modele personnalise d'utilisateur

#
class Utilisateur(AbstractBaseUser, PermissionsMixin):

    email= models.EmailField('adresse e-mail', unique=True)
    pseudo=models.CharField(max_length=60,unique=True)
    cree_le=models.DateTimeField(auto_now_add=True, editable=False)
    is_staff=models.BooleanField(default=False, editable=False)
    is_active=models.BooleanField(default=True, editable=False)
    is_superuser = models.BooleanField(default=False, editable=False)
    vu_a = models.DateTimeField(auto_now=True, editable=False)
    groups = models.ManyToManyField(Group)
    user_permissions= models.ManyToManyField(Permission)

    objects = CustomAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['pseudo',]


    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

    def __str__(self):
        return self.pseudo


@receiver(post_save, sender=Utilisateur)
def utilisateur_post_save_receiver(sender, instance, created, *args, **kwargs):
    if created:
        qs_historique = HistoriqueTauxDeChange.objects.filter(utilisateur_id=instance)
        exists = qs_historique.exists()
        if not exists:
            HistoriqueTauxDeChange.objects.create(utilisateur_id=instance)
            






# historique taux de change pour un utilisateur
class HistoriqueTauxDeChange(models.Model):
    utilisateur_id = models.OneToOneField(Utilisateur, on_delete=models.CASCADE, related_name='historique')
    cree_le = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        verbose_name = 'Historique Taux de Change'
        verbose_name_plural = 'Historiques Taux de Change'

    def __str__(self):
        return f"{self.utilisateur_id}"



# Conversion de devise
class ConversionDeDevise(models.Model):
    historique_id = models.ForeignKey(HistoriqueTauxDeChange, on_delete=models.CASCADE, related_name='conversions')
    monnaie_locale = models.CharField(max_length=20)
    monnaie_etrangere = models.CharField(max_length=20)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    montant_converti = models.DecimalField(max_digits=10, decimal_places=2)
    taux_du_jour = models.DecimalField(max_digits=5, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Conversion de Devise'
        verbose_name_plural = 'Conversions de Devise'

    def __str__(self):
        return f"{self.historique_id} - {self.montant} {self.monnaie_locale} -> {self.montant_converti} {self.monnaie_etrangere}"