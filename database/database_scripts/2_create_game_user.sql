/* Create the game's user */

USE undercooked;

DROP USER IF EXISTS 'game'@'%';

CREATE USER 'game'@'%'  IDENTIFIED BY 'pancake_sandwich';

GRANT SELECT, INSERT, CREATE VIEW, DELETE, SHOW VIEW, EXECUTE, UPDATE ON undercooked.* TO 'game'@'%';

FLUSH PRIVILEGES;