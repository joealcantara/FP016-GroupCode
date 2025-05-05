import tkinter as tk
import random
import time



5652765
# Status effects class
class StatusEffect:
    def __init__(self, name, duration):
        self.name = name
        self.duration = duration

    def apply(self, target):
        pass

    def tick(self, target):
        self.duration -= 1
        return self.duration <= 0

    def __str__(self):
        return f"{self.name} ({self.duration} turns)"

5652765
class BurnEffect(StatusEffect):
    def __init__(self, duration, damage_per_turn):
        super().__init__("Burn", duration)
        self.damage_per_turn = damage_per_turn

    def apply(self, target):
        print(f"{target.name} is burning!")
        target.take_damage(self.damage_per_turn, "Fire")

    def tick(self, target):
        print(f"{target.name} takes {self.damage_per_turn} burn damage.")
        target.take_damage(self.damage_per_turn, "Fire")
        return super().tick(target)

5652765
class StunEffect(StatusEffect):
    def __init__(self, duration=1):
        super().__init__("Stun", duration)

    def apply(self, target):
        print(f"{target.name} is stunned and can't move!")
        target.can_act = False

5652765
class PoisonEffect(StatusEffect):
    def __init__(self, duration, damage_sequence):
        super().__init__("Poison", duration)
        self.damage_sequence = list(damage_sequence)
        self.current_tick = 0

    def apply(self, target):
        print(f"{target.name} is poisoned!")
        self.tick(target)

    def tick(self, target):
        if self.current_tick < len(self.damage_sequence):
            damage = self.damage_sequence[self.current_tick]
            print(f"{target.name} takes {damage} poison damage.")
            target.take_damage(damage, "Poison")
            self.current_tick += 1
        return super().tick(target)

5652765
class DefenseReductionEffect(StatusEffect):
    def __init__(self, duration, reduction_percentage):
        super().__init__("Defense Reduction", duration)
        self.reduction_percentage = reduction_percentage
        self.original_defense = 0

    def apply(self, target):
        print(f"{target.name}'s defense is reduced by {self.reduction_percentage}%!")
        self.original_defense = target.defense
        target.defense -= int(target.defense * (self.reduction_percentage / 100))

    def remove(self, target):
        target.defense = self.original_defense
        print(f"{target.name}'s defense returns to normal.")

5652765
class SlowEffect(StatusEffect):
    def __init__(self, duration=1):
        super().__init__("Slow", duration)

    def apply(self, target):
        print(f"{target.name} is slowed!")
        target.can_act = False


# Special abilities class
5652765
class SpecialAbilities:
    class ApplyBurn:
        def __init__(self, duration=2, damage_per_turn=5):
            self.duration = duration
            self.damage_per_turn = damage_per_turn

        def activate(self, game_state, source, target):
            if target:
                burn = BurnEffect(self.duration, self.damage_per_turn)
                target.apply_status_effect(burn)
5652765
    class PreventAttackNextTurn:
        def activate(self, game_state, source, target):
            if target:
                stun = StunEffect(duration=1)
                target.apply_status_effect(stun)
5652765
    class ApplyStun:
        def __init__(self, chance=0.5, duration=1):
            self.chance = chance
            self.duration = duration

        def activate(self, game_state, source, target):
            if target and random.random() < self.chance:
                stun = StunEffect(self.duration)
                target.apply_status_effect(stun)
                print(f"{target.name} is stunned!")
            else:
                print(f"{target.name} resisted the stun.")
5652765
    class ApplyPoison:
        def __init__(self, duration=3, damage_sequence=[5, 10, 15]):
            self.duration = duration
            self.damage_sequence = damage_sequence

        def activate(self, game_state, source, target):
            if target:
                poison = PoisonEffect(self.duration, self.damage_sequence)
                target.apply_status_effect(poison)
5652765
    class ReduceOpponentDefense:
        def __init__(self, duration=1, reduction_percentage=30):
            self.duration = duration
            self.reduction_percentage = reduction_percentage

        def activate(self, game_state, source, target):
            if target:
                defense_reduction = DefenseReductionEffect(self.duration, self.reduction_percentage)
                target.apply_status_effect(defense_reduction)
5652765
    class BlockFireAttack:
        def activate(self, game_state, source, target=None):
            print(f"{source.name} blocks fire attacks.")
            source.fire_shield_active = True
5652765
    class BlockIceAttackAndSlow:
        def activate(self, game_state, source, target=None):
            print(f"{source.name} blocks ice attacks and slows the opponent.")
            source.ice_wall_active = True
            if target:
                slow = SlowEffect(duration=1)
                target.apply_status_effect(slow)
