from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<section_name>[A-Za-z0-9_]+)/$', views.section, name='section')
]
