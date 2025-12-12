# game_generator.py - Sistema de geração procedural de jogos JRPG
import random
import noise
from PIL import Image, ImageDraw, ImageFont
from dataclasses import dataclass
from typing import List, Dict, Tuple

@dataclass
class NPC:
    name: str
    x: int
    y: int
    dialogue: List[str]
    quest: Dict
    sprite_color: Tuple[int, int, int]

@dataclass
class Quest:
    title: str
    description: str
    objective: str
    reward: str

@dataclass
class GameWorld:
    name: str
    story: str
    biome: str
    npcs: List[NPC]
    quests: List[Quest]
    controls: Dict[str, str]
    special_mechanics: List[str]

class JRPGGenerator:
    """Gerador procedural de jogos completos estilo JRPG"""
    
    # Temas de histórias
    STORY_THEMES = {
        'hero_journey': [
            "Um jovem herói desperta em {biome} sem memórias do passado.",
            "Antigos cristais começam a brilhar pela primeira vez em mil anos.",
            "O equilíbrio entre luz e sombra está sendo rompido.",
            "Você é o escolhido para restaurar a paz nesta terra."
        ],
        'ancient_evil': [
            "Um mal ancestral foi selado em {biome} há milênios.",
            "Os selos estão enfraquecendo e criaturas das trevas emergem.",
            "Apenas o portador da {artifact} pode salvar este mundo.",
            "Você deve reunir os fragmentos do poder perdido."
        ],
        'time_travel': [
            "Um portal temporal se abriu em {biome}.",
            "Você foi transportado para uma era esquecida.",
            "Suas ações aqui mudarão o futuro para sempre.",
            "Encontre a forma de retornar à sua linha temporal."
        ],
        'rebellion': [
            "Um império tirânico domina {biome} com mão de ferro.",
            "Você lidera a resistência contra a opressão.",
            "Reúna aliados e fortaleça a rebelião.",
            "A liberdade está próxima, mas o caminho é perigoso."
        ]
    }
    
    # Nomes procedurais
    NAME_PREFIXES = ['Aer', 'Lun', 'Sol', 'Nox', 'Zeph', 'Cael', 'Thal', 'Eld']
    NAME_SUFFIXES = ['ion', 'ara', 'or', 'is', 'yn', 'eth', 'os', 'ia']
    
    ARTIFACTS = ['Espada do Tempo', 'Cristal Etéreo', 'Anel das Eras', 'Orbe Celestial', 
                 'Cajado da Luz', 'Amuleto Ancestral', 'Coroa dos Reis', 'Grimório Perdido']
    
    def __init__(self, seed: int):
        self.seed = seed
        random.seed(seed)
    
    def generate_name(self) -> str:
        """Gera nome procedural para NPCs e locais"""
        return random.choice(self.NAME_PREFIXES) + random.choice(self.NAME_SUFFIXES)
    
    def generate_story(self, biome: str) -> str:
        """Gera história procedural baseada no bioma"""
        theme = random.choice(list(self.STORY_THEMES.keys()))
        story_parts = self.STORY_THEMES[theme]
        
        artifact = random.choice(self.ARTIFACTS)
        
        story = "\n".join(story_parts)
        story = story.replace('{biome}', biome.capitalize())
        story = story.replace('{artifact}', artifact)
        
        return story
    
    def generate_quest(self, biome: str) -> Quest:
        """Gera quest procedural"""
        quest_types = {
            'collect': {
                'title': f'Coleta de {random.choice(["Cristais", "Ervas", "Fragmentos", "Relíquias"])}',
                'description': 'Um sábio local precisa de itens raros.',
                'objective': f'Colete {random.randint(3, 8)} itens especiais',
                'reward': f'{random.randint(50, 200)} moedas de ouro'
            },
            'escort': {
                'title': 'Proteção de Viajante',
                'description': 'Um mercador precisa atravessar território perigoso.',
                'objective': 'Escorte o NPC até o destino com segurança',
                'reward': f'{random.randint(100, 300)} moedas + item raro'
            },
            'defeat': {
                'title': f'Caça ao {random.choice(["Dragão", "Espectro", "Golem", "Demônio"])}',
                'description': 'Uma criatura ameaça a região.',
                'objective': f'Derrote o boss em {biome}',
                'reward': f'{random.randint(200, 500)} EXP + equipamento lendário'
            },
            'explore': {
                'title': 'Exploração Antiga',
                'description': f'Ruínas foram descobertas em {biome}.',
                'objective': 'Explore a dungeon e encontre o tesouro',
                'reward': 'Artefato mágico'
            }
        }
        
        quest_data = random.choice(list(quest_types.values()))
        return Quest(**quest_data)
    
    def generate_npcs(self, biome: str, num_npcs: int = 5) -> List[NPC]:
        """Gera NPCs procedurais com diálogos"""
        npcs = []
        
        # Cores de sprites por tipo de NPC
        npc_colors = {
            'warrior': (255, 59, 48),
            'mage': (88, 86, 214),
            'merchant': (255, 204, 0),
            'elder': (142, 142, 147),
            'healer': (52, 199, 89)
        }
        
        dialogue_templates = {
            'greeting': [
                f"Bem-vindo a {biome}, viajante!",
                "Há quanto tempo não vejo um aventureiro por aqui...",
                "Você parece ser forte. Precisamos de sua ajuda.",
                "Os tempos estão difíceis nestas terras."
            ],
            'quest': [
                "Tenho uma tarefa importante para você.",
                "Há algo que você pode fazer por mim?",
                "Se provar seu valor, tenho uma recompensa.",
                "Preciso de ajuda com algo urgente."
            ],
            'lore': [
                f"Dizem que {biome} foi criado pelos antigos deuses.",
                "Há uma profecia sobre um herói que surgirá.",
                "Os cristais de poder estão espalhados por este mundo.",
                "Cuidado com as sombras que espreitam à noite."
            ]
        }
        
        for i in range(num_npcs):
            npc_type = random.choice(list(npc_colors.keys()))
            name = self.generate_name()
            
            # Posição aleatória
            x = random.randint(64, 448)
            y = random.randint(64, 448)
            
            # Diálogo procedural
            dialogue = [
                random.choice(dialogue_templates['greeting']),
                random.choice(dialogue_templates['quest']),
                random.choice(dialogue_templates['lore'])
            ]
            
            # Quest associada
            quest = self.generate_quest(biome)
            
            npcs.append(NPC(
                name=name,
                x=x,
                y=y,
                dialogue=dialogue,
                quest=quest.__dict__,
                sprite_color=npc_colors[npc_type]
            ))
        
        return npcs
    
    def generate_controls(self, biome: str) -> Dict[str, str]:
        """Gera controles específicos para este jogo"""
        base_controls = {
            '↑↓←→': 'Movimento',
            'SPACE': 'Interagir/Confirmar',
            'E': 'Abrir Menu',
            'I': 'Inventário',
            'M': 'Mapa'
        }
        
        # Controles especiais por bioma
        special_controls = {
            'forest': {'F': 'Plantar Sementes'},
            'desert': {'D': 'Usar Bússola'},
            'mountain': {'C': 'Escalar'},
            'cave': {'L': 'Tocha (iluminar)'}
        }
        
        if biome in special_controls:
            base_controls.update(special_controls[biome])
        
        return base_controls
    
    def generate_mechanics(self, biome: str) -> List[str]:
        """Gera mecânicas especiais para este jogo"""
        all_mechanics = {
            'forest': [
                'Sistema de Clima Dinâmico (chuva faz plantas crescerem)',
                'Animais podem ser domados como companheiros',
                'Ciclo dia/noite afeta NPCs e inimigos'
            ],
            'desert': [
                'Tempestades de areia limitam visibilidade',
                'Oásis recuperam HP e MP',
                'Miragens podem enganar o jogador'
            ],
            'mountain': [
                'Escalada vertical em paredes rochosas',
                'Avalanches aleatórias criam novos caminhos',
                'Altitude afeta consumo de stamina'
            ],
            'cave': [
                'Sistema de luz (tocha tem duração limitada)',
                'Cristais mágicos concedem buffs temporários',
                'Ecos revelam salas secretas'
            ]
        }
        
        return all_mechanics.get(biome, ['Exploração livre', 'Combate em turnos', 'Sistema de experiência'])
    
    def generate_complete_world(self, biome: str) -> GameWorld:
        """Gera um mundo de jogo completo"""
        world_name = f"{self.generate_name()} - {biome.capitalize()} Realm"
        story = self.generate_story(biome)
        npcs = self.generate_npcs(biome)
        quests = [self.generate_quest(biome) for _ in range(3)]
        controls = self.generate_controls(biome)
        mechanics = self.generate_mechanics(biome)
        
        return GameWorld(
            name=world_name,
            story=story,
            biome=biome,
            npcs=npcs,
            quests=quests,
            controls=controls,
            special_mechanics=mechanics
        )


