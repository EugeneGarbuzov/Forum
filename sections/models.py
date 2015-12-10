from django.db import models

# Create your models here.


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        return self.question_text


class Choice(models.Model):
    question = models.ForeignKey(Question)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text


class Journal(models.Model):
    entry_id = models.BigIntegerField(db_column='Entry_ID', primary_key=True)  # Field name made lowercase.
    user = models.ForeignKey('Users', db_column='User_ID')  # Field name made lowercase.
    description = models.TextField(db_column='Description')  # Field name made lowercase.
    date = models.DateTimeField(db_column='Date')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'journal'


class Messages(models.Model):
    message_id = models.BigIntegerField(db_column='Message_ID', primary_key=True)  # Field name made lowercase.
    user = models.ForeignKey('Users', db_column='User_ID')  # Field name made lowercase.
    topic = models.ForeignKey('Topics', db_column='Topic_ID')  # Field name made lowercase.
    date = models.DateTimeField(db_column='Date')  # Field name made lowercase.
    text = models.TextField(db_column='Text')  # Field name made lowercase.
    rating = models.IntegerField(db_column='Rating')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'messages'


class Ranks(models.Model):
    rank_id = models.BigIntegerField(db_column='Rank_ID', primary_key=True)  # Field name made lowercase.
    rank_name = models.CharField(db_column='Rank_Name', unique=True, max_length=30)  # Field name made lowercase.
    bonus_rating = models.IntegerField(db_column='Bonus_Rating')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ranks'


class Roles(models.Model):
    role_id = models.BigIntegerField(db_column='Role_ID', primary_key=True)  # Field name made lowercase.
    role_name = models.CharField(db_column='Role_Name', unique=True, max_length=30)  # Field name made lowercase.
    description = models.TextField(db_column='Description')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'roles'


class RolesSections(models.Model):
    role = models.ForeignKey('Roles', db_column='Role_ID')  # Field name made lowercase.
    section = models.ForeignKey('Sections', db_column='Section_ID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'roles_sections'
        unique_together = ['role', 'section']


class Sections(models.Model):
    section_id = models.BigIntegerField(db_column='Section_ID', primary_key=True)  # Field name made lowercase.
    user = models.ForeignKey('Users', db_column='User_ID')  # Field name made lowercase.
    name = models.CharField(db_column='Name', unique=True, max_length=30)  # Field name made lowercase.
    date = models.DateTimeField(db_column='Date')  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=30)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'sections'


class SectionsUsers(models.Model):
    section = models.ForeignKey(Sections, db_column='Section_ID')  # Field name made lowercase.
    user = models.ForeignKey('Users', db_column='User_ID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'sections_users'
        unique_together = ['section', 'user']


class Tags(models.Model):
    tag_id = models.BigIntegerField(db_column='Tag_ID', primary_key=True)  # Field name made lowercase.
    tag_name = models.CharField(db_column='Tag_Name', unique=True, max_length=30)  # Field name made lowercase.
    references_number = models.IntegerField(db_column='References_Number')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tags'


class TagsTopics(models.Model):
    tag = models.ForeignKey(Tags, db_column='Tag_ID')  # Field name made lowercase.
    topic = models.ForeignKey('Topics', db_column='Topic_ID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tags_topics'
        unique_together = ['tag', 'topic']


class Topics(models.Model):
    topic_id = models.BigIntegerField(db_column='Topic_ID', primary_key=True)  # Field name made lowercase.
    user = models.ForeignKey('Users', db_column='User_ID')  # Field name made lowercase.
    section = models.ForeignKey(Sections, db_column='Section_ID')  # Field name made lowercase.
    name = models.CharField(db_column='Name', unique=True, max_length=30)  # Field name made lowercase.
    date = models.DateTimeField(db_column='Date')  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=30)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'topics'


class Trophies(models.Model):
    trophy_id = models.BigIntegerField(db_column='Trophy_ID', primary_key=True)  # Field name made lowercase.
    trophy_name = models.CharField(db_column='Trophy_Name', unique=True, max_length=30)  # Field name made lowercase.
    trophy_image = models.TextField(db_column='Trophy_Image', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'trophies'


class TrophiesUsers(models.Model):
    trophy = models.ForeignKey(Trophies, db_column='Trophy_ID')  # Field name made lowercase.
    user = models.ForeignKey('Users', db_column='User_ID')  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=30)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'trophies_users'
        unique_together = ['trophy', 'user']


class Users(models.Model):
    user_id = models.BigIntegerField(db_column='User_ID', primary_key=True)  # Field name made lowercase.
    role = models.ForeignKey(Roles, db_column='Role_ID')  # Field name made lowercase.
    rank = models.ForeignKey(Ranks, db_column='Rank_ID')  # Field name made lowercase.
    login = models.CharField(db_column='Login', max_length=30)  # Field name made lowercase.
    password = models.CharField(db_column='Password', max_length=30)  # Field name made lowercase.
    email = models.CharField(max_length=30)
    user_image = models.TextField(db_column='User_Image', blank=True, null=True)  # Field name made lowercase.
    nickname = models.CharField(db_column='Nickname', max_length=30)  # Field name made lowercase.
    full_name = models.CharField(db_column='Full_Name', max_length=30)  # Field name made lowercase.
    date = models.DateTimeField(db_column='Date')  # Field name made lowercase.
    status = models.CharField(db_column='Status', max_length=30)  # Field name made lowercase.
    signature = models.CharField(db_column='Signature', max_length=50)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'users'
        unique_together = ['login', 'email']
