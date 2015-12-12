from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^$', views.index, name='index'),
    url(r'^(?P<section_name>[A-Za-z0-9_]+)/$', views.section, name='section'),
    url(r'^(?P<section_name>[A-Za-z0-9_]+)/(?P<topic_name>[A-Za-z0-9_]+)$', views.topic, name='topic')
]
