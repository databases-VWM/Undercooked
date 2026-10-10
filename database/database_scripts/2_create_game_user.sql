/* Create the game's user */

USE undercooked;

CREATE USER 'game'@'%'  IDENTIFIED BY 'pancake_sandwich';

GRANT SELECT, INSERT, CREATE VIEW, DELETE, SHOW VIEW, UPDATE ON undercooked.* TO 'game'@'%';

FLUSH PRIVILEGES;