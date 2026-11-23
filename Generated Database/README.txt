# Undercooked content pack

Files:
- `undercooked_content.sql`: inserts for the existing content tables only.
- `weapons.json`: weapon definitions, preserving the supplied JSON structure.
- `armor.json`: armor definitions, preserving the supplied JSON structure.

Design notes:
- 20 areas, ordered from early game to the final area around day 80.
- Every area has 2 fish, 2 plant, and 2 meat ingredients; 3 regular enemies; 1 boss.
- Each area has one cookbook and two recipes. Recipe ingredients are restricted to that area's six ingredients.
- Bosses are included in the normal `area_enemies` pool with weight 1. Regular enemies have higher weights.
- The existing area names Blasted Beach, Craw's Domain, and Bombastic Badlands are retained.
- Bombastic Badlands `area_power` is set to 115 rather than retaining the apparent placeholder value 1000, so the progression remains playable.
- Equipment is offered by area: 3 weapon playstyles (consistent dagger, balanced sword, high-variance heavy weapon) and 3 armor archetypes (light, medium, heavy).
- Existing Dev Armor, Debug Stick, My Rabbit, Frying Pan, and Chef's Garbs entries are retained.
- SQL does not drop/recreate the database and does not insert into rooms/users/inventory/customers/unlocked_cookbooks.
- `area_power` is a recommended player combat-power target, not enemy power. The numbers are a first-pass progression curve and should be playtested against your actual player stat growth.

Important integration check:
Your database stores ingredient types as `fish`, `plant`, and `meat`. Your `Area.generate_node()` snippet uses category labels `fishing`, `flora`, and `fauna`. If there is no mapping elsewhere in your current loader, those labels need to be translated in Python; this pack intentionally keeps the existing database values unchanged.
