from django.conf.urls import patterns, url

from Centar import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index')
)