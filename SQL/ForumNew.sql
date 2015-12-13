drop database if exists Forum;
create database Forum;

-- CREATE USER 'Admin'@'localhost' IDENTIFIED BY '1234';
-- GRANT ALL PRIVILEGES ON Forum.* TO 'Admin'@'localhost';
-- FLUSH PRIVILEGES;
-- 
-- show grants for 'Admin'@'localhost';

use Forum;

create table Roles
(
	Role_ID              serial,
    
	Role_Name            varchar(30) not null,
	Description          text not null,
	
	primary key (Role_ID),
	unique (Role_Name)
);

create table Ranks
(
	Rank_ID              serial,
    
	Rank_Name            varchar(30) not null,
	Bonus_Rating         integer unsigned not null,
	
	primary key (RanK_ID),
	unique (Rank_Name)
);

create table Trophies
(
	Trophy_ID            serial,
    
	Trophy_Name          varchar(30) not null,
	Trophy_Image         longblob null,
	
	primary key (Trophy_ID),
	unique (Trophy_Name)
);

create table Tags
(
	Tag_ID               serial,
    
	Tag_Name             varchar(30) not null,
	References_Number    integer unsigned not null,
	
	primary key (Tag_ID),
	unique (Tag_Name)
);

create table Users
(
	User_ID              serial,
	Role_ID              bigint unsigned not null,
	Rank_ID              bigint unsigned not null,
    
	Login                varchar(30) not null,
	Password             varchar(30) not null,
	email                varchar(30) not null,
    
	User_Image           longblob null,
	Nickname             varchar(30) not null,
	Full_Name            varchar(30) not null,
	Date                 datetime not null,
	Status               varchar(30) not null,
	Signature            varchar(50) not null,
	
	primary key (User_ID),
	foreign key (Role_ID) references Roles (Role_ID),
	foreign key (Rank_ID) references Ranks (Rank_ID),
	unique (Login, email)
);

create table Journal
(
	Entry_ID             serial,
	User_ID              bigint unsigned not null,
    
	Description          text not null,
	Date                 datetime not null,
	
	primary key (Entry_ID),
	foreign key (User_ID) references Users (User_ID) on delete cascade
);

create table Sections
(
	Section_ID           serial,
	Role_ID              bigint unsigned not null,
  
	Name                 varchar(30) not null,
	Date                 datetime not null,
	Description          varchar(30) not null,
	
	primary key (Section_ID),
	foreign key (Role_ID) references Roles (Role_ID),
	unique (Name)
);

create table Topics
(
	Topic_ID             serial,
	User_ID              bigint unsigned not null,
	Section_ID           bigint unsigned not null,
	
	Name                 varchar(30) not null,
	Date                 datetime not null,
	Description          varchar(30) not null,
	
	primary key (Topic_ID),
	foreign key (Section_ID) references Sections (Section_ID) on delete cascade,
	foreign key (User_ID) references Users (User_ID) on delete cascade,
	unique (Name)
);

create table Messages
(
	Message_ID           serial,
	User_ID              bigint unsigned not null,
	Topic_ID             bigint unsigned not null,
    
	Date                 datetime not null,
	Text                 text not null,
	Rating               integer unsigned not null,
	
	primary key (Message_ID),
	foreign key (Topic_ID) references Topics (Topic_ID) on delete cascade,
	foreign key (User_ID) references Users (User_ID) on delete cascade
);

create table Trophies_Users
(
	Trophy_ID            bigint unsigned not null,
	User_ID              bigint unsigned not null,
    
	Description          varchar(30) not null,
    
	primary key (Trophy_ID, User_ID),
	foreign key (Trophy_ID) references Trophies (Trophy_ID) on delete cascade,
	foreign key (User_ID) references Users (User_ID) on delete cascade
);

create table Sections_Users
(
	Section_ID           bigint unsigned not null,
	User_ID              bigint unsigned not null,
    
	primary key (Section_ID, User_ID),
	foreign key (Section_ID) references Sections (Section_ID) on delete cascade,
	foreign key (User_ID) references Users (User_ID) on delete cascade
);

create table Tags_Topics
(
	Tag_ID               bigint unsigned not null,
	Topic_ID             bigint unsigned not null,
	

	primary key (Topic_ID,Tag_ID),
	foreign key (Topic_ID) references Topics (Topic_ID) on delete cascade,
	foreign key (Tag_ID) references Tags (Tag_ID) on delete cascade
);

-- create table Roles_Sections
-- (
-- 	Role_ID              bigint unsigned not null,
-- 	Section_ID           bigint unsigned not null,
--     
-- 	primary key (Role_ID,Section_ID),
-- 	foreign key (Role_ID) references Roles (Role_ID) on delete cascade,
-- 	foreign key (Section_ID) references Sections (Section_ID) on delete cascade
-- );