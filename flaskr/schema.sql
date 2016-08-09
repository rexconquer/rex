create table IF NOT EXISTS entries (
  id int primary key auto_increment,
  title varchar(30) not null,
  text varchar(50) not null
);
create table IF NOT EXISTS entries_app (
  id int primary key auto_increment,
  title varchar(30) not null,
  text varchar(50) not null
);
