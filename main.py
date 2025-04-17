import tkinter as tk
import random
import time


class Card:
    def __init__(self, name, energy):
        self.name = name
        self.energy = energy

    def __str__(self):
        return f"{self.name} (Energy: {self.energy})"


class AttackCard(Card):
    def __init__(self, name, element, damage, energy, special_effect=None):
        super().__init__(name, energy)
        self.element = element
        self.damage = damage
        self.special_effect = special_effect

    def __str__(self):
        info = f"{super().__str__()} - Element: {self.element}, Damage: {self.damage}"
        if self.special_effect:
            info += f", Special Effect: {self.special_effect}"
        return info


class DefenseCard(Card):
    def __init__(self, name, block_value, energy, special_effect=None):
        super().__init__(name, energy)
        self.block_value = block_value
        self.special_effect = special_effect

    def __str__(self):
        info = f"{super().__str__()} - Block Value: {self.block_value}"
        if self.special_effect:
            info += f", Special Effect: {self.special_effect}"
        return info


class SpellCard(Card):
    def __init__(self, name, energy, special_effect):
        super().__init__(name, energy)
        self.special_effect = special_effect

    def __str__(self):
        return f"{super().__str__()} - Special Effect: {self.special_effect}"

5677995
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

5665548
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
5665548

class Enemy:
    def __init__(self, name, health, attributes=None):
        self.name = name
        self.health = health
        self.attributes = attributes if attributes else []
        self.shield = 0
        self.stamina = 20

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

    def __str__(self):
        resources_str = " | ".join([f"{k}: {v}" for k, v in self.resources.items()])
        return f"{self.name} | HP: {self.health}/{self.max_health} | Stamina: {self.stamina}/{self.max_stamina} | Shield: {self.shield}\n{resources_str}\n{self.weapon}\n{self.shield_item}\n{self.armor}"

    def inflict_attack(self, attack, target):
        if self.stamina < attack.energy:
            return False

        self.stamina -= attack.energy
        target.inflicted_attack(attack.damage)
        return True

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
    def create_card_decks(self):
        self.attack_deck = [
            AttackCard("Flame Sword", "Fire", 15, 2, "Burns the opponent for 2 turns"),
            AttackCard("Ice Spear", "Ice", 10, 1, "Prevents the opponent from attacking next turn"),
            AttackCard("Lightning Strike", "Electric", 20, 2, "50% chance to stun the opponent"),
            AttackCard("Poison Arrow", "Poison", 12, 1, "Poisons the opponent for 3 turns"),
            AttackCard("Stone Storm", "Earth", 18, 2, "Reduces the opponent's defense")
        ]
        self.defense_deck = [
            DefenseCard("Fire Shield", 20, 2, "Completely blocks fire attacks"),
            DefenseCard("Ice Wall", 15, 1, "Blocks ice attacks and slows the opponent"),
            DefenseCard("Lightning Reflect", 10, 1, "Reflects 50% of electric damage"),
            DefenseCard("Poison Cleanse", 0, 1, "Clears poison effects and heals 5 HP"),
            DefenseCard("Stone Armor", 25, 3, "Reduces incoming damage by 50%")
        ]
        self.spell_deck = [
            SpellCard("Element Fusion", 3, "Combines 2 elemental cards"),
            SpellCard("Mana Burst", 2, "Gain 2 extra AP this turn"),
            SpellCard("Time Warp", 3, "Skip the opponent's turn"),
            SpellCard("Summon Element", 2, "Draw a random elemental card"),
            SpellCard("Dispel Magic", 1, "Cancels the opponent's last played spell")
        ]
        self.full_deck = self.attack_deck + self.defense_deck + self.spell_deck
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


    def enemy_turn(self):
        attack_damage = random.randint(10, 20)
        self.player.inflicted_attack(attack_damage)
        self.update_stats()

5665548
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

5665548
if __name__ == "__main__":
    root = tk.Tk()
    game = Game(root)
    root.mainloop()
5665548
