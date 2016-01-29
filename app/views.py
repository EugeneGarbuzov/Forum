from django.contrib import auth
from django.core.urlresolvers import reverse
from django.db import connection
from django.http import HttpResponseRedirect
from django.shortcuts import render

from Forum.tools import fetch_to_dict, check_roles, log


# Create your views here.


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
                cursor.execute('''INSERT INTO users(role_id, rank_id, username, password, email, nickname, full_name, date, status,signature)
                                  SELECT role_id, rank_id, %s, %s, %s, %s, %s, now(), %s, %s FROM ROLES, ranks
                                  WHERE role_name = 'newbie' AND rank_name = 'rank_1';''',
                               (request.POST['username'], request.POST['password'], request.POST['email'],
                                request.POST['nickname'], request.POST['full_name'],
                                request.POST['status'], request.POST['signature']))
                user = auth.authenticate(username=request.POST['username'], password=request.POST['password'])
                auth.login(request, user)

                # журналирование событий в базе данных
                log(request.POST['username'], 'registered')
                return HttpResponseRedirect(reverse('index'))
        except:
            return render(request, 'register.html', {'error': 1})

    return render(request, "register.html")


def profile(request, username):
    try:
        with connection.cursor() as cursor:
            cursor.execute('''SELECT username, nickname, full_name, DATE, status,
                              signature, role_name, rank_name, bonus_rating
                              FROM USERS, ROLES, ranks
                              WHERE USERS.role_id = ROLES.role_id
                              AND ranks.rank_id = USERS.rank_id
                              AND username = %s;''', username)
            user = fetch_to_dict(cursor)[0]

            cursor.execute('''SELECT trophy_name, description
                              FROM trophies, trophies_users, users
                              WHERE trophies.trophy_id = trophies_users.trophy_id
                              AND trophies_users.user_id = users.user_id
                              AND username = %s;''', username)
            trophies = fetch_to_dict(cursor)

            cursor.execute('''SELECT sections.name
                              FROM users, sections_users, sections
                              WHERE sections.section_id = sections_users.section_id
                              AND sections_users.user_id = users.user_id
                              AND username = %s;''', username)
            moderated_sections = cursor.fetchall()

            if moderated_sections:
                moderated_sections = moderated_sections[0]

            context = {'user_info': user, 'trophies': trophies, 'moderated_sections': moderated_sections}
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
                cursor.execute('''SELECT email, nickname, full_name, status, signature
                                  FROM users
                                  WHERE username = %s;''', username)
                user = fetch_to_dict(cursor)[0]
                return render(request, 'edit_profile.html', user)

            elif request.method == 'POST':
                cursor.execute('''UPDATE users SET password = %s, email = %s, nickname = %s,
                                  full_name = %s, status = %s, signature = %s
                                  WHERE username = %s;''',
                               (request.POST['password'], request.POST['email'],
                                request.POST['nickname'], request.POST['full_name'],
                                request.POST['status'], request.POST['signature'],
                                username))
                log(request.user.username, 'edited profile')
                return HttpResponseRedirect(reverse('index'))
    except:
        return render(request, 'edit_profile.html', {'error': 1})


def index(request):
    username = request.user.username

    with connection.cursor() as cursor:
        if username:
            cursor.execute('''SELECT nickname, role_name
                              FROM users, roles
                              WHERE roles.role_id = users.role_id
                              AND username = %s;''', username)
            nickname, role = cursor.fetchone()
        else:
            nickname = ''
            role = 'newbie'

        roles = check_roles(role)

        cursor.execute('''SELECT s.name, s.description, s.date,
                          (SELECT role_name FROM roles WHERE roles.role_id = s.role_id)  AS role_name
                          FROM sections AS s, ROLES AS r
                          WHERE s.role_id = r.role_id
                          AND r.role_name IN %s;''', [tuple(roles)])
        sections = fetch_to_dict(cursor)

        for section in sections:
            cursor.execute('''SELECT username, nickname
                              FROM users, sections, sections_users
                              WHERE users.user_id = sections_users.user_id
                              AND sections_users.section_id = sections.section_id
                              AND name = %s;''', section['name'])
            section['moderators'] = fetch_to_dict(cursor)

    context = {'user': {'nickname': nickname, 'username': username, 'is_admin': role == 'admin'},
               'sections': sections}

    return render(request, 'index.html', context)


