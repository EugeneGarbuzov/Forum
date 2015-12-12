from django.contrib.auth import authenticate
from django.core.urlresolvers import reverse
from django.db import connection
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from Forum.tools import fetch_to_dict

# Create your views here.

user_login = 'User_1'


def index(request):
    cursor = connection.cursor()
    cursor.execute('''SELECT s.Name, s.Description, s.Date, u.Nickname
                        FROM sections AS s, users AS u
                          WHERE s.User_ID = u.User_ID;''')

    context = {'cursor': fetch_to_dict(cursor)}
    return render(request, 'index.html', context)


def section(request, section_name):
    cursor = connection.cursor()
    cursor.execute('''SELECT t.Name, t.Description, t.Date, u.Nickname, s.Name AS SectionName
                        FROM topics as t, users as u, sections as s
                          WHERE u.User_ID = t.User_ID
                          AND t.Section_ID = s.Section_ID
                          AND s.Name = %s;''', section_name)

    context = {'cursor': fetch_to_dict(cursor)}
    return render(request, 'section.html', context)


def topic(request, section_name, topic_name):
    # todo implement
    return HttpResponse('Not implemented yet.')


def login(request):
    if request.method == 'POST':
        login = request.POST['Login']
        password = request.POST['Password']
        user = authenticate(username=login, password=password)
        if user:
            login(request, user)
            return HttpResponseRedirect(reverse('index'))
        else:
            return render(request, 'login.html', {
                'error': 1,
            })
    else:
        return render(request, "login.html")
