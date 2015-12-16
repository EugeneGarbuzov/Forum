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
                cursor.execute('''insert into users(role_id, rank_id, username, password, email, nickname, full_name, date, status,signature)
                                  select role_id, rank_id, %s, %s, %s, %s, %s, now(), %s, %s from roles, ranks
                                  where role_name = 'newbie' and rank_name = 'rank_1';''',
                               (request.POST['username'], request.POST['password'], request.POST['email'],
                                request.POST['nickname'], request.POST['full_name'],
                                request.POST['status'], request.POST['signature']))
                user = auth.authenticate(username=request.POST['username'], password=request.POST['password'])
                auth.login(request, user)
                log(request.POST['username'], 'registered')
                return HttpResponseRedirect(reverse('index'))
        except:
            return render(request, 'register.html', {'error': 1})

    return render(request, "register.html")


def profile(request, username):
    try:
        with connection.cursor() as cursor:
            cursor.execute('''select username, nickname, full_name, date, status,
                              signature, role_name, rank_name, bonus_rating
                              from users, roles, ranks
                              where users.role_id = roles.role_id
                              and ranks.rank_id = users.rank_id
                              and username = %s;''', username)
            user = fetch_to_dict(cursor)[0]

            cursor.execute('''select trophy_name, description
                              from trophies, trophies_users, users
                              where trophies.trophy_id = trophies_users.trophy_id
                              and trophies_users.user_id = users.user_id
                              and username = %s;''', username)
            trophies = fetch_to_dict(cursor)

            cursor.execute('''select sections.name
                              from users, sections_users, sections
                              where sections.section_id = sections_users.section_id
                              and sections_users.user_id = users.user_id
                              and username = %s;''', username)
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
                cursor.execute('''select email, nickname, full_name, status, signature
                                  from users
                                  where username = %s;''', username)
                user = fetch_to_dict(cursor)[0]
                return render(request, 'edit_profile.html', user)

            elif request.method == 'POST':
                cursor.execute('''update users set password = %s, email = %s, nickname = %s,
                                  full_name = %s, status = %s, signature = %s
                                  where username = %s;''',
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
            cursor.execute('''select nickname, role_name
                              from users, roles
                              where roles.role_id = users.role_id
                              and username = %s;''', username)
            nickname, role = cursor.fetchone()
        else:
            nickname = ''
            role = 'newbie'

        roles = check_roles(role)

        cursor.execute('''select s.name, s.description, s.date,
                          (select role_name from roles where roles.role_id = s.role_id)  as role_name
                          from sections as s, roles as r
                          where s.role_id = r.role_id
                          and r.role_name in %s;''', [tuple(roles)])
        sections = fetch_to_dict(cursor)

        for section in sections:
            cursor.execute('''select username, nickname
                              from users, sections, sections_users
                              where users.user_id = sections_users.user_id
                              and sections_users.section_id = sections.section_id
                              and name = %s;''', section['name'])
            section['moderators'] = fetch_to_dict(cursor)

    context = {'user': {'nickname': nickname, 'username': username, 'is_admin': role == 'admin'},
               'sections': sections}

    return render(request, 'index.html', context)


def add_section(request):
    username = request.user.username

    if username:
        try:
            with connection.cursor() as cursor:
                cursor.execute('''select role_name
                                  from users, roles
                                  where roles.role_id = users.role_id
                                  and username = %s;''', username)
                role = cursor.fetchone()[0]

                if role == 'admin':
                    if request.method == 'GET':
                        return render(request, 'add_section.html')
                    elif request.method == 'POST':
                        cursor.execute('''insert into sections(role_id, name, date, description)
                                          select role_id, %s, now(), %s
                                          from roles where role_name = %s;''',
                                       (request.POST['name'], request.POST['description'], request.POST['role_name']))
                        log(request.user.username, 'added section {}'.format(request.POST['name']))
        except:
            return render(request, 'add_section.html', {'error': 1})

    return HttpResponseRedirect(reverse('index'))


def remove_section(request, section_name):
    username = request.user.username

    if username:
        with connection.cursor() as cursor:
            cursor.execute('''select role_name
                              from users, roles
                              where roles.role_id = users.role_id
                              and username = %s;''', username)
            role = cursor.fetchone()[0]

            if role == 'admin':
                cursor.execute('''delete from sections where name = %s''', section_name)
                log(request.user.username, 'removed section {}'.format(section_name))

    return HttpResponseRedirect(reverse('index'))


def section(request, section_name):
    username = request.user.username

    with connection.cursor() as cursor:
        if username:
            cursor.execute('''select role_name
                              from users, roles
                              where roles.role_id = users.role_id
                              and username = %s;''', username)
            user_role = cursor.fetchone()[0]
        else:
            user_role = 'newbie'

        cursor.execute('''select role_name
                          from sections, roles
                          where roles.role_id = sections.role_id
                          and name = %s;''', section_name)
        section_role = cursor.fetchone()[0]

        if section_role not in check_roles(user_role):
            return HttpResponseRedirect(reverse('index'))

        cursor.execute('''select username
                          from users, sections, sections_users
                          where users.user_id = sections_users.user_id
                          and sections_users.section_id = sections.section_id
                          and name = %s;''', section_name)
        moderators = (row[0] for row in cursor.fetchall())

        is_moderator = user_role == 'admin' or (user_role == 'moderator' and username in moderators)

        cursor.execute('''select t.name, t.description, t.date, u.nickname, u.username, s.name as section_name
                          from topics as t, users as u, sections as s
                          where u.user_id = t.user_id
                          and t.section_id = s.section_id
                          and s.name = %s;''', section_name)
        topics = fetch_to_dict(cursor)

        for topic in topics:
            cursor.execute('''select tag_name from tags_topics
                              join tags on tags.tag_id = tags_topics.tag_id
                              join topics on topics.topic_id = tags_topics.topic_id
                              where name = %s;''', topic['name'])
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
            cursor.execute('''select role_name
                              from users, roles
                              where roles.role_id = users.role_id
                              and username = %s;''', username)
            user_role = cursor.fetchone()[0]
        else:
            user_role = 'newbie'

        cursor.execute('''select role_name
                          from sections, roles
                          where roles.role_id = sections.role_id
                          and name = %s;''', section_name)
        section_role = cursor.fetchone()[0]

        if section_role in check_roles(user_role):
            if request.method == 'GET':
                return render(request, 'add_topic.html', {'section_name': section_name})

            elif request.method == 'POST':
                try:
                    cursor.execute('''insert into topics(section_id, user_id, name, date, description)
                                      select section_id, user_id, %s, now(), %s
                                      from sections, users
                                      where name = %s
                                      and username = %s;''',
                                   (request.POST['name'], request.POST['description'], section_name, username))
                    log(request.user.username, 'added topic {}'.format(request.POST['name']))

                    if request.POST['tags']:
                        tags = set(request.POST['tags'].split())
                        cursor.execute('''SELECT tag_name FROM tags;''')
                        existing_tags = (row[0] for row in cursor.fetchall())
                        for tag in tags:
                            if tag not in existing_tags:
                                cursor.execute('''insert into tags(tag_name) values (%s);''', tag)
                            cursor.execute('''insert into tags_topics(tag_id, topic_id)
                                              select tag_id, topic_id from tags, topics
                                              where tag_name = %s
                                              and name = %s;''', (tag, request.POST['name']))
                except:
                    return render(request, 'add_topic.html', {'section_name': section_name, 'error': 1})

    return HttpResponseRedirect(reverse('section', args=(section_name,)))


def remove_topic(request, section_name, topic_name):
    username = request.user.username

    if username:
        with connection.cursor() as cursor:

            cursor.execute('''select role_name
                              from users, roles
                              where roles.role_id = users.role_id
                              and username = %s;''', username)
            user_role = cursor.fetchone()[0]

            if user_role in ('admin', 'moderator'):

                cursor.execute('''select username
                                  from users, sections, sections_users
                                  where users.user_id = sections_users.user_id
                                  and sections_users.section_id = sections.section_id
                                  and name = %s;''', section_name)
                moderators = (row[0] for row in cursor.fetchall())

                if user_role == 'admin' or username in moderators:
                    cursor.execute('''delete from topics where name = %s''', topic_name)
                    log(request.user.username, 'removed topic {}'.format(topic_name))

    return HttpResponseRedirect(reverse('section', args=(section_name,)))


def topics_by_tag(request, tag_name):
    username = request.user.username

    with connection.cursor() as cursor:
        if username:
            cursor.execute('''select role_name
                              from users, roles
                              where roles.role_id = users.role_id
                              and username = %s;''', username)
            user_role = cursor.fetchone()[0]
        else:
            user_role = 'newbie'

        allowed_roles = check_roles(user_role)

        cursor.execute('''select tp.name, tp.description, tp.date, u.nickname, u.username, s.name as section_name
                          from tags as tg, tags_topics as tt, topics as tp, sections as s, roles as r, users as u
                          where u.user_id = tp.user_id
                          and s.role_id = r.role_id
                          and r.role_name in %s
                          and s.section_id = tp.section_id
                          and tp.topic_id = tt.topic_id
                          and tt.tag_id = tg.tag_id
                          and tg.tag_name = %s;''', [tuple(allowed_roles), tag_name])
        topics = fetch_to_dict(cursor)

    context = {'tag_name': tag_name, 'topics': topics}

    return render(request, 'topics_by_tag.html', context)


def topic(request, section_name, topic_name):
    username = request.user.username

    with connection.cursor() as cursor:
        if username:
            cursor.execute('''select role_name
                              from users, roles
                              where roles.role_id = users.role_id
                              and username = %s;''', username)
            user_role = cursor.fetchone()[0]
        else:
            user_role = 'newbie'

        cursor.execute('''select role_name
                          from sections, roles
                          where roles.role_id = sections.role_id
                          and name = %s;''', section_name)
        section_role = cursor.fetchone()[0]

        if section_role in check_roles(user_role):
            cursor.execute('''select count(*) from topics where topics.name = %s;''', topic_name)

            if cursor.fetchone()[0]:
                cursor.execute('''select message_id, username, nickname, text, messages.date, rating
                                  from messages, users, topics
                                  where users.user_id = messages.user_id
                                  and messages.topic_id = topics.topic_id
                                  and topics.name = %s;''', topic_name)
                messages = fetch_to_dict(cursor)

                cursor.execute('''select username
                                  from users, sections, sections_users
                                  where users.user_id = sections_users.user_id
                                  and sections_users.section_id = sections.section_id
                                  and name = %s;''', section_name)
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
            cursor.execute('''select role_name
                              from users, roles
                              where roles.role_id = users.role_id
                              and username = %s;''', username)
            user_role = cursor.fetchone()[0]

            cursor.execute('''select role_name
                              from sections, roles
                              where roles.role_id = sections.role_id
                              and name = %s;''', section_name)
            section_role = cursor.fetchone()[0]

            if section_role in check_roles(user_role, mode='write'):
                cursor.execute('''insert into messages (date, text, rating, user_id, topic_id)
                                  select now(), %s, 0, users.user_id, topics.topic_id
                                  from users, topics
                                  where users.username = %s
                                  and topics.name = %s;''',
                               (request.POST['text'], username, topic_name))
                log(request.user.username, 'added message')

    return HttpResponseRedirect(reverse('topic', args=(section_name, topic_name)))


def like_message(request, section_name, topic_name, message_id):
    username = request.user.username

    if username:
        with connection.cursor() as cursor:
            cursor.execute('''select bonus_rating
                              from users, ranks
                              where ranks.rank_id = users.rank_id
                              and username = %s;''', username)
            bonus_rating = cursor.fetchone()[0]

            cursor.execute('''update messages set rating = messages.rating + %s
                            where message_id = %s;''', (bonus_rating, message_id))

    return HttpResponseRedirect(reverse('topic', args=(section_name, topic_name)))


def remove_message(request, section_name, topic_name, message_id):
    username = request.user.username

    if username:
        with connection.cursor() as cursor:
            cursor.execute('''select role_name
                              from users, roles
                              where roles.role_id = users.role_id
                              and username = %s;''', username)
            user_role = cursor.fetchone()[0]

            cursor.execute('''select username
                              from messages, users
                              where users.user_id = messages.user_id
                              and messages.message_id = %s;''', message_id)
            message_creator = cursor.fetchone()[0]

            cursor.execute('''select username
                              from users, sections, sections_users
                              where users.user_id = sections_users.user_id
                              and sections_users.section_id = sections.section_id
                              and name = %s;''', section_name)
            moderators = (row[0] for row in cursor.fetchall())

            if username == message_creator or user_role == 'admin' or (
                            user_role == 'moderator' and username in moderators):
                cursor.execute('''delete from messages where message_id = %s''', message_id)
                log(request.user.username, 'removed message id:{}'.format(message_id))

    return HttpResponseRedirect(reverse('topic', args=(section_name, topic_name)))


def edit_message(request, section_name, topic_name, message_id):
    username = request.user.username

    if username:
        with connection.cursor() as cursor:
            cursor.execute('''select role_name
                              from users, roles
                              where roles.role_id = users.role_id
                              and username = %s;''', username)
            user_role = cursor.fetchone()[0]

            cursor.execute('''select username
                              from messages, users
                              where users.user_id = messages.user_id
                              and messages.message_id = %s;''', message_id)
            message_creator = cursor.fetchone()[0]

            cursor.execute('''select username
                              from users, sections, sections_users
                              where users.user_id = sections_users.user_id
                              and sections_users.section_id = sections.section_id
                              and name = %s;''', section_name)
            moderators = (row[0] for row in cursor.fetchall())

            if username == message_creator or user_role == 'admin' or (
                            user_role == 'moderator' and username in moderators):
                if request.method == 'GET':
                    cursor.execute('''select message_id, username, nickname, text, messages.date, rating
                                      from messages, users
                                      where users.user_id = messages.user_id
                                      and message_id = %s;''', message_id)

                    message = fetch_to_dict(cursor)[0]
                    context = {'section_name': section_name, 'topic_name': topic_name, 'message_id': message_id,
                               'message': message}
                    return render(request, 'edit_message.html', context)
                elif request.method == 'POST':
                    cursor.execute('''update messages set text = %s
                                      where message_id = %s;''',
                                   (request.POST['text'], message_id))
                    log(request.user.username, 'edited message id:{}'.format(message_id))

    return HttpResponseRedirect(reverse('topic', args=(section_name, topic_name)))
