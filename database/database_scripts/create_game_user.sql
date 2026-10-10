CREATE USER 'game'@'%'  IDENTIFIED BY 'pancake_sandwich';

GRANT SELECT, INSERT, CREATE VIEW, DELETE, SHOW VIEW, UPDATE ON undercooked.* TO 'game'@'%';