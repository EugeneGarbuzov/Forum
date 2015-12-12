from django.db import connection
from django.http import HttpResponse
from django.shortcuts import render

from Forum.tools import fetch_to_dict


# Create your views here.


def index(request):
    login = request.user.username

    if login:
        with connection.cursor() as cursor:
            cursor.execute('''SELECT Nickname FROM users
                              WHERE Login = %s;''', login)
            nickname = cursor.fetchone()[0]
    else:
        nickname = ''

    with connection.cursor() as cursor:
        cursor.execute('''SELECT s.Name, s.Description, s.Date, u.Nickname
                          FROM sections AS s, users AS u
                          WHERE s.User_ID = u.User_ID;''')
        sections = fetch_to_dict(cursor)

    context = {'nickname': nickname,
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


