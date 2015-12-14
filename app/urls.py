from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^register/$', views.register, name='register'),
    url(r'^profile/(?P<username>[A-Za-z0-9_]+)$', views.profile, name='profile'),
    url(r'^edit_profile/$', views.edit_profile, name='edit_profile'),

    url(r'^$', views.index, name='index'),
    url(r'^add/$', views.add_section, name='add_section'),
    url(r'^remove/(?P<section_name>[A-Za-z0-9_]+)$', views.remove_section, name='remove_section'),

    url(r'^(?P<section_name>[A-Za-z0-9_]+)/$', views.section, name='section'),
    url(r'^(?P<section_name>[A-Za-z0-9_]+)/(?P<topic_name>[A-Za-z0-9_]+)$', views.topic, name='topic')
]