def add_section(request):
    username = request.user.username

    if username:
        try:
            with connection.cursor() as cursor:
                cursor.execute('''SELECT role_name
                                  FROM users, roles
                                  WHERE roles.role_id = users.role_id
                                  AND username = %s;''', username)
                role = cursor.fetchone()[0]

                if role == 'admin':
                    if request.method == 'GET':
                        return render(request, 'add_section.html')
                    elif request.method == 'POST':
                        cursor.execute('''INSERT INTO sections(role_id, name, date, description)
                                          SELECT role_id, %s, now(), %s
                                          FROM ROLES WHERE role_name = %s;''',
                                       (request.POST['name'], request.POST['description'], request.POST['role_name']))
                        log(request.user.username, 'added section {}'.format(request.POST['name']))
        except:
            return render(request, 'add_section.html', {'error': 1})

    return HttpResponseRedirect(reverse('index'))


def remove_section(request, section_name):
    username = request.user.username

    if username:
        with connection.cursor() as cursor:
            cursor.execute('''SELECT role_name
                              FROM users, roles
                              WHERE roles.role_id = users.role_id
                              AND username = %s;''', username)
            role = cursor.fetchone()[0]

            if role == 'admin':
                cursor.execute('''DELETE FROM sections WHERE name = %s''', section_name)
                log(request.user.username, 'removed section {}'.format(section_name))

    return HttpResponseRedirect(reverse('index'))


def section(request, section_name):
    username = request.user.username

    with connection.cursor() as cursor:
        if username:
            cursor.execute('''SELECT role_name
                              FROM users, roles
                              WHERE roles.role_id = users.role_id
                              AND username = %s;''', username)
            user_role = cursor.fetchone()[0]
        else:
            user_role = 'newbie'

        cursor.execute('''SELECT role_name
                          FROM sections, roles
                          WHERE roles.role_id = sections.role_id
                          AND name = %s;''', section_name)
        section_role = cursor.fetchone()[0]

        if section_role not in check_roles(user_role):
            return HttpResponseRedirect(reverse('index'))

        cursor.execute('''SELECT username
                          FROM users, sections, sections_users
                          WHERE users.user_id = sections_users.user_id
                          AND sections_users.section_id = sections.section_id
                          AND name = %s;''', section_name)
        moderators = (row[0] for row in cursor.fetchall())

        is_moderator = user_role == 'admin' or (user_role == 'moderator' and username in moderators)

        cursor.execute('''SELECT t.name, t.description, t.date, u.nickname, u.username, s.name AS section_name
                          FROM topics AS t, USERS AS u, sections AS s
                          WHERE u.user_id = t.user_id
                          AND t.section_id = s.section_id
                          AND s.name = %s;''', section_name)
        topics = fetch_to_dict(cursor)

        for topic in topics:
            cursor.execute('''SELECT tag_name FROM tags_topics
                              JOIN tags ON tags.tag_id = tags_topics.tag_id
                              JOIN topics ON topics.topic_id = tags_topics.topic_id
                              WHERE name = %s;''', topic['name'])
            topic['tags'] = (row[0] for row in cursor.fetchall())

    context = {'can_create_topic': section_role in check_roles(user_role, 'write'),
               'is_moderator': is_moderator,
               'section_name': section_name,
               'topics': topics}

    return render(request, 'section.html', context)


def add_topic(request, section_name):
    username = request.user.username

    with connection.cursor() as cursor:
        if username:
            cursor.execute('''SELECT role_name
                              FROM users, roles
                              WHERE roles.role_id = users.role_id
                              AND username = %s;''', username)
            user_role = cursor.fetchone()[0]
        else:
            user_role = 'newbie'

        cursor.execute('''SELECT role_name
                          FROM sections, roles
                          WHERE roles.role_id = sections.role_id
                          AND name = %s;''', section_name)
        section_role = cursor.fetchone()[0]

        if section_role in check_roles(user_role):
            if request.method == 'GET':
                return render(request, 'add_topic.html', {'section_name': section_name})

            elif request.method == 'POST':
                try:
                    cursor.execute('''INSERT INTO topics(section_id, user_id, name, date, description)
                                      SELECT section_id, user_id, %s, now(), %s
                                      FROM sections, USERS
                                      WHERE NAME = %s
                                      AND username = %s;''',
                                   (request.POST['name'], request.POST['description'], section_name, username))
                    log(request.user.username, 'added topic {}'.format(request.POST['name']))

                    if request.POST['tags']:
                        tags = set(request.POST['tags'].split())
                        cursor.execute('''SELECT tag_name FROM tags;''')
                        existing_tags = (row[0] for row in cursor.fetchall())
                        for tag in tags:
                            if tag not in existing_tags:
                                cursor.execute('''INSERT INTO tags(tag_name) VALUES (%s);''', tag)
                            cursor.execute('''INSERT INTO tags_topics(tag_id, topic_id)
                                              SELECT tag_id, topic_id FROM tags, topics
                                              WHERE tag_name = %s
                                              AND name = %s;''', (tag, request.POST['name']))
                except:
                    return render(request, 'add_topic.html', {'section_name': section_name, 'error': 1})

    return HttpResponseRedirect(reverse('section', args=(section_name,)))


