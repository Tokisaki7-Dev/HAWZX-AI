# combat_system.py - Sistema de combate em turnos estilo JRPG
import random
from dataclasses import dataclass
from typing import List, Dict, Tuple

@dataclass
class Enemy:
    name: str
    level: int
    hp: int
    max_hp: int
    mp: int
    max_mp: int
    attack: int
    defense: int
    magic: int
    speed: int
    exp_reward: int
    gold_reward: int
    item_drop: str
    sprite_color: Tuple[int, int, int]
    skills: List[Dict]

@dataclass
class Item:
    name: str
    type: str  # 'consumable', 'weapon', 'armor', 'key_item'
    effect: str
    value: int
    description: str
    icon_color: Tuple[int, int, int]

@dataclass
class PlayerStats:
    level: int
    exp: int
    exp_to_next: int
    hp: int
    max_hp: int
    mp: int
    max_mp: int
    attack: int
    defense: int
    magic: int
    speed: int
    gold: int

class CombatSystem:
    """Sistema de combate procedural em turnos"""
    
    # Prefixos e sufixos para nomes de inimigos
    ENEMY_PREFIXES = ['Shadow', 'Fire', 'Ice', 'Thunder', 'Poison', 'Dark', 
                      'Ancient', 'Wild', 'Cursed', 'Mad', 'Feral']
    
    ENEMY_TYPES = {
        'forest': ['Wolf', 'Bear', 'Treant', 'Sprite', 'Deer', 'Boar'],
        'desert': ['Scorpion', 'Snake', 'Vulture', 'Golem', 'Mummy', 'Djinn'],
        'mountain': ['Yeti', 'Eagle', 'Goat', 'Dragon', 'Harpy', 'Wyvern'],
        'cave': ['Bat', 'Spider', 'Slime', 'Ghost', 'Skeleton', 'Wraith']
    }
    
    # Cores de sprites por tipo
    ENEMY_COLORS = {
        'forest': [(34, 139, 34), (107, 142, 35), (46, 125, 50)],
        'desert': [(210, 180, 140), (244, 164, 96), (188, 143, 143)],
        'mountain': [(176, 196, 222), (119, 136, 153), (112, 128, 144)],
        'cave': [(75, 0, 130), (72, 61, 139), (106, 90, 205)]
    }
    
    def __init__(self, seed: int):
        self.seed = seed
        random.seed(seed)
    
    def generate_enemy(self, biome: str, player_level: int) -> Enemy:
        """Gera inimigo procedural baseado no bioma e nível do jogador"""
        
        # Nome procedural
        prefix = random.choice(self.ENEMY_PREFIXES)
        base_type = random.choice(self.ENEMY_TYPES.get(biome, self.ENEMY_TYPES['forest']))
        name = f"{prefix} {base_type}"
        
        # Nível próximo ao do jogador (±2 níveis)
        level = max(1, player_level + random.randint(-2, 2))
        
        # Stats baseados no nível
        max_hp = 20 + (level * 10) + random.randint(-5, 5)
        max_mp = 10 + (level * 5) + random.randint(-3, 3)
        attack = 5 + (level * 2) + random.randint(-1, 2)
        defense = 3 + (level * 1) + random.randint(-1, 1)
        magic = 4 + (level * 2) + random.randint(-1, 2)
        speed = 5 + random.randint(-2, 3)
        
        # Recompensas
        exp_reward = 10 + (level * 5)
        gold_reward = 5 + (level * 3) + random.randint(0, 10)
        
        # Drop de item
        item_drop = self._generate_item_drop(biome, level)
        
        # Cor do sprite
        color = random.choice(self.ENEMY_COLORS.get(biome, self.ENEMY_COLORS['forest']))
        
        # Skills do inimigo
        skills = self._generate_enemy_skills(biome, level)
        
        return Enemy(
            name=name,
            level=level,
            hp=max_hp,
            max_hp=max_hp,
            mp=max_mp,
            max_mp=max_mp,
            attack=attack,
            defense=defense,
            magic=magic,
            speed=speed,
            exp_reward=exp_reward,
            gold_reward=gold_reward,
            item_drop=item_drop,
            sprite_color=color,
            skills=skills
        )
    
    def _generate_item_drop(self, biome: str, level: int) -> str:
        """Gera item que o inimigo pode dropar"""
        drops = {
            'forest': ['Herb', 'Leaf', 'Berry', 'Feather', 'Wood'],
            'desert': ['Crystal', 'Sand Vial', 'Scale', 'Gem', 'Fossil'],
            'mountain': ['Ice Shard', 'Rock', 'Ore', 'Fur', 'Claw'],
            'cave': ['Mushroom', 'Bone', 'Ectoplasm', 'Rune', 'Gem']
        }
        
        base_item = random.choice(drops.get(biome, drops['forest']))
        
        if level > 5:
            return f"Rare {base_item}"
        return base_item
    
    def _generate_enemy_skills(self, biome: str, level: int) -> List[Dict]:
        """Gera habilidades do inimigo"""
        skills = [
            {'name': 'Attack', 'mp_cost': 0, 'power': 1.0, 'type': 'physical'}
        ]
        
        # Skills por bioma
        biome_skills = {
            'forest': [
                {'name': 'Vine Whip', 'mp_cost': 5, 'power': 1.3, 'type': 'magic'},
                {'name': 'Poison Spore', 'mp_cost': 8, 'power': 1.2, 'type': 'magic', 'effect': 'poison'}
            ],
            'desert': [
                {'name': 'Sand Storm', 'mp_cost': 7, 'power': 1.4, 'type': 'magic'},
                {'name': 'Heat Wave', 'mp_cost': 6, 'power': 1.3, 'type': 'magic'}
            ],
            'mountain': [
                {'name': 'Ice Shard', 'mp_cost': 6, 'power': 1.4, 'type': 'magic'},
                {'name': 'Avalanche', 'mp_cost': 10, 'power': 1.8, 'type': 'magic'}
            ],
            'cave': [
                {'name': 'Shadow Bolt', 'mp_cost': 7, 'power': 1.5, 'type': 'magic'},
                {'name': 'Curse', 'mp_cost': 9, 'power': 1.3, 'type': 'magic', 'effect': 'curse'}
            ]
        }
        
        # Adiciona 1-2 skills baseadas no nível
        if level >= 3:
            available_skills = biome_skills.get(biome, biome_skills['forest'])
            skills.append(random.choice(available_skills))
        
        if level >= 6:
            available_skills = biome_skills.get(biome, biome_skills['forest'])
            skills.append(random.choice(available_skills))
        
        return skills
    
    def calculate_damage(self, attacker_stats: Dict, defender_stats: Dict, 
                        skill: Dict, is_critical: bool = False) -> int:
        """Calcula dano de um ataque"""
        
        base_damage = 0
        
        if skill['type'] == 'physical':
            base_damage = attacker_stats['attack'] - (defender_stats['defense'] // 2)
        else:  # magic
            base_damage = attacker_stats['magic'] - (defender_stats['defense'] // 4)
        
        # Multiplica pelo poder da skill
        base_damage = int(base_damage * skill['power'])
        
        # Adiciona variação aleatória (±15%)
        variation = random.uniform(0.85, 1.15)
        base_damage = int(base_damage * variation)
        
        # Crítico (x2)
        if is_critical:
            base_damage *= 2
        
        return max(1, base_damage)  # Mínimo 1 de dano
    
    def check_critical(self, attacker_speed: int, defender_speed: int) -> bool:
        """Verifica se ataque é crítico baseado em velocidade"""
        speed_diff = attacker_speed - defender_speed
        crit_chance = 0.05 + (speed_diff * 0.01)  # 5% base + diferença de velocidade
        crit_chance = max(0.05, min(0.30, crit_chance))  # Entre 5% e 30%
        
        return random.random() < crit_chance


class ItemSystem:
    """Sistema de itens e inventário"""
    
    ITEM_DATABASE = {
        # Consumíveis
        'Potion': Item('Potion', 'consumable', 'heal', 50, 'Restaura 50 HP', (255, 0, 0)),
        'Hi-Potion': Item('Hi-Potion', 'consumable', 'heal', 150, 'Restaura 150 HP', (255, 100, 100)),
        'Mega Potion': Item('Mega Potion', 'consumable', 'heal', 300, 'Restaura 300 HP', (255, 150, 150)),
        'Ether': Item('Ether', 'consumable', 'mp_restore', 30, 'Restaura 30 MP', (0, 0, 255)),
        'Elixir': Item('Elixir', 'consumable', 'full_restore', 0, 'Restaura HP e MP completos', (255, 215, 0)),
        'Antidote': Item('Antidote', 'consumable', 'cure_poison', 0, 'Cura envenenamento', (76, 175, 80)),
        
        # Armas
        'Iron Sword': Item('Iron Sword', 'weapon', 'attack', 10, '+10 Ataque', (192, 192, 192)),
        'Steel Sword': Item('Steel Sword', 'weapon', 'attack', 20, '+20 Ataque', (169, 169, 169)),
        'Mythril Sword': Item('Mythril Sword', 'weapon', 'attack', 35, '+35 Ataque', (176, 224, 230)),
        'Fire Staff': Item('Fire Staff', 'weapon', 'magic', 15, '+15 Magia', (255, 69, 0)),
        'Ice Staff': Item('Ice Staff', 'weapon', 'magic', 15, '+15 Magia', (135, 206, 250)),
        
        # Armaduras
        'Leather Armor': Item('Leather Armor', 'armor', 'defense', 5, '+5 Defesa', (139, 69, 19)),
        'Chain Mail': Item('Chain Mail', 'armor', 'defense', 12, '+12 Defesa', (192, 192, 192)),
        'Plate Armor': Item('Plate Armor', 'armor', 'defense', 25, '+25 Defesa', (105, 105, 105)),
        
        # Itens chave
        'Forest Key': Item('Forest Key', 'key_item', 'unlock', 0, 'Abre portões da floresta', (34, 139, 34)),
        'Desert Compass': Item('Desert Compass', 'key_item', 'navigation', 0, 'Revela caminhos no deserto', (244, 164, 96)),
        'Mountain Pick': Item('Mountain Pick', 'key_item', 'mining', 0, 'Permite quebrar rochas', (128, 128, 128)),
        'Cave Torch': Item('Cave Torch', 'key_item', 'light', 0, 'Ilumina cavernas escuras', (255, 140, 0))
    }
    
    @staticmethod
    def get_item(item_name: str) -> Item:
        """Retorna item do banco de dados"""
        return ItemSystem.ITEM_DATABASE.get(item_name)
    
    @staticmethod
    def get_starter_items() -> List[str]:
        """Retorna itens iniciais do jogador"""
        return ['Potion', 'Potion', 'Potion', 'Iron Sword', 'Leather Armor']


class LevelSystem:
    """Sistema de experiência e níveis"""
    
    @staticmethod
    def calculate_exp_to_next_level(level: int) -> int:
        """Calcula EXP necessária para próximo nível"""
        # Fórmula: 100 * (level^1.5)
        return int(100 * (level ** 1.5))
    
    @staticmethod
    def calculate_level_up_stats(current_stats: PlayerStats) -> PlayerStats:
        """Calcula novos stats ao subir de nível"""
        new_stats = PlayerStats(
            level=current_stats.level + 1,
            exp=0,
            exp_to_next=LevelSystem.calculate_exp_to_next_level(current_stats.level + 1),
            hp=current_stats.hp,
            max_hp=current_stats.max_hp + random.randint(8, 15),
            mp=current_stats.mp,
            max_mp=current_stats.max_mp + random.randint(5, 10),
            attack=current_stats.attack + random.randint(2, 4),
            defense=current_stats.defense + random.randint(1, 3),
            magic=current_stats.magic + random.randint(2, 4),
            speed=current_stats.speed + random.randint(0, 2),
            gold=current_stats.gold
        )
        
        # HP e MP recuperados ao subir de nível
        new_stats.hp = new_stats.max_hp
        new_stats.mp = new_stats.max_mp
        
        return new_stats
    
    @staticmethod
    def add_exp(current_stats: PlayerStats, exp_gained: int) -> Tuple[PlayerStats, bool]:
        """Adiciona EXP e verifica level up"""
        current_stats.exp += exp_gained
        leveled_up = False
        
        while current_stats.exp >= current_stats.exp_to_next:
            current_stats.exp -= current_stats.exp_to_next
            current_stats = LevelSystem.calculate_level_up_stats(current_stats)
            leveled_up = True
        
        return current_stats, leveled_up


def create_initial_player_stats() -> PlayerStats:
    """Cria stats iniciais do jogador"""
    return PlayerStats(
        level=1,
        exp=0,
        exp_to_next=LevelSystem.calculate_exp_to_next_level(1),
        hp=100,
        max_hp=100,
        mp=50,
        max_mp=50,
        attack=10,
        defense=5,
        magic=8,
        speed=7,
        gold=100
    )
