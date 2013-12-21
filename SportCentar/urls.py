from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'SportCentar.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^Centar/', include('Centar.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
