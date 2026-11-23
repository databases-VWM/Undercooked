import mysql.connector
# Allows for dynamic creation of an object from JSON from just its name
class Entity:
    def __init__(self, entity_name: str, connection, player: bool = False):
        cursor = connection.cursor()
        self.ELITE_ENEMY_HEALTH_SCALAR: int = 3
        self.ELITE_ENEMY_DAMAGE_SCALAR: int = 2
        self.ELITE_ENEMY_DEFENSE_SCALAR: int = 2

        if player != True:
            try:
                # Setup all non dice values
                cursor.execute(
                    "SELECT * FROM enemies WHERE enemy_name = %s",
                    (entity_name,)
                )

                enemy_tuple = cursor.fetchone()
                self.name: str = entity_name
                # self.weapon: str = ""
                # self.armor: str = ""
                self.health = enemy_tuple[1]
                self.max_health = self.health
                self.defense = enemy_tuple[2]
                self.description = enemy_tuple[4]
                self.is_elite: bool = False
                self.is_boss = enemy_tuple[3]
                self.power: int = 0
                self.attack_dice: list[list[int]] = []
                self.is_player = False
                
                cursor.execute(
                    "SELECT * FROM enemy_attack_dice WHERE enemy_name = %s",
                    (entity_name, )
                )
                
                dice_tuples = cursor.fetchall()
                # Adds dice from the database
                for dice_tuple in dice_tuples:
                    temp_dice_list = []
                    temp_dice_list.append(dice_tuple[1])
                    temp_dice_list.append(dice_tuple[2])
                    self.attack_dice.append(temp_dice_list)

            finally:
                cursor.close()
        
        else:
            # Testing defaults
            self.name: str = entity_name
            # self.weapon: str = "These hands"
            # self.weapon_ID: int = 0
            # self.armor: str = "Traveler's Garbs"
            # self.armor_ID: int = 0
            self.health: int = 100
            self.max_health: int = self.health
            self.defense: int = 10
            self.attack_dice: list[list[int]] = [[2,5], [10,10]] # Default for combat demo testing
            self.block_dice: list[list[int]] = [[5,2]]
            self.dodge_dice: list[list[int]] = [[2,12]]
            self.description: str = "A mighty chef"
            self.is_elite = False
            self.is_boss: bool = False
            self.power: int = 0
            self.is_player = True

            self.get_player_data_from_database()
            self.calculate_power()

    # This functions fills in all the player data from the database
    def get_player_data_from_database(self):
        pass
    
    # Power is a formulaic, general metric of how strong a player is
    def calculate_power(self):
        temp_power: int = 0
        if self.is_player:
            temp_power += self.max_health // 10
            temp_power += self.defense
            temp_power += dice_avg(self.attack_dice) // 2
            temp_power += dice_avg(self.block_dice) // 3
            temp_power += dice_avg(self.dodge_dice) // 3
            self.power = temp_power
        else:
            temp_power += self.max_health // 10
            temp_power += self.defense
            temp_power += dice_avg(self.attack_dice)
            self.power = temp_power
        
#Returns the average of a set of dice
def dice_avg(dice_array: list[list[int]]) -> int:
    total_avg: int = 0
    for i in range(len(dice_array)):
        num_dice: int = dice_array[i][0]
        num_sides: int = dice_array[i][1]
        one_die_avg = (1 + num_sides) // 2
        total_avg += one_die_avg* num_dice
    
    return total_avg
        
        
# Takes a category of dice and an entity and transforms that array into an appended string for display
# Type = "attack", "guard", "dodge"
def transform_dice_to_str(dice_array: list[list[int]]) -> str:
    # Each die rolled
    die_str = ""
    for die_num in range(len(dice_array)):
        die_str += str(dice_array[die_num][0])
        die_str += "d"
        die_str += str(dice_array[die_num][1])
        if die_num != (len(dice_array) - 1):
            die_str += ", "
    
    return die_str
        
    
#Function that puts stats into an array to be outputted by another function
def output_entity_stats(entity: Entity, extended: bool = False) -> list[str]:
    entity_array: list[str] = []
    # Update power
    entity.calculate_power()
    entity_array.append(f"{entity.name}'s stats:")
    entity_array.append(f"Power: {entity.power}")
    entity_array.append(f"{entity.health} / {entity.max_health} Health")
    if extended == True:
        attack_die_str = transform_dice_to_str(entity.attack_dice)
        
        entity_array.append(f"Defense: {entity.defense}")
        entity_array.append(f"Damage: {attack_die_str}")
        if entity.is_player:
            guard_die_str = transform_dice_to_str(entity.block_dice)
            dodge_die_str = transform_dice_to_str(entity.dodge_dice)
            entity_array.append(f"Guard: {guard_die_str}")
            entity_array.append(f"Dodge: {dodge_die_str}")
    entity_array.append(f"\"{entity.description}\"")
    return entity_array
        
# Returns the names of all enemies
def get_enemy_names(connection) -> list[str]:
    cursor = connection.cursor()
    enemies_names_list: list[str] = []
    try:
        cursor.execute(
            "SELECT enemy_name FROM enemies"
        )
        result = cursor.fetchall()
        for enemy in result:
            enemies_names_list.append(enemy[0])
        return enemies_names_list
    finally:cursor.close()
    
