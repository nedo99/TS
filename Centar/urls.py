from django.conf.urls import patterns, url

from Centar import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^register/$', views.register, name='register'),
    url(r'^user/(?P<u_id>\d+)/$', views.user, name='user'),
    url(r'^teren/(?P<t_id>\d+)/$', views.teren, name='teren'),
    url(r'^out/$', views.out, name='out'),
)