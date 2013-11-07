from django.conf.urls import patterns, url

from frontend import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^sample$', views.samplegenerate, name='samplegenerate'),
    url(r'^sample/$', views.samplegenerate, name='samplegenerate'),
)
