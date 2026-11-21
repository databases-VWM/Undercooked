/* Table Creation */

DROP DATABASE IF EXISTS undercooked;

CREATE DATABASE undercooked;

USE undercooked;

-- State preservation tables

CREATE TABLE rooms (
    room_id int not null,
    restaurant_name varchar(50) not null,
    current_money int not null,
    game_day int not null,
    day_time int,
    PRIMARY KEY (room_id)
);

CREATE TABLE users (
    user_id int not null,
    username varchar(15) not null,
    password varchar(255) not null,
    in_use bool not null,
    room_id int,
    PRIMARY KEY (user_id),
    FOREIGN KEY (room_id) REFERENCES rooms
);

CREATE TABLE inventory (
    type_id int not null,
    item_id int not null,
    item_name varchar(30) not null,
    quantity int not null,
    room_id int not null,
    PRIMARY KEY(type_id, item_id, room_id),
    FOREIGN KEY (room_id) REFERENCES rooms
);

-- Lookup tables

-- No dependencies
CREATE TABLE ingredients (
    ingredient_id int not null,
    ingredient_name varchar(50) not null,
    ingredient_type varchar(10) not null,
    PRIMARY KEY(ingredient_id)
);

-- No dependencies
CREATE TABLE areas (
    area_name varchar(100) not null,
    area_power int,
    PRIMARY KEY(area_name)
);

-- Depends on ingredients and areas. Junction table
CREATE TABLE area_ingredients (
    area_name varchar(100) not null,
    ingredient_id int not null,
    ingredient_weight int not null,
    PRIMARY KEY (area_name, ingredient_id),
    FOREIGN KEY (area_name) REFERENCES areas,
    FOREIGN KEY (ingredient_id) REFERENCES ingredients
);

-- Depends on areas
CREATE TABLE cookbooks (
    cookbook_name varchar(100) not null,
    area_name varchar(100),
    cookbook_price int,
    PRIMARY KEY (cookbook_name),
    FOREIGN KEY (area_name) REFERENCES areas
);

-- State table dependent on cookbooks
CREATE TABLE unlocked_cookbooks (
    cookbook_name varchar(100) not null,
    room_id int not null,
    PRIMARY KEY (cookbook_name, room_id),
    FOREIGN KEY (room_id) REFERENCES rooms,
    FOREIGN KEY (cookbook_name) REFERENCES cookbooks
);


-- Depends on cookbooks
CREATE TABLE recipes (
    recipe_name varchar(100) not null,
    cookbook_name varchar(100), 
    recipe_price int,
    PRIMARY KEY (recipe_name),
    FOREIGN KEY (cookbook_name) REFERENCES cookbooks
);

-- State preservation table. Depends on recipes
CREATE TABLE customers (
    customer_name varchar(100) not null,
    room_id int not null,
    recipe_name varchar(100) not null,
    PRIMARY KEY (customer_name, room_id),
    FOREIGN KEY (room_id) references rooms,
    FOREIGN KEY (recipe_name) REFERENCES recipes
);

-- No dependencies
CREATE TABLE enemies (
    enemy_name varchar(100) not null,
    enemy_health int not null,
    enemy_def int not null,
    is_boss bool not null,
    description varchar(500),
    PRIMARY KEY(enemy_name)
);

-- Reference table for enemies for their attack dice. Depends on enemies
CREATE TABLE enemy_attack_dice (
    enemy_name varchar(100) not null,
    num_dice int not null,
    dice_sides int not null,
    PRIMARY KEY (enemy_name, num_dice, dice_sides),
    FOREIGN KEY (enemy_name) REFERENCES enemies
);

-- Depends on enemies and areas. Junction table
CREATE TABLE area_enemies (
    area_name varchar(100) not null,
    enemy_name varchar(100) not null,
    enemy_weight int not null,
    PRIMARY KEY (area_name, enemy_name),
    FOREIGN KEY (area_name) references areas,
    FOREIGN KEY (enemy_name) REFERENCES enemies
);