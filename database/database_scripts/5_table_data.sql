-- Data should be inserted in this order(for dependencies):
-- ingredients, areas, area_ingredients, cookbooks, recipes, 
-- enemy_attack_dice, enemies, area_enemies, 

-- Ingredients
INSERT INTO ingredients VALUES(
    1,
    "Salmon",
    "fish"
);

INSERT INTO ingredients VALUES(
    2,
    "Catfish",
    "fish"
);

INSERT INTO ingredients VALUES(
    3,
    "Funni Mushroom",
    "plant"
);

INSERT INTO ingredients VALUES(
    4,
    "Boar Meat",
    "meat"
);

INSERT INTO ingredients VALUES(
    5,
    "Raw Hummingbird",
    "meat"
);

-- Areas
INSERT INTO areas VALUES(
    "Blasted Beach",
    22
);

INSERT INTO areas VALUES(
    "Craw's Domain",
    70
);

INSERT INTO areas VALUES(
    "Bombastic Badlands",
    1000
);

-- area_ingredients
INSERT INTO area_ingredients VALUES(
    "Blasted Beach",
    1,
    3
);

INSERT INTO area_ingredients VALUES(
    "Blasted Beach",
    2,
    2
);

INSERT INTO area_ingredients VALUES(
    "Blasted Beach",
    3,
    5
);

INSERT INTO area_ingredients VALUES(
    "Blasted Beach",
    5,
    2
);

INSERT INTO area_ingredients VALUES(
    "Craw's Domain",
    1,
    3
);

INSERT INTO area_ingredients VALUES(
    "Craw's Domain",
    2,
    3
);

INSERT INTO area_ingredients VALUES(
    "Craw's Domain",
    3,
    5
);

INSERT INTO area_ingredients VALUES(
    "Craw's Domain",
    4,
    2
);

INSERT INTO area_ingredients VALUES(
    "Craw's Domain",
    5,
    1
);

-- cookbooks
INSERT INTO cookbooks VALUES(
    "Badlands Barbecue",
    "Bombastic Badlands",
    500
);

-- recipes
INSERT INTO recipes VALUES (
    "Mushroom Stew",
    NULL,
    10
);

-- recipe_ingredients
INSERT INTO recipe_ingredients VALUES (
    "Mushroom Stew",
    3,
    2
);

INSERT INTO recipe_ingredients VALUES (
    "Mushroom Stew",
    1,
    1
);

-- Enemies
INSERT INTO enemies VALUES (
    "The Big Craw",
    21,
    2,
    False,
    "He's literally the biggest of craws"
);

INSERT INTO enemies VALUES (
    "Vincent's Procrastination",
    100,
    69,
    False,
    "Maybe exists"
);

-- enemy_attack_dice
INSERT INTO enemy_attack_dice VALUES (
    "The Big Craw", 
    2, 
    4
);

INSERT INTO enemy_attack_dice VALUES (
    "Vincent's Procrastination", 
    11, 
    11
);

-- area_enemies
INSERT INTO area_enemies VALUES (
    "Blasted Beach",
    "Vincent's Procrastination",
    2
);

INSERT INTO area_enemies VALUES (
    "Craw's Domain",
    "Vincent's Procrastination",
    1
);

INSERT INTO area_enemies VALUES (
    "Craw's Domain",
    "The Big Craw",
    5
);