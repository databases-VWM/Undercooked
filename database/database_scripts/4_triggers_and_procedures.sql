-- Procedure that updates the day by 1 for a given room

DROP PROCEDURE IF EXISTS increment_day

DELIMITER //

CREATE PROCEDURE increment_day(IN input_room_id int)
BEGIN
    UPDATE rooms 
    SET rooms.game_day = rooms.game_day + 1 
    WHERE room_id = input_room_id;
END //

DELIMITER ;