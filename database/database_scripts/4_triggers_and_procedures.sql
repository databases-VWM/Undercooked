-- Procedure that updates the day by 1 for a given room

DROP PROCEDURE IF EXISTS increment_day

DELIMITER //

CREATE PROCEDURE increment_day(IN input_room_id int)
BEGIN
    UPDATE users SET day = day + 1 WHERE room_id = input_room_id;
END //

DELIMITER ;