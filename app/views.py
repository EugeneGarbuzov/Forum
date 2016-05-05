import cx_Oracle
from django.contrib import auth
from django.core.urlresolvers import reverse
from django.db import connection
from django.http import HttpResponseRedirect
from django.shortcuts import render

from Forum.tools import fetch_to_dict, fetch_to_tuple, cursor_callfunc


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
            moderated_sections = cursor.callfunc('user_moderated_sections', cx_Oracle.CURSOR, (username,)).fetchall()

            if moderated_sections:
                moderated_sections = moderated_sections[0]

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
            nickname, role = cursor.callfunc('user_role_nickname', cx_Oracle.CURSOR, (username,)).fetchone()
        else:
            nickname = ''
            role = 'newbie'

        roles = fetch_to_tuple(cursor.callfunc('check_roles', cx_Oracle.CURSOR, (role,)))
        sections = fetch_to_dict(cursor_callfunc('get_allowed_sections', cx_Oracle.CURSOR, roles, cursor))

        for section in sections:
            section['MODERATORS'] = fetch_to_dict(
                cursor.callfunc('get_section_moderators', cx_Oracle.CURSOR, (section['NAME'],)))

    context = {'USER': {'NICKNAME': nickname, 'USERNAME': username, 'IS_ADMIN': role == 'admin'},
               'SECTIONS': sections}

    return render(request, 'index.html', context)


def add_section(request):
    username = request.user.username

    if username:
        try:
            with connection.cursor() as cursor:
                nickname, role = cursor.callfunc('user_role_nickname', cx_Oracle.CURSOR, (username,)).fetchone()

                if role == 'admin':
                    if request.method == 'GET':
                        return render(request, 'add_section.html')
                    elif request.method == 'POST':
                        cursor.callproc("add_section", (
                            username, request.POST['name'], request.POST['description'],
                            request.POST['role_name']))
        except:
            return render(request, 'add_section.html', {'ERROR': 1})
    return HttpResponseRedirect(reverse('index'))


def remove_section(request, section_name):
    username = request.user.username

    if username:
        with connection.cursor() as cursor:
            cursor.callproc("remove_section", (username, section_name))

    return HttpResponseRedirect(reverse('index'))


def section(request, section_name):
    username = request.user.username

    with connection.cursor() as cursor:
        if username:
            nickname, user_role = cursor.callfunc('user_role_nickname', cx_Oracle.CURSOR, (username,)).fetchone()
        else:
            user_role = 'newbie'

        section_role = cursor.callfunc('section_role', cx_Oracle.STRING, (section_name,))

        roles = fetch_to_tuple(cursor.callfunc('check_roles', cx_Oracle.CURSOR, (user_role,)))
        if section_role not in roles:
            return HttpResponseRedirect(reverse('index'))

        moderators = (row[0] for row in
                      cursor.callfunc('get_section_moderators', cx_Oracle.CURSOR, (section_name,)).fetchall())

        is_moderator = user_role == 'admin' or (user_role == 'moderator' and username in moderators)
        topics = fetch_to_dict(cursor.callfunc('get_topics', cx_Oracle.CURSOR, (section_name,)))

        for topic in topics:
            topic['TAGS'] = (row[0] for row in
                             cursor.callfunc('get_topic_tags', cx_Oracle.CURSOR, (topic['NAME'],)).fetchall())

        roles = fetch_to_tuple(cursor.callfunc('check_roles', cx_Oracle.CURSOR, (user_role, 'write')))

    context = {'CAN_CREATE_TOPIC': section_role in roles,
               'IS_MODERATOR': is_moderator,
               'SECTION_NAME': section_name,
               'TOPICS': topics}

    return render(request, 'section.html', context)


