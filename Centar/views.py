from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
import md5
from Centar.models import Privilegije, Korisnici, Rezervacije, Tereni, SportCentri
from django import forms
from django.forms import CharField, Form, PasswordInput
from django.http import Http404
from datetime import datetime
from datetime import date, timedelta
from django.utils.timezone import utc
from django.utils import timezone

def usercheck(request, u_id):
  if request.session.get('log', False):
    if request.session.get('id') == int(u_id):
      if request.session.get('vrsta') == 'user':
	m1 = md5.new()
	m1.update(str(u_id) + request.session.get('vrsta'))
	if request.session.get('tag') == m1.hexdigest():
	  return True
	else:
	  return False
      else:
	return False
    else:
      return False
  else:
    return False

class RegisterForm(forms.Form):
      username = forms.CharField(max_length=20)
      password = CharField(widget=PasswordInput())
      password1 = CharField(widget=PasswordInput())
      ime = forms.CharField(max_length=20)
      prezime = forms.CharField(max_length=20)
      mail = forms.EmailField()
      telefon = forms.CharField(max_length=20)
      adresa = forms.CharField(max_length=200)
      rodjenje = forms.DateField()
      
class LoginForm(forms.Form):
     korisnicko_ime = forms.CharField(max_length=20)
     sifra = CharField(widget=PasswordInput())

def index(request):
    if request.POST:
      form = LoginForm(request.POST)
      if form.is_valid():
	user = form.cleaned_data['korisnicko_ime']
	pass1 = form.cleaned_data['sifra']
	m = md5.new()
	m.update(pass1)
	korisnik_count = Korisnici.objects.filter(username = user, password = m.hexdigest()).count()
	if korisnik_count == 0:
	  return render_to_response("Centar/index.html", {'error_message' : 'Pogresna sifra ili korisnicko ime', 'form': form}, context_instance = RequestContext(request))
	else:
	  korisnik = Korisnici.objects.get(username = user, password = m.hexdigest())
	  request.session['log'] = True
	  request.session['id'] = korisnik.id
	  request.session['vrsta'] = korisnik.vrsta.tip
	  m1 = md5.new()
	  m1.update(str(korisnik.id) + korisnik.vrsta.tip)
	  request.session['tag'] = m1.hexdigest()
	  if korisnik.vrsta.tip == 'user':
	    return HttpResponseRedirect("user/" + str (korisnik.id))
	  if korisnik.vrsta.tip == 'admin':
	    return render_to_response("Centar/admin.html", {"Korisnici" : korisnik})
	  if korisnik.vrsta.tip == 'superadmin':
	    return render_to_response("Centar/superadmin.html", {"Korisnici" : korisnik})
      else:
	return render_to_response("Centar/index.html", {'error_message' : 'Doslo je do greske prilikom prijave.', 'form': form}, context_instance = RequestContext(request))
    else:
      form = LoginForm()
      return render_to_response("Centar/index.html", {'form': form}, context_instance = RequestContext(request))
      
def register(request):
    if request.POST:
      form = RegisterForm(request.POST) # A form bound to the POST data
      if form.is_valid():
	  user = form.cleaned_data['username']
	  pass1 = form.cleaned_data['password']
	  pass2 = form.cleaned_data['password1']
	  ime = form.cleaned_data['ime']
	  prezime = form.cleaned_data['prezime']
	  mail = form.cleaned_data['mail']
	  telefon = form.cleaned_data['telefon']
	  adresa = form.cleaned_data['adresa']
	  rodjenje = form.cleaned_data['rodjenje']
	  if pass1 != pass2:
	    return render_to_response("Centar/register.html", {'error_message' : 'Sifre nisu jednake', 'form': form}, context_instance = RequestContext(request))
	  pr = Privilegije.objects.get(tip = 'user')
	  m = md5.new()
	  m.update(pass1)
	  korisnik = Korisnici(username = user, password = m.hexdigest(), ime = ime, prezime = prezime, mail = mail, telefon = telefon, adresa = adresa, datum_rodjenja = rodjenje, vrsta = pr)
	  korisnik.save()
	  return render_to_response("Centar/register.html", {'info_message' : 'Uspjesno ste registrovani. Sada se mozete prijaviti.'}, context_instance = RequestContext(request))
      else:
	  return render_to_response("Centar/register.html", {'error_message' : 'Doslo je do greske prilikom registracije.', 'form': form}, context_instance = RequestContext(request))
    else :
	  form = RegisterForm()
	  return render_to_response("Centar/register.html", {'form' : form, 'info_message' : 'Unesite vase informacije.'}, context_instance = RequestContext(request))
	  
