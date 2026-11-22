DROP PROCEDURE IF EXISTS increment_day;
DROP PROCEDURE IF EXISTS add_inventory_item;
DROP PROCEDURE IF EXISTS remove_inventory_item;
DROP TRIGGER IF EXISTS cleanup_deleted_room;

DELIMITER //

-- Procedure that updates the day by 1 for a given room
CREATE PROCEDURE increment_day(IN input_room_id int)
BEGIN
    UPDATE rooms 
    SET rooms.game_day = rooms.game_day + 1 
    WHERE room_id = input_room_id;
END //

-- Procedure that adds an item to the inventory
-- If the item already exists, then it just adds to the existing item
-- but if it doesn't, then it will add a new row for the item
CREATE PROCEDURE add_inventory_item(
    IN p_type_id INT,
    IN p_item_id INT,
    IN p_item_name VARCHAR(30),
    IN p_quantity INT,
    IN p_room_id INT
)
BEGIN
    IF EXISTS (
        SELECT * FROM inventory
        WHERE type_id = p_type_id
        AND item_id = p_item_id
        AND room_id = p_room_id
    ) THEN
        UPDATE inventory
        SET inventory.quantity = inventory.quantity + p_quantity
        WHERE type_id = p_type_id
        AND item_id = p_item_id
        AND room_id = p_room_id;
    ELSE
        INSERT INTO inventory VALUES (
            p_type_id,
            p_item_id,
            p_item_name,
            p_quantity,
            p_room_id
        );
    END IF;
END //

-- Procedure that removes an item from the inventory
-- Drops the item from the inventory if removing items results in the
-- quantity being zero
CREATE PROCEDURE remove_inventory_item(
    IN p_type_id INT,
    IN p_item_id INT,
    IN p_quantity INT,
    IN p_room_id INT
)
BEGIN
    UPDATE inventory
    SET inventory.quantity = inventory.quantity - p_quantity
    WHERE type_id = p_type_id
    AND item_id = p_item_id
    AND room_id = p_room_id;

    DELETE FROM inventory
    WHERE inventory.quantity <= 0;
END //

DELIMITER ;

DELIMITER //
-- Trigger for room cleanup when a room is deleted
CREATE TRIGGER cleanup_deleted_room
BEFORE DELETE ON rooms
FOR EACH ROW
BEGIN
    -- remove room inv
    DELETE FROM inventory
    WHERE room_id = OLD.room_id;

    -- Cookbooks that are unlocked
    DELETE FROM unlocked_cookbooks
    WHERE room_id = OLD.room_id;

    -- Customers
    DELETE FROM customers
    WHERE room_id = OLD.room_id;

    UPDATE users
    SET room_id = NULL
    WHERE room_id = OLD.room_id;
END //

DELIMITER ;