5652765
    class ReflectElectricDamage:
        def __init__(self, reflect_percentage=0.5):
            self.reflect_percentage = reflect_percentage

        def activate(self, game_state, source, target=None):
            print(f"{source.name} reflects {int(self.reflect_percentage * 100)}% of electric damage.")
            source.lightning_reflect_active = self.reflect_percentage
5652765
    class ClearPoisonAndHeal:
        def __init__(self, heal_amount=5):
            self.heal_amount = heal_amount

        def activate(self, game_state, source, target=None):
            if source.has_status_effect("Poison"):
                source.remove_status_effect("Poison")
                print(f"Poison cleared from {source.name}.")
            source.heal(self.heal_amount)
            print(f"{source.name} healed {self.heal_amount} HP.")
5652765
    class ReduceIncomingDamage:
        def __init__(self, duration=2, reduction_percentage=50):
            self.duration = duration
            self.reduction_percentage = reduction_percentage

        def activate(self, game_state, source, target=None):
            print(f"{source.name} reduces incoming damage by {self.reduction_percentage}%.")
            source.damage_reduction_active = (self.reduction_percentage / 100, self.duration)


# Card class
5652765
class Card:
    def __init__(self, name, card_type, cost=0, damage=0, block=0, description="", ability=None, tags=None):
        self.name = name
        self.card_type = card_type
        self.cost = cost
        self.damage = damage
        self.block = block
        self.description = description
        self.ability = ability
        self.tags = tags if tags is not None else []

    def __str__(self):
        info = f"{self.name} ({self.card_type}) - Cost: {self.cost}"
        if self.damage > 0:
            info += f", Damage: {self.damage}"
        if self.block > 0:
            info += f", Block: {self.block}"
        info += f"\nDescription: {self.description}"
        return info

    def play(self, game_state, player, target=None):
        print(f"{player.name} played {self.name} card.")
        if self.ability:
            self.ability.activate(game_state, player, target)
        if self.damage > 0 and target:
            print(f"{target.name} takes {self.damage} damage.")
            target.take_damage(self.damage)
        if self.block > 0:
            player.defense += self.block
            print(f"{player.name} gains {self.block} defense.")

5652765
# Elemental attack cards
flame_sword_card = Card(
    name="Flame Sword",
    card_type="Attack",
    cost=2,
    damage=15,
    description="Burns the opponent for 2 turns (+5 damage per turn)",
    ability=SpecialAbilities.ApplyBurn(duration=2, damage_per_turn=5),
    tags=["Fire"]
)

ice_spear_card = Card(
    name="Ice Spear",
    card_type="Attack",
    cost=1,
    damage=10,
    description="Prevents opponent from attacking next turn",
    ability=SpecialAbilities.PreventAttackNextTurn(),
    tags=["Ice"]
)

lightning_strike_card = Card(
    name="Lightning Strike",
    card_type="Attack",
    cost=2,
    damage=20,
    description="50% chance to stun the opponent for 1 turn",
    ability=SpecialAbilities.ApplyStun(chance=0.5),
    tags=["Electric"]
)

poison_arrow_card = Card(
    name="Poison Arrow",
    card_type="Attack",
    cost=1,
    damage=12,
    description="Poisons the opponent for 3 turns (5 → 10 → 15 damage)",
    ability=SpecialAbilities.ApplyPoison(duration=3, damage_sequence=[5, 10, 15]),
    tags=["Poison"]
)

stone_storm_card = Card(
    name="Stone Storm",
    card_type="Attack",
    cost=2,
    damage=18,
    description="Reduces opponent's defense by 30% for 1 turn",
    ability=SpecialAbilities.ReduceOpponentDefense(duration=1, reduction_percentage=30),
    tags=["Earth"]
)

# Defense cards
fire_shield_card = Card(
    name="Fire Shield",
    card_type="Defense",
    cost=2,
    block=20,
    description="Completely blocks fire attacks",
    ability=SpecialAbilities.BlockFireAttack(),
    tags=["Fire"]
)

ice_wall_card = Card(
    name="Ice Wall",
    card_type="Defense",
    cost=1,
    block=15,
    description="Blocks ice attacks and slows the opponent",
    ability=SpecialAbilities.BlockIceAttackAndSlow(),
    tags=["Ice"]
)

lightning_reflect_card = Card(
    name="Lightning Reflect",
    card_type="Defense",
    cost=1,
    block=10,
    description="Reflects 50% of electric damage",
    ability=SpecialAbilities.ReflectElectricDamage(reflect_percentage=0.5),
    tags=["Electric"]
)

poison_cleanse_card = Card(
    name="Poison Cleanse",
    card_type="Defense",
    cost=1,
    block=0,
    description="Clears poison and heals 5 HP",
    ability=SpecialAbilities.ClearPoisonAndHeal(heal_amount=5),
    tags=["Poison"]
)

