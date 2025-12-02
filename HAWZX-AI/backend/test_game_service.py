import pytest
from unittest.mock import MagicMock, patch
from backend.game_service import (
    Fish, Game, Action, GameService, GameStrategyAI, 
    FishType, ActiveSkill, PassiveSkill, ActionInfo, AssertInfo
)

# --- Testes para a Classe Fish ---
def test_fish_initialization():
    fish = Fish(id=1, hp=100, atk=10, is_expose=False, fish_type=FishType.spray)
    assert fish.id == 1
    assert fish.hp == 100
    assert fish.atk == 10
    assert fish.is_expose == False
    assert fish.fish_type == FishType.spray
    assert fish.state == "ALIVE"
    assert fish.max_hp == 100

def test_fish_is_dead():
    alive_fish = Fish(id=1, hp=100, atk=10)
    assert not alive_fish.is_dead()

    dead_fish_hp = Fish(id=2, hp=0, atk=10)
    assert dead_fish_hp.is_dead()

    dead_fish_state = Fish(id=3, hp=50, atk=10)
    dead_fish_state.state = "DEAD"
    assert dead_fish_state.is_dead()

def test_fish_get_type():
    fish = Fish(id=1, hp=100, atk=10, fish_type=FishType.eel)
    assert fish.get_type() == FishType.eel

# --- Testes para a Classe Game ---
def test_game_initialization():
    game = Game()
    assert isinstance(game.my_fish, list)
    assert isinstance(game.enemy_fish, list)
    assert game.avatar_id == -1
    assert isinstance(game.enemy_action, ActionInfo)
    assert isinstance(game.my_action, ActionInfo)

def test_game_get_my_living_fishes():
    game = Game()
    fish1 = Fish(id=1, hp=100, atk=10)
    fish2 = Fish(id=2, hp=0, atk=10) # Dead
    fish3 = Fish(id=3, hp=50, atk=10)
    game.my_fish = [fish1, fish2, fish3]
    
    living_fishes = game.get_my_living_fishes()
    assert len(living_fishes) == 2
    assert fish1 in living_fishes
    assert fish3 in living_fishes
    assert fish2 not in living_fishes

def test_game_get_enemy_living_fishes():
    game = Game()
    fish1 = Fish(id=1, hp=100, atk=10)
    fish2 = Fish(id=2, hp=0, atk=10) # Dead
    game.enemy_fish = [fish1, fish2]
    
    living_fishes = game.get_enemy_living_fishes()
    assert len(living_fishes) == 1
    assert fish1 in living_fishes
    assert fish2 not in living_fishes

def test_game_get_my_fish_by_pos():
    game = Game()
    fish1 = Fish(id=1, hp=100, atk=10)
    game.my_fish = [fish1]
    assert game.get_my_fish_by_pos(0) == fish1
    assert game.get_my_fish_by_pos(99) is None

def test_game_get_enemy_fish_by_pos():
    game = Game()
    fish1 = Fish(id=1, hp=100, atk=10)
    game.enemy_fish = [fish1]
    assert game.get_enemy_fish_by_pos(0) == fish1
    assert game.get_enemy_fish_by_pos(99) is None

# --- Testes para a Classe Action ---
def test_action_initialization():
    game = Game()
    action = Action(game)
    assert action._game == game
    assert action._action_fish == -1
    assert action._action_type == ActiveSkill.normalattack

def test_action_setters():
    game = Game()
    action = Action(game)
    action.set_action_fish(0)
    action.set_action_type(ActiveSkill.aoe)
    action.set_enemy_target(1)
    action.set_my_target_list([0, 2])
    action.set_enemy_target_list([1, 3])

    assert action._action_fish == 0
    assert action._action_type == ActiveSkill.aoe
    assert action._enemy_target == 1
    assert action._my_target_list == [0, 2]
    assert action._enemy_target_list == [1, 3]

def test_action_to_action_info():
    game = Game()
    action = Action(game)
    action.set_action_fish(0)
    action.set_action_type(ActiveSkill.crit)
    action.set_enemy_target(1)

    action_info = action.to_action_info()
    assert action_info.action_fish == 0
    assert action_info.is_skill == True
    assert action_info.active_skill_type == ActiveSkill.crit
    assert action_info.target_fish == 1

