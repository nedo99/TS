from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
import md5
from Centar.models import Privilegije, Korisnici, Rezervacije, Tereni, SportCentri, Radnici
from django import forms
from django.forms import CharField, Form, PasswordInput
from django.http import Http404
from datetime import datetime
from datetime import date, timedelta
from django.utils.timezone import utc
from django.utils import timezone
from itertools import izip

def usercheck(request, u_id, vrsta):
  if request.session.get('log', False):
    if request.session.get('id') == int(u_id):
      if request.session.get('vrsta') == vrsta:
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
     
class UserSearch(forms.Form):
     word = forms.CharField(max_length = 30)
     
class CentarRegister(forms.Form):
     naziv = forms.CharField(max_length = 50)
     adresa = forms.CharField(max_length = 200)

class TerenRegister(forms.Form):
     naziv = forms.CharField(max_length=200)
     sport = forms.CharField(max_length=20)

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
	  request.session.set_expiry(0)
	  if korisnik.vrsta.tip == 'user':
	    return HttpResponseRedirect("user/" + str (korisnik.id))
	  if korisnik.vrsta.tip == 'admin':
	    return HttpResponseRedirect("employee/" + str(korisnik.id))
	  if korisnik.vrsta.tip == 'superadmin':
	    return HttpResponseRedirect("superadmin/" + str(korisnik.id))
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
  if usercheck(request, u_id, 'user'):
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
  if usercheck(request, request.session.get('id'), 'user'):
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
	  rezervacije_count = Rezervacije.objects.filter(teren = terend, pocetak = pocetak_object).count()
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
      rezervacije = 0
      if rezervacije_count > 0:
	rezervacije = Rezervacije.objects.filter(teren = terend)
      dani = []
      for i in range (0, 9):
	dani.append(date.today() + timedelta(i+1))
      brojevi = []
      for i in range (0, 14):
	brojevi.append(i)
      brojevi1 = []
      for i in range (0, 10):
	brojevi1.append(i)
      ttable = []
      for j in range(0,9):
	#ttable.append(j)
	be = []
	for i in range(0, 14):
	  a = 0
	  if rezervacije != 0:
	    for rezervacija in rezervacije:
	      if dani[j] == rezervacija.pocetak.date():
		if (i+8) == rezervacija.pocetak.hour:
		  be.append(1)
		  a = 1
	  if a == 0:
	    be.append(0)
	ttable.append(be)
      print ttable
      da = izip(dani, ttable)
      return render_to_response("Centar/teren.html", { 'korisnik' : korisnik, 'teren' : terend, 'rezervacije' : rezervacije, 'dani' : dani, 'brojevi' : brojevi, 'brojevi1' : brojevi1, 'message' : message, 'table' : ttable, 'da' : da}, context_instance = RequestContext(request))
    else:
      raise Http404
  else:
    raise Http404
  
def out(request):
  request.session.flush()
  return HttpResponseRedirect('/Centar/')
  
def superadmin(request, u_id):
  if usercheck(request, u_id, 'superadmin'):
    korisnik = Korisnici.objects.get ( id = u_id)
    message = ''
    korisnici = 0
    form = UserSearch()
    if request.POST.get('pretraga'):
      form = UserSearch(request.POST)
      if form.is_valid():
	word = form.cleaned_data['word']
	korisnici_count = Korisnici.objects.filter(ime__icontains = word).count()
	if korisnici_count > 0:
	  korisnici = Korisnici.objects.filter(ime__icontains = word)
	else:
	  message = "Nisu pronadjeni rezultati."
    if request.POST.get('brisanje'):
      brisanje_id = request.POST['id']
      if brisanje_id != u_id:
	korisnici_count = Korisnici.objects.filter(id = brisanje_id).count()
	if korisnici_count > 0:
	  korisnikdel = Korisnici.objects.filter(id = brisanje_id)
	  korisnikdel.delete()
	  message="Korisnik izbrisan"
	else:
	  message = "Doslo je do greske prilikom brisanja korisnika"
    if request.POST.get('dodajcentar'):
      formCentar = CentarRegister(request.POST)
      if formCentar.is_valid():
	naziv = formCentar.cleaned_data['naziv']
	adresa = formCentar.cleaned_data['adresa']
	centar = SportCentri( naziv = naziv, adresa = adresa)
	centar.save()
	message = "Sport centar dodan"
        formCentar = CentarRegister()
      return render_to_response("Centar/superadmin.html", {"korisnik" : korisnik, 'form' : form, 'message' : message, 'korisnici' : korisnici, 'formcentar' : formCentar}, context_instance = RequestContext(request))
      
    formCentar = CentarRegister()
    return render_to_response("Centar/superadmin.html", {"korisnik" : korisnik, 'form' : form, 'message' : message, 'korisnici' : korisnici, 'formcentar' : formCentar}, context_instance = RequestContext(request))
  else:
    raise Http404
  