def add_topic(request, section_name):
    username = request.user.username

    with connection.cursor() as cursor:
        if username:
            nickname, user_role = cursor.callfunc('user_role_nickname', cx_Oracle.CURSOR, (username,)).fetchone()
        else:
            user_role = 'newbie'

        section_role = cursor.callfunc('section_role', cx_Oracle.STRING, (section_name,))

        if section_role in fetch_to_tuple(cursor.callfunc('check_roles', cx_Oracle.CURSOR, (user_role,))):
            if request.method == 'GET':
                return render(request, 'add_topic.html', {'section_name': section_name})

            elif request.method == 'POST':
                cursor.callproc('add_topic',
                                (request.POST['name'], request.POST['description'], section_name, username))
                try:
                    if request.POST['tags']:
                        tags = set(request.POST['tags'].split())
                        for tag in tags:
                            cursor.callproc('add_tag', (tag, request.POST['name']))
                except:
                    return render(request, 'add_topic.html', {'section_name': section_name, 'error': 1})

    return HttpResponseRedirect(reverse('section', args=(section_name,)))


def remove_topic(request, section_name, topic_name):
    username = request.user.username

    if username:
        with connection.cursor() as cursor:

            nickname, user_role = cursor.callfunc('user_role_nickname', cx_Oracle.CURSOR, (username,)).fetchone()

            if user_role in ('admin', 'moderator'):

                moderators = (row[0] for row in
                              cursor.callfunc('get_section_moderators', cx_Oracle.CURSOR, (section_name,)).fetchall())

                if user_role == 'admin' or username in moderators:
                    cursor.callproc('remove_topic', (topic_name, request.user.username))

    return HttpResponseRedirect(reverse('section', args=(section_name,)))


def topics_by_tag(request, tag_name):
    username = request.user.username

    with connection.cursor() as cursor:
        if username:
            nickname, user_role = cursor.callfunc('user_role_nickname', cx_Oracle.CURSOR, (username,)).fetchone()
        else:
            user_role = 'newbie'

        allowed_roles = fetch_to_tuple(cursor.callfunc('check_roles', cx_Oracle.CURSOR, (user_role,)))

        cursor.execute('''SELECT tp.name, tp.description, tp.create_date, u.nickname, u.username, s.name AS section_name
                          FROM tags tg, tags_topics tt, topics tp, sections s, ROLES r, USERS u
                          WHERE u.id = tp.user_id
                          AND s.role_id = r.id
                          AND r.name IN {0}
                          AND s.id = tp.section_id
                          AND tp.id = tt.topic_id
                          AND tt.tag_id = tg.id
                          AND tg.name = %s;'''.format(allowed_roles), (tag_name,))
        topics = fetch_to_dict(cursor)

    context = {'TAG_NAME': tag_name, 'TOPICS': topics}

    return render(request, 'topics_by_tag.html', context)


def topic(request, section_name, topic_name):
    username = request.user.username

    with connection.cursor() as cursor:
        if username:
            nickname, user_role = cursor.callfunc('user_role_nickname', cx_Oracle.CURSOR, (username,)).fetchone()
        else:
            user_role = 'newbie'

        section_role = cursor.callfunc('section_role', cx_Oracle.STRING, (section_name,))

        if section_role in fetch_to_tuple(cursor.callfunc('check_roles', cx_Oracle.CURSOR, (user_role,))):
            exists = cursor.callfunc('topic_exists', cx_Oracle.NUMBER, (topic_name,))
            if int(exists):
                messages = fetch_to_dict(cursor.callfunc('get_messages', cx_Oracle.CURSOR, (topic_name,)))

                moderators = (row[0] for row in
                              cursor.callfunc('get_section_moderators', cx_Oracle.CURSOR, (section_name,)).fetchall())

                is_moderator = user_role == 'admin' or (user_role == 'moderator' and username in moderators)
                can_add_message = section_role in fetch_to_tuple(
                    cursor.callfunc('check_roles', cx_Oracle.CURSOR, (user_role, 'write'))) and username

                context = {'SECTION_NAME': section_name, 'TOPIC_NAME': topic_name,
                           'MESSAGES': messages,
                           'USER': {'IS_MODERATOR': is_moderator, 'USERNAME': username,
                                    'CAN_ADD_MESSAGE': can_add_message}}

                return render(request, 'topic.html', context)

    return HttpResponseRedirect(reverse('section', args=(section_name,)))


