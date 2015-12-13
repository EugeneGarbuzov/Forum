start transaction;

use forum;

insert into Roles(Role_Name, Description) values
    ('Admin', 'Полный доступ.'),
    ('Moderator', 'Руководит закреплёнными за ним разделами.'),
    ('Regular', 'Обычный пользователь.'),
    ('Newbie', 'Может читать разделы для обычных пользователей, но писать только в песочнице.');

insert into Ranks(Rank_Name, Bonus_Rating) values
    ('Rank_1', 2),
    ('Rank_2', 5),
    ('Rank_3', 3),
    ('Rank_4', 4);

insert into Trophies(Trophy_Name) values
    ('Trophy_1'),
    ('Trophy_2'),
    ('Trophy_3'),
    ('Trophy_4'),
    ('Trophy_5');

insert into Tags(Tag_Name, References_Number) values
    ('Tag_1', 1),
    ('Tag_2', 1),
    ('Tag_3', 1),
    ('Tag_4', 1);

insert into Users
	(Role_ID,
	Rank_ID,
    
	Login,
	Password,
	email,
    
	Nickname,
	Full_Name,
	Date,
	Status,
	Signature) 

	select
    
	Role_ID,
	Rank_ID,
    
	'User_1',
	'password',
	'user1@example.com',
    
	'User_1',
	'Name1 Surname1',
	now(),
	'Status_1',
	'Signature_1'
    
	from Roles, Ranks
    where Roles.Role_Name = 'Regular' and Ranks.Rank_Name = 'Rank_1'
    limit 1;
    
insert into Users(Role_ID,
	Rank_ID,
    
	Login,
	Password,
	email,
    
	Nickname,
	Full_Name,
	Date,
	Status,
	Signature) 

	select
    
	Role_ID,
	Rank_ID,
    
	'User_2',
	'password',
	'user2@example.com',
    
	'User_2',
	'Name2 Surname2',
	now(),
	'Status_2',
	'Signature_2'
    
	from Roles, Ranks
    where Role_Name = 'Newbie' and Rank_Name = 'Rank_1'
    limit 1;
    
    insert into Users
	(Role_ID,
	Rank_ID,
    
	Login,
	Password,
	email,
    
	Nickname,
	Full_Name,
	Date,
	Status,
	Signature) 

	select
    
	Role_ID,
	Rank_ID,
    
	'Admin',
	'admin',
	'admin@example.com',
    
	'Admin',
	'Name Surname',
	now(),
	'Status',
	'Signature'
    
	from Roles, Ranks
    where Roles.Role_Name = 'Admin' and Ranks.Rank_Name = 'Rank_4';

-- update Users set Password='Pas100,./' where Login = 'User_1';
-- 
-- update Users set Status='Status_2' where Login = 'User_2';


insert into Journal(User_ID, Description, Date)
	select User_ID, 'Action_1', now() from Users where Login = 'User_1';
    
insert into Journal(User_ID, Description, Date)
	select User_ID, 'Action_2', now() from Users where Login = 'User_2';
    

insert into Sections(Role_ID, Name, Date, Description) values
	(3 ,'Section_1', now(), 'Section_1 description'),
    (4 , 'Section_2', now(), 'Section_2 description');


insert into Topics(Name, Date, Description, Section_ID, User_ID)
	select 'Topic_1', now(), 'Description of topic Topic_1', Sections.Section_ID, Users.User_ID from Sections, Users
		where Sections.Name = 'Section_1' and Users.Login = 'User_1'
        limit 1;

insert into Topics(Name, Date, Description, Section_ID, User_ID)
	select 'Topic_2', now(), 'Description of topic Topic_2', Sections.Section_ID, Users.User_ID from Sections, Users
		where Sections.Name = 'Section_2' and Users.Login = 'User_2'
        limit 1;


insert into Messages(Date, Text, Rating, User_ID, Topic_ID)
	select now(), 'Message_1', 1, Users.User_ID, Topics.Topic_ID from Users, Topics
		where Users.Login = 'User_1' and Topics.Name = 'Topic_1'
        limit 1;
        
insert into Messages(Date, Text, Rating, User_ID, Topic_ID)
	select now(), 'Message_1', 1, Users.User_ID, Topics.Topic_ID from Users, Topics
		where Users.Login = 'User_2' and Topics.Name = 'Topic_2'
        limit 1;


insert into Trophies_Users(Trophy_ID, User_ID, Description)
	select Trophies.Trophy_ID, Users.User_ID, 'Trophy_1 User_1 description.' from Trophies, Users
		where Trophies.Trophy_Name = 'Trophy_1' and Users.Login = 'User_1'
        limit 1;
        
insert into Trophies_Users(Trophy_ID, User_ID, Description)
	select Trophies.Trophy_ID, Users.User_ID, 'Trophy_2 User_2 description.' from Trophies, Users
		where Trophies.Trophy_Name = 'Trophy_2' and Users.Login = 'User_2'
        limit 1;


insert into Sections_Users(Section_ID, User_ID)
	select Sections.Section_ID, Users.User_ID from Sections, Users
		where Sections.Name = 'Section_1' and Users.Login = 'User_1'
        limit 1;
        
insert into Sections_Users(Section_ID, User_ID)
	select Sections.Section_ID, Users.User_ID from Sections, Users
		where Sections.Name = 'Section_2' and Users.Login = 'User_2'
        limit 1;


insert into Tags_Topics(Tag_ID, Topic_ID)
	select Tags.Tag_ID, Topics.Topic_ID from Tags, Topics
		where Tags.Tag_Name = 'Tag_1' and Topics.Name = 'Topic_1'
        limit 1;


insert into Tags_Topics(Tag_ID, Topic_ID)
	select Tags.Tag_ID, Topics.Topic_ID from Tags, Topics
		where Tags.Tag_Name = 'Tag_2' and Topics.Name = 'Topic_2'
        limit 1;


-- insert into Roles_Sections(Role_ID, Section_ID)
-- 	select Roles.Role_ID, Sections.Section_ID from Roles, Sections
-- 		where Roles.Role_Name = 'Role_1' and Sections.Name = 'Section_1'
--         limit 1;
-- 
-- insert into Roles_Sections(Role_ID, Section_ID)
-- 	select Roles.Role_ID, Sections.Section_ID from Roles, Sections
-- 		where Roles.Role_Name = 'Role_2' and Sections.Name = 'Section_2'
--         limit 1;

-- delete from Messages where Message_ID = 1;

commit;
