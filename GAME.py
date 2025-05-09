import pygame
import sys
import json
import os
import textwrap
import random
import math

# Initialize pygame
pygame.init()
pygame.font.init()


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


class StunEffect(StatusEffect):
    def __init__(self, duration=1):
        super().__init__("Stun", duration)

    def apply(self, target):
        print(f"{target.name} is stunned and can't move!")
        target.can_act = False


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


class SlowEffect(StatusEffect):
    def __init__(self, duration=1):
        super().__init__("Slow", duration)

    def apply(self, target):
        print(f"{target.name} is slowed!")
        target.can_act = False


class SpecialAbilities:
    class ApplyBurn:
        def __init__(self, duration=2, damage_per_turn=5):
            self.duration = duration
            self.damage_per_turn = damage_per_turn

        def activate(self, game_state, source, target):
            if target:
                burn = BurnEffect(self.duration, self.damage_per_turn)
                target.apply_status_effect(burn)

    class PreventAttackNextTurn:
        def activate(self, game_state, source, target):
            if target:
                stun = StunEffect(duration=1)
                target.apply_status_effect(stun)

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

    class ApplyPoison:
        def __init__(self, duration=3, damage_sequence=[5, 10, 15]):
            self.duration = duration
            self.damage_sequence = damage_sequence

        def activate(self, game_state, source, target):
            if target:
                poison = PoisonEffect(self.duration, self.damage_sequence)
                target.apply_status_effect(poison)

    class ReduceOpponentDefense:
        def __init__(self, duration=1, reduction_percentage=30):
            self.duration = duration
            self.reduction_percentage = reduction_percentage

        def activate(self, game_state, source, target):
            if target:
                defense_reduction = DefenseReductionEffect(self.duration, self.reduction_percentage)
                target.apply_status_effect(defense_reduction)

    class BlockFireAttack:
        def activate(self, game_state, source, target=None):
            print(f"{source.name} blocks fire attacks.")
            source.fire_shield_active = True

    class BlockIceAttackAndSlow:
        def activate(self, game_state, source, target=None):
            print(f"{source.name} blocks ice attacks and slows the opponent.")
            source.ice_wall_active = True
            if target:
                slow = SlowEffect(duration=1)
                target.apply_status_effect(slow)

    class ReflectElectricDamage:
        def __init__(self, reflect_percentage=0.5):
            self.reflect_percentage = reflect_percentage

        def activate(self, game_state, source, target=None):
            print(f"{source.name} reflects {int(self.reflect_percentage * 100)}% of electric damage.")
            source.lightning_reflect_active = self.reflect_percentage

    class ClearPoisonAndHeal:
        def __init__(self, heal_amount=5):
            self.heal_amount = heal_amount

        def activate(self, game_state, source, target=None):
            if source.has_status_effect("Poison"):
                source.remove_status_effect("Poison")
                print(f"Poison cleared from {source.name}.")
            source.heal(self.heal_amount)
            print(f"{source.name} healed {self.heal_amount} HP.")

    class ReduceIncomingDamage:
        def __init__(self, duration=2, reduction_percentage=50):
            self.duration = duration
            self.reduction_percentage = reduction_percentage

        def activate(self, game_state, source, target=None):
            print(f"{source.name} reduces incoming damage by {self.reduction_percentage}%.")
            source.damage_reduction_active = (self.reduction_percentage / 100, self.duration)


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


# Card Definitions
flame_sword_card = Card(
    name="Flame Sword", card_type="Attack", cost=2, damage=15,
    description="Burns opponent for 2 turns (+5 damage/turn)",
    ability=SpecialAbilities.ApplyBurn(duration=2, damage_per_turn=5),
    tags=["Fire"])

ice_spear_card = Card(
    name="Ice Spear", card_type="Attack", cost=1, damage=10,
    description="Prevents opponent from attacking next turn",
    ability=SpecialAbilities.PreventAttackNextTurn(),
    tags=["Ice"])

lightning_strike_card = Card(
    name="Lightning Strike", card_type="Attack", cost=2, damage=20,
    description="50% chance to stun opponent for 1 turn",
    ability=SpecialAbilities.ApplyStun(chance=0.5),
    tags=["Electric"])

poison_arrow_card = Card(
    name="Poison Arrow", card_type="Attack", cost=1, damage=12,
    description="Poisons opponent for 3 turns (5→10→15 damage)",
    ability=SpecialAbilities.ApplyPoison(duration=3, damage_sequence=[5, 10, 15]),
    tags=["Poison"])

stone_storm_card = Card(
    name="Stone Storm", card_type="Attack", cost=2, damage=18,
    description="Reduces opponent's defense by 30% for 1 turn",
    ability=SpecialAbilities.ReduceOpponentDefense(duration=1, reduction_percentage=30),
    tags=["Earth"])

fire_shield_card = Card(
    name="Fire Shield", card_type="Defense", cost=2, block=20,
    description="Completely blocks fire attacks",
    ability=SpecialAbilities.BlockFireAttack(),
    tags=["Fire"])

ice_wall_card = Card(
    name="Ice Wall", card_type="Defense", cost=1, block=15,
    description="Blocks ice attacks and slows opponent",
    ability=SpecialAbilities.BlockIceAttackAndSlow(),
    tags=["Ice"])

lightning_reflect_card = Card(
    name="Lightning Reflect", card_type="Defense", cost=1, block=10,
    description="Reflects 50% of electric damage",
    ability=SpecialAbilities.ReflectElectricDamage(reflect_percentage=0.5),
    tags=["Electric"])

poison_cleanse_card = Card(
    name="Poison Cleanse", card_type="Defense", cost=1, block=0,
    description="Clears poison and heals 5 HP",
    ability=SpecialAbilities.ClearPoisonAndHeal(heal_amount=5),
    tags=["Poison"])

stone_armor_card = Card(
    name="Stone Armor", card_type="Defense", cost=3, block=25,
    description="Reduces incoming damage by 50% for 2 turns",
    ability=SpecialAbilities.ReduceIncomingDamage(duration=2, reduction_percentage=50),
    tags=["Earth"])


class ActionHistory:
    def __init__(self):
        self.stack = []

    def push(self, action):
        self.stack.append(action)

    def pop(self):
        return self.stack.pop() if self.stack else None


class Player:
    def __init__(self, name="Player", max_health=100):
        self.name = name
        self.max_health = max_health
        self.health = max_health
        self.defense = 0
        self.deck = self.create_default_deck()
        self.hand = []
        self.stamina = 0
        self.max_stamina = 10
        self.status_effects = []
        self.can_act = True
        self.fire_shield_active = False
        self.ice_wall_active = False
        self.lightning_reflect_active = 0
        self.damage_reduction_active = (0, 0)
        self.history = ActionHistory()

    def create_default_deck(self):
        default_deck = []
        cards = [
            flame_sword_card, ice_spear_card, lightning_strike_card,
            poison_arrow_card, stone_storm_card, fire_shield_card,
            ice_wall_card, lightning_reflect_card, poison_cleanse_card,
            stone_armor_card
        ]
        for _ in range(3):
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

    def play_card(self, card_index, game_state, target=None):
        if 0 <= card_index < len(self.hand):
            card = self.hand[card_index]

            # Save state before playing
            self.history.push({
                'type': 'play_card',
                'card': card,
                'card_index': card_index,
                'target': target,
                'player_health': self.health,
                'target_health': target.health if target else None,
                'player_stamina': self.stamina,
                'player_defense': self.defense,
                'status_effects': [str(e) for e in self.status_effects],
                'fire_shield': self.fire_shield_active,
                'ice_wall': self.ice_wall_active,
                'lightning_reflect': self.lightning_reflect_active,
                'damage_reduction': self.damage_reduction_active
            })

            if self.stamina >= card.cost:
                self.stamina -= card.cost
                card.play(game_state, self, target)
                self.hand.pop(card_index)
                return True
            else:
                print("Not enough AP!")
        return False

    def undo_last_action(self, game_state):
        last_action = self.history.pop()
        if not last_action:
            print("No action to undo!")
            return False

        if last_action['type'] == 'play_card':
            print(f"\nUNDO: Reverting last card play ({last_action['card'].name})")

            # Restore card to hand
            self.hand.insert(last_action['card_index'], last_action['card'])

            # Restore stamina
            self.stamina += last_action['card'].cost

            # Restore player state
            self.health = last_action['player_health']
            self.defense = last_action['player_defense']
            self.fire_shield_active = last_action['fire_shield']
            self.ice_wall_active = last_action['ice_wall']
            self.lightning_reflect_active = last_action['lightning_reflect']
            self.damage_reduction_active = last_action['damage_reduction']

            # Restore status effects
            self.status_effects = [
                eff for eff in self.status_effects
                if str(eff) in last_action['status_effects']
            ]

            # Restore target health
            if last_action['target']:
                last_action['target'].health = last_action['target_health']

            return True
        return False

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

    def heal(self, amount):
        self.health = min(self.health + amount, self.max_health)
        print(f"{self.name} heals {amount} HP. New HP: {self.health}")

    def apply_status_effect(self, effect):
        self.status_effects.append(effect)
        effect.apply(self)

    def remove_status_effect(self, effect_name):
        for effect in self.status_effects[:]:
            if effect.name == effect_name:
                if hasattr(effect, 'remove'):
                    effect.remove(self)
                self.status_effects.remove(effect)
                print(f"{effect_name} effect removed.")

    def has_status_effect(self, effect_name):
        return any(effect.name == effect_name for effect in self.status_effects)

    def begin_turn(self):
        self.can_act = True
        self.stamina = min(self.stamina + 3, self.max_stamina)
        self.defense = 0
        self.fire_shield_active = False
        self.ice_wall_active = False
        self.draw_card()
        print(f"\n{self.name}'s turn begins. AP: {self.stamina}")

    def end_turn(self):
        for effect in self.status_effects[:]:
            if effect.tick(self):
                self.remove_status_effect(effect.name)

        if self.damage_reduction_active[1] > 0:
            duration_left = self.damage_reduction_active[1] - 1
            self.damage_reduction_active = (self.damage_reduction_active[0], duration_left)
            if duration_left <= 0:
                print("Damage reduction effect ended.")
                self.damage_reduction_active = (0, 0)

        print(f"{self.name}'s turn ends.")

    def show_hand(self):
        print(f"\n{self.name}'s hand:")
        for i, card in enumerate(self.hand):
            print(f"{i + 1}. {card}")


