/* Table Creation */

CREATE TABLE rooms (room_id int not null,
restaurant_name varchar(50) not null,
PRIMARY KEY (room_id));

CREATE TABLE users (user_id int not null,
username varchar(15) not null,
room_id int,
PRIMARY KEY (user_id),
FOREIGN KEY (room_id) REFERENCES rooms);

CREATE TABLE inventory (type_id int not null,
item_id int not null,
quantity int not null,
room_id int not null,
PRIMARY KEY(type_id, item_id),
FOREIGN KEY (room_id) REFERENCES rooms);

CREATE TABLE cookbooks (cookbook_id int not null,
room_id int not null,
cookbook_name varchar(100),
cookbook_purchased BOOL not null DEFAULT FALSE,
PRIMARY KEY (cookbook_id),
FOREIGN KEY (room_id) REFERENCES rooms);

CREATE TABLE recipes (recipe_id int not null,
room_id int not null,
recipe_name varchar(100) not null,
cookbook_id int not null,
recipe_unlocked bool not NULL DEFAULT FALSE,
PRIMARY KEY (recipe_id),
FOREIGN KEY (room_id) REFERENCES rooms,
FOREIGN KEY (cookbook_id) REFERENCES cookbooks);

CREATE TABLE customers ( customer_id int not null,
room_id int not null,
recipe_id int not null,
PRIMARY KEY (customer_id, room_id),
FOREIGN KEY (room_id) references rooms,
FOREIGN KEY (recipe_id) references recipes)