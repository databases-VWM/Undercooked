-- Merges quantities and eliminates duplicate items when inserting new item to inventory
DROP TRIGGER IF EXISTS add_inventory_item;
delimiter //

CREATE TRIGGER add_inventory_item
BEFORE INSERT 
ON inventory 
FOR EACH ROW
BEGIN
-- If item already exists in table for your room
IF NEW.item_id = item_id AND NEW.type_id = type_id AND NEW.room_id = room_id
THEN 
SET NEW.quantity = quantity + NEW.quantity;
DELETE FROM inventory WHERE NEW.item_id = item_id AND NEW.type_id = type_id AND NEW.room_id = room_id;

END IF;

END//

delimiter ;