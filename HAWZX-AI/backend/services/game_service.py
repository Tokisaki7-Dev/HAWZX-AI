import random
import logging
from typing import List, Tuple, Dict, Any, Optional

import random
import logging
from typing import List, Tuple, Dict, Any, Optional
from enum import IntEnum # For Enums

# --- Enums from the C++ snippet ---
class FishType(IntEnum):
    spray = 1
    flame = 2
    eel = 3
    sunfish = 4
    barracuda = 5
    mobula = 6
    octopus = 8
    whiteshark = 9
    hammerhead = 10
    
class ActiveSkill(IntEnum):
    normalattack = 0
    aoe = 1
    infight = 2
    crit = 3
    subtle = 4

class PassiveSkill(IntEnum):
    counter = 0
    deflect = 1
    reduce = 2
    heal = 3
    explode = 4

# --- New Info Classes ---
class ActionInfo:
    def __init__(self, action_fish: int = -1, is_skill: bool = False, active_skill_type: ActiveSkill = ActiveSkill.normalattack, 
                 target_fish: int = -1, friend_passives_id: List[int] = None, friend_types: List[FishType] = None,
                 enemy_passives_id: List[int] = None, enemy_types: List[FishType] = None):
        self.action_fish = action_fish
        self.is_skill = is_skill
        self.active_skill_type = active_skill_type
        self.target_fish = target_fish
        self.friend_passives_id = friend_passives_id if friend_passives_id is not None else []
        self.friend_types = friend_types if friend_types is not None else []
        self.enemy_passives_id = enemy_passives_id if enemy_passives_id is not None else []
        self.enemy_types = enemy_types if enemy_types is not None else []

class AssertInfo:
    def __init__(self, fish_pos: int = -1, fish_type: FishType = FishType.spray):
        self.fish_pos = fish_pos
        self.fish_type = fish_type

# --- Refined Fish Class ---
class Fish:
    def __init__(self, id: int, hp: int, atk: int, is_expose: bool = False, 
                 fish_type: FishType = FishType.spray, active_skill: ActiveSkill = ActiveSkill.normalattack, 
                 passive_skill: PassiveSkill = PassiveSkill.counter):
        self.id = id
        self.hp = hp
        self.max_hp = hp # Assuming max_hp is initial hp for simplicity
        self.atk = atk
        self.is_expose = is_expose
        self.state = "ALIVE" # "ALIVE", "DEAD"
        self.fish_type = fish_type
        self.active_skill = active_skill
        self.passive_skill = passive_skill

    def is_dead(self):
        return self.state == "DEAD" or self.hp <= 0

    def get_type(self) -> FishType:
        return self.fish_type

# --- Refined Game Class ---
class Game:
    def __init__(self):
        self.my_fish: List[Fish] = [] # Player's fish
        self.enemy_fish: List[Fish] = [] # Enemy's fish
        self.avatar_id: int = -1
        self.first_mover: int = -1 # 0 for me, 1 for enemy
        self.enemy_action: ActionInfo = ActionInfo()
        self.my_action: ActionInfo = ActionInfo()
        self.enemy_assert: AssertInfo = AssertInfo()
        self.my_assert: AssertInfo = AssertInfo()
        self.round: int = 0
        self.round_wins: int = 0
        self.last_round_finish_reason: int = -1 # Placeholder for win/lose reason
        self.state_limit_exceed: bool = False

    def get_my_living_fishes(self) -> List[Fish]:
        return [f for f in self.my_fish if not f.is_dead()]

    def get_enemy_living_fishes(self) -> List[Fish]:
        return [f for f in self.enemy_fish if not f.is_dead()]
    
    def get_my_fish_by_pos(self, pos: int) -> Optional[Fish]:
        if 0 <= pos < len(self.my_fish):
            return self.my_fish[pos]
        return None
    
    def get_enemy_fish_by_pos(self, pos: int) -> Optional[Fish]:
        if 0 <= pos < len(self.enemy_fish):
            return self.enemy_fish[pos]
        return None

# --- Refined Action Class ---
class Action:
    def __init__(self, game: Game):
        self._game = game
        self._action_fish: int = -1
        self._action_type: ActiveSkill = ActiveSkill.normalattack
        self._enemy_target: int = -1
        self._my_target_list: List[int] = []
        self._enemy_target_list: List[int] = []

    def set_action_fish(self, fish_pos: int):
        self._action_fish = fish_pos

    def set_action_type(self, action_type: ActiveSkill):
        self._action_type = action_type

    def set_enemy_target(self, target_pos: int):
        self._enemy_target = target_pos

    def set_my_target_list(self, target_list: List[int]):
        self._my_target_list = target_list

    def set_enemy_target_list(self, target_list: List[int]):
        self._enemy_target_list = target_list
    
    def to_action_info(self) -> ActionInfo:
        return ActionInfo(
            action_fish=self._action_fish,
            is_skill=(self._action_type != ActiveSkill.normalattack),
            active_skill_type=self._action_type,
            target_fish=self._enemy_target,
            # friend_passives_id, friend_types, enemy_passives_id, enemy_types would need to be populated from game state
        )

