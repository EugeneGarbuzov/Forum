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


def register(request):
    if request.user.username:
        return HttpResponseRedirect(reverse('index'))

    if request.method == 'POST':
        with connection.cursor() as cursor:
            try:
                cursor.execute('''INSERT INTO Users(Role_ID, Rank_ID,Login,Password,email,Nickname,Full_Name,Date,Status,Signature)
                                  SELECT Role_ID, Rank_ID, %s, %s, %s, %s, %s, now(), %s, %s
                                  FROM Roles, Ranks
                                  WHERE Role_Name = 'Newbie' AND Rank_Name = 'Rank_1';''',
                               (request.POST['Login'], request.POST['Password'], request.POST['email'],
                                request.POST['Nickname'], request.POST['Full_Name'],
                                request.POST['Status'], request.POST['Signature']))
                user = auth.authenticate(username=request.POST['Login'], password=request.POST['Password'])
                auth.login(request, user)
                return HttpResponseRedirect(reverse('index'))
            except:
                return render(request, 'register.html', {'error': 1, })
    else:
        return render(request, "register.html")


def profile(request, user_login):
    with connection.cursor() as cursor:
        try:
            cursor.execute('''SELECT Nickname, Full_Name, Date, Status, Signature, Role_Name
                          FROM users as u, roles as r
                          WHERE u.Login = %s
                          AND r.Role_ID = u.Role_ID;''', user_login)
            user = fetch_to_dict(cursor)[0]
            return render(request, 'profile.html', user)
        except:
            return HttpResponseRedirect(reverse('index'))


def index(request):
    login = request.user.username

    if login:
        with connection.cursor() as cursor:
            cursor.execute('''SELECT u.Login, u.Nickname, r.Role_Name
                              FROM users as u, roles as r
                              WHERE u.Login = %s
                              AND r.Role_ID = u.Role_ID;''', login)
            login, nickname, role = cursor.fetchone()
    else:
        nickname = ''
        role = 'Regular'

    roles = check_roles(role)

    with connection.cursor() as cursor:
        cursor.execute('''SELECT s.Name, s.Description, s.Date,
                          (SELECT Role_Name FROM roles WHERE roles.Role_ID = s.Role_ID)  as Role_Name
                          FROM sections AS s, roles as r
                          WHERE s.Role_ID = r.Role_ID
                          AND r.Role_Name in %s;''', [tuple(roles)])
        sections = fetch_to_dict(cursor)

    context = {'user': {'nickname': nickname, 'login': login, 'is_admin': role == 'Admin'},
               'sections': sections}
    return render(request, 'index.html', context)


def add_section(request):
    login = request.user.username

    if login:
        with connection.cursor() as cursor:
            cursor.execute('''SELECT r.Role_Name
                              FROM users as u, roles as r
                              WHERE r.Role_ID = u.Role_ID
                              AND u.Login = %s;''', login)
            role, = cursor.fetchone()
        if role == 'Admin' and request.method == 'POST':
            with connection.cursor() as cursor:
                try:
                    cursor.execute('''insert into Sections(Role_ID, Name, Date, Description)
                                      select Role_ID, %s, now(), %s
                                      from Roles where Role_Name = %s;''',
                                   (request.POST['Name'], request.POST['Description'], request.POST['Role_Name']))
                    return HttpResponseRedirect(reverse('index'))
                except:
                    return render(request, 'add_section.html', {'error': 1})
        else:
            return render(request, "add_section.html")

    return HttpResponseRedirect(reverse('index'))


def remove_section(request, section_name):
    login = request.user.username

    if login:
        with connection.cursor() as cursor:
            cursor.execute('''SELECT r.Role_Name
                              FROM users as u, roles as r
                              WHERE r.Role_ID = u.Role_ID
                              AND u.Login = %s;''', login)
            role, = cursor.fetchone()
        if role == 'Admin':
            with connection.cursor() as cursor:
                cursor.execute('''DELETE FROM sections WHERE Name = %s''', section_name)
    return HttpResponseRedirect(reverse('index'))


def section(request, section_name):
    with connection.cursor() as cursor:
        cursor.execute('''SELECT t.Name, t.Description, t.Date, u.Nickname, s.Name AS SectionName
                          FROM topics as t, users as u, sections as s
                          WHERE u.User_ID = t.User_ID
                          AND t.Section_ID = s.Section_ID
                          AND s.Name = %s;''', section_name)
        topics = fetch_to_dict(cursor)

    for topic in topics:
        with connection.cursor() as cursor:
            cursor.execute('''SELECT Tag_Name FROM Tags_Topics
                              JOIN Tags ON Tags.Tag_ID = Tags_Topics.Tag_ID
                              JOIN Topics ON Topics.Topic_ID = Tags_Topics.Topic_ID
                              WHERE Name = %s;''', topic['Name'])
            topic['Tags'] = tuple(row[0] for row in cursor.fetchall())

    context = {'topics': topics}
    return render(request, 'section.html', context)


def topic(request, section_name, topic_name):
    # todo implement
    return HttpResponse('Not implemented yet.')