# --- Testes para GameService Helper Methods ---
@pytest.fixture
def populated_game():
    game = Game()
    game.my_fish = [
        Fish(id=1, hp=100, atk=20, fish_type=FishType.spray),
        Fish(id=2, hp=0, atk=15, fish_type=FishType.eel), # Dead
        Fish(id=3, hp=80, atk=25, fish_type=FishType.barracuda)
    ]
    game.enemy_fish = [
        Fish(id=10, hp=60, atk=12, fish_type=FishType.flame),
        Fish(id=11, hp=20, atk=8, fish_type=FishType.sunfish),
        Fish(id=12, hp=0, atk=10, fish_type=FishType.octopus) # Dead
    ]
    return game

@pytest.fixture
def game_service():
    return GameService()

def test_gameservice_get_my_living_fishes(game_service, populated_game):
    living_fishes_pos = game_service.get_my_living_fishes(populated_game)
    assert living_fishes_pos == [0, 2]

def test_gameservice_get_enemy_living_fishes(game_service, populated_game):
    living_fishes_pos = game_service.get_enemy_living_fishes(populated_game)
    assert living_fishes_pos == [0, 1]

def test_gameservice_get_lowest_health_enemy(game_service, populated_game):
    lowest_hp_pos = game_service.get_lowest_health_enemy(populated_game)
    assert lowest_hp_pos == 1 # Fish at pos 1 has 20 HP

def test_gameservice_get_my_atk(game_service, populated_game):
    assert game_service.get_my_atk(populated_game, 0) == 20
    assert game_service.get_my_atk(populated_game, 1) == 15 # Even if dead, atk value is there
    assert game_service.get_my_atk(populated_game, 99) == 0

def test_gameservice_get_enemy_hp(game_service, populated_game):
    assert game_service.get_enemy_hp(populated_game, 0) == 60
    assert game_service.get_enemy_hp(populated_game, 2) == 0 # Dead
    assert game_service.get_enemy_hp(populated_game, 99) == 0

def test_gameservice_get_enemy_id(game_service, populated_game):
    assert game_service.get_enemy_id(populated_game, 0) == FishType.flame.value
    assert game_service.get_enemy_id(populated_game, 99) == -1

def test_gameservice_get_my_id(game_service, populated_game):
    assert game_service.get_my_id(populated_game, 0) == FishType.spray.value
    assert game_service.get_my_id(populated_game, 99) == -1

def test_gameservice_auto_valid_action_retarget_dead_enemy(game_service, populated_game):
    action = Action(populated_game)
    action.set_action_fish(0)
    action.set_action_type(ActiveSkill.normalattack)
    action.set_enemy_target(2) # Target a dead fish

    # Mock random.choice to return a predictable valid target
    with patch('random.choice', return_value=0) as mock_choice:
        valid_action = game_service.auto_valid_action(populated_game, 0, action)
        assert valid_action._enemy_target == 0 # Should retarget to position 0
        mock_choice.assert_called_once()

def test_gameservice_auto_valid_action_action_fish_dead(game_service, populated_game):
    action = Action(populated_game)
    action.set_action_fish(1) # Action fish is dead
    action.set_action_type(ActiveSkill.normalattack)
    action.set_enemy_target(0)

    with patch('random.choice', return_value=0) as mock_choice:
        valid_action = game_service.auto_valid_action(populated_game, 1, action)
        assert valid_action._action_fish == 0 # Should pick another living fish
        mock_choice.assert_called_once()

def test_gameservice_auto_valid_action_no_valid_enemy_target(game_service):
    game = Game()
    game.my_fish = [Fish(id=1, hp=100, atk=10)]
    game.enemy_fish = [Fish(id=10, hp=0, atk=5)] # All enemies dead

    action = Action(game)
    action.set_action_fish(0)
    action.set_action_type(ActiveSkill.normalattack)
    action.set_enemy_target(0)

    valid_action = game_service.auto_valid_action(game, 0, action)
    assert valid_action._enemy_target == -1 # Should be -1 as no living enemies

# --- Testes para GameStrategyAI ---
@pytest.fixture
def game_strategy_ai():
    return GameStrategyAI(stage=1)

def test_gamestrategyai_pick_stage_1(game_strategy_ai, populated_game, game_service):
    # For stage 1, Pick should return the dummy list
    picked_types = game_strategy_ai.Pick(populated_game, game_service)
    expected_types = [FishType.spray, FishType.flame, FishType.eel, FishType.sunfish]
    assert picked_types == expected_types

def test_gamestrategyai_assert_stage_1(game_strategy_ai, populated_game, game_service):
    # Assert should return (-1, FishType.spray) for stage 1
    fish_pos, fish_type = game_strategy_ai.Assert(populated_game, game_service)
    assert fish_pos == -1
    assert fish_type == FishType.spray

