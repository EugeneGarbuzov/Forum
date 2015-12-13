from django.contrib import auth
from django.core.urlresolvers import reverse
from django.db import connection
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from Forum.tools import fetch_to_dict, check_roles


# Create your views here.


def login(request):
    if request.user.username:
        return HttpResponseRedirect(reverse('index'))

    if request.method == 'POST':
        login = request.POST['Login']
        password = request.POST['Password']
        user = auth.authenticate(username=login, password=password)
        if user:
            auth.login(request, user)
            return HttpResponseRedirect(reverse('index'))
        else:
            return render(request, 'login.html', {
                'error': 1,
            })
    else:
        return render(request, "login.html")


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('index'))


def index(request):
    login = request.user.username

    if login:
        with connection.cursor() as cursor:
            cursor.execute('''SELECT u.Nickname, r.Role_Name
                              FROM users as u, roles as r
                              WHERE u.Login = %s
                              AND r.Role_ID = u.Role_ID;''', login)
            nickname, role = cursor.fetchone()
    else:
        nickname = ''
        role = 'Regular'

    role = check_roles(role, 'write')

    with connection.cursor() as cursor:

        # todo привести эту дичь к нормальному виду

        cursor.execute('''SELECT s.Name, s.Description, s.Date, u.Nickname,
                          (SELECT Role_Name FROM roles WHERE roles.Role_ID = s.Role_ID)  as Role_Name
                          FROM sections AS s, users AS u, roles as r
                          WHERE s.User_ID = u.User_ID
                          AND s.Role_ID = r.Role_ID
                          AND r.Role_Name in %s;''', [tuple(role)])
        sections = fetch_to_dict(cursor)

    context = {'user': {'nickname': nickname, 'is_admin': role == 'Admin'},
               'sections': sections}
    return render(request, 'index.html', context)


def section(request, section_name):
    with connection.cursor() as cursor:
        cursor.execute('''SELECT t.Name, t.Description, t.Date, u.Nickname, s.Name AS SectionName
                          FROM topics as t, users as u, sections as s
                          WHERE u.User_ID = t.User_ID
                          AND t.Section_ID = s.Section_ID
                          AND s.Name = %s;''', section_name)
        topics = fetch_to_dict(cursor)

    context = {'topics': topics}
    return render(request, 'section.html', context)


def topic(request, section_name, topic_name):
    # todo implement
    return HttpResponse('Not implemented yet.')
