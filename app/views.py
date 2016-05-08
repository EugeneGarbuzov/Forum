import cx_Oracle
from django.contrib import auth
from django.core.urlresolvers import reverse
from django.db import connection
from django.http import HttpResponseRedirect
from django.shortcuts import render

from Forum.tools import fetch_to_dict


def login(request):
    if request.user.username:
        return HttpResponseRedirect(reverse('index'))

    if request.method == 'POST':
        user = auth.authenticate(username=request.POST['username'], password=request.POST['password'])
        if user:
            auth.login(request, user)
            return HttpResponseRedirect(reverse('index'))
        else:
            return render(request, 'login.html', {'error': 1})
    else:
        return render(request, "login.html")


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('index'))


def register(request):
    if request.user.username:
        return HttpResponseRedirect(reverse('index'))

    if request.method == 'POST':
        try:
            with connection.cursor() as cursor:
                cursor.callproc("register", (request.POST['username'], request.POST['password'], request.POST['email'],
                                             request.POST['nickname'], request.POST['full_name'],
                                             request.POST['status'], request.POST['signature']))
                user = auth.authenticate(username=request.POST['username'], password=request.POST['password'])
                auth.login(request, user)

                return HttpResponseRedirect(reverse('index'))
        except:
            return render(request, 'register.html', {'ERROR': 1})

    return render(request, "register.html")


def profile(request, username):
    try:
        with connection.cursor() as cursor:
            user = fetch_to_dict(cursor.callfunc('user_info', cx_Oracle.CURSOR, (username,)))[0]
            trophies = fetch_to_dict(cursor.callfunc('user_trophies', cx_Oracle.CURSOR, (username,)))
            moderated_sections = [row[0] for row in
                                  cursor.callfunc('user_moderated_sections', cx_Oracle.CURSOR, (username,)).fetchall()]

            context = {'USER_INFO': user, 'TROPHIES': trophies, 'MODERATED_SECTIONS': moderated_sections}
            return render(request, 'profile.html', context)
    except:
        return HttpResponseRedirect(reverse('index'))


def edit_profile(request):
    username = request.user.username
    if not username:
        return HttpResponseRedirect(reverse('index'))

    try:
        with connection.cursor() as cursor:
            if request.method == 'GET':
                user = fetch_to_dict(cursor.callfunc('private_user_info', cx_Oracle.CURSOR, (username,)))[0]
                return render(request, 'edit_profile.html', user)

            elif request.method == 'POST':
                cursor.callproc("update_private_user_info", (username, request.POST['password'], request.POST['email'],
                                                             request.POST['nickname'], request.POST['full_name'],
                                                             request.POST['status'], request.POST['signature']))
                return HttpResponseRedirect(reverse('index'))
    except:
        return render(request, 'edit_profile.html', {'ERROR': 1})


def index(request):
    username = request.user.username

    with connection.cursor() as cursor:
        if username:
            user = fetch_to_dict(cursor.callfunc('user_info', cx_Oracle.CURSOR, (username,)))[0]
            nickname, user_role = user['NICKNAME'], user['ROLE_NAME']
        else:
            nickname, user_role = '', 'newbie'

        sections = fetch_to_dict(cursor.callfunc('get_allowed_sections', cx_Oracle.CURSOR, (username,)))

        for section in sections:
            section['MODERATORS'] = fetch_to_dict(
                cursor.callfunc('get_section_moderators', cx_Oracle.CURSOR, (section['NAME'],)))

    context = {'USER': {'NICKNAME': nickname, 'USERNAME': username, 'IS_ADMIN': user_role == 'admin'},
               'SECTIONS': sections}

    return render(request, 'index.html', context)


def add_section(request):
    username = request.user.username

    if username:
        try:
            with connection.cursor() as cursor:
                user_role = cursor.callfunc('get_user_role', cx_Oracle.STRING, (username,))

                if request.method == 'GET' and user_role == 'admin':
                    return render(request, 'add_section.html')
                elif request.method == 'POST':
                    cursor.callproc("add_section", (
                        username, request.POST['name'], request.POST['description'], request.POST['role_name']))
        except:
            return render(request, 'add_section.html', {'ERROR': 1})

    return HttpResponseRedirect(reverse('index'))


def remove_section(request, section_name):
    with connection.cursor() as cursor:
        cursor.callproc("remove_section", (request.user.username, section_name))

    return HttpResponseRedirect(reverse('index'))


