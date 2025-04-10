from django.contrib import admin

from .models import (
    Utilisateur,
    TauxDeChange, 
    ConversionDeDevise, 
    HistoriqueTauxDeChange
)

from django.contrib.auth.admin import UserAdmin





#                           #### Register your models here. ####



class UserAdminConfig(UserAdmin):
    model = Utilisateur

    search_fields = ('email', 'pseudo',)
    list_filter = ('is_active', 'is_staff')
    ordering = ('-cree_le',)
    list_display = ('email', 'pseudo','is_active', 'is_staff')
    

admin.site.register(Utilisateur, UserAdminConfig)




class TauxDeChangeAdmin(admin.ModelAdmin):
    list_display = ('monnaie_locale', 'monnaie_etrangere', 'taux_du_jour', 'est_reference', 'modifie_le')
    search_fields = ('monnaie_locale', 'monnaie_etrangere')
    list_filter = ('est_reference',)
    ordering = ('-modifie_le',)
    actions = ['mark_as_reference']

admin.site.register(TauxDeChange, TauxDeChangeAdmin)


class ConversionDeDeviseAdmin(admin.ModelAdmin):
    list_display = ('id', 'historique_id', 'monnaie_locale', 'monnaie_etrangere', 'montant', 'montant_converti', 'taux_du_jour', 'date')
    search_fields = ()
    list_filter = ()
    ordering = ('-date',)

admin.site.register(ConversionDeDevise, ConversionDeDeviseAdmin)


class HistoriqueTauxDeChangeAdmin(admin.ModelAdmin):
    list_display = ('id', 'utilisateur_id', 'cree_le')
    search_fields = ()
    list_filter = ()
    ordering = ('-cree_le',)

admin.site.register(HistoriqueTauxDeChange, HistoriqueTauxDeChangeAdmin)
