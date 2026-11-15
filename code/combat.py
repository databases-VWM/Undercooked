import random

from entity import Entity
from area import Area
from functions import sample_item


# Combat balancing
FLEE_CHANCE = 0.50


# Dice rolling functions
def roll_dice(number_of_dice, sides):
    if number_of_dice < 0:
        raise ValueError("Number of dice cannot be negative.")

    if sides < 1:
        raise ValueError("Dice must have at least 1 side.")

    rolls = []

    for i in range(number_of_dice):
        rolls.append(random.randint(1, sides))

    return sum(rolls)


def roll_dice_pool(dice_groups, flat_modifier=0):
    total = 0
    all_rolls = []

    for number_of_dice, sides in dice_groups:

        if number_of_dice < 0:
            raise ValueError("Number of dice cannot be negative.")

        if sides < 1:
            raise ValueError("Dice must have at least 1 side.")

        group_rolls = []

        for _ in range(number_of_dice):
            result = random.randint(1, sides)
            group_rolls.append(result)

        all_rolls.extend(group_rolls)
        total += sum(group_rolls)

    total += flat_modifier

    return {
        "rolls": all_rolls,
        "modifier": flat_modifier,
        "total": total
    }


# PLAYER ACTIONS

def combat_attack(player: Entity, enemy: Entity, log_list: list[str]=[]):
    attack_roll = roll_dice_pool(player.attack_dice)

    log_print(log_list, f"Attack Roll: {attack_roll['rolls']}")
    log_print(log_list, f"Total Roll: {attack_roll['total']}")

    damage = max(0, attack_roll["total"] - enemy.defense)

    enemy.health -= damage

    log_print(log_list, f"Enemy Defense: {enemy.defense}")
    log_print(log_list, f"Damage Dealt: {damage}")
    log_print(log_list, f"Enemy Health: {max(0, enemy.health)}/{enemy.max_health}")



def combat_parry_counter(player: Entity, enemy: Entity, log_list: list[str]=[]):
    # Counterattack
    attack_roll = roll_dice_pool(player.attack_dice)

    log_print(log_list, f"Attack Roll: {attack_roll['rolls']}")

    # Apply enemy defense, then halve the resulting damage
    damage = max(0, int((attack_roll["total"] - enemy.defense) * 0.5))

    enemy.health -= damage

    log_print(log_list, f"Counter Damage: {damage}")
    log_print(log_list, f"Enemy Health: {max(0, enemy.health)}/{enemy.max_health}")

    # Roll dodge dice for the incoming enemy attack
    dodge_roll = roll_dice_pool(player.dodge_dice)

    log_print(log_list, f"Your Dodge Roll: {dodge_roll['total']}")

    return dodge_roll["total"]


def combat_defend(player: Entity, log_list: list[str]=[]):
    defense_roll = roll_dice_pool(player.block_dice)

    log_print(log_list, f"Defense Roll: {defense_roll['rolls']}")
    log_print(log_list, f"Total Defense: {defense_roll['total']}")

    return defense_roll["total"]

def combat_flee(player: Entity, enemy: Entity, log_list: list[str]=[]):
    # Roll dodge dice
    dodge_roll = roll_dice_pool(player.dodge_dice)

    # Roll enemy attack dice
    attack_roll = roll_dice_pool(enemy.attack_dice)

    log_print(log_list, f"Your Dodge Roll: {dodge_roll['total']}")
    log_print(log_list, f"Enemy Attack Roll: {attack_roll['total']}")

    if dodge_roll["total"] > attack_roll["total"]:
        log_print(log_list, "You successfully escaped!")
        return True

    log_print(log_list, "You failed to flee")
    return False


# ENEMY ACTION
def combat_enemy_attack(player: Entity, enemy: Entity, block_bonus: int=0, dodge_roll=None, log_list: list[str]=[]):

    attack_roll = roll_dice_pool(enemy.attack_dice)

    enemy_damage = attack_roll["total"]
    # Increases enemy's damage by the constant scalar if elite
    if enemy.is_elite:
        enemy_damage *= enemy.ELITE_ENEMY_DAMAGE_SCALAR

    log_print(log_list, f"Enemy Attack Roll: {attack_roll['rolls']}")
    log_print(log_list, f"Enemy Attack Total: {enemy_damage}")

    # Check whether the player's parry/dodge succeeded
    if dodge_roll is not None and dodge_roll > enemy_damage:
        log_print(log_list, "You successfully dodged the attack!")
        return

    # Calculate incoming damage
    damage = max(0, enemy_damage - player.defense - block_bonus)


    player.health -= damage

    log_print(log_list, f"Your Defense: {player.defense}")
    log_print(log_list, f"Block Bonus: {block_bonus}")
    log_print(log_list, f"Damage Taken: {damage}")
    log_print(log_list, f"Your Health: {max(0, player.health)}")


def log_print(log_list: list[str], message: str):
    log_list.append(str(message))
    if len(log_list) > 20:
        log_list.pop(0)