def test_gamestrategyai_get_fish_type_from_pos(game_strategy_ai, populated_game):
    assert game_strategy_ai.get_fish_type_from_pos(populated_game, 0) == FishType.spray
    assert game_strategy_ai.get_fish_type_from_pos(populated_game, 1) == FishType.eel
    assert game_strategy_ai.get_fish_type_from_pos(populated_game, 99) == FishType.spray # Default for invalid pos

def test_gamestrategyai_get_specific_fish_pos_by_type(game_strategy_ai, populated_game):
    my_alive_positions = [0, 2] # spray, barracuda
    
    # Test for existing type
    pos = game_strategy_ai.get_specific_fish_pos_by_type(populated_game, my_alive_positions, [FishType.barracuda])
    assert pos == 2

    # Test for non-existing type
    pos = game_strategy_ai.get_specific_fish_pos_by_type(populated_game, my_alive_positions, [FishType.octopus])
    assert pos == -1

    # Test for multiple types, first match
    pos = game_strategy_ai.get_specific_fish_pos_by_type(populated_game, my_alive_positions, [FishType.eel, FishType.spray])
    assert pos == 0

# Test Act method
def test_gamestrategyai_act_normal_attack_finisher(game_strategy_ai, populated_game, game_service):
    # Setup scenario where normal attack can finish an enemy
    populated_game.my_fish[0].atk = 100 # Spray fish has high attack
    populated_game.enemy_fish[1].hp = 10 # Sunfish has low HP
    
    action = game_strategy_ai.Act(populated_game, game_service)
    assert action._action_fish == 0
    assert action._action_type == ActiveSkill.normalattack
    assert action._enemy_target == 1 # Target lowest HP enemy (Sunfish)

def test_gamestrategyai_act_aoe_skill(game_strategy_ai, populated_game, game_service):
    # Setup scenario for AOE skill
    populated_game.my_fish[0].fish_type = FishType.spray # Ensure fish at pos 0 is spray (AOE)
    populated_game.enemy_fish.append(Fish(id=13, hp=30, atk=5, fish_type=FishType.mobula)) # Add another enemy
    
    action = game_strategy_ai.Act(populated_game, game_service)
    assert action._action_fish == 0 # Spray fish
    assert action._action_type == ActiveSkill.aoe
    assert action._enemy_target_list == [0, 1, 3] # All living enemies

def test_gamestrategyai_act_crit_skill(game_strategy_ai, populated_game, game_service):
    # Setup scenario for Crit skill
    populated_game.my_fish[2].fish_type = FishType.barracuda # Ensure fish at pos 2 is barracuda (Crit)
    populated_game.enemy_fish[1].hp = 50 # Increase sunfish HP so it's not a finisher
    
    action = game_strategy_ai.Act(populated_game, game_service)
    assert action._action_fish == 2 # Barracuda fish
    assert action._action_type == ActiveSkill.crit
    assert action._enemy_target == 1 # Target lowest HP enemy (Sunfish)

def test_gamestrategyai_act_fallback_normal_attack(game_strategy_ai, populated_game, game_service):
    # Scenario where no special conditions are met, fallback to max_atk_pos normal attack
    # Ensure no finishers, no AOE conditions, no crit conditions easily met
    populated_game.my_fish[0].atk = 20 # Reset atk
    populated_game.my_fish[0].fish_type = FishType.sunfish # Not AOE
    populated_game.my_fish[2].fish_type = FishType.eel # Not Crit
    populated_game.enemy_fish[1].hp = 50 # Not finisher for any

    action = game_strategy_ai.Act(populated_game, game_service)
    # Max atk fish is at pos 2 (barracuda originally, now eel with 25 atk)
    assert action._action_fish == 2 
    assert action._action_type == ActiveSkill.normalattack
    assert action._enemy_target == 1 # Still lowest HP enemy (sunfish)

def test_gamestrategyai_act_no_living_my_fish(game_strategy_ai, populated_game, game_service):
    populated_game.my_fish[0].hp = 0
    populated_game.my_fish[1].hp = 0
    populated_game.my_fish[2].hp = 0
    
    action = game_strategy_ai.Act(populated_game, game_service)
    # Should return a default action or handle gracefully
    assert action._action_fish == -1 

def test_gamestrategyai_act_no_living_enemy_fish(game_strategy_ai, populated_game, game_service):
    populated_game.enemy_fish[0].hp = 0
    populated_game.enemy_fish[1].hp = 0
    populated_game.enemy_fish[2].hp = 0

    action = game_strategy_ai.Act(populated_game, game_service)
    # Should return a default action or handle gracefully
    assert action._enemy_target == -1
