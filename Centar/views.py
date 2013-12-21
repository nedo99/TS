from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
import md5
from Centar.models import Privilegije, Korisnici

def index(request):
    try:
      user = request.POST['username']
      pass1 = request.POST['pass']
      m = md5.new()
      m.update(pass1)
      try:
	korisnik_count = Korisnici.objects.filter(username = user, password = m.hexdigest()).count()
	if korisnik_count == 0:
	  return render_to_response("Centar/index.html", {'error_message' : 'Pogresna sifra ili korisnicko ime'}, context_instance = RequestContext(request))
      except (KeyError):
	return render_to_response("Centar/index.html", {'error_message' : 'Pogresna sifra ili korisnicko ime'}, context_instance = RequestContext(request))
      else:
	korisnik = Korisnici.objects.get(username = user, password = m.hexdigest())
	request.session['log'] = True
	request.session['id'] = korisnik.id
	request.session['vrsta'] = korisnik.vrsta.tip
	m1 = md5.new()
	m1.update(str(korisnik.id) + korisnik.vrsta.tip)
	request.session['tag'] = m1.hexdigest()
	if korisnik.vrsta.tip == 'user':
	  return render_to_response("Centar/korisnik.html", {"Korisnici" : korisnik})
	if korisnik.vrsta.tip == 'admin':
	  return render_to_response("Centar/admin.html", {"Korisnici" : korisnik})
	if korisnik.vrsta.tip == 'superadmin':
	  return render_to_response("Centar/superadmin.html", {"Korisnici" : korisnik})
    except (KeyError):
      return render_to_response("Centar/index.html", {'info_message' : 'ok je'}, context_instance = RequestContext(request))