# --- End Dummy Classes ---

class GameService:
    def __init__(self):
        logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
        self.current_game_ai: Optional[GameStrategyAI] = None
        print("GameService initialized.")

    def load_game_strategy(self, game_name: str, stage: int):
        """Loads a specific AI strategy for a given game."""
        # This will eventually load strategy dynamically, for now, we'll use a placeholder
        print(f"Loading strategy for game: {game_name}, stage: {stage}")
        self.current_game_ai = GameStrategyAI(stage)

    def get_current_game_ai(self) -> Optional['GameStrategyAI']:
        return self.current_game_ai

    # Helper methods that interact with the actual Game object
    def get_my_living_fishes(self, game: Game) -> List[int]:
        """Returns the positions (indices) of living player's fishes."""
        return [i for i, fish in enumerate(game.my_fish) if not fish.is_dead()]

    def get_enemy_living_fishes(self, game: Game) -> List[int]:
        """Returns the positions (indices) of living enemy's fishes."""
        return [i for i, fish in enumerate(game.enemy_fish) if not fish.is_dead()]
    
    def get_lowest_health_enemy(self, game: Game) -> int:
        """Returns the position (index) of the enemy fish with the lowest health."""
        living_enemies = game.get_enemy_living_fishes(game)
        if not living_enemies:
            return -1 # No living enemies
        
        lowest_hp = float('inf')
        lowest_hp_pos = -1
        for i, fish in enumerate(game.enemy_fish):
            if not fish.is_dead() and fish.hp < lowest_hp:
                lowest_hp = fish.hp
                lowest_hp_pos = i
        return lowest_hp_pos

    def get_my_atk(self, game: Game, pos: int) -> int:
        """Returns the attack value of a specific player's fish."""
        fish = game.get_my_fish_by_pos(pos)
        return fish.atk if fish else 0

    def get_enemy_hp(self, game: Game, pos: int) -> int:
        """Returns the current HP of a specific enemy fish."""
        fish = game.get_enemy_fish_by_pos(pos)
        return fish.hp if fish else 0

    def get_enemy_id(self, game: Game, fish_pos: int) -> int:
        """Returns the ID (FishType value) of a specific enemy fish."""
        fish = game.get_enemy_fish_by_pos(fish_pos)
        return fish.fish_type.value if fish else -1

    def get_my_id(self, game: Game, fish_pos: int) -> int:
        """Returns the ID (FishType value) of a specific player's fish."""
        fish = game.get_my_fish_by_pos(fish_pos)
        return fish.fish_type.value if fish else -1

    def auto_valid_action(self, game: Game, my_pos: int, action: Action) -> Action:
        """
        Adjusts the action to be valid given the current game state.
        This is a placeholder and would contain complex game-specific validation logic.
        """
        # For example, if target is dead, re-target to another living enemy
        if action._enemy_target != -1 and game.get_enemy_fish_by_pos(action._enemy_target) and \
           game.get_enemy_fish_by_pos(action._enemy_target).is_dead():
            living_enemies_pos = self.get_enemy_living_fishes(game)
            if living_enemies_pos:
                action.set_enemy_target(random.choice(living_enemies_pos))
            else:
                action.set_enemy_target(-1) # No valid target

        # Ensure action fish is alive
        if game.get_my_fish_by_pos(my_pos) and game.get_my_fish_by_pos(my_pos).is_dead():
            # If the selected action fish is dead, try to find another living fish
            living_my_fishes = self.get_my_living_fishes(game)
            if living_my_fishes:
                action.set_action_fish(random.choice(living_my_fishes))
            else:
                action.set_action_fish(-1) # No valid fish to act

        return action