stone_armor_card = Card(
    name="Stone Armor",
    card_type="Defense",
    cost=3,
    block=25,
    description="Reduces incoming damage by 50% for 2 turns",
    ability=SpecialAbilities.ReduceIncomingDamage(duration=2, reduction_percentage=50),
    tags=["Earth"]
)
    def create_default_deck(self):
        default_deck = []
        cards = [
            flame_sword_card, ice_spear_card, lightning_strike_card,
            poison_arrow_card, stone_storm_card, fire_shield_card,
            ice_wall_card, lightning_reflect_card, poison_cleanse_card,
            stone_armor_card
        ]
        for _ in range(3):  # 3 copies of each card
            default_deck.extend(cards)
        random.shuffle(default_deck)
        return default_deck

    def draw_card(self):
        if len(self.hand) < 7 and self.deck:
            card = self.deck.pop()
            self.hand.append(card)
            print(f"{self.name} drew {card.name} card.")
            return card
        return None

#5677995
def load_cards(file_path="cards.json"):
    with open(file_path) as f:
        return json.load(f)
[{"name": "Ice Spear", "type": "attack", "element": "ice", "damage": 15, "description": "Deals ice damage."},
  {"name": "Stone Storm", "type": "attack", "element": "earth", "damage": 10, "description": "Hits all enemies."}]
#random variables not sure of the actuall weapons right now as billy coded that
def save_game(player, filename="save.json"):
    with open(filename, "w") as f:
        json.dump(player.to_dict(), f)

def load_game(filename="save.json"):
class CardViewer:
    def __init__(self, root, card_info_frame):
        self.label = tk.Label(card_info_frame, text="", wraplength=200, justify='left')
        self.label.pack()

    def show_card_info(self, card):
        self.label.config(text=f"{card['name']}\n\n{card['description']}")

def check_combo(self, played_cards):
    if {"Ice Spear", "Stone Storm"}.issubset(set(played_cards)):
        print("Combo triggered: Frozen Armor Crumble!")
        return {"bonus_damage": 20}
    return {}

class CombatManager:
    def __init__(self, player, enemy):
        self.player = player
        self.enemy = enemy

    def play_card(self, card):
# resolve card effect and check for combos
#5677995
# Class representing a looted goods that can restore health
class LootedGoods:
    def __init__(self, name, restore_health=0):
        self.name = name
        self.restore_health = restore_health

# Represents a weapon with upgradeable attributes
class Weapon:
    def __init__(self, name, base_level_damage):
        self.name = name
        self.base_level_damage = base_level_damage # Base damage of the weapon
        self.attributes = []

    def upgrade(self, attribute):
        if attribute not in self.attributes:
            self.attributes.append(attribute)

    # String representation of the weapon for easy printing
    def __str__(self):
        attributes_list = ", ".join(self.attributes) if self.attributes else "None"
        return f"Weapon: {self.name} | Damage: {self.base_level_damage} | Attributes: {attributes_list}"

# Represents a shield with strength and potential attributes
class Shield:
    def __init__(self, strength):
        self.strength = strength
        self.attributes = []
        
    # Method to upgrade shield's strength or add new attributes
    def upgrade(self, attribute):
        if attribute == "strength":
            self.strength += 10
        elif attribute not in self.attributes:
            self.attributes.append(attribute)

    # String representation of the shield
    def __str__(self):
        attributes_list = ", ".join(self.attributes) if self.attributes else "None"
        return f"Shield | Durability: {self.strength} | Attributes: {attributes_list}"

5665548 5677995
class Armor:
    def __init__(self, name, defense):
        self.name = name
        self.defense = defense
        self.attributes = []

    def upgrade(self, attribute):
        if attribute == "defense":
            self.defense += 5
        elif attribute not in self.attributes:
            self.attributes.append(attribute)

    def __str__(self):
        attributes_list = ", ".join(self.attributes) if self.attributes else "None"
        return f"Armor: {self.name} | Defense: {self.defense} | Attributes: {attributes_list}"
5665548 5677995

# Represents an enemy character with lootable attributes
class Enemy:
    def __init__(self, name, health, attributes=None):
        self.name = name
        self.health = health
        self.attributes = attributes if attributes else []
        self.shield = 0
        self.stamina = 20

    # String representation of the enemy
    def __str__(self):
        return f"Enemy: {self.name} | HP: {self.health} | Attributes: {', '.join(self.attributes)}"

    def inflicted_attack(self, damage):
        if self.shield > 0:
            absorbed_damage = min(self.shield, damage)
            self.shield -= absorbed_damage
            actual_damage = damage - absorbed_damage
        else:
            actual_damage = damage

        self.health = max(self.health - actual_damage, 0)