def add_message(request, section_name, topic_name):
    username = request.user.username

    if username and request.method == 'POST':
        with connection.cursor() as cursor:
            nickname, user_role = cursor.callfunc('user_role_nickname', cx_Oracle.CURSOR, (username,)).fetchone()

            section_role = cursor.callfunc('section_role', cx_Oracle.STRING, (section_name,))

            if section_role in fetch_to_tuple(cursor.callfunc('check_roles', cx_Oracle.CURSOR, (user_role, 'write'))):
                cursor.callproc('add_message', (request.POST['text'], request.user.username, topic_name))

    return HttpResponseRedirect(reverse('topic', args=(section_name, topic_name)))


def like_message(request, section_name, topic_name, message_id):
    username = request.user.username

    if username:
        with connection.cursor() as cursor:
            cursor.callproc('add_like', (username, message_id))

    return HttpResponseRedirect(reverse('topic', args=(section_name, topic_name)))


def remove_message(request, section_name, topic_name, message_id):
    username = request.user.username

    if username:
        with connection.cursor() as cursor:
            nickname, user_role = cursor.callfunc('user_role_nickname', cx_Oracle.CURSOR, (username,)).fetchone()

            cursor.execute('''SELECT username
                              FROM messages, users
                              WHERE users.id = messages.user_id
                              AND messages.id = %s;''', (message_id,))
            message_creator = cursor.fetchone()[0]

            moderators = (row[0] for row in
                          cursor.callfunc('get_section_moderators', cx_Oracle.CURSOR, (section_name,)).fetchall())

            if username == message_creator or user_role == 'admin' or (
                            user_role == 'moderator' and username in moderators):
                cursor.execute('''DELETE FROM messages WHERE id = %s''', (message_id,))
                cursor.callproc("log_add", (request.user.username, 'removed message id:{}'.format(message_id)))

    return HttpResponseRedirect(reverse('topic', args=(section_name, topic_name)))


def edit_message(request, section_name, topic_name, message_id):
    username = request.user.username

    if username:
        with connection.cursor() as cursor:
            nickname, user_role = cursor.callfunc('user_role_nickname', cx_Oracle.CURSOR, (username,)).fetchone()

            cursor.execute('''SELECT username
                              FROM messages, users
                              WHERE users.id = messages.user_id
                              AND messages.id = %s;''', (message_id,))
            message_creator = cursor.fetchone()[0]

            moderators = (row[0] for row in
                          cursor.callfunc('get_section_moderators', cx_Oracle.CURSOR, (section_name,)).fetchall())

            if username == message_creator or user_role == 'admin' or (
                            user_role == 'moderator' and username in moderators):
                if request.method == 'GET':
                    cursor.execute('''SELECT messages.id, username, nickname, text, messages.create_date, rating
                                      FROM messages, users
                                      WHERE users.id = messages.user_id
                                      AND messages.id = %s;''', (message_id,))

                    message = fetch_to_dict(cursor)[0]
                    context = {'SECTION_NAME': section_name, 'TOPIC_NAME': topic_name, 'MESSAGE_ID': message_id,
                               'MESSAGE': message}
                    return render(request, 'edit_message.html', context)
                elif request.method == 'POST':
                    cursor.execute('''UPDATE messages SET text = %s
                                      WHERE ID = %s;''',
                                   (request.POST['text'], message_id))
                    cursor.callproc("log_add", (request.user.username, 'edited message id:{}'.format(message_id)))

    return HttpResponseRedirect(reverse('topic', args=(section_name, topic_name)))
