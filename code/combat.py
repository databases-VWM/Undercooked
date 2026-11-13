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

def attack(player, enemy, log_list=None):
    log_print(log_list, "\nYou attack!")

    attack_roll = roll_dice_pool(player.attack_dice)

    log_print(log_list, f"Attack Roll: {attack_roll['rolls']}")
    log_print(log_list, f"Total Roll: {attack_roll['total']}")

    damage = max(0, attack_roll["total"] - enemy.defense)

    enemy.health -= damage

    log_print(log_list, f"Enemy Defense: {enemy.defense}")
    log_print(log_list, f"Damage Dealt: {damage}")
    log_print(log_list, f"Enemy Health: {max(0, enemy.health)}/{enemy.max_health}")


def parry_counter(player, enemy, log_list=None):
    log_print(log_list, "\nYou attempt a parry and counter!")

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


def defend(player, log_list=None):
    log_print(log_list, "\nYou prepare to defend!")

    defense_roll = roll_dice_pool(player.block_dice)

    log_print(log_list, f"Defense Roll: {defense_roll['rolls']}")
    log_print(log_list, f"Total Defense: {defense_roll['total']}")

    return defense_roll["total"]


def flee(player, enemy, log_list=None):
    log_print(log_list, "\nYou attempt to flee!")

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

def enemy_attack(player, enemy, block_bonus=0, dodge_roll=None, log_list=None):
    log_print(log_list, f"\n{enemy.name} attacks!")

    attack_roll = roll_dice_pool(enemy.attack_dice)

    enemy_damage = attack_roll["total"]

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

# MAIN COMBAT FUNCTION

def start_combat(player: Entity, area: Area):

    # Make sure the area has enemies
    if not area.enemies_list:
        print("There are no enemies in this area!")
        return

    # Randomly select an enemy from the area
    enemy_name = sample_item(area.enemies_list)
    enemy = Entity(enemy_name)

    print("\n" + "=" * 40)
    print("COMBAT STARTED")
    print("=" * 40)

    print(f"\nEnemy: {enemy.name}")
    print(f"Enemy Health: {enemy.health}/{enemy.max_health}")
    print(f"Enemy Defense: {enemy.defense}")

    print(f"\nPlayer: {player.name}")
    print(f"Player Health: {player.health}")
    print(f"Player Defense: {player.defense}")

    # Main combat loop
    while player.health > 0 and enemy.health > 0:

        print("\n" + "=" * 40)
        print("YOUR TURN")
        print("=" * 40)

        print(f"\n{player.name}: {player.health} HP")
        print(f"{enemy.name}: {enemy.health} HP")

        print("\n1. Attack")
        print("2. Parry/Counter")
        print("3. Defend")
        print("4. Flee")

        choice = input("\nChoose your action: ").strip().lower()

        # Reset turn-specific bonuses
        block_bonus = 0
        dodge_roll = None

        if choice in ["1"]:
            attack(player, enemy)

        elif choice in ["2"]:
            dodge_roll = parry_counter(player, enemy)

        elif choice in ["3"]:
            block_bonus = defend(player)

        elif choice in ["4"]:
            if flee():
                print("\nPlayer escaped.")
                return

        else:
            print("Invalid action. Try again.")
            continue

        # Check if enemy was defeated
        if enemy.health <= 0:
            break

        # Enemy's turn
        enemy_attack(
            player,
            enemy,
            block_bonus=block_bonus,
            dodge_roll=dodge_roll
        )

        # Check if player was defeated
        if player.health <= 0:
            break

    # Combat results
    print("\n" + "=" * 40)

    if enemy.health <= 0:
        print(f"VICTORY! You defeated {enemy.name}!")

    elif player.health <= 0:
        print("DEFEAT! You have been defeated.")

    print("=" * 40)


# Standalone testing
if __name__ == "__main__":

    test_player = Entity("Player")
    test_area = Area("Craw's Domain")

    start_combat(test_player, test_area)
