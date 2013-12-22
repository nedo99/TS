from django.conf.urls import patterns, url

from Centar import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^register/$', views.register, name='register'),
    url(r'^user/(?P<u_id>\d+)/$', views.user, name='user'),
    url(r'^teren/(?P<t_id>\d+)/$', views.teren, name='teren'),
    url(r'^out/$', views.out, name='out'),
    url(r'^superadmin/(?P<u_id>\d+)/$', views.superadmin, name='superadmin'),
    url(r'^employee/(?P<u_id>\d+)/$', views.employee, name='employee'),
    url(r'^employee/(?P<u_id>\d+)/termini/$', views.emp_termini, name='emp_termini'),
    url(r'^employee/(?P<u_id>\d+)/korisnici/$', views.emp_korisnici, name='emp_korisnici'),
    url(r'^employee/(?P<u_id>\d+)/tereni/$', views.emp_tereni, name='emp_tereni'),
)