class AIPlayer(Player):
    def __init__(self, name="Computer", max_health=100):
        super().__init__(name, max_health)
        self.difficulty = "medium"  # easy, medium, hard

    def make_decision(self, game_state):
        opponent = game_state.opponent()

        # Check defensive cards first
        defense_cards = [card for card in self.hand if card.card_type == "Defense"]
        attack_cards = [card for card in self.hand if card.card_type == "Attack"]

        # Emergency control (low health)
        if self.health < 0.3 * self.max_health:
            # Use a healing card if available
            heal_card = next((card for card in defense_cards if "heal" in card.name.lower()), None)
            if heal_card and heal_card.cost <= self.stamina:
                return self.play_card(self.hand.index(heal_card), game_state)

            # Use defense card
            if defense_cards:
                # Choose the best defense card (highest block)
                best_defense = max(defense_cards, key=lambda x: x.block)
                if best_defense.cost <= self.stamina:
                    return self.play_card(self.hand.index(best_defense), game_state)

        # Make moves according to your opponent's situation
        if opponent.status_effects:
            # If the opponent already has a status effect, focus on dealing direct damage
            if attack_cards:
                # Choose the card with the highest damage
                best_attack = max(attack_cards, key=lambda x: x.damage)
                if best_attack.cost <= self.stamina:
                    return self.play_card(self.hand.index(best_attack), game_state, opponent)
        else:
            # Prefer cards that apply status effects
            status_attack_cards = [card for card in attack_cards if card.ability is not None]
            if status_attack_cards:
                # Select a random status effect card
                selected_card = random.choice(status_attack_cards)
                if selected_card.cost <= self.stamina:
                    return self.play_card(self.hand.index(selected_card), game_state, opponent)

        # If not enough AP, pass
        if self.stamina < min(card.cost for card in self.hand if card.cost > 0):
            return False

        # Play a random card
        playable_cards = [card for card in self.hand if card.cost <= self.stamina]
        if playable_cards:
            # Strategy according to difficulty level
            if self.difficulty == "easy":
                card = random.choice(playable_cards)
            elif self.difficulty == "medium":
                # Choose better cards
                card = max(playable_cards, key=lambda x: x.damage if x.card_type == "Attack" else x.block)
            else:  # hard
                # Check combinations
                if any(eff.name == "Defense Reduction" for eff in opponent.status_effects):
                    # If defense is low, deal high damage
                    high_dmg = max((c for c in playable_cards if c.card_type == "Attack"),
                                   key=lambda x: x.damage, default=None)
                    if high_dmg:
                        card = high_dmg
                else:
                    # First lower your defense, then attack
                    defense_reducer = next((c for c in playable_cards
                                            if "ReduceOpponentDefense" in str(c.ability)), None)
                    if defense_reducer:
                        card = defense_reducer
                    else:
                        card = max(playable_cards, key=lambda x: x.damage if x.card_type == "Attack" else x.block)

            return self.play_card(self.hand.index(card), game_state, opponent if card.card_type == "Attack" else None)

        return False


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

        if isinstance(current, AIPlayer):
            print(f"\n{current.name}'s turn:")
            current.show_hand()
            current.make_decision(self)
        else:
            current.show_hand()
            if current.hand:
                played = False
                while not played:
                    try:
                        choice = input("Enter card number (1-5), 'u' to undo, or 0 to end turn: ")
                        if choice == '0':
                            break
                        elif choice.lower() == 'u':
                            current.undo_last_action(self)
                            current.show_hand()
                            continue

                        card_index = int(choice) - 1
                        played = current.play_card(card_index, self, opponent)
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


def main():
    print("Welcome to REDEMPTION!")
    player_name = input("Please enter your name: ")

    difficulty = input("Select AI difficulty (easy, medium, hard): ").lower()
    while difficulty not in ["easy", "medium", "hard"]:
        difficulty = input("Invalid difficulty. Please choose easy, medium or hard: ").lower()

    player = Player(player_name)
    computer = AIPlayer("Computer")
    computer.difficulty = difficulty

    game = GameState(player, computer)

    # Starting hand
    for _ in range(5):
        player.draw_card()
        computer.draw_card()

    while not game.is_game_over():
        game.display_status()
        game.play_turn()
        time.sleep(1)

    game.display_status()
    winner = player if player.health > 0 else computer
    print(f"\nGame over! Winner: {winner.name}")


if __name__ == "__main__":
    main()
# Screen setup
WIDTH, HEIGHT = 1024, 768
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("The King: Card Adventure")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GOLD = (212, 175, 55)
RED = (200, 50, 50)
GREEN = (50, 150, 50)
BLUE = (50, 50, 200)
CARD_BROWN = (139, 69, 19)
CARD_BEIGE = (245, 245, 220)
GRAY = (128, 128, 128)

# Fonts
font_title = pygame.font.SysFont("Georgia", 48, bold=True)
font_subtitle = pygame.font.SysFont("Georgia", 36, bold=True)
font_body = pygame.font.SysFont("Arial", 28)
font_button = pygame.font.SysFont("Arial", 32, bold=True)

# Button class
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, 3, border_radius=10)  # Border
        if self.text:
            text_surf = font_button.render(self.text, True, WHITE)
            text_rect = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rect)

    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(pos):
                return True
        return False

    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