5677995
# Player class with health, stamina, weapon, and shield
class Player:
    def __init__(self, name):
        self.name = name
        self.max_health = 300
        self.health = 300
        self.max_stamina = 50
        self.stamina = 20
        self.shield = 0
        self.weapon = Weapon("Crimson Double Edge Sword", 20)
        self.shield_item = Shield(20)
        self.armor = Armor("Knight's Plate", 15)
        self.inventory_looted_goods = []
        self.resources = {}
        }

    #Default deck for player
    5652765 
      def create_default_deck(self):
        default_deck = []
          
        cards = [
            flame_sword_card, ice_spear_card, lightning_strike_card,
            poison_arrow_card, stone_storm_card, fire_shield_card,
            ice_wall_card, lightning_reflect_card, poison_cleanse_card,
            stone_armor_card
        ]
          
        for _ in range(3):  # 3 copies of each card
            default_deck.extend(cards)
        random.shuffle(default_deck)
        return default_deck
    56562765
    def draw_card(self): #functionf for drawing card
        if len(self.hand) < 7 and self.deck:
            card = self.deck.pop()
            self.hand.append(card)
            print(f"{self.name} drew {card.name} card.")
            return card
        return None  
    5652765
    def play_card(self, card_index, game_state, target=None):
        if 0 <= card_index < len(self.hand):
            card = self.hand[card_index]
            if self.stamina >= card.cost:
                self.stamina -= card.cost
                card.play(game_state, self, target)
                self.hand.pop(card_index)
                return True
            else:
                print("Not enough AP!")
        return False
    5652765 5677995
    def take_damage(self, amount, damage_type="Physical"):
        if damage_type == "Fire" and self.fire_shield_active:
            print("Fire attack blocked!")
            return
        if damage_type == "Ice" and self.ice_wall_active:
            print("Ice attack blocked!")
            return

        final_damage = amount
        if self.damage_reduction_active[0] > 0:
            reduction = self.damage_reduction_active[0]
            final_damage = int(final_damage * (1 - reduction))
            print(f"Damage reduced by {reduction * 100}%.")

        if damage_type == "Electric" and self.lightning_reflect_active > 0:
            reflected = int(final_damage * self.lightning_reflect_active)
            final_damage -= reflected
            print(f"{self.lightning_reflect_active * 100}% damage reflected.")

        self.health -= max(0, final_damage - self.defense)
        print(f"{self.name} takes {max(0, final_damage - self.defense)} damage. Remaining HP: {self.health}")
        
    5652765
    def heal(self, amount):
        self.health = min(self.health + amount, self.max_health)
        print(f"{self.name} heals {amount} HP. New HP: {self.health}")
        
    5652765
    def apply_status_effect(self, effect):
        self.status_effects.append(effect)
        effect.apply(self)
        
    5652765
    def remove_status_effect(self, effect_name):
        for effect in self.status_effects[:]:
            if effect.name == effect_name:
                if hasattr(effect, 'remove'):
                    effect.remove(self)
                self.status_effects.remove(effect)
                print(f"{effect_name} effect removed.")
    5652765
    def begin_turn(self):
        self.can_act = True
        self.stamina = min(self.stamina + 3, self.max_stamina)
        self.defense = 0
        self.fire_shield_active = False
        self.ice_wall_active = False
        self.draw_card()
        print(f"\n{self.name}'s turn begins. AP: {self.stamina}")

    5677995 
    # String representation of the player showing stats, weapon, and shield
    def __str__(self):
        resources_str = " | ".join([f"{k}: {v}" for k, v in self.resources.items()])
        return f"{self.name} | HP: {self.health}/{self.max_health} | Stamina: {self.stamina}/{self.max_stamina} | Shield: {self.shield}\n{resources_str}\n{self.weapon}\n{self.shield_item}\n{self.armor}"

    # defining how inflicted attacks would be dealt to a target
    def inflict_attack(self, attack, target):
        if self.stamina < attack.energy:
            return False

        self.stamina -= attack.energy
        target.inflicted_attack(attack.damage)
        return True

    # defining how to handle being attacked (damage taken and shield impact logic)
    def inflicted_attack(self, damage):
        self.stamina = max(self.stamina - damage * 0.25, 0)

        if self.shield > 0:
            absorbed_damage = min(self.shield, damage)
            self.shield -= absorbed_damage
            actual_damage = damage - absorbed_damage
        else:
            actual_damage = damage

        actual_damage = max(0, actual_damage - self.armor.defense)
        self.health = max(self.health - actual_damage, 0)

    # Adding looted goods to player inventory
    def loot_goods(self, looted_goods):
        self.inventory_looted_goods.append(looted_goods)

    def consume_looted_goods(self, looted_goods_name):
        for goods in self.inventory_looted_goods:
            if goods.name == looted_goods_name:
                self.health = min(self.max_health, self.health + goods.restore_health)
                self.inventory_looted_goods.remove(goods)
                return True
        return False

    def increase_shield(self, amount):
        self.shield += amount

    def defeat_enemy(self, enemy):
        self.loot_enemy_attributes(enemy)

    # Loots special attributes from an enemy and lets the player choose where to apply them
    def loot_enemy_attributes(self, enemy):
        for attribute in enemy.attributes:
            while True:
                choice = input(f"Apply attribute '{attribute}' to weapon, shield or armor? (w/s/a): ").strip().lower()
                if choice == 'w':
                    self.weapon.upgrade(attribute)
                    break
                elif choice == 's':
                    self.shield_item.upgrade(attribute)
                    break
                elif choice == 'a':
                    self.armor.upgrade(attribute)
