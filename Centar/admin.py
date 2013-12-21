from django.contrib import admin
from Centar.models import Privilegije, Korisnici, Radnici, Tereni, SportCentri, Rezervacije

admin.site.register(Privilegije)
admin.site.register(Korisnici)
admin.site.register(Tereni)
admin.site.register(Radnici)
admin.site.register(SportCentri)
admin.site.register(Rezervacije)


# Register your models here.
