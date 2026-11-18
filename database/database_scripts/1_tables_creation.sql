/* Table Creation */

CREATE DATABASE undercooked;

USE undercooked;

CREATE TABLE rooms (room_id int not null,
restaurant_name varchar(50) not null,
current_money int not null,
game_day int not null,
day_time time,
PRIMARY KEY (room_id));

CREATE TABLE users (user_id int not null,
username varchar(15) not null,
password varchar(255) not null,
in_use bool not null,
room_id int,
PRIMARY KEY (user_id),
FOREIGN KEY (room_id) REFERENCES rooms);

CREATE TABLE inventory (type_id int not null,
item_id int not null,
item_name varchar(30) not null,
quantity int not null,
room_id int not null,
PRIMARY KEY(type_id, item_id, room_id),
FOREIGN KEY (room_id) REFERENCES rooms);

CREATE TABLE cookbooks (cookbook_id int not null,
room_id int not null,
cookbook_name varchar(100),
cookbook_purchased BOOL not null DEFAULT FALSE,
PRIMARY KEY (cookbook_id, room_id),
FOREIGN KEY (room_id) REFERENCES rooms);

CREATE TABLE customers (customer_id int not null,
room_id int not null,
recipe_id int not null,
PRIMARY KEY (customer_id, room_id),
FOREIGN KEY (room_id) references rooms);

CREATE TABLE shop_queue (type_id int not null,
item_id int not null,
item_name varchar(30) not null,
ordered bool not null,
quantity int not null,
room_id int not null,
PRIMARY KEY (type_id, item_id, room_id),
FOREIGN KEY (room_id) REFERENCES rooms);