5677995
#Tree structure - skills progression
class SkillNode:
    def __init__(self, name, unlocked=False):
        self.name = name
        self.unlocked = unlocked
        self.children = []

    def add_child(self, child_node):
        self.children.append(child_node)

    def unlock(self):
        if self.unlocked:
            print(f"Skill '{self.name}' already unlocked.")
            return
        self.unlocked = True
        print(f"Skill '{self.name}' has been unlocked!")

    def display_tree(self, level=0):
        indent = " " * (level * 4)
        status = "✓" if self.unlocked else "✗"
        print(f"{indent}{self.name} [{status}]")
        for child in self.children:
            child.display_tree(level + 1)


#graph structure: game(world)map
class WorldMap:
    def __init__(self):
        self.graph = {}

    def add_location(self, location):
        if location not in self.graph:
            self.graph[location] = []

    def connect_locations(self, loc1, loc2):
        self.graph[loc1].append(loc2)
        self.graph[loc2].append(loc1)  # i made this one Undirected for simplicity

    def get_neighbors(self, location):
        return self.graph.get(location, [])

    def display_map(self):
        for location, neighbors in self.graph.items():
            print(f"{location} → {', '.join(neighbors)}")
5677995
5665548
class Game:
    def __init__(self, base):
        self.base = base
        self.base.title("Fantasy Card Game")
        self.base.geometry("1000x700")
        self.main_frame = tk.Frame(base)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.player = Player("Hero")
        self.current_enemy = Enemy("Goblin", 100, ["fire resistance"])
        self.create_card_decks()
        self.player_hand = self.draw_initial_hand()
        self.decision_deck = [
            {"description": "",
             "effects": {}},
            {"description": "",
             "effects": {}},
            {"description": "",
             "effects": {}},
            {"description": "",
             "effects": {}},
            {"description": "",
             "effects": {}}
        ]
        self.setup_ui()
        self.current_phase = "resource"
        self.draw_decision_card()
    5665548

 
Billy and 5665548