def user(request, u_id):
  if usercheck(request, u_id):
    message = ''
    if request.POST:
      rez_id = request.POST['id']
      rezervacija_del = Rezervacije.objects.get( id = rez_id)
      now = timezone.now()
      poc = rezervacija_del.pocetak
      if now < poc:
	razlika = poc - now
	razlika = razlika.total_seconds()//3600
	if int(razlika) < 24:
	  message = "Ne mozete otkazati termin 24h prije."
	else:
	  rezervacija_del.delete()
	  message = "Termin je odjavljen."
      else:
	message = "Ne mozete odjaviti termin koji je prosao."
    korisnik = Korisnici.objects.get(id = u_id)
    kid = korisnik.id
    rezervacije_count = Rezervacije.objects.filter(korisnik = korisnik).count()
    rezervacije = 0
    if rezervacije_count > 0:
      rezervacije = Rezervacije.objects.filter(korisnik = korisnik)
    tereni = Tereni.objects.all()
    centri = SportCentri.objects.all()
    return render_to_response("Centar/korisnik.html", {'info_message' : message, 'korisnik' : korisnik, 'rezervacije' : rezervacije, 'tereni' : tereni, 'centri' : centri}, context_instance = RequestContext(request))
  else:
    raise Http404
    
def teren(request, t_id):  
  if usercheck(request, request.session.get('id')):
    korisnik = Korisnici.objects.get(id = request.session.get('id'))
    message = ''
    teren_count = Tereni.objects.filter( id = int(t_id)).count()
    if teren_count > 0:
      terend = Tereni.objects.get( id = t_id)
      if request.POST:
	number = request.POST['order']
	dan = request.POST['date']
	if number > 7 or number < 22:
	  pocetak = dan +' ' + number +':00'
	  kraj = dan + ' ' + str(int(number)+1) +':00'
	  pocetak_object = datetime.strptime(pocetak, '%b. %d, %Y %H:%M')
	  kraj_object = datetime.strptime(kraj, '%b. %d, %Y %H:%M')
	  rezervacije_count = Rezervacije.objects.filter(pocetak = pocetak_object).count()
	  if rezervacije_count == 0:
	    r = Rezervacije(teren = terend, korisnik = korisnik, pocetak = pocetak_object, kraj = kraj_object, koristeno = 0 )
	    r.save()
	    message = 'Termin rezervisan'
	  else:
	    message = "Termin zauzet"
	else:
	  message = 'Pogresno uneseni podaci'
      now = timezone.now()
      rezervacije_count = Rezervacije.objects.filter(teren = terend).count()
      if rezervacije_count > 0:
	rezervacije = Rezervacije.objects.filter(teren = terend)
      dani = []
      for i in range (0, 9):
	dani.append(date.today() + timedelta(i+1))
      brojevi = []
      for i in range (8, 22):
	brojevi.append(i)
      return render_to_response("Centar/teren.html", { 'teren' : terend, 'rezervacije' : rezervacije, 'dani' : dani, 'brojevi' : brojevi, 'message' : message}, context_instance = RequestContext(request))
    else:
      raise Http404
  else:
    raise Http404