class GameStrategyAI:
    def __init__(self, stage: int) -> None:
        self.stage = stage
        self.guessed: List[List[FishType]] = [[], [], [], []] # Store guessed FishTypes
        self.last_fish_pos = -1
        self.last_fish_type = FishType.spray # Using enum
        
        self.name_to_id: Dict[str, FishType] = {
            "spray": FishType.spray, "flame": FishType.flame, "eel": FishType.eel, 
            "sunfish": FishType.sunfish, "barracuda": FishType.barracuda, "mobula": FishType.mobula, 
            "octopus": FishType.octopus, "whiteshark": FishType.whiteshark, "hammerhead": FishType.hammerhead
        }
        self.id_to_name: Dict[FishType, str] = {v: k for k, v in self.name_to_id.items()}
        
        # Skill types mapping to string representation
        self.skill_type_str: Dict[ActiveSkill, str] = {
            ActiveSkill.aoe: 'AOE', ActiveSkill.infight: 'Infight', 
            ActiveSkill.crit: 'Crit', ActiveSkill.subtle: 'Subtle', 
            ActiveSkill.normalattack: 'Normal'
        }
        self.passive_type_str: Dict[PassiveSkill, str] = {
            PassiveSkill.counter: 'Counter', PassiveSkill.deflect: 'Deflect', 
            PassiveSkill.reduce: 'Reduce', PassiveSkill.heal: 'Heal', 
            PassiveSkill.explode: 'Explode'
        }
        self.clue = {
            FishType.spray: ["AOE", "Counter"], FishType.flame: ["Infight", "Counter"], 
            FishType.eel: ["AOE", "Deflect"], FishType.sunfish: ["Infight", "Deflect"], 
            FishType.barracuda: ["Crit", "Reduce"], FishType.mobula: ["Subtle", "Reduce"], 
            FishType.octopus: ["Subtle", "Heal"], FishType.whiteshark: ["Crit", "Heal"],
            FishType.hammerhead: ["Crit", "Explode"]
        }
        logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

        self.ai_fish_types: List[FishType] = [] # To store types of AI's fish if needed
        random.seed(42)

    def Pick(self, game: Game, game_service: GameService) -> List[FishType]:
        """
        Picks the fish types for the current game based on game stage or other factors.
        For now, returns a dummy list.
        """
        pick_list: List[FishType] = []     
        
        # In a real scenario, this would involve strategy based on game context
        # For example, if stage == 1, pick a default set of fish types.
        # This implementation is a placeholder, returning known types.
        enemy_fish_types_to_pick = [FishType.spray, FishType.flame, FishType.eel, FishType.sunfish] 

        for fish_type in enemy_fish_types_to_pick:
            pick_list.append(fish_type)
        
        # random.shuffle(pick_list) # If order doesn't matter
        return pick_list
    
    def add_possible(self, fish_pos: int, fish_type: FishType):
        if fish_pos >= 0 and fish_pos < len(self.guessed):
            if fish_type not in self.guessed[fish_pos]:
                self.guessed[fish_pos].append(fish_type)

    def ass(self, fish_pos: int, fish_type: FishType) -> Tuple[int, FishType]:
        self.last_fish_pos = fish_pos
        self.last_fish_type = fish_type
        return (fish_pos, fish_type)
    
    def Assert(self, game: Game, game_service: GameService) -> Tuple[int, FishType]:
        """
        Asserts the type of an enemy fish based on observed actions and clues.
        """
        if self.stage == 1:
            return (-1, FishType.spray) # No assertion in stage 1

        enemy_action = game.enemy_action
        my_action = game.my_action
            
        live_enemy_positions = game_service.get_enemy_living_fishes(game)
        live_enemy_positions.sort()
        
        # If enemy_action.action_fish is unknown (-1 means unknown or not set)
        if game.get_enemy_fish_by_pos(enemy_action.action_fish) is None:
            if enemy_action.is_skill:
                # Add clue based on active skill type
                # Assuming enemy_action.active_skill_type correctly maps to clue strings
                self.add_possible(enemy_action.action_fish, enemy_action.active_skill_type) # Need to map enum to string clues

            # Process passive skills clues
            for passive_id_val, fish_type_val in zip(enemy_action.friend_passives_id + my_action.enemy_passives_id, 
                                                     enemy_action.friend_types + my_action.enemy_types):
                # Assuming passive_id_val is FishType and fish_type_val is PassiveSkill enum value
                # This part needs careful mapping from enum to string clues.
                # For example: self.add_possible(passive_id_val, self.passive_type_str[PassiveSkill(fish_type_val)])
                pass
        
        # Check if any fish's type can be definitively guessed
        for i in range(len(game.enemy_fish)):
            for fish_type_enum in FishType:
                if fish_type_enum != FishType.spray: # Exclude a default or unknown if it exists
                    clues_for_type = self.clue.get(fish_type_enum, [])
                    # Check if all collected guessed clues match for this fish_type_enum
                    if all(clue_str in [self.skill_type_str.get(sk) for sk in game.enemy_fish[i].active_skill] + 
                                       [self.passive_type_str.get(ps) for ps in game.enemy_fish[i].passive_skill]
                           for clue_str in clues_for_type): # Simplified check for now
                        if game.get_enemy_fish_by_pos(i) and game.get_enemy_fish_by_pos(i).fish_type.value == -1: # If type is unknown
                            return self.ass(i, fish_type_enum)
        
        # Fallback to random assertion if no definitive guess
        known_positions = []
        known_types = list(self.name_to_id.values())
        
        for i in range(len(game.enemy_fish)):
            if game.get_enemy_fish_by_pos(i) and game.get_enemy_fish_by_pos(i).fish_type.value == -1: # If fish type is unknown
                known_positions.append(i)
            # Remove types that are already identified from known_types (not implemented here)
        
        if not known_positions:
            return (-1, FishType.spray) # Cannot assert
        else:
            return self.ass(random.choice(known_positions), random.choice(known_types))
        
    def get_fish_type_from_pos(self, game: Game, fish_pos: int) -> FishType:
        fish = game.get_my_fish_by_pos(fish_pos)
        return fish.get_type() if fish else FishType.spray
    
    def get_specific_fish_pos_by_type(self, game: Game, my_alive_positions: List[int], desired_types: List[FishType]) -> int:
        for desired_type in desired_types:
            for fish_pos in my_alive_positions:
                if self.get_fish_type_from_pos(game, fish_pos) == desired_type:
                    return fish_pos
        return -1
    
    # Estratégia: Selecionar Ação
    def Act(self, game: Game, game_service: GameService) -> Action:
        action = Action(game)
        
        my_alive_positions = game_service.get_my_living_fishes(game)
        enemy_alive_positions = game_service.get_enemy_living_fishes(game)
        
        # If no living fish to act or no enemies to target
        if not my_alive_positions or not enemy_alive_positions:
            logging.warning("No living fish to act or no enemies to target. Returning default action.")
            return action

        # Find fish with max attack
        max_atk_pos = -1
        max_atk = 0
        for my_pos in my_alive_positions:
            current_atk = game_service.get_my_atk(game, my_pos)
            if max_atk < current_atk:
                max_atk = current_atk
                max_atk_pos = my_pos
            
        lowest_hp_enemy_pos = game_service.get_lowest_health_enemy(game)
        
        # Decision logic based on strategy:
        # 1. If a normal attack can finish the lowest HP enemy
        if max_atk_pos != -1 and lowest_hp_enemy_pos != -1:
            my_fish_atk = game_service.get_my_atk(game, max_atk_pos)
            enemy_fish_hp = game_service.get_enemy_hp(game, lowest_hp_enemy_pos)
            
            if my_fish_atk * 0.5 >= enemy_fish_hp: # Assuming some damage calculation
                action.set_action_fish(max_atk_pos)
                action.set_action_type(ActiveSkill.normalattack)
                action.set_enemy_target(lowest_hp_enemy_pos)
                return game_service.auto_valid_action(game, max_atk_pos, action)
            
        # 2. Use AOE skill if multiple enemies are alive
        if len(enemy_alive_positions) >= 2:
            aoe_fish_pos = self.get_specific_fish_pos_by_type(game, my_alive_positions, [FishType.spray, FishType.eel])
            if aoe_fish_pos != -1:
                action.set_action_fish(aoe_fish_pos)
                action.set_action_type(ActiveSkill.aoe)
                action.set_enemy_target_list(enemy_alive_positions) 
                return game_service.auto_valid_action(game, aoe_fish_pos, action)
        
        # 3. Use critical/burst skill on lowest HP enemy
        crit_fish_pos = self.get_specific_fish_pos_by_type(game, my_alive_positions, [FishType.barracuda, FishType.whiteshark, FishType.hammerhead])
        if crit_fish_pos != -1 and lowest_hp_enemy_pos != -1:
            action.set_action_fish(crit_fish_pos)
            action.set_action_type(ActiveSkill.crit) # Assuming crit skill type
            action.set_enemy_target(lowest_hp_enemy_pos)    
            return game_service.auto_valid_action(game, crit_fish_pos, action)
        
        # 4. Fallback to normal attack with max_atk_pos
        if max_atk_pos != -1:
            action.set_action_fish(max_atk_pos)
            action.set_action_type(ActiveSkill.normalattack)
            
            # Target enemy action fish if it's alive, otherwise target lowest HP enemy
            target_pos_for_normal_attack = lowest_hp_enemy_pos
            if game.enemy_action.action_fish != -1 and game.get_enemy_fish_by_pos(game.enemy_action.action_fish) and \
               not game.get_enemy_fish_by_pos(game.enemy_action.action_fish).is_dead():
                target_pos_for_normal_attack = game.enemy_action.action_fish
            
            if target_pos_for_normal_attack != -1:
                action.set_enemy_target(target_pos_for_normal_attack)
            else:
                # If no specific target, pick first alive enemy
                if enemy_alive_positions:
                    action.set_enemy_target(enemy_alive_positions[0])
                else:
                    logging.warning("Act: No valid enemy target found for normal attack.")
                    return action # Cannot perform action if no target
            
            return game_service.auto_valid_action(game, max_atk_pos, action)
        
        logging.warning("Act: No valid action could be determined. Returning default (empty) action.")
        return action