5665548
    def draw_initial_hand(self):
        hand = []
        for _ in range(5):
            if self.full_deck:
                card = random.choice(self.full_deck)
                self.full_deck.remove(card)
                hand.append(card)
        return hand

    def setup_ui(self):
        self.resource_frame = tk.Frame(self.main_frame)
        self.resource_frame.pack(fill=tk.X, padx=10, pady=10)
        self.resource_labels = {}
        col = 0
        for resource, value in self.player.resources.items():
            label = tk.Label(self.resource_frame, text=f"{resource}: {value}", font=("Arial", 12))
            label.grid(row=0, column=col, padx=10)
            self.resource_labels[resource] = label
            col += 1
        self.game_area = tk.Frame(self.main_frame, bg="lightblue")
        self.game_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.canvas = tk.Canvas(self.game_area, bg="lightblue", width=800, height=400)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.status_frame = tk.Frame(self.main_frame)
        self.status_frame.pack(fill=tk.X, padx=10, pady=10)
        self.player_stats = tk.Label(self.status_frame, text=str(self.player), font=("Arial", 10))
        self.player_stats.pack(side=tk.LEFT)
        self.enemy_stats = tk.Label(self.status_frame, text=str(self.current_enemy), font=("Arial", 10))
        self.enemy_stats.pack(side=tk.RIGHT)
        self.button_frame = tk.Frame(self.main_frame)
        self.button_frame.pack(fill=tk.X, padx=10, pady=10)
        self.combat_button = tk.Button(self.button_frame, text="Start Combat", command=self.start_combat)
        self.combat_button.pack(side=tk.LEFT, padx=5)
        self.inventory_button = tk.Button(self.button_frame, text="Use Item", command=self.use_item)
        self.inventory_button.pack(side=tk.LEFT, padx=5)
        self.warning_label = tk.Label(self.main_frame, text="", fg="red", font=("Arial", 12))
        self.warning_label.pack(pady=5)

    def draw_decision_card(self):
        if self.decision_deck:
            self.current_decision = random.choice(self.decision_deck)
            self.canvas.delete("all")
            self.card = self.canvas.create_rectangle(200, 50, 600, 250, fill="white", outline="black")
            self.card_text = self.canvas.create_text(400, 150, text=self.current_decision["description"],
                                                     font=("Arial", 14), width=380)
            self.canvas.create_text(150, 300, text="Swipe Left: No", fill="red", font=("Arial", 14))
            self.canvas.create_text(650, 300, text="Swipe Right: Yes", fill="green", font=("Arial", 14))
            self.canvas.bind("<Button-1>", self.on_card_click)
            self.canvas.bind("<B1-Motion>", self.on_card_drag)
            self.canvas.bind("<ButtonRelease-1>", self.on_card_release)
            self.start_x = None
        else:
            self.game_over("No more decisions available!")

    def on_card_click(self, event):
        self.start_x = event.x

    def on_card_drag(self, event):
        if self.card and self.start_x:
            dx = event.x - self.start_x
            self.canvas.move(self.card, dx, 0)
            self.canvas.move(self.card_text, dx, 0)
            self.start_x = event.x

    def on_card_release(self, event):
        if self.card and self.start_x:
            card_x1, _, card_x2, _ = self.canvas.coords(self.card)
            card_width = card_x2 - card_x1

            if card_x2 < 400 - (card_width * 0.3):
                self.apply_decision_effects("left")
            elif card_x1 > 400 + (card_width * 0.3):
                self.apply_decision_effects("right")
            else:
                self.canvas.coords(self.card, 200, 50, 600, 250)
                self.canvas.coords(self.card_text, 400, 150)
5665548

5665548
    def apply_decision_effects(self, direction):
        effects = self.current_decision["effects"]
        for resource, change in effects.items():
            if direction == "right":
                self.player.resources[resource] += change
            else:
                self.player.resources[resource] -= change * 0.5

        for resource, value in self.player.resources.items():
            self.player.resources[resource] = max(0, min(10, value))
            self.resource_labels[resource].config(text=f"{resource}: {int(self.player.resources[resource])}")

        warning_message = ""
        for resource, value in self.player.resources.items():
            if value <= 2:
                warning_message += f"Warning: {resource} is too low! "
            elif value >= 8:
                warning_message += f"Warning: {resource} is too high! "
        self.warning_label.config(text=warning_message)

        for resource, value in self.player.resources.items():
            if value <= 0:
                self.game_over(f"{resource} has fallen to critical levels!")
                return
            elif value >= 10:
                self.game_over(f"{resource} has reached maximum capacity!")
                return

        self.decision_deck.append(self.current_decision)
        self.current_phase = "combat"
        self.canvas.delete("all")
        self.prepare_combat()

    def prepare_combat(self):
        self.canvas.delete("all")
        self.canvas.create_text(400, 30, text=f"Combat: {self.player.name} vs {self.current_enemy.name}",
                                font=("Arial", 16))
        y = 60
        for i, card in enumerate(self.player_hand):
            card_rect = self.canvas.create_rectangle(50, y, 750, y + 60, fill="lightgreen")
            self.canvas.create_text(400, y + 30, text=str(card), font=("Arial", 10))
            self.canvas.tag_bind(card_rect, "<Button-1>", lambda event, idx=i: self.use_card(idx))
            y += 70
        self.canvas.create_text(900, 150, text=f"{self.current_enemy.name}\nHP: {self.current_enemy.health}",
                                font=("Arial", 14))
        self.update_stats()

    def use_card(self, card_index):
        if card_index < len(self.player_hand):
            selected_card = self.player_hand[card_index]

            if isinstance(selected_card, AttackCard):
                success = self.player.inflict_attack(selected_card, self.current_enemy)
                if success:
                    self.player_hand.pop(card_index)
                    if self.full_deck:
                        new_card = random.choice(self.full_deck)
                        self.full_deck.remove(new_card)
                        self.player_hand.append(new_card)
                    self.enemy_turn()
                    if self.current_enemy.health <= 0:
                        self.combat_victory()
                    elif self.player.health <= 0:
                        self.game_over("You have been defeated!")
                    else:
                        self.prepare_combat()

            elif isinstance(selected_card, DefenseCard):
                self.player.increase_shield(selected_card.block_value)
                self.player.stamina -= selected_card.energy
                self.player_hand.pop(card_index)
                if self.full_deck:
                    new_card = random.choice(self.full_deck)
                    self.full_deck.remove(new_card)
                    self.player_hand.append(new_card)
                self.enemy_turn()
                self.prepare_combat()

            elif isinstance(selected_card, SpellCard):
                if selected_card.name == "Mana Burst":
                    self.player.stamina += 2
                elif selected_card.name == "Summon Element":
                    if self.full_deck:
                        new_card = random.choice(self.full_deck)
                        self.full_deck.remove(new_card)
                        self.player_hand.append(new_card)

                self.player.stamina -= selected_card.energy
                self.player_hand.pop(card_index)
                if self.full_deck:
                    new_card = random.choice(self.full_deck)
                    self.full_deck.remove(new_card)
                    self.player_hand.append(new_card)
                if selected_card.name != "Time Warp":
                    self.enemy_turn()
                self.prepare_combat()