def employee(request, u_id):
  if usercheck(request, u_id, 'admin'):    
    korisnik = Korisnici.objects.get ( id = u_id)
    message = "" 
    
    radnik = Radnici.objects.get(radnik = korisnik)
    centar = radnik.centar
    
    return render_to_response("Centar/employee.html", {"korisnik" : korisnik, 'centar' : centar, 'message' : message}, context_instance = RequestContext(request))
  else:
    raise Http404
  
def emp_tereni(request, u_id):
  if usercheck(request, u_id, 'admin'):
    message = ''
    
    korisnik = Korisnici.objects.get(id = u_id)
    radnik = Radnici.objects.get(radnik = korisnik)
    centar = radnik.centar
        
    tereni_count = Tereni.objects.filter(centar=centar).count()

    if tereni_count > 0:
      tereni = Tereni.objects.filter(centar=centar)
    else:
      tereni=0
      message="Trenutno nema registrovanih terena u sport centru."
	
    if request.POST.get('brisanje'):
      brisanje_id = request.POST['id']
      if tereni_count > 0:
	  terendel = Tereni.objects.filter(id = brisanje_id)
	  terendel.delete()
	  message="Teren izbrisan!"
      else:
	  message = "Doslo je do greske prilikom brisanja terena."

    if request.POST.get('dodajteren'):
      formteren= TerenRegister(request.POST)
      if formteren.is_valid():
	naziv = formteren.cleaned_data['naziv']
	sport = formteren.cleaned_data['sport']
	teren = Tereni(centar=centar, naziv=naziv, sport=sport)
	teren.save()
	message = "Teren dodan."
        formteren = TerenRegister()
      return render_to_response("Centar/emp_tereni.html", {'info_message' : message, 'korisnik' : korisnik, 'tereni' : tereni, 'centar' : centar, 'formteren' : formteren}, context_instance = RequestContext(request))
      
    formteren = TerenRegister()
	
    return render_to_response("Centar/emp_tereni.html", {'info_message' : message, 'korisnik' : korisnik, 'tereni' : tereni, 'centar' : centar, 'formteren' : formteren}, context_instance = RequestContext(request))
        
  else:
    raise Http404
  
def emp_korisnici(request, u_id):
  if usercheck(request, u_id, 'admin'):
    message = ''
    
    korisnik = Korisnici.objects.get(id = u_id)
    kid = korisnik.id
    
    
    return render_to_response("Centar/emp_korisnici.html", {'info_message' : message, 'korisnik' : korisnik}, context_instance = RequestContext(request))
  else:
    raise Http404
  
def emp_termini(request, u_id):
  if usercheck(request, u_id, 'admin'):
    message = ''
    
    korisnik = Korisnici.objects.get(id = u_id)
    kid = korisnik.id
    
    return render_to_response("Centar/emp_termini.html", {'info_message' : message, 'korisnik' : korisnik}, context_instance = RequestContext(request))
  else:
    raise Http404