def remove_topic(request, section_name, topic_name):
    username = request.user.username

    if username:
        with connection.cursor() as cursor:

            cursor.execute('''SELECT role_name
                              FROM users, roles
                              WHERE roles.role_id = users.role_id
                              AND username = %s;''', username)
            user_role = cursor.fetchone()[0]

            if user_role in ('admin', 'moderator'):

                cursor.execute('''SELECT username
                                  FROM users, sections, sections_users
                                  WHERE users.user_id = sections_users.user_id
                                  AND sections_users.section_id = sections.section_id
                                  AND name = %s;''', section_name)
                moderators = (row[0] for row in cursor.fetchall())

                if user_role == 'admin' or username in moderators:
                    cursor.execute('''DELETE FROM topics WHERE name = %s''', topic_name)
                    log(request.user.username, 'removed topic {}'.format(topic_name))

    return HttpResponseRedirect(reverse('section', args=(section_name,)))


def topics_by_tag(request, tag_name):
    username = request.user.username

    with connection.cursor() as cursor:
        if username:
            cursor.execute('''SELECT role_name
                              FROM users, roles
                              WHERE roles.role_id = users.role_id
                              AND username = %s;''', username)
            user_role = cursor.fetchone()[0]
        else:
            user_role = 'newbie'

        allowed_roles = check_roles(user_role)

        cursor.execute('''SELECT tp.name, tp.description, tp.date, u.nickname, u.username, s.name AS section_name
                          FROM tags AS tg, tags_topics AS tt, topics AS tp, sections AS s, ROLES AS r, USERS AS u
                          WHERE u.user_id = tp.user_id
                          AND s.role_id = r.role_id
                          AND r.role_name IN %s
                          AND s.section_id = tp.section_id
                          AND tp.topic_id = tt.topic_id
                          AND tt.tag_id = tg.tag_id
                          AND tg.tag_name = %s;''', [tuple(allowed_roles), tag_name])
        topics = fetch_to_dict(cursor)

    context = {'tag_name': tag_name, 'topics': topics}

    return render(request, 'topics_by_tag.html', context)


def topic(request, section_name, topic_name):
    username = request.user.username

    with connection.cursor() as cursor:
        if username:
            cursor.execute('''SELECT role_name
                              FROM users, roles
                              WHERE roles.role_id = users.role_id
                              AND username = %s;''', username)
            user_role = cursor.fetchone()[0]
        else:
            user_role = 'newbie'

        cursor.execute('''SELECT role_name
                          FROM sections, roles
                          WHERE roles.role_id = sections.role_id
                          AND name = %s;''', section_name)
        section_role = cursor.fetchone()[0]

        if section_role in check_roles(user_role):
            cursor.execute('''SELECT count(*) FROM topics WHERE topics.name = %s;''', topic_name)

            if cursor.fetchone()[0]:
                cursor.execute('''SELECT message_id, username, nickname, text, messages.date, rating
                                  FROM messages, users, topics
                                  WHERE users.user_id = messages.user_id
                                  AND messages.topic_id = topics.topic_id
                                  AND topics.name = %s;''', topic_name)
                messages = fetch_to_dict(cursor)

                cursor.execute('''SELECT username
                                  FROM users, sections, sections_users
                                  WHERE users.user_id = sections_users.user_id
                                  AND sections_users.section_id = sections.section_id
                                  AND name = %s;''', section_name)
                moderators = (row[0] for row in cursor.fetchall())

                is_moderator = user_role == 'admin' or (user_role == 'moderator' and username in moderators)
                can_add_message = section_role in check_roles(user_role, mode='write') and username

                context = {'section_name': section_name, 'topic_name': topic_name,
                           'messages': messages,
                           'user': {'is_moderator': is_moderator, 'username': username,
                                    'can_add_message': can_add_message}}

                return render(request, 'topic.html', context)

    return HttpResponseRedirect(reverse('section', args=(section_name,)))


def add_message(request, section_name, topic_name):
    username = request.user.username

    if username and request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute('''SELECT role_name
                              FROM users, roles
                              WHERE roles.role_id = users.role_id
                              AND username = %s;''', username)
            user_role = cursor.fetchone()[0]

            cursor.execute('''SELECT role_name
                              FROM sections, roles
                              WHERE roles.role_id = sections.role_id
                              AND name = %s;''', section_name)
            section_role = cursor.fetchone()[0]

            if section_role in check_roles(user_role, mode='write'):
                cursor.execute('''INSERT INTO messages (date, text, rating, user_id, topic_id)
                                  SELECT now(), %s, 0, USERS.user_id, topics.topic_id
                                  FROM USERS, topics
                                  WHERE USERS.username = %s
                                  AND topics.name = %s;''',
                               (request.POST['text'], username, topic_name))
                log(request.user.username, 'added message')

    return HttpResponseRedirect(reverse('topic', args=(section_name, topic_name)))


def like_message(request, section_name, topic_name, message_id):
    username = request.user.username

    if username:
        with connection.cursor() as cursor:
            cursor.execute('''SELECT bonus_rating
                              FROM users, ranks
                              WHERE ranks.rank_id = users.rank_id
                              AND username = %s;''', username)
            bonus_rating = cursor.fetchone()[0]

            cursor.execute('''SELECT count(*) FROM likes
                              JOIN users ON users.user_id = likes.user_id
                              WHERE message_id = %s
                              AND username = %s;''', (message_id, username))
            already_liked = cursor.fetchone()[0] > 0

            cursor.execute('''SELECT username FROM messages
                              JOIN users ON users.user_id = messages.user_id
                              WHERE message_id = %s;''', message_id)
            is_message_author = cursor.fetchone()[0] == username

            if not already_liked and not is_message_author:
                cursor.execute('''UPDATE messages SET rating = messages.rating + %s
                                  WHERE message_id = %s;''', (bonus_rating, message_id))
                cursor.execute('''INSERT INTO likes (message_id, user_id)
                                  SELECT %s, user_id FROM USERS
                                  WHERE username = %s;''', (message_id, username))

    return HttpResponseRedirect(reverse('topic', args=(section_name, topic_name)))


def remove_message(request, section_name, topic_name, message_id):
    username = request.user.username

    if username:
        with connection.cursor() as cursor:
            cursor.execute('''SELECT role_name
                              FROM users, roles
                              WHERE roles.role_id = users.role_id
                              AND username = %s;''', username)
            user_role = cursor.fetchone()[0]

            cursor.execute('''SELECT username
                              FROM messages, users
                              WHERE users.user_id = messages.user_id
                              AND messages.message_id = %s;''', message_id)
            message_creator = cursor.fetchone()[0]

            cursor.execute('''SELECT username
                              FROM users, sections, sections_users
                              WHERE users.user_id = sections_users.user_id
                              AND sections_users.section_id = sections.section_id
                              AND name = %s;''', section_name)
            moderators = (row[0] for row in cursor.fetchall())

            if username == message_creator or user_role == 'admin' or (
                            user_role == 'moderator' and username in moderators):
                cursor.execute('''DELETE FROM messages WHERE message_id = %s''', message_id)
                log(request.user.username, 'removed message id:{}'.format(message_id))

    return HttpResponseRedirect(reverse('topic', args=(section_name, topic_name)))


def edit_message(request, section_name, topic_name, message_id):
    username = request.user.username

    if username:
        with connection.cursor() as cursor:
            cursor.execute('''SELECT role_name
                              FROM users, roles
                              WHERE roles.role_id = users.role_id
                              AND username = %s;''', username)
            user_role = cursor.fetchone()[0]

            cursor.execute('''SELECT username
                              FROM messages, users
                              WHERE users.user_id = messages.user_id
                              AND messages.message_id = %s;''', message_id)
            message_creator = cursor.fetchone()[0]

            cursor.execute('''SELECT username
                              FROM users, sections, sections_users
                              WHERE users.user_id = sections_users.user_id
                              AND sections_users.section_id = sections.section_id
                              AND name = %s;''', section_name)
            moderators = (row[0] for row in cursor.fetchall())

            if username == message_creator or user_role == 'admin' or (
                            user_role == 'moderator' and username in moderators):
                if request.method == 'GET':
                    cursor.execute('''SELECT message_id, username, nickname, text, messages.date, rating
                                      FROM messages, users
                                      WHERE users.user_id = messages.user_id
                                      AND message_id = %s;''', message_id)

                    message = fetch_to_dict(cursor)[0]
                    context = {'section_name': section_name, 'topic_name': topic_name, 'message_id': message_id,
                               'message': message}
                    return render(request, 'edit_message.html', context)
                elif request.method == 'POST':
                    cursor.execute('''UPDATE messages SET text = %s
                                      WHERE message_id = %s;''',
                                   (request.POST['text'], message_id))
                    log(request.user.username, 'edited message id:{}'.format(message_id))

    return HttpResponseRedirect(reverse('topic', args=(section_name, topic_name)))