5665548


5677995
#Looted Goods
class LootedGoods:
    def __init__(self, name, restore_health=0):
        self.name = name
        self.restore_health = restore_health

    def __str__(self):
        return f"{self.name} (+{self.restore_health} HP)"

#Weapon Class
class Weapon:
    def __init__(self, name, base_level_damage):
        self.name = name
        self.base_level_damage = base_level_damage
        self.attributes = []

    def upgrade(self, attribute):
        if attribute not in self.attributes:
            self.attributes.append(attribute)
            print(f"{self.name} has obtained the attribute: {attribute} from opponent.")

    def __str__(self):
        attr = ", ".join(self.attributes) if self.attributes else "None"
        return f"Weapon: {self.name} | Damage: {self.base_level_damage} | Attributes: {attr}"

#Shield Class
class Shield:
    def __init__(self, strength):
        self.strength = strength
        self.attributes = []

    def upgrade(self, attribute):
        if attribute == "strength":
            self.strength += 10
            print("Shield strength increased by 10.")
        elif attribute not in self.attributes:
            self.attributes.append(attribute)
            print(f"Shield obtained attribute: {attribute}.")

    def __str__(self):
        attr = ", ".join(self.attributes) if self.attributes else "None"
        return f"Shield | Strength: {self.strength} | Attributes: {attr}"

#armour class
class Armour:
    def __init__(self, defense):
        self.defense = defense
        self.attributes = []

    def upgrade(self, attribute):
        if attribute == "defense":
            self.defense += 10
            print("Armour defense increased by 10.")
        elif attribute not in self.attributes:
            self.attributes.append(attribute)
            print(f"Armour gained attribute: {attribute}.")

    def __str__(self):
        attr = ", ".join(self.attributes) if self.attributes else "None"
        return f"Armour | Defense: {self.defense} | Attributes: {attr}"

#Enemy Class
class Enemy:
    def __init__(self, name, health, attributes=None):
        self.name = name
        self.health = health
        self.attributes = attributes if attributes else []

    def __str__(self):
        return f"Enemy: {self.name} | HP: {self.health} | Attributes: {', '.join(self.attributes)}"

# Player Class
class Player:
    def __init__(self, name):
        self.name = name
        self.max_health = 300
        self.health = 300
        self.max_stamina = 50
        self.stamina = 3
        self.weapon = Weapon("Crimson Double Edge Sword", base_level_damage=20)
        self.shield = Shield(strength=20)
        self.armour = Armour(defense=20)
        self.inventory_looted_goods = []

    def __str__(self):
        return f"{self.name} | HP: {self.health} | Stamina: {self.stamina}\n{self.weapon}\n{self.shield}"

    def attack(self, enemy):
        if self.stamina >= 1:
            damage = self.weapon.base_level_damage
            print(f"{self.name} attacks {enemy.name} for {damage} damage!")
            enemy.health = max(0, enemy.health - damage)
            self.stamina -= 1
        else:
            print(f"{self.name} has no stamina to attack.")

    def consume_looted_goods(self, item_name):
        for item in self.inventory_looted_goods:
            if item.name.lower() == item_name.lower():
                self.health = min(self.max_health, self.health + item.restore_health)
                self.inventory_looted_goods.remove(item)
                print(f"{self.name} consumed {item.name}, restoring {item.restore_health} HP.")
                return
        print(f"{self.name} has no {item_name} to consume.")

    def loot_goods(self, item):
        self.inventory_looted_goods.append(item)
        print(f"{self.name} looted {item.name}.")

    def loot_enemy_attributes(self, enemy):
        print(f"{self.name} acquires attribute(s) from {enemy.name}.")
        for attribute in enemy.attributes:
            while True:
                choice = input(f"Apply attribute '{attribute}' to weapon, shield, armour or skip? (w/s/a/x): ").strip().lower()
                if choice == 'w':
                    self.weapon.upgrade(attribute)
                    break
                elif choice == 's':
                    self.shield.upgrade(attribute)
                    break
                elif choice == 'a':
                    self.armour.upgrade(attribute)
                    break
                elif choice == 'x':
                    print(f"Skipped attribute '{attribute}'.")
                    break
                else:
                    print("Invalid input. Enter 'w', 's', or 'x'.")

    def defeat_enemy(self, enemy):
        print(f"{self.name} defeated {enemy.name}!")
        self.loot_enemy_attributes(enemy)