def generate_enhanced_terrain(biome: str, seed: int, width: int = 512, height: int = 512) -> Tuple[Image.Image, GameWorld]:
    """Gera terreno + metadados do jogo completo"""
    
    # Gera mundo procedural
    generator = JRPGGenerator(seed)
    world = generator.generate_complete_world(biome)
    
    # Gera visual do terreno
    random.seed(seed)
    tile_size = 16  # Tiles maiores para melhor visualização
    tiles_x = width // tile_size
    tiles_y = height // tile_size
    
    img = Image.new('RGB', (width, height))
    pixels = img.load()
    
    # Paletas SNES melhoradas
    palettes = {
        'forest': {
            'grass': [(76, 175, 80), (56, 142, 60), (46, 125, 50), (27, 94, 32)],
            'tree': [(62, 39, 35), (51, 105, 30)],
            'path': [(121, 85, 72), (93, 64, 55)],
            'water': [(33, 150, 243), (25, 118, 210)]
        },
        'desert': {
            'sand': [(255, 235, 59), (255, 213, 79), (255, 193, 7), (255, 179, 0)],
            'rock': [(141, 110, 99), (121, 85, 72)],
            'oasis': [(46, 125, 50), (33, 150, 243)]
        },
        'mountain': {
            'stone': [(158, 158, 158), (117, 117, 117), (97, 97, 97)],
            'snow': [(250, 250, 250), (238, 238, 238), (224, 224, 224)],
            'ice': [(187, 222, 251), (144, 202, 249)]
        },
        'cave': {
            'wall': [(66, 66, 66), (55, 55, 55), (38, 50, 56)],
            'floor': [(97, 97, 97), (84, 84, 84), (69, 69, 69)],
            'crystal': [(171, 71, 188), (156, 39, 176), (142, 36, 170)]
        }
    }
    
    palette = palettes.get(biome, palettes['forest'])
    
    # Gera mapa de tiles com mais complexidade
    for ty in range(tiles_y):
        for tx in range(tiles_x):
            # Múltiplas camadas de noise para variedade
            base_noise = noise.pnoise2(tx / 8.0, ty / 8.0, octaves=4, persistence=0.5, base=seed)
            detail_noise = noise.pnoise2(tx / 3.0, ty / 3.0, octaves=2, persistence=0.3, base=seed + 100)
            
            combined = base_noise + detail_noise * 0.3
            
            # Seleciona cor baseado em thresholds
            colors = list(palette.values())[0]  # Primeira paleta do bioma
            
            if combined > 0.5:
                color = colors[0]
            elif combined > 0.2:
                color = colors[1] if len(colors) > 1 else colors[0]
            elif combined > -0.2:
                color = colors[2] if len(colors) > 2 else colors[1] if len(colors) > 1 else colors[0]
            else:
                color = colors[-1]
            
            # Desenha tile
            for py in range(tile_size):
                for px in range(tile_size):
                    x = tx * tile_size + px
                    y = ty * tile_size + py
                    if x < width and y < height:
                        # Textura pixel-by-pixel
                        variation = random.randint(-12, 12)
                        final_color = tuple(max(0, min(255, c + variation)) for c in color)
                        pixels[x, y] = final_color
    
    # Desenha NPCs no mapa
    draw = ImageDraw.Draw(img)
    for npc in world.npcs:
        # Sprite simples do NPC (8x8 pixels)
        npc_x = npc.x
        npc_y = npc.y
        
        # Corpo
        draw.rectangle([npc_x, npc_y + 4, npc_x + 8, npc_y + 12], fill=npc.sprite_color)
        # Cabeça
        draw.ellipse([npc_x + 1, npc_y, npc_x + 7, npc_y + 6], fill=(255, 220, 177))
        # Olhos
        draw.point((npc_x + 2, npc_y + 2), fill=(0, 0, 0))
        draw.point((npc_x + 5, npc_y + 2), fill=(0, 0, 0))
    
    return img, world