# Card class for Reigns-style swiping
class SwipeCard:
    def __init__(self, width, height, content):
        self.width = width
        self.height = height
        self.content = content
        self.x = (WIDTH - width) // 2
        self.y = (HEIGHT - height) // 2
        self.target_x = self.x
        self.grabbed = False
        self.grab_offset = 0
        self.rotation = 0
        self.decision_made = False
        self.decision = None
        self.surface = self.create_surface()
        self.swipe_threshold = width * 0.3  # Distance needed to trigger a decision

    def create_surface(self):
        card = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        card.fill(CARD_BEIGE)
        pygame.draw.rect(card, CARD_BROWN, (0, 0, self.width, self.height), 10, border_radius=20)

        title = font_title.render(self.content["title"], True, BLACK)
        title_rect = title.get_rect(center=(self.width // 2, 60))
        card.blit(title, title_rect)

        wrapped_text = textwrap.wrap(self.content["description"], width=45)
        for i, line in enumerate(wrapped_text[:5]):  # Limit to 5 lines
            text = font_body.render(line, True, BLACK)
            text_rect = text.get_rect(center=(self.width // 2, 140 + i * 40))
            card.blit(text, text_rect)

        if "options" in self.content and len(self.content["options"]) >= 2:
            left_option = font_body.render(f"← {self.content['options'][0]['text']}", True, RED)
            right_option = font_body.render(f"{self.content['options'][1]['text']} →", True, GREEN)
            card.blit(left_option, (30, self.height - 60))
            card.blit(right_option, (self.width - right_option.get_width() - 30, self.height - 60))

        return card

    def handle_event(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            card_rect = pygame.Rect(self.x, self.y, self.width, self.height)
            if card_rect.collidepoint(mouse_pos):
                self.grabbed = True
                self.grab_offset = mouse_pos[0] - self.x
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.grabbed:
                self.grabbed = False
                offset = self.x - ((WIDTH - self.width) // 2)
                if offset < -self.swipe_threshold:
                    self.decision = "left"
                    self.decision_made = True
                    self.target_x = -self.width
                elif offset > self.swipe_threshold:
                    self.decision = "right"
                    self.decision_made = True
                    self.target_x = WIDTH
                else:
                    self.target_x = (WIDTH - self.width) // 2

    def update(self, mouse_pos):
        if self.grabbed:
            self.x = mouse_pos[0] - self.grab_offset
            center_offset = self.x - ((WIDTH - self.width) // 2)
            self.rotation = center_offset * 0.05
        elif self.x != self.target_x:
            diff = self.target_x - self.x
            self.x += diff * 0.2
            center_offset = self.x - ((WIDTH - self.width) // 2)
            self.rotation = center_offset * 0.05

    def draw(self, surface):
        rotated_card = pygame.transform.rotate(self.surface, self.rotation)
        rotated_rect = rotated_card.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        surface.blit(rotated_card, rotated_rect.topleft)
        offset = self.x - ((WIDTH - self.width) // 2)
        if offset < -10:
            pygame.draw.rect(surface, (255, 0, 0, min(abs(offset) / 2, 100)),
                             (50, 50, 100, HEIGHT - 100), border_radius=10)
        elif offset > 10:
            pygame.draw.rect(surface, (0, 255, 0, min(abs(offset) / 2, 100)),
                             (WIDTH - 150, 50, 100, HEIGHT - 100), border_radius=10)

class GameState:
    def __init__(self):
        self.current_scene = "start"
        self.choices = []
        self.boss_path = None
        self.boss_defeated = False
        self.decision_count = 0
        self.card = None
        self.next_scene = None
        self.transition_timer = 0
        self.game_mode = "menu"  # menu, playing, combat, game_over

    def initialize_card(self, scenes):
        if self.current_scene in scenes:
            self.card = SwipeCard(800, 500, scenes[self.current_scene])
        else:
            print(f"Error: Scene '{self.current_scene}' not found. Falling back to start scene.")
            self.current_scene = "start"
            self.card = SwipeCard(800, 500, scenes[self.current_scene])

    def add_choice(self, choice, scenes):
        self.choices.append(choice)
        self.decision_count += 1
        if self.decision_count == 1:
            if choice == "A":
                self.boss_path = "medusa"
            elif choice == "B":
                self.boss_path = "swamp"
            else:
                self.boss_path = "dragon"
        if self.decision_count >= 5 and not self.current_scene.startswith("boss_"):
            self.next_scene = f"boss_{self.boss_path}"
        self.save_progress()

    def update(self):
        if self.next_scene:
            self.transition_timer += 1
            if self.transition_timer > 30:
                self.current_scene = self.next_scene
                self.next_scene = None
                self.transition_timer = 0
                return True
        return False

    def save_progress(self):
        progress = {
            "current_scene": self.current_scene,
            "choices": self.choices,
            "boss_path": self.boss_path,
            "decision_count": self.decision_count
        }
        try:
            with open('progress.json', 'w') as f:
                json.dump(progress, f, indent=4)
        except Exception as e:
            print(f"Error saving progress: {e}")

    def load_progress(self, scenes):
        try:
            with open('progress.json', 'r') as f:
                progress = json.load(f)
                self.current_scene = progress.get("current_scene", "start")
                self.choices = progress.get("choices", [])
                self.boss_path = progress.get("boss_path")
                self.decision_count = progress.get("decision_count", 0)
                self.initialize_card(scenes)
                return True
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            print(f"Error loading progress: {e}")
            return False

class CombatSystem:
    def __init__(self, boss_type):
        self.boss_type = boss_type
        self.player_health = 100
        self.boss_health = 150
        self.player_cards = self.generate_player_cards()
        self.boss_abilities = self.get_boss_abilities()
        self.current_turn = "player"
        self.message = "Your turn! Select a card to play."
        self.message_timer = 0
        self.last_ability = None

    def generate_player_cards(self):
        base_cards = [
            {"name": "Sword Strike", "damage": 15, "type": "attack"},
            {"name": "Shield Block", "defense": 20, "type": "defense"},
            {"name": "Healing Potion", "heal": 25, "type": "heal"},
            {"name": "Fire Spell", "damage": 30, "type": "attack", "cost": 2}
        ]
        cards = []
        for _ in range(4):
            cards.append(random.choice(base_cards).copy())
        return cards

    def get_boss_abilities(self):
        abilities = {
            "medusa": [
                {"name": "Petrifying Gaze", "damage": 25, "effect": "stun"},
                {"name": "Serpent Strike", "damage": 15},
                {"name": "Stone Curse", "damage": 20, "effect": "slow"}
            ],
            "swamp": [
                {"name": "Toxic Cloud", "damage": 20, "effect": "poison"},
                {"name": "Bog Trap", "damage": 10, "effect": "root"},
                {"name": "Monster Charge", "damage": 30}
            ],
            "dragon": [
                {"name": "Fire Breath", "damage": 35},
                {"name": "Tail Swipe", "damage": 20},
                {"name": "Wing Buffet", "damage": 15, "effect": "knockback"}
            ]
        }
        return abilities.get(self.boss_type, [])

    def player_attack(self, card_index):
        if 0 <= card_index < len(self.player_cards):
            card = self.player_cards[card_index]
            if card["type"] == "attack":
                self.boss_health -= card.get("damage", 0)
                self.message = f"You deal {card.get('damage', 0)} damage with {card['name']}!"
            elif card["type"] == "heal":
                heal_amount = card.get("heal", 0)
                self.player_health = min(100, self.player_health + heal_amount)
                self.message = f"You heal {heal_amount} health with {card['name']}!"
            elif card["type"] == "defense":
                self.message = f"You prepare to defend with {card['name']}!"
            self.player_cards.pop(card_index)
            self.player_cards.append(self.generate_player_cards()[0])
            self.current_turn = "boss"
            self.message_timer = 60
            return True
        return False

    def boss_attack(self):
        ability = random.choice(self.boss_abilities)
        damage = ability.get("damage", 0)
        self.player_health -= damage
        self.message = f"Boss uses {ability['name']} for {damage} damage!"
        if "effect" in ability:
            self.message += f" ({ability['effect']} effect)"
        self.current_turn = "player"
        self.message_timer = 60
        self.last_ability = ability
        return ability

    def update(self):
        if self.message_timer > 0:
            self.message_timer -= 1
        if self.current_turn == "boss" and self.message_timer == 0:
            self.boss_attack()

def create_scenes_file():
    scenes = {
        "start": {
            "title": "Trapped in the Cursed Mine",
            "description": "You awake in a dark mine, head throbbing from a blow you don’t recall. Your miner’s pick lies nearby, and strange whispers echo through the tunnels. The mine feels alive, cursed. You must escape, but three paths lie ahead, each hinting at a different guardian.",
            "options": [
                {"text": "Snake-carved tunnel", "next": "decision1_A"},
                {"text": "Mushroom-lit tunnel", "next": "decision1_B"},
                {"text": "Scorched tunnel", "next": "decision1_C"}
            ],
            "image": None
        },
        # Medusa Path (A)
        "decision1_A": {
            "title": "The Serpent’s Call",
            "description": "The tunnel is damp, etched with snake carvings that seem to writhe in your torchlight. A sibilant whisper promises secrets but warns of a serpent queen. You find an old miner’s journal mentioning a ‘Medusa’ guarding the exit.",
            "options": [
                {"text": "Read the journal", "next": "decision2_AA"},
                {"text": "Ignore it, proceed", "next": "decision2_AB"}
            ],
            "image": None
        },
        "decision2_AA": {
            "title": "Ancient Warnings",
            "description": "The journal describes Medusa’s petrifying gaze and suggests reflective surfaces might help. You pocket a small, cracked mirror from the journal’s pages. The tunnel narrows, and you hear slithering ahead.",
            "options": [
                {"text": "Use mirror to scout", "next": "decision3_AAA"},
                {"text": "Move stealthily", "next": "decision3_AAB"}
            ],
            "image": None
        },
        "decision2_AB": {
            "title": "Pressing Forward",
            "description": "Ignoring the journal, you hurry on. The carvings grow more intricate, depicting a crowned serpent woman. The air grows colder, and you feel watched. A faint glow reveals a fork in the path.",
            "options": [
                {"text": "Follow the glow", "next": "decision3_ABA"},
                {"text": "Stay in shadows", "next": "decision3_ABB"}
            ],
            "image": None
        },
        "decision3_AAA": {
            "title": "Reflected Danger",
            "description": "Using the mirror, you spot a snake slithering in the dark, avoiding its gaze. The tunnel opens to a chamber with stone statues, their faces frozen in terror. You sense Medusa’s presence growing stronger.",
            "options": [
                {"text": "Search for clues", "next": "decision4_AAAA"},
                {"text": "Prepare for combat", "next": "decision4_AAAB"}
            ],
            "image": None
        },
        "decision3_AAB": {
            "title": "Stealthy Advance",
            "description": "Moving quietly, you avoid detection but miss potential clues. The tunnel leads to a chamber filled with statues, some holding weapons. Medusa’s hissing is closer now, echoing off the walls.",
            "options": [
                {"text": "Take a weapon", "next": "decision4_AABA"},
                {"text": "Keep moving", "next": "decision4_AABB"}
            ],
            "image": None
        },
        "decision3_ABA": {
            "title": "Glowing Path",
            "description": "The glow leads to a shrine with a snake idol. Touching it triggers a vision of Medusa commanding snakes. You feel cursed but gain knowledge of her movements. The path continues toward her lair.",
            "options": [
                {"text": "Use vision to plan", "next": "decision4_ABAA"},
                {"text": "Shake off the curse", "next": "decision4_ABAB"}
            ],
            "image": None
        },
        "decision3_ABB": {
            "title": "Shadowed Path",
            "description": "Staying in shadows, you avoid traps but feel the curse’s weight. You reach a chamber with statues and hear Medusa’s voice, taunting you to face her. The exit is near, but she blocks it.",
            "options": [
                {"text": "Confront her taunts", "next": "decision4_ABBA"},
                {"text": "Search for exit", "next": "decision4_ABBB"}
            ],
            "image": None
        },
        "decision4_AAAA": {
            "title": "Statue Clues",
            "description": "Among the statues, you find a shield with a polished surface, perfect for reflecting Medusa’s gaze. Armed with the mirror and shield, you feel ready to face her. Her lair is just ahead.",
            "options": [
                {"text": "Enter the lair", "next": "decision5_AAAAA"},
                {"text": "Set a trap", "next": "decision5_AAAAB"}
            ],
            "image": None
        },
        "decision4_AAAB": {
            "title": "Combat Ready",
            "description": "You sharpen your pick and brace for battle, relying on the mirror. The statue chamber leads to Medusa’s lair, where snakes slither in the dark. You hear her mocking laughter.",
            "options": [
                {"text": "Charge in", "next": "decision5_AAABA"},
                {"text": "Wait for an opening", "next": "decision5_AAABB"}
            ],
            "image": None
        },
        "decision4_AABA": {
            "title": "Armed with Stone",
            "description": "You pry a sword from a statue’s grip. It’s heavy but sharp. Medusa’s hissing grows louder as you approach her lair, the air thick with her presence.",
            "options": [
                {"text": "Advance boldly", "next": "decision5_AABAA"},
                {"text": "Move cautiously", "next": "decision5_AABAB"}
            ],
            "image": None
        },
        "decision4_AABB": {
            "title": "No Weapon",
            "description": "You bypass the statues, relying on your pick. Medusa’s lair is close, and her snakes are everywhere. You feel underprepared but determined to escape.",
            "options": [
                {"text": "Face her now", "next": "decision5_AABBA"},
                {"text": "Find another way", "next": "decision5_AABBB"}
            ],
            "image": None
        },
        "decision4_ABAA": {
            "title": "Vision Strategy",
            "description": "Using the vision, you predict Medusa’s movements and find a hidden path to her lair. You’re cursed but confident. Her snakes guard the entrance.",
            "options": [
                {"text": "Sneak past snakes", "next": "decision5_ABAAA"},
                {"text": "Fight through", "next": "decision5_ABAAB"}
            ],
            "image": None
        },
        "decision4_ABAB": {
            "title": "Curse Resistance",
            "description": "You resist the curse, but it weakens you. The path leads to Medusa’s lair, where her gaze feels omnipresent. You must act quickly.",
            "options": [
                {"text": "Rush to confront", "next": "decision5_ABABA"},
                {"text": "Hide and plan", "next": "decision5_ABABB"}
            ],
            "image": None
        },
        "decision4_ABBA": {
            "title": "Facing Taunts",
            "description": "You shout back at Medusa, drawing her attention. Her snakes swarm, but you find a reflective shard on the ground, a last hope against her gaze.",
            "options": [
                {"text": "Use the shard", "next": "decision5_ABBAA"},
                {"text": "Attack directly", "next": "decision5_ABBAB"}
            ],
            "image": None
        },
        "decision4_ABBB": {
            "title": "Exit Blocked",
            "description": "Searching for an exit, you realize Medusa controls the mine’s paths. Her lair is the only way out. You feel her curse tightening its grip.",
            "options": [
                {"text": "Enter her lair", "next": "decision5_ABBBA"},
                {"text": "Break the curse", "next": "decision5_ABBBB"}
            ],
            "image": None
        },
        "decision5_AAAAA": {
            "title": "Medusa’s Lair",
            "description": "With shield and mirror, you enter Medusa’s lair. Her snakes hiss, and her gaze pierces the darkness. The mine’s curse pulses, but you’re ready to end it.",
            "options": [
                {"text": "Face Medusa", "next": "boss_medusa"},
                {"text": "Face Medusa", "next": "boss_medusa"}
            ],
            "image": None
        },
        "decision5_AAAAB": {
            "title": "Trapped Queen",
            "description": "You set a trap using the shield, luring Medusa’s snakes away. Her lair is open, but she’s enraged, her gaze more deadly than ever.",
            "options": [
                {"text": "Face Medusa", "next": "boss_medusa"},
                {"text": "Face Medusa", "next": "boss_medusa"}
            ],
            "image": None
        },
        "decision5_AAABA": {
            "title": "Bold Charge",
            "description": "Charging in with your mirror, you meet Medusa’s gaze indirectly. Her snakes attack, but you’re in her lair now, ready for the final fight.",
            "options": [
                {"text": "Face Medusa", "next": "boss_medusa"},
                {"text": "Face Medusa", "next": "boss_medusa"}
            ],
            "image": None
        },
        "decision5_AAABB": {
            "title": "Waiting Game",
            "description": "Waiting for an opening, you spot Medusa’s reflection in your mirror. Her lair is a maze of statues, but you’re ready to confront her.",
            "options": [
                {"text": "Face Medusa", "next": "boss_medusa"},
                {"text": "Face Medusa", "next": "boss_medusa"}
            ],
            "image": None
        },
        "decision5_AABAA": {
            "title": "Sword and Courage",
            "description": "With the statue’s sword, you storm Medusa’s lair. Her snakes recoil, but her gaze is unrelenting. The mine shakes as you prepare to fight.",
            "options": [
                {"text": "Face Medusa", "next": "boss_medusa"},
                {"text": "Face Medusa", "next": "boss_medusa"}
            ],
            "image": None
        },
        "decision5_AABAB": {
            "title": "Cautious Entry",
            "description": "Moving cautiously with the sword, you enter Medusa’s lair. Her presence is overwhelming, but you’re determined to end the curse.",
            "options": [
                {"text": "Face Medusa", "next": "boss_medusa"},
                {"text": "Face Medusa", "next": "boss_medusa"}
            ],
            "image": None
        },
        "decision5_AABBA": {
            "title": "Desperate Fight",
            "description": "With only your pick, you face Medusa in her lair. Her snakes are everywhere, and her gaze is deadly. The mine’s curse is at its peak.",
            "options": [
                {"text": "Face Medusa", "next": "boss_medusa"},
                {"text": "Face Medusa", "next": "boss_medusa"}
            ],
            "image": None
        },
        "decision5_AABBB": {
            "title": "Last Hope",
            "description": "Searching for another way, you’re cornered in Medusa’s lair. With no weapon but your pick, you must face her to escape the mine.",
            "options": [
                {"text": "Face Medusa", "next": "boss_medusa"},
                {"text": "Face Medusa", "next": "boss_medusa"}
            ],
            "image": None
        },
        "decision5_ABAAA": {
            "title": "Sneaky Approach",
            "description": "Sneaking past the snakes, you enter Medusa’s lair with the vision’s guidance. Her gaze is deadly, but you know her patterns.",
            "options": [
                {"text": "Face Medusa", "next": "boss_medusa"},
                {"text": "Face Medusa", "next": "boss_medusa"}
            ],
            "image": None
        },
        "decision5_ABAAB": {
            "title": "Fighting Through",
            "description": "Battling the snakes, you reach Medusa’s lair, bloodied but guided by the vision. She awaits, her curse strong but your resolve stronger.",
            "options": [
                {"text": "Face Medusa", "next": "boss_medusa"},
                {"text": "Face Medusa", "next": "boss_medusa"}
            ],
            "image": None
        },
        "decision5_ABABA": {
            "title": "Weakened Rush",
            "description": "Weakened by the curse, you rush into Medusa’s lair. Her snakes swarm, but you’re driven by the need to escape the mine’s grip.",
            "options": [
                {"text": "Face Medusa", "next": "boss_medusa"},
                {"text": "Face Medusa", "next": "boss_medusa"}
            ],
            "image": None
        },
        "decision5_ABABB": {
            "title": "Hidden Plan",
            "description": "Hiding from the curse, you plan your attack in Medusa’s lair. Her gaze is everywhere, but you’re ready to strike from the shadows.",
            "options": [
                {"text": "Face Medusa", "next": "boss_medusa"},
                {"text": "Face Medusa", "next": "boss_medusa"}
            ],
            "image": None
        },
        "decision5_ABBAA": {
            "title": "Shard’s Power",
            "description": "Using the reflective shard, you enter Medusa’s lair, deflecting her lesser snakes. She faces you directly, her gaze a final challenge.",
            "options": [
                {"text": "Face Medusa", "next": "boss_medusa"},
                {"text": "Face Medusa", "next": "boss_medusa"}
            ],
            "image": None
        },
        "decision5_ABBAB": {
            "title": "Direct Assault",
            "description": "Ignoring the shard, you attack Medusa’s lair with raw determination. Her snakes overwhelm, but you reach her, ready for battle.",
            "options": [
                {"text": "Face Medusa", "next": "boss_medusa"},
                {"text": "Face Medusa", "next": "boss_medusa"}
            ],
            "image": None
        },
        "decision5_ABBBA": {
            "title": "No Escape",
            "description": "The mine forces you into Medusa’s lair. Her curse is suffocating, but you face her with nothing but your will to survive.",
            "options": [
                {"text": "Face Medusa", "next": "boss_medusa"},
                {"text": "Face Medusa", "next": "boss_medusa"}
            ],
            "image": None
        },
        "decision5_ABBBB": {
            "title": "Curse Breaker",
            "description": "You attempt to break the curse, weakening Medusa slightly. Her lair is open, and you face her with renewed hope but no tools.",
            "options": [
                {"text": "Face Medusa", "next": "boss_medusa"},
                {"text": "Face Medusa", "next": "boss_medusa"}
            ],
            "image": None
        },
        # Swamp Path (B)
        "decision1_B": {
            "title": "The Glowing Mire",
            "description": "The tunnel glows with bioluminescent mushrooms, their spores thick in the humid air. A foul stench suggests a swamp ahead, home to a monstrous creature. You find a vial of glowing spores.",
            "options": [
                {"text": "Use spores for light", "next": "decision2_BA"},
                {"text": "Avoid spores", "next": "decision2_BB"}
            ],
            "image": None
        },
        "decision2_BA": {
            "title": "Spore Illumination",
            "description": "The spores light your way, revealing a path through a toxic swamp. You notice claw marks and hear a low growl. The Swamp Horror’s territory is near, and the spores make you cough.",
            "options": [
                {"text": "Follow claw marks", "next": "decision3_BAA"},
                {"text": "Find cleaner air", "next": "decision3_BAB"}
            ],
            "image": None
        },
        "decision2_BB": {
            "title": "Careful Steps",
            "description": "Avoiding the spores, you move slowly through the dark. The swamp’s stench grows stronger, and you find a rusted machete, possibly useful against the Swamp Horror.",
            "options": [
                {"text": "Take the machete", "next": "decision3_BBA"},
                {"text": "Leave it", "next": "decision3_BBB"}
            ],
            "image": None
        },
        "decision3_BAA": {
            "title": "Horror’s Tracks",
            "description": "The claw marks lead to a pool of toxic sludge. The spores’ light shows a massive shape moving beneath. The Swamp Horror knows you’re here, and the air is poisonous.",
            "options": [
                {"text": "Create a distraction", "next": "decision4_BAAA"},
                {"text": "Prepare to fight", "next": "decision4_BAAB"}
            ],
            "image": None
        },
        "decision3_BAB": {
            "title": "Cleaner Air",
            "description": "Seeking cleaner air, you find a raised path above the swamp. The spores’ effects linger, but you spot the Swamp Horror’s tentacles in the distance.",
            "options": [
                {"text": "Use high ground", "next": "decision4_BABA"},
                {"text": "Approach quietly", "next": "decision4_BABB"}
            ],
            "image": None
        },
        "decision3_BBA": {
            "title": "Machete in Hand",
            "description": "The machete feels sturdy. You reach a swampy clearing where the Swamp Horror’s tentacles thrash. The mushrooms glow brighter, warning of danger.",
            "options": [
                {"text": "Cut through vines", "next": "decision4_BBAA"},
                {"text": "Stay hidden", "next": "decision4_BBAB"}
            ],
            "image": None
        },
        "decision3_BBB": {
            "title": "Unarmed Advance",
            "description": "Without the machete, you rely on your pick. The swamp grows denser, and the Swamp Horror’s growls shake the ground. You’re close to its lair.",
            "options": [
                {"text": "Find a weapon", "next": "decision4_BBBA"},
                {"text": "Confront it now", "next": "decision4_BBBB"}
            ],
            "image": None
        },
        "decision4_BAAA": {
            "title": "Distraction Set",
            "description": "You throw glowing spores, luring the Swamp Horror’s tentacles away. Its lair is exposed, a toxic pool where it waits. You’re ready to face it.",
            "options": [
                {"text": "Enter the lair", "next": "decision5_BAAAA"},
                {"text": "Attack from afar", "next": "decision5_BAAAB"}
            ],
            "image": None
        },
        "decision4_BAAB": {
            "title": "Ready for Battle",
            "description": "You brace for combat, spores still glowing. The Swamp Horror rises from the sludge, its tentacles reaching. The swamp vibrates with its power.",
            "options": [
                {"text": "Charge in", "next": "decision5_BAABA"},
                {"text": "Wait for an opening", "next": "decision5_BAABB"}
            ],
            "image": None
        },
        "decision4_BABA": {
            "title": "High Ground",
            "description": "From the raised path, you see the Swamp Horror’s lair clearly. The spores weaken you, but the high ground gives an advantage.",
            "options": [
                {"text": "Attack from above", "next": "decision5_BABAA"},
                {"text": "Descend to fight", "next": "decision5_BABAB"}
            ],
            "image": None
        },
        "decision4_BABB": {
            "title": "Silent Approach",
            "description": "Moving quietly, you reach the Swamp Horror’s lair unnoticed. The toxic air burns, but you’re close enough to strike first.",
            "options": [
                {"text": "Surprise attack", "next": "decision5_BABBA"},
                {"text": "Observe first", "next": "decision5_BABBB"}
            ],
            "image": None
        },
        "decision4_BBAA": {
            "title": "Cleared Path",
            "description": "The machete cuts through vines, opening a path to the Swamp Horror’s lair. Its tentacles lash out, sensing your approach.",
            "options": [
                {"text": "Enter with machete", "next": "decision5_BBAAA"},
                {"text": "Set a trap", "next": "decision5_BBAAB"}
            ],
            "image": None
        },
        "decision4_BBAB": {
            "title": "Hidden in Swamp",
            "description": "Hiding with the machete, you avoid the Swamp Horror’s notice. Its lair is a toxic mire, and you must act before the spores overwhelm you.",
            "options": [
                {"text": "Strike from hiding", "next": "decision5_BBABA"},
                {"text": "Wait for a chance", "next": "decision5_BBABB"}
            ],
            "image": None
        },
        "decision4_BBBA": {
            "title": "Desperate Search",
            "description": "You find a sharpened bone in the swamp, better than your pick. The Swamp Horror’s lair is ahead, its growls shaking the mire.",
            "options": [
                {"text": "Use the bone", "next": "decision5_BBBAA"},
                {"text": "Rush in", "next": "decision5_BBBAB"}
            ],
            "image": None
        },
        "decision4_BBBB": {
            "title": "No Time Left",
            "description": "With only your pick, you face the Swamp Horror’s lair. The swamp pulses with its presence, and you feel the spores taking hold.",
            "options": [
                {"text": "Confront it", "next": "decision5_BBBBA"},
                {"text": "Find cover", "next": "decision5_BBBBB"}
            ],
            "image": None
        },
        "decision5_BAAAA": {
            "title": "Horror’s Lair",
            "description": "The distraction worked, and you enter the Swamp Horror’s lair. Its tentacles thrash in the toxic pool, ready to crush you.",
            "options": [
                {"text": "Face the Horror", "next": "boss_swamp"},
                {"text": "Face the Horror", "next": "boss_swamp"}
            ],
            "image": None
        },
        "decision5_BAAAB": {
            "title": "Ranged Assault",
            "description": "Throwing rocks from afar, you anger the Swamp Horror. It charges from its lair, toxic sludge dripping as it prepares to fight.",
            "options": [
                {"text": "Face the Horror", "next": "boss_swamp"},
                {"text": "Face the Horror", "next": "boss_swamp"}
            ],
            "image": None
        },
        "decision5_BAABA": {
            "title": "Bold Charge",
            "description": "Charging with the spores’ light, you meet the Swamp Horror head-on. Its tentacles lash out, but you’re in its lair, ready to fight.",
            "options": [
                {"text": "Face the Horror", "next": "boss_swamp"},
                {"text": "Face the Horror", "next": "boss_swamp"}
            ],
            "image": None
        },
        "decision5_BAABB": {
            "title": "Waiting Game",
            "description": "Waiting for an opening, you spot the Swamp Horror’s weak spot. Its lair is a toxic trap, but you’re ready to strike.",
            "options": [
                {"text": "Face the Horror", "next": "boss_swamp"},
                {"text": "Face the Horror", "next": "boss_swamp"}
            ],
            "image": None
        },
        "decision5_BABAA": {
            "title": "High Ground Strike",
            "description": "From above, you leap into the Swamp Horror’s lair, aiming for its core. The spores burn, but your position is strong.",
            "options": [
                {"text": "Face the Horror", "next": "boss_swamp"},
                {"text": "Face the Horror", "next": "boss_swamp"}
            ],
            "image": None
        },
        "decision5_BABAB": {
            "title": "Descending Fight",
            "description": "Descending into the Swamp Horror’s lair, you face its full wrath. The toxic air chokes, but you’re committed to the battle.",
            "options": [
                {"text": "Face the Horror", "next": "boss_swamp"},
                {"text": "Face the Horror", "next": "boss_swamp"}
            ],
            "image": None
        },
        "decision5_BABBA": {
            "title": "Surprise Strike",
            "description": "Your surprise attack catches the Swamp Horror off guard. Its lair is a toxic maze, but you’ve got the upper hand.",
            "options": [
                {"text": "Face the Horror", "next": "boss_swamp"},
                {"text": "Face the Horror", "next": "boss_swamp"}
            ],
            "image": None
        },
        "decision5_BABBB": {
            "title": "Observant Plan",
            "description": "Observing the Swamp Horror, you learn its patterns. Entering its lair, you’re ready to exploit its weaknesses.",
            "options": [
                {"text": "Face the Horror", "next": "boss_swamp"},
                {"text": "Face the Horror", "next": "boss_swamp"}
            ],
            "image": None
        },
        "decision5_BBAAA": {
            "title": "Machete Charge",
            "description": "With machete in hand, you storm the Swamp Horror’s lair. Its tentacles thrash, but you’re ready to carve through.",
            "options": [
                {"text": "Face the Horror", "next": "boss_swamp"},
                {"text": "Face the Horror", "next": "boss_swamp"}
            ],
            "image": None
        },
        "decision5_BBAAB": {
            "title": "Trapped Horror",
            "description": "You set a trap with vines, slowing the Swamp Horror. Its lair is open, and you enter with the machete, ready for battle.",
            "options": [
                {"text": "Face the Horror", "next": "boss_swamp"},
                {"text": "Face the Horror", "next": "boss_swamp"}
            ],
            "image": None
        },
        "decision5_BBABA": {
            "title": "Hidden Strike",
            "description": "Striking from hiding, you wound the Swamp Horror. Its lair is a toxic mire, but your machete gives you an edge.",
            "options": [
                {"text": "Face the Horror", "next": "boss_swamp"},
                {"text": "Face the Horror", "next": "boss_swamp"}
            ],
            "image": None
        },
        "decision5_BBABB": {
            "title": "Patient Strike",
            "description": "Waiting for a chance, you spot the Swamp Horror’s weak spot. You enter its lair with the machete, ready to end it.",
            "options": [
                {"text": "Face the Horror", "next": "boss_swamp"},
                {"text": "Face the Horror", "next": "boss_swamp"}
            ],
            "image": None
        },
        "decision5_BBBAA": {
            "title": "Bone Weapon",
            "description": "The sharpened bone feels light but deadly. You enter the Swamp Horror’s lair, ready to face its toxic wrath.",
            "options": [
                {"text": "Face the Horror", "next": "boss_swamp"},
                {"text": "Face the Horror", "next": "boss_swamp"}
            ],
            "image": None
        },
        "decision5_BBBAB": {
            "title": "Desperate Rush",
            "description": "Rushing in with your pick, you face the Swamp Horror in its lair. The spores overwhelm, but you fight for survival.",
            "options": [
                {"text": "Face the Horror", "next": "boss_swamp"},
                {"text": "Face the Horror", "next": "boss_swamp"}
            ],
            "image": None
        },
        "decision5_BBBBA": {
            "title": "Direct Confrontation",
            "description": "With only your pick, you confront the Swamp Horror in its lair. The swamp pulses with its power, but you stand firm.",
            "options": [
                {"text": "Face the Horror", "next": "boss_swamp"},
                {"text": "Face the Horror", "next": "boss_swamp"}
            ],
            "image": None
        },
        "decision5_BBBBB": {
            "title": "Last Stand",
            "description": "Hiding for cover, you’re forced into the Swamp Horror’s lair. With your pick, you face it, hoping to survive.",
            "options": [
                {"text": "Face the Horror", "next": "boss_swamp"},
                {"text": "Face the Horror", "next": "boss_swamp"}
            ],
            "image": None
        },
        # Dragon Path (C)
        "decision1_C": {
            "title": "The Fiery Depths",
            "description": "The tunnel reeks of sulfur, its walls scorched black. A distant roar shakes the mine, hinting at a dragon guardian. You find a charred shield, still warm.",
            "options": [
                {"text": "Take the shield", "next": "decision2_CA"},
                {"text": "Leave it", "next": "decision2_CB"}
            ],
            "image": None
        },
        "decision2_CA": {
            "title": "Shielded Path",
            "description": "The shield protects you from sudden bursts of heat. The tunnel opens to a chasm with a lava river below, and the dragon’s roars grow louder.",
            "options": [
                {"text": "Cross the bridge", "next": "decision3_CAA"},
                {"text": "Find another way", "next": "decision3_CAB"}
            ],
            "image": None
        },
        "decision2_CB": {
            "title": "Unprotected Advance",
            "description": "Without the shield, you feel the heat intensely. The tunnel leads to a crystal cavern, reflecting the dragon’s fiery glow in the distance.",
            "options": [
                {"text": "Examine crystals", "next": "decision3_CBA"},
                {"text": "Move quickly", "next": "decision3_CBB"}
            ],
            "image": None
        },
        "decision3_CAA": {
            "title": "Bridge of Fire",
            "description": "The shield blocks heat as you cross the narrow bridge. Below, lava stirs, and the dragon’s eyes glow. You’re halfway to its lair.",
            "options": [
                {"text": "Run across", "next": "decision4_CAAA"},
                {"text": "Move carefully", "next": "decision4_CAAB"}
            ],
            "image": None
        },
        "decision3_CAB": {
            "title": "Alternate Route",
            "description": "You find a ledge along the chasm, avoiding the bridge. The heat is bearable with the shield, but the dragon’s roars shake the mine.",
            "options": [
                {"text": "Follow the ledge", "next": "decision4_CABA"},
                {"text": "Search for tools", "next": "decision4_CABB"}
            ],
            "image": None
        },
        "decision3_CBA": {
            "title": "Crystal Visions",
            "description": "The crystals show visions of the dragon’s fiery attacks. You learn its patterns but feel the heat rising. The path to its lair is clear.",
            "options": [
                {"text": "Use vision knowledge", "next": "decision4_CBAA"},
                {"text": "Ignore visions", "next": "decision4_CBAB"}
            ],
            "image": None
        },
        "decision3_CBB": {
            "title": "Swift Escape",
            "description": "Moving quickly, you avoid the crystals but feel the dragon’s heat. You reach a scorched cavern, the entrance to its lair.",
            "options": [
                {"text": "Prepare for battle", "next": "decision4_CBBA"},
                {"text": "Search for cover", "next": "decision4_CBBB"}
            ],
            "image": None
        },
        "decision4_CAAA": {
            "title": "Across the Chasm",
            "description": "Running across the bridge, you reach a fiery cavern. The dragon’s scales glint, and your shield is scorched but intact.",
            "options": [
                {"text": "Enter the lair", "next": "decision5_CAAAA"},
                {"text": "Set a trap", "next": "decision5_CAAAB"}
            ],
            "image": None
        },
        "decision4_CAAB": {
            "title": "Careful Crossing",
            "description": "Moving carefully, you cross safely with the shield. The dragon’s lair is ahead, its heat overwhelming but your resolve firm.",
            "options": [
                {"text": "Face the dragon", "next": "decision5_CAABA"},
                {"text": "Find an advantage", "next": "decision5_CAABB"}
            ],
            "image": None
        },
        "decision4_CABA": {
            "title": "Ledge Path",
            "description": "The ledge leads to the dragon’s lair. The shield protects you, but the path crumbles, forcing you to face the beast soon.",
            "options": [
                {"text": "Enter boldly", "next": "decision5_CABAA"},
                {"text": "Prepare first", "next": "decision5_CABAB"}
            ],
            "image": None
        },
        "decision4_CABB": {
            "title": "Tool Search",
            "description": "You find a fire-resistant cloak among the rocks. With the shield, you’re well-equipped for the dragon’s lair ahead.",
            "options": [
                {"text": "Use cloak and enter", "next": "decision5_CABBA"},
                {"text": "Enter without cloak", "next": "decision5_CABBB"}
            ],
            "image": None
        },
        "decision4_CBAA": {
            "title": "Vision Strategy",
            "description": "Using the crystal visions, you plan your attack. The dragon’s lair is a fiery trap, but you know its weaknesses.",
            "options": [
                {"text": "Exploit weaknesses", "next": "decision5_CBAAA"},
                {"text": "Charge in", "next": "decision5_CBAAB"}
            ],
            "image": None
        },
        "decision4_CBAB": {
            "title": "Ignoring Visions",
            "description": "Ignoring the visions, you rely on instinct. The dragon’s lair is close, and the heat is unbearable without a shield.",
            "options": [
                {"text": "Face the dragon", "next": "decision5_CBABA"},
                {"text": "Find protection", "next": "decision5_CBABB"}
            ],
            "image": None
        },
        "decision4_CBBA": {
            "title": "Battle Ready",
            "description": "You sharpen your pick and enter the scorched cavern. The dragon’s roars deafen, but you’re ready to fight.",
            "options": [
                {"text": "Attack directly", "next": "decision5_CBBAA"},
                {"text": "Wait for an opening", "next": "decision5_CBBAB"}
            ],
            "image": None
        },
        "decision4_CBBB": {
            "title": "Seeking Cover",
            "description": "You find a boulder to hide behind, but the dragon’s flames light the cavern. You must face it soon, unprepared.",
            "options": [
                {"text": "Confront now", "next": "decision5_CBBBA"},
                {"text": "Find a weapon", "next": "decision5_CBBBB"}
            ],
            "image": None
        },
        "decision5_CAAAA": {
            "title": "Dragon’s Lair",
            "description": "With the shield, you enter the dragon’s lair. Its flames roar, but you’re ready to face the guardian of the mine.",
            "options": [
                {"text": "Face the Dragon", "next": "boss_dragon"},
                {"text": "Face the Dragon", "next": "boss_dragon"}
            ],
            "image": None
        },
        "decision5_CAAAB": {
            "title": "Trapped Dragon",
            "description": "You set a trap, weakening the dragon’s defenses. Its lair is open, and you enter with the shield, ready for battle.",
            "options": [
                {"text": "Face the Dragon", "next": "boss_dragon"},
                {"text": "Face the Dragon", "next": "boss_dragon"}
            ],
            "image": None
        },
        "decision5_CAABA": {
            "title": "Shielded Fight",
            "description": "The shield holds as you face the dragon in its lair. Its flames are intense, but you’re prepared for the fight.",
            "options": [
                {"text": "Face the Dragon", "next": "boss_dragon"},
                {"text": "Face the Dragon", "next": "boss_dragon"}
            ],
            "image": None
        },
        "decision5_CAABB": {
            "title": "Seeking Advantage",
            "description": "You find a weak spot in the dragon’s lair. With the shield, you’re ready to exploit it in the coming battle.",
            "options": [
                {"text": "Face the Dragon", "next": "boss_dragon"},
                {"text": "Face the Dragon", "next": "boss_dragon"}
            ],
            "image": None
        },
        "decision5_CABAA": {
            "title": "Bold Entry",
            "description": "With the shield, you storm the dragon’s lair. Its roars shake the mine, but you’re ready to end its reign.",
            "options": [
                {"text": "Face the Dragon", "next": "boss_dragon"},
                {"text": "Face the Dragon", "next": "boss_dragon"}
            ],
            "image": None
        },
        "decision5_CABAB": {
            "title": "Prepared Fight",
            "description": "Preparing with the shield, you enter the dragon’s lair. The heat is overwhelming, but you’re ready to face it.",
            "options": [
                {"text": "Face the Dragon", "next": "boss_dragon"},
                {"text": "Face the Dragon", "next": "boss_dragon"}
            ],
            "image": None
        },
        "decision5_CABBA": {
            "title": "Cloaked Warrior",
            "description": "With shield and cloak, you enter the dragon’s lair. The flames are less deadly, and you’re ready to fight.",
            "options": [
                {"text": "Face the Dragon", "next": "boss_dragon"},
                {"text": "Face the Dragon", "next": "boss_dragon"}
            ],
            "image": None
        },
        "decision5_CABBB": {
            "title": "Shield Alone",
            "description": "Without the cloak, you rely on the shield in the dragon’s lair. The heat is intense, but you face the beast.",
            "options": [
                {"text": "Face the Dragon", "next": "boss_dragon"},
                {"text": "Face the Dragon", "next": "boss_dragon"}
            ],
            "image": None
        },
        "decision5_CBAAA": {
            "title": "Weakness Exploited",
            "description": "Using the visions, you enter the dragon’s lair, targeting its weak spots. The flames roar, but you’re confident.",
            "options": [
                {"text": "Face the Dragon", "next": "boss_dragon"},
                {"text": "Face the Dragon", "next": "boss_dragon"}
            ],
            "image": None
        },
        "decision5_CBAAB": {
            "title": "Instinctive Charge",
            "description": "Charging in without visions, you face the dragon in its lair. The heat is unbearable, but your resolve holds.",
            "options": [
                {"text": "Face the Dragon", "next": "boss_dragon"},
                {"text": "Face the Dragon", "next": "boss_dragon"}
            ],
            "image": None
        },
        "decision5_CBABA": {
            "title": "Unprotected Fight",
            "description": "Without a shield, you face the dragon in its lair. The visions guide you, but the flames are relentless.",
            "options": [
                {"text": "Face the Dragon", "next": "boss_dragon"},
                {"text": "Face the Dragon", "next": "boss_dragon"}
            ],
            "image": None
        },
        "decision5_CBABB": {
            "title": "Desperate Protection",
            "description": "You find a makeshift shield and enter the dragon’s lair. The visions help, but the battle will be tough.",
            "options": [
                {"text": "Face the Dragon", "next": "boss_dragon"},
                {"text": "Face the Dragon", "next": "boss_dragon"}
            ],
            "image": None
        },
        "decision5_CBBAA": {
            "title": "Pick and Courage",
            "description": "With only your pick, you storm the dragon’s lair. The cavern shakes, but you’re ready to fight.",
            "options": [
                {"text": "Face the Dragon", "next": "boss_dragon"},
                {"text": "Face the Dragon", "next": "boss_dragon"}
            ],
            "image": None
        },
        "decision5_CBBAB": {
            "title": "Waiting Game",
            "description": "Waiting for an opening, you spot the dragon’s weak spot. You enter its lair, ready to strike with your pick.",
            "options": [
                {"text": "Face the Dragon", "next": "boss_dragon"},
                {"text": "Face the Dragon", "next": "boss_dragon"}
            ],
            "image": None
        },
        "decision5_CBBBA": {
            "title": "Last Stand",
            "description": "With no protection, you face the dragon in its lair. The flames are deadly, but you fight for survival.",
            "options": [
                {"text": "Face the Dragon", "next": "boss_dragon"},
                {"text": "Face the Dragon", "next": "boss_dragon"}
            ],
            "image": None
        },
        "decision5_CBBBB": {
            "title": "Final Weapon",
            "description": "You find a spear in the cavern and enter the dragon’s lair. It’s your last chance to defeat the beast.",
            "options": [
                {"text": "Face the Dragon", "next": "boss_dragon"},
                {"text": "Face the Dragon", "next": "boss_dragon"}
            ],
            "image": None
        },
        "boss_medusa": {
            "title": "The Serpent Queen",
            "description": "Medusa stands before you, snakes writhing in her hair. Her gaze could turn you to stone, but your choices have led you here. Defeat her to break the mine’s curse.",
            "options": [
                {"text": "Begin battle", "next": "combat_medusa"},
                {"text": "Begin battle", "next": "combat_medusa"}
            ],
            "image": None
        },
        "boss_swamp": {
            "title": "The Swamp Horror",
            "description": "The Swamp Horror rises from its toxic pool, tentacles lashing. The spores choke the air, but your journey has prepared you. Defeat it to escape the mine.",
            "options": [
                {"text": "Begin battle", "next": "combat_swamp"},
                {"text": "Begin battle", "next": "combat_swamp"}
            ],
            "image": None
        },
        "boss_dragon": {
            "title": "The Dragon",
            "description": "The dragon towers over you, flames curling from its jaws. The mine shakes with its power, but your path has led to this. Defeat it to win your freedom.",
            "options": [
                {"text": "Begin battle", "next": "combat_dragon"},
                {"text": "Begin battle", "next": "combat_dragon"}
            ],
            "image": None
        },
        "victory": {
            "title": "Freedom Earned",
            "description": "The guardian falls, and the mine’s curse lifts. You stumble into sunlight, scarred but alive. Your choices shaped your escape, a tale for the ages.",
            "options": [
                {"text": "Play again", "next": "start"},
                {"text": "Play again", "next": "start"}
            ],
            "image": None
        },
        "defeat": {
            "title": "Swallowed by Darkness",
            "description": "The guardian’s final blow ends your struggle. The mine claims another soul, your choices lost to its depths. Another may yet escape.",
            "options": [
                {"text": "Try again", "next": "start"},
                {"text": "Try again", "next": "start"}
            ],
            "image": None
        }
    }

    try:
        with open('scenes.json', 'w') as f:
            json.dump(scenes, f, indent=4)
    except Exception as e:
        print(f"Error writing scenes.json: {e}")

    return scenes

def draw_combat_cards(surface, cards, combat_system):
    if not cards:  # Handle empty card list
        return
    card_width, card_height = 150, 200
    cards_start_x = (WIDTH - (len(cards) * (card_width + 20) - 20)) // 2

    for i, card in enumerate(cards):
        card_x = cards_start_x + i * (card_width + 20)
        card_y = HEIGHT - card_height - 50
        card_surface = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
        pygame.draw.rect(card_surface, CARD_BEIGE, (0, 0, card_width, card_height), border_radius=10)
        pygame.draw.rect(card_surface, CARD_BROWN, (0, 0, card_width, card_height), 3, border_radius=10)
        title_text = font_subtitle.render(card["name"], True, BLACK)
        title_rect = title_text.get_rect(center=(card_width // 2, 30))
        card_surface.blit(title_text, title_rect)
        type_color = BLUE
        if card["type"] == "attack":
            type_color = RED
        elif card["type"] == "heal":
            type_color = GREEN
        type_text = font_body.render(card["type"].capitalize(), True, type_color)
        type_rect = type_text.get_rect(center=(card_width // 2, 60))
        card_surface.blit(type_text, type_rect)
        if "damage" in card:
            effect_text = font_body.render(f"DMG: {card['damage']}", True, BLACK)
        elif "heal" in card:
            effect_text = font_body.render(f"HEAL: {card['heal']}", True, BLACK)
        elif "defense" in card:
            effect_text = font_body.render(f"DEF: {card['defense']}", True, BLACK)
        else:
            effect_text = font_body.render("Special", True, BLACK)
        effect_rect = effect_text.get_rect(center=(card_width // 2, 100))
        card_surface.blit(effect_text, effect_rect)
        surface.blit(card_surface, (card_x, card_y))
        if combat_system.current_turn == "player":
            card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
            mouse_pos = pygame.mouse.get_pos()
            if card_rect.collidepoint(mouse_pos):
                pygame.draw.rect(surface, GOLD, (card_x - 5, card_y - 5, card_width + 10, card_height + 10), 3,
                                 border_radius=15)

def draw_health_bars(surface, player_health, boss_health):
    pygame.draw.rect(surface, GRAY, (50, 50, 200, 30))
    pygame.draw.rect(surface, GREEN, (50, 50, max(0, player_health * 2), 30))
    pygame.draw.rect(surface, WHITE, (50, 50, 200, 30), 2)
    health_text = font_body.render(f"Player: {max(0, player_health)}/100", True, WHITE)
    surface.blit(health_text, (60, 55))
    pygame.draw.rect(surface, GRAY, (WIDTH - 250, 50, 200, 30))
    pygame.draw.rect(surface, RED, (WIDTH - 250, 50, max(0, boss_health * 200 / 150), 30))
    pygame.draw.rect(surface, WHITE, (WIDTH - 250, 50, 200, 30), 2)
    health_text = font_body.render(f"Boss: {max(0, boss_health)}/150", True, WHITE)
    surface.blit(health_text, (WIDTH - 240, 55))

def draw_boss(surface, boss_type):
    if boss_type == "medusa":
        color = (100, 200, 100)
    elif boss_type == "swamp":
        color = (100, 100, 50)
    else:
        color = (200, 50, 50)
    pygame.draw.ellipse(surface, color, (WIDTH // 2 - 100, HEIGHT // 2 - 150, 200, 150))
    pygame.draw.rect(surface, color, (WIDTH // 2 - 50, HEIGHT // 2, 100, 100))
    pygame.draw.circle(surface, WHITE, (WIDTH // 2 - 50, HEIGHT // 2 - 100), 20)
    pygame.draw.circle(surface, WHITE, (WIDTH // 2 + 50, HEIGHT // 2 - 100), 20)
    pygame.draw.circle(surface, BLACK, (WIDTH // 2 - 45, HEIGHT // 2 - 100), 10)
    pygame.draw.circle(surface, BLACK, (WIDTH // 2 + 45, HEIGHT // 2 - 100), 10)

def main():
    clock = pygame.time.Clock()
    scenes = create_scenes_file()  # Regenerate scenes.json with new story
    game_state = GameState()
    combat_system = None
    buttons = [
        Button(WIDTH // 2 - 150, HEIGHT // 2 - 100, 300, 60, "Play", BLUE, (100, 100, 200)),
        Button(WIDTH // 2 - 150, HEIGHT // 2, 300, 60, "Continue", BLUE, (100, 100, 200)),
        Button(WIDTH // 2 - 150, HEIGHT // 2 + 100, 300, 60, "Restart", BLUE, (100, 100, 200))
    ]
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if game_state.game_mode == "menu":
                for button in buttons:
                    button.update(mouse_pos)
                    if button.is_clicked(mouse_pos, event):
                        if button.text == "Play":
                            game_state = GameState()
                            game_state.game_mode = "playing"
                            game_state.initialize_card(scenes)
                        elif button.text == "Continue":
                            if game_state.load_progress(scenes):
                                game_state.game_mode = "playing"
                            else:
                                print("No saved progress found.")
                        elif button.text == "Restart":
                            if os.path.exists('progress.json'):
                                os.remove('progress.json')
                            game_state = GameState()
                            game_state.game_mode = "playing"
                            game_state.initialize_card(scenes)
            elif game_state.game_mode == "playing":
                if game_state.card:
                    game_state.card.handle_event(event, mouse_pos)
                    if game_state.card.decision_made:
                        current_scene = scenes[game_state.current_scene]
                        if game_state.card.decision == "left":
                            choice = "A"
                            next_scene = current_scene["options"][0]["next"]
                        else:
                            choice = "B"
                            next_scene = current_scene["options"][1]["next"]
                        game_state.add_choice(choice, scenes)
                        game_state.next_scene = next_scene
                        if next_scene.startswith("combat_"):
                            boss_type = next_scene.split("_")[1]
                            combat_system = CombatSystem(boss_type)
                            game_state.game_mode = "combat"
            elif game_state.game_mode == "combat":
                if combat_system.current_turn == "player" and event.type == pygame.MOUSEBUTTONDOWN:
                    card_width, card_height = 150, 200
                    cards_start_x = (WIDTH - (len(combat_system.player_cards) * (card_width + 20) - 20)) // 2
                    card_y = HEIGHT - card_height - 50
                    for i in range(len(combat_system.player_cards)):
                        card_x = cards_start_x + i * (card_width + 20)
                        card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
                        if card_rect.collidepoint(mouse_pos):
                            combat_system.player_attack(i)
                            break
            elif game_state.game_mode == "game_over":
                restart_button = Button(WIDTH // 2 - 150, HEIGHT - 150, 300, 60, "Play Again", BLUE, (100, 100, 200))
                restart_button.update(mouse_pos)
                if restart_button.is_clicked(mouse_pos, event):
                    if os.path.exists('progress.json'):
                        os.remove('progress.json')
                    game_state = GameState()
                    game_state.game_mode = "playing"
                    game_state.initialize_card(scenes)
                    combat_system = None

        screen.fill(BLACK)
        if game_state.game_mode == "menu":
            title_text = font_title.render("King", True, GOLD)
            title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 200))
            screen.blit(title_text, title_rect)
            for button in buttons:
                button.draw(screen)
        elif game_state.game_mode == "playing":
            if game_state.update():
                game_state.initialize_card(scenes)
            if game_state.card:
                game_state.card.update(mouse_pos)
                game_state.card.draw(screen)
                if game_state.boss_path:
                    path_text = font_body.render(f"Path: {game_state.boss_path.capitalize()}", True, WHITE)
                    screen.blit(path_text, (20, 20))
                decisions_text = font_body.render(f"Decisions: {game_state.decision_count}/5", True, WHITE)
                screen.blit(decisions_text, (20, 60))
        elif game_state.game_mode == "combat":
            combat_system.update()
            if combat_system.player_health <= 0:
                game_state.game_mode = "game_over"
                game_state.current_scene = "defeat"
            elif combat_system.boss_health <= 0:
                game_state.game_mode = "game_over"
                game_state.current_scene = "victory"
            draw_boss(screen, combat_system.boss_type)
            draw_health_bars(screen, combat_system.player_health, combat_system.boss_health)
            draw_combat_cards(screen, combat_system.player_cards, combat_system)
            message_text = font_subtitle.render(combat_system.message, True, BLUE)
            message_rect = message_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 150))
            screen.blit(message_text, message_rect)
            turn_text = font_title.render(f"{combat_system.current_turn.capitalize()}'s Turn", True, GOLD)
            turn_rect = turn_text.get_rect(center=(WIDTH // 2, 20))
            screen.blit(turn_text, turn_rect)
        elif game_state.game_mode == "game_over":
            restart_button = Button(WIDTH // 2 - 150, HEIGHT - 150, 300, 60, "Play Again", BLUE, (100, 100, 200))
            if game_state.current_scene in scenes:
                scene = scenes[game_state.current_scene]
                title_color = GOLD if game_state.current_scene == "victory" else RED
                title_text = font_title.render(scene["title"], True, title_color)
                title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 200))
                screen.blit(title_text, title_rect)

                wrapped_text = textwrap.wrap(scene["description"], width=50)
                for i, line in enumerate(wrapped_text[:5]):
                    text = font_body.render(line, True, WHITE)
                    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100 + i * 40))
                    screen.blit(text, text_rect)

                if game_state.boss_path:
                    summary_text = font_subtitle.render(f"You chose the {game_state.boss_path.capitalize()} path", True, WHITE)
                    summary_rect = summary_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
                    screen.blit(summary_text, summary_rect)

                    # Display player's choices
                    choices_str = ", ".join(game_state.choices) if game_state.choices else "No choices made"
                    choices_text = font_subtitle.render(f"Your Choices: {choices_str}", True, WHITE)
                    choices_rect = choices_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 150))
                    screen.blit(choices_text, choices_rect)

                    # Draw and handle restart button
                    restart_button.draw(screen)
                    restart_button.update(mouse_pos)


        # Update display and maintain frame rate
        pygame.display.flip()
        clock.tick(60)

    # Cleanup
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error running game: {e}")
        pygame.quit()
        sys.exit(1)