5677995


5665548
    def enemy_turn(self):
        attack_damage = random.randint(10, 20)
        self.player.inflicted_attack(attack_damage)
        self.update_stats()

    def combat_victory(self):
        self.player.defeat_enemy(self.current_enemy)
        loot_options = [
            LootedGoods("Health Potion", 50),
            LootedGoods("Elixir of Vitality", 75),
            LootedGoods("Mysterious Herb", 25)
        ]
        loot = random.choice(loot_options)
        self.player.loot_goods(loot)
        enemy_types = [
            ("Orc Warrior", 120, ["strength", "fire resistance"]),
            ("Dark Mage", 80, ["magic power", "ice mastery"]),
            ("Giant Spider", 100, ["poison", "agility"]),
            ("Stone Golem", 150, ["earth power", "defense"])
        ]
        enemy_data = random.choice(enemy_types)
        self.current_enemy = Enemy(*enemy_data)
        self.current_phase = "resource"
        self.draw_decision_card()

    def update_stats(self):
        self.player_stats.config(text=str(self.player))
        self.enemy_stats.config(text=str(self.current_enemy))

    def start_combat(self):
        if self.current_phase == "resource":
            self.current_phase = "combat"
            self.prepare_combat()

    def use_item(self):
        if not self.player.inventory_looted_goods:
            self.warning_label.config(text="No items in inventory!")
            return

        items_window = tk.Toplevel(self.base)
        items_window.title("Inventory")
        items_window.geometry("300x200")

        for i, item in enumerate(self.player.inventory_looted_goods):
            item_frame = tk.Frame(items_window)
            item_frame.pack(fill=tk.X, padx=5, pady=5)
            tk.Label(item_frame, text=f"{item.name} (+{item.restore_health} HP)").pack(side=tk.LEFT)
            tk.Button(item_frame, text="Use",
                      command=lambda name=item.name: [self.player.consume_looted_goods(name),
                                                      self.update_stats(),
                                                      items_window.destroy()]).pack(side=tk.RIGHT)

    def game_over(self, message):
        self.canvas.delete("all")
        self.canvas.create_text(400, 150, text=f"Game Over: {message}", font=("Arial", 20), fill="red")
        self.canvas.unbind("<Button-1>")
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")
5665548

5652765 5677995
# Game state class
class GameState:
    def __init__(self, player1, player2):
        self.players = [player1, player2]
        self.current_player_index = 0
        self.turn = 1

    def current_player(self):
        return self.players[self.current_player_index]

    def opponent(self):
        return self.players[1 - self.current_player_index]

    def switch_player(self):
        self.current_player_index = 1 - self.current_player_index

    def play_turn(self):
        current = self.current_player()
        opponent = self.opponent()

        current.begin_turn()
        current.show_hand()

        if current.hand:
            played = False
            while not played:
                try:
                    choice = int(input("Enter the card number you want to play (0 to exit): ")) - 1
                    if choice == -1:
                        break
                    played = current.play_card(choice, self, opponent)
                except (ValueError, IndexError):
                    print("Invalid input!")

        current.end_turn()
        self.switch_player()
        self.turn += 1

    def is_game_over(self):
        return any(player.health <= 0 for player in self.players)

    def display_status(self):
        print("\n" + "=" * 40)
        print(f"Turn {self.turn}")
        for player in self.players:
            status = f"{player.name}: HP {player.health}/{player.max_health}"
            if player.status_effects:
                status += f" | Effects: {', '.join(str(effect) for effect in player.status_effects)}"
            print(status)
        print("=" * 40)
5652765
# Game initialization
def main():
    print("Welcome to  Redemption!")
    player_name = input("Please enter your name: ")

    player = Player(player_name)
    computer = Player("Computer")

    game = GameState(player, computer)
    
    5652765
    # Starting hand
    for _ in range(5):
        player.draw_card()
        computer.draw_card()

    while not game.is_game_over():
        game.display_status()
        game.play_turn()

    game.display_status()
    winner = player if player.health > 0 else computer
    print(f"\nGame over! Winner: {winner.name}")
    


5665548
if __name__ == "__main__":
    root = tk.Tk()
    game = Game(root)
    root.mainloop()
5665548



