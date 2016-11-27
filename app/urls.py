from django.conf.urls import url

from app.settings import url_sections_allowed_chars
from . import views

urlpatterns = [
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^register/$', views.register, name='register'),
    url(r'^profile/(?P<username>[{}]+)$'.format(url_sections_allowed_chars), views.profile, name='profile'),
    url(r'^edit_profile/$', views.edit_profile, name='edit_profile'),

    url(r'^$', views.index, name='index'),
    url(r'^add/$', views.add_section, name='add_section'),
    url(r'^remove/(?P<section_name>[{}]+)$'.format(url_sections_allowed_chars), views.remove_section,
        name='remove_section'),
    url(r'^f/(?P<section_name>[{}]+)/$'.format(url_sections_allowed_chars), views.section,
        name='section'),

    url(r'^f/(?P<section_name>[{}]+)/add/$'.format(url_sections_allowed_chars), views.add_topic, name='add_topic'),
    url(r'^f/(?P<section_name>[{0}]+)/remove/(?P<topic_name>[{0}]+)$'.format(url_sections_allowed_chars),
        views.remove_topic, name='remove_topic'),
    url(r'^tag/(?P<tag_name>[{}]+)$'.format(url_sections_allowed_chars), views.topics_by_tag, name='topics_by_tag'),
    url(r'^f/(?P<section_name>[{0}]+)/(?P<topic_name>[{0}]+)$'.format(url_sections_allowed_chars), views.topic,
        name='topic'),

    url(r'^f/(?P<section_name>[{0}]+)/(?P<topic_name>[{0}]+)/add/$'.format(url_sections_allowed_chars),
        views.add_message, name='add_message'),
    url(r'^f/(?P<section_name>[{0}]+)/(?P<topic_name>[{0}]+)/remove/(?P<message_id>[0-9]+)$'.format(
        url_sections_allowed_chars), views.remove_message, name='remove_message'),
    url(r'^f/(?P<section_name>[{0}]+)/(?P<topic_name>[{0}]+)/edit/(?P<message_id>[0-9]+)$'.format(
        url_sections_allowed_chars), views.edit_message, name='edit_message'),
    url(r'^f/(?P<section_name>[{0}]+)/(?P<topic_name>[{0}]+)/like/(?P<message_id>[0-9]+)$'.format(
        url_sections_allowed_chars), views.like_message, name='like_message'),
]
