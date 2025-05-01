# Backlog for the Game

## Tasks to complete

3) Pathways and choices 
4) weapon upgrade system and looting system (tsola)
5) *Left/right choice triggers events (tsola)

7) *Load & display cards from a pool (yagız)
8) *UI/UX & Visual Design (yagız)



TSOLA WILL DO THIS below
as well as create 2 bosses  

I watched YouTube videos and took some ideas that could improve the game's effectiveness. I then researched how I could implement these ideas if not covered in the YouTube video I watched. If it's confusing, let me know

1. Card Effect System
Right now, special effects like "Burn" or "Stun" are just text. To make them meaningful:
* Add a status effect handler (status_effects = []) for both Player and Enemy. found online
* Apply effects per turn (e.g., reduce HP, skip turn, reduce attack power).
* Implement effect duration tracking.
  

  
3. Computer Behavior
* Make the enemy choose different attack strategies based on its attributes.
* Implement "status-aware" AI (e.g., if poisoned, use cleanse card).
  
4. Card Descriptions in UI
* Hovering or clicking on a card shows a tooltip or side panel with full effects.
* Helps players make strategic choices without relying on memory.
5. Combo/Elemental Synergy System
* Example: Playing "Ice Spear" + "Stone Storm" applies “Frozen Armor Crumble” (bonus damage).
* Encourage creative card chaining.
  

  
7. Separation of Concerns
* Move combat logic into a CombatManager class.
* Move resource decision handling into a DecisionManager.
* Helps with scaling and maintenance.
  
8. Data Storage for Cards & Decisions
* Store cards and decisions in JSON or external files, and load them.
* Easier to expand without touching game logic.
  
9. Autosave/Load
* Save player state (health, inventory, resources) to a file.
* Offer a "Continue Game" option when relaunching.



## Tasks completed
2) Heath, stamina and Shield level and how they depreciate over time (tsola)

-) Load & display cards from a pool (yagiz) -> Check the demo code for a complete working test. I also uploaded the "deck" and the "drawing card" part separately from demo.
-) Card Data structure => (billy) 

-) Fighting mechanics (I will try to do if I can #billy)
-). Turn System Improvements #billy
* Add a clear turn indicator (e.g., a label that says "Your Turn" or "Enemy Turn").
* Disable input during enemy's turn to avoid multiple card clicks.
 -) . Deck Management Optimization #billy
* Use random.shuffle() and pop from a deck stack instead of random.choice() and remove.
* drawing cards
* special card abbilities
*initial deck
* take damage / play card / heal / apply status /remove status / show hand functions
* main menu
* game turns  