def section(request, section_name):
    username = request.user.username

    with connection.cursor() as cursor:
        if not int(cursor.callfunc('check_access_to_section', cx_Oracle.NUMBER, (username, section_name))):
            return HttpResponseRedirect(reverse('index'))

        topics = fetch_to_dict(cursor.callfunc('get_topics', cx_Oracle.CURSOR, (section_name,)))
        for topic in topics:
            topic['TAGS'] = (row[0] for row in
                             cursor.callfunc('get_topic_tags', cx_Oracle.CURSOR, (topic['NAME'],)).fetchall())

        can_create_topic = int(
            cursor.callfunc('check_access_to_section', cx_Oracle.NUMBER, (username, section_name, 'write')))
        is_moderator = int(cursor.callfunc('is_section_moderator', cx_Oracle.NUMBER, (username, section_name,)))

    context = {'CAN_CREATE_TOPIC': can_create_topic,
               'IS_MODERATOR': is_moderator,
               'SECTION_NAME': section_name,
               'TOPICS': topics}

    return render(request, 'section.html', context)


def add_topic(request, section_name):
    username = request.user.username

    with connection.cursor() as cursor:
        if int(cursor.callfunc('check_access_to_section', cx_Oracle.NUMBER, (username, section_name, 'write'))):
            if request.method == 'GET':
                return render(request, 'add_topic.html', {'section_name': section_name})

            if request.method == 'POST':
                try:
                    cursor.callproc('add_topic',
                                    (username, section_name, request.POST['name'], request.POST['description']))
                except:
                    return render(request, 'add_topic.html', {'section_name': section_name, 'error': 1})

                if request.POST['tags']:
                    cursor.callproc('add_tags', (request.POST['name'], request.POST['tags']))

    return HttpResponseRedirect(reverse('section', args=(section_name,)))


def remove_topic(request, section_name, topic_name):
    with connection.cursor() as cursor:
        cursor.callproc('remove_topic', (request.user.username, topic_name))

    return HttpResponseRedirect(reverse('section', args=(section_name,)))


def topics_by_tag(request, tag_name):
    with connection.cursor() as cursor:
        topics = fetch_to_dict(cursor.callfunc('topics_by_tag', cx_Oracle.CURSOR, (request.user.username, tag_name)))

    context = {'TAG_NAME': tag_name, 'TOPICS': topics}

    return render(request, 'topics_by_tag.html', context)


def topic(request, section_name, topic_name):
    username = request.user.username

    with connection.cursor() as cursor:
        if int(cursor.callfunc('check_access_to_section', cx_Oracle.NUMBER, (username, section_name))):
            messages = fetch_to_dict(cursor.callfunc('get_messages', cx_Oracle.CURSOR, (topic_name,)))

            can_add_message = int(
                cursor.callfunc('check_access_to_section', cx_Oracle.NUMBER, (username, section_name, 'write')))
            is_moderator = int(cursor.callfunc('is_section_moderator', cx_Oracle.NUMBER, (username, section_name,)))

            context = {'SECTION_NAME': section_name, 'TOPIC_NAME': topic_name, 'MESSAGES': messages,
                       'USER': {'CAN_ADD_MESSAGE': can_add_message, 'IS_MODERATOR': is_moderator,
                                'USERNAME': username}}

            return render(request, 'topic.html', context)

    return HttpResponseRedirect(reverse('section', args=(section_name,)))


def add_message(request, section_name, topic_name):
    username = request.user.username

    if username and request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.callproc('add_message', (username, topic_name, request.POST['text']))

    return HttpResponseRedirect(reverse('topic', args=(section_name, topic_name)))


def like_message(request, section_name, topic_name, message_id):
    with connection.cursor() as cursor:
        cursor.callproc('add_like', (request.user.username, message_id))

    return HttpResponseRedirect(reverse('topic', args=(section_name, topic_name)))


def remove_message(request, section_name, topic_name, message_id):
    with connection.cursor() as cursor:
        cursor.callproc("remove_message", (request.user.username, message_id))

    return HttpResponseRedirect(reverse('topic', args=(section_name, topic_name)))


def edit_message(request, section_name, topic_name, message_id):
    username = request.user.username

    if username:
        with connection.cursor() as cursor:
            message = fetch_to_dict(cursor.callfunc('get_message', cx_Oracle.CURSOR, (message_id,)))[0]
            is_moderator = int(cursor.callfunc('is_section_moderator', cx_Oracle.NUMBER, (username, section_name,)))

            if username == message['USERNAME'] or is_moderator:
                if request.method == 'GET':
                    context = {'SECTION_NAME': section_name, 'TOPIC_NAME': topic_name,
                               'MESSAGE_ID': message_id, 'MESSAGE': message}
                    return render(request, 'edit_message.html', context)

                elif request.method == 'POST':
                    cursor.callproc("edit_message", (username, message_id, request.POST['text']))

    return HttpResponseRedirect(reverse('topic', args=(section_name, topic_name)))
