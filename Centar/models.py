from django.db import models
import datetime

class Privilegije(models.Model):
    tip = models.CharField(max_length = 20)
    def __unicode__(self):  # Python 3: def __str__(self):
        return self.tip

class Korisnici(models.Model):
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=50)
    ime = models.CharField(max_length=20)
    prezime = models.CharField(max_length=20)
    mail = models.CharField(max_length=50)
    telefon = models.CharField(max_length=20)
    adresa = models.CharField(max_length=200)
    datum_rodjenja = models.DateTimeField('datum rodjenja')
    vrsta = models.ForeignKey(Privilegije)
    def __unicode__(self):  # Python 3: def __str__(self):
        return self.ime + self.prezime

class SportCentri(models.Model):
    naziv = models.CharField(max_length=200)
    adresa = models.CharField(max_length=200)
    def __unicode__(self):  # Python 3: def __str__(self):
        return self.naziv
    
class Radnici(models.Model):
    radnik = models.ForeignKey(Korisnici)
    centar = models.ForeignKey(SportCentri)
    
class Tereni(models.Model):
    centar = models.ForeignKey(SportCentri)
    naziv = models.CharField(max_length=200)
    sport = models.CharField(max_length=20)
    def __unicode__(self):  # Python 3: def __str__(self):
        return self.naziv
    
class Rezervacije(models.Model):
    teren = models.ForeignKey(Tereni)
    korisnik = models.ForeignKey(Korisnici)
    pocetak = models.DateTimeField('pocetak termina')
    kraj = models.DateTimeField('kraj termina')
    koristeno = models.IntegerField(default=0)
    def __unicode__(self):  # Python 3: def __str__(self):
        return self.pocetak
    
    
    
