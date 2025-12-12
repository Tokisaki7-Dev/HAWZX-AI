# backend/main.py
import os
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import base64
from io import BytesIO
from supabase import create_client, Client
from datetime import datetime
from PIL import Image, ImageDraw
import random
import noise
from game_generator import generate_enhanced_terrain
from combat_system import (
    CombatSystem, ItemSystem, LevelSystem, 
    create_initial_player_stats, Enemy, PlayerStats
)
from minecraft_world import MinecraftWorldGenerator
from physics_engine import PhysicsEngine, CollisionDetector

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Inicializa Supabase
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = None

if supabase_url and supabase_key:
    supabase = create_client(supabase_url, supabase_key)
    print("✅ Supabase conectado!")
else:
    print("⚠️ Supabase não configurado - funcionando sem banco de dados")

app = FastAPI()

# Inicializa gerador de mundo Minecraft
minecraft_world = None

def get_minecraft_world(seed: int = None):
    """Obtém ou cria instância do gerador de mundo"""
    global minecraft_world
    if minecraft_world is None or (seed is not None and minecraft_world.seed != seed):
        minecraft_world = MinecraftWorldGenerator(seed or 12345)
    return minecraft_world

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Prompt(BaseModel):
    prompt: str

class CombatAction(BaseModel):
    action_type: str  # 'attack', 'skill', 'item', 'flee'
    skill_index: int = 0
    item_name: str = ''

class SaveData(BaseModel):
    player_stats: dict
    inventory: list
    current_biome: str
    world_seed: int

# Monta os arquivos estáticos (frontend)
app.mount("/static", StaticFiles(directory="static"), name="static")

def generate_procedural_terrain(biome, seed, width=512, height=512):
    """Gera terreno estilo pixel art 16-bit (Chrono Trigger style)"""
    random.seed(seed)
    
    # Tamanho dos tiles (8x8 pixels)
    tile_size = 8
    tiles_x = width // tile_size
    tiles_y = height // tile_size
    
    img = Image.new('RGB', (width, height))
    pixels = img.load()
    
    # Paletas de cores estilo SNES 16-bit por bioma
    palettes = {
        'forest': {
            'grass': [(76, 175, 80), (56, 142, 60), (46, 125, 50)],
            'tree': [(62, 39, 35), (51, 105, 30), (27, 94, 32)],
            'path': [(121, 85, 72), (93, 64, 55)],
            'flower': [(255, 235, 59), (244, 67, 54)]
        },
        'desert': {
            'sand': [(255, 224, 130), (255, 213, 79), (255, 193, 7)],
            'rock': [(141, 110, 99), (121, 85, 72)],
            'cactus': [(46, 125, 50), (27, 94, 32)],
            'detail': [(255, 152, 0)]
        },
        'mountain': {
            'stone': [(158, 158, 158), (117, 117, 117), (97, 97, 97)],
            'snow': [(250, 250, 250), (238, 238, 238)],
            'path': [(78, 52, 46), (62, 39, 35)],
            'ice': [(187, 222, 251), (144, 202, 249)]
        },
        'cave': {
            'wall': [(66, 66, 66), (55, 55, 55), (38, 50, 56)],
            'floor': [(97, 97, 97), (84, 84, 84)],
            'crystal': [(171, 71, 188), (142, 36, 170), (123, 31, 162)],
            'light': [(255, 235, 59)]
        }
    }
    
    palette = palettes.get(biome, palettes['forest'])
    
    # Gera mapa de tiles usando Perlin noise
    tile_map = []
    for y in range(tiles_y):
        row = []
        for x in range(tiles_x):
            # Noise para determinar tipo de tile
            noise_val = noise.pnoise2(x / 10.0, y / 10.0, octaves=3, persistence=0.5, base=seed)
            row.append(noise_val)
        tile_map.append(row)
    
    # Desenha tiles
    for ty in range(tiles_y):
        for tx in range(tiles_x):
            noise_val = tile_map[ty][tx]
            
            # Escolhe cor do tile baseado no bioma e noise
            if biome == 'forest':
                if noise_val > 0.3:
                    color = random.choice(palette['tree'])
                elif noise_val > 0:
                    color = random.choice(palette['grass'])
                else:
                    color = random.choice(palette['path'])
            elif biome == 'desert':
                if noise_val > 0.4:
                    color = random.choice(palette['rock'])
                else:
                    color = random.choice(palette['sand'])
            elif biome == 'mountain':
                if noise_val > 0.5:
                    color = random.choice(palette['snow'])
                elif noise_val > 0:
                    color = random.choice(palette['stone'])
                else:
                    color = random.choice(palette['path'])
            else:  # cave
                if noise_val > 0.3:
                    color = random.choice(palette['wall'])
                else:
                    color = random.choice(palette['floor'])
            
            # Desenha o tile
            for py in range(tile_size):
                for px in range(tile_size):
                    x = tx * tile_size + px
                    y = ty * tile_size + py
                    if x < width and y < height:
                        # Adiciona variação pixel a pixel para textura
                        variation = random.randint(-8, 8)
                        final_color = tuple(max(0, min(255, c + variation)) for c in color)
                        pixels[x, y] = final_color
    
    # Adiciona detalhes estilo pixel art
    draw = ImageDraw.Draw(img)
    
    # Árvores/objetos decorativos
    num_objects = random.randint(8, 20)
    for _ in range(num_objects):
        ox = random.randint(0, tiles_x - 3) * tile_size
        oy = random.randint(0, tiles_y - 4) * tile_size
        
        if biome == 'forest':
            # Árvore estilo pixel art
            trunk_color = palette['tree'][0]
            leaves_color = palette['tree'][1]
            
            # Tronco (2 tiles de largura, 3 de altura)
            draw.rectangle([ox + 4, oy + 16, ox + 12, oy + 32], fill=trunk_color)
            # Copa (3x2 tiles)
            draw.ellipse([ox, oy, ox + 16, oy + 20], fill=leaves_color)
            
        elif biome == 'desert':
            # Cacto pixel art
            cactus_color = palette['cactus'][0]
            draw.rectangle([ox + 6, oy + 8, ox + 10, oy + 24], fill=cactus_color)
            draw.rectangle([ox + 2, oy + 14, ox + 6, oy + 18], fill=cactus_color)
            
        elif biome == 'mountain':
            # Pedra/rocha pixel art
            rock_color = palette['stone'][0]
            points = [(ox + 8, oy), (ox + 16, oy + 12), (ox + 12, oy + 16), (ox, oy + 16), (ox + 4, oy + 8)]
            draw.polygon(points, fill=rock_color)
            
        elif biome == 'cave':
            # Cristal pixel art
            crystal_color = palette['crystal'][0]
            points = [(ox + 8, oy), (ox + 12, oy + 8), (ox + 8, oy + 16), (ox + 4, oy + 8)]
            draw.polygon(points, fill=crystal_color)
    
    # Adiciona grid sutil para efeito pixel art
    for x in range(0, width, tile_size):
        for y in range(0, height, tile_size):
            if random.random() < 0.1:  # Grid sutil em alguns tiles
                draw.rectangle([x, y, x + tile_size - 1, y + tile_size - 1], outline=(0, 0, 0), width=1)
    
    return img

@app.get("/")
def read_root():
    return FileResponse("static/index.html")

@app.post("/generate-frame")
async def generate_frame_endpoint(prompt_data: Prompt):
    """
    Gera mundo completo de jogo JRPG com NPCs, história, quests e comandos
    """
    prompt = prompt_data.prompt
    
    # Detecta bioma do prompt
    biome = "forest"
    if "desert" in prompt.lower() or "sand" in prompt.lower():
        biome = "desert"
    elif "mountain" in prompt.lower() or "snow" in prompt.lower():
        biome = "mountain"
    elif "cave" in prompt.lower() or "cavern" in prompt.lower():
        biome = "cave"
    
    # Gera seed baseado no prompt para consistência
    seed = hash(prompt) % 1000000
    
    print(f"Gerando mundo JRPG completo - Bioma: {biome}, Seed: {seed}")
    
    # Gera terreno + mundo completo
    img, world = generate_enhanced_terrain(biome, seed)
    
    # Converte imagem para base64
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode()
    image_data = f"data:image/png;base64,{img_base64}"
    
    # Prepara metadados do mundo
    world_data = {
        'name': world.name,
        'story': world.story,
        'biome': world.biome,
        'npcs': [{
            'name': npc.name,
            'x': npc.x,
            'y': npc.y,
            'dialogue': npc.dialogue,
            'quest': npc.quest
        } for npc in world.npcs],
        'quests': [{
            'title': q.title,
            'description': q.description,
            'objective': q.objective,
            'reward': q.reward
        } for q in world.quests],
        'controls': world.controls,
        'special_mechanics': world.special_mechanics
    }
    
    # Salva no Supabase (se configurado)
    if supabase:
        try:
            supabase.table("generations").insert({
                "prompt": prompt,
                "image_base64": img_base64,
                "world_data": world_data,
                "created_at": datetime.utcnow().isoformat()
            }).execute()
            print("✅ Mundo completo salvo no Supabase")
        except Exception as e:
            print(f"⚠️ Erro ao salvar no Supabase: {e}")
    
    return {
        "message": f"Mundo JRPG '{world.name}' gerado com sucesso!",
        "image_url": image_data,
        "world": world_data
    }

@app.post("/generate-enemy")
async def generate_enemy_endpoint(data: dict):
    """Gera inimigo procedural para combate"""
    biome = data.get('biome', 'forest')
    player_level = data.get('player_level', 1)
    seed = data.get('seed', random.randint(1, 1000000))
    
    combat_system = CombatSystem(seed)
    enemy = combat_system.generate_enemy(biome, player_level)
    
    return {
        "success": True,
        "enemy": {
            "name": enemy.name,
            "level": enemy.level,
            "hp": enemy.hp,
            "max_hp": enemy.max_hp,
            "mp": enemy.mp,
            "max_mp": enemy.max_mp,
            "attack": enemy.attack,
            "defense": enemy.defense,
            "magic": enemy.magic,
            "speed": enemy.speed,
            "exp_reward": enemy.exp_reward,
            "gold_reward": enemy.gold_reward,
            "item_drop": enemy.item_drop,
            "sprite_color": enemy.sprite_color,
            "skills": enemy.skills
        }
    }

@app.post("/combat-action")
async def combat_action_endpoint(data: dict):
    """Processa ação de combate"""
    player_stats = data.get('player_stats')
    enemy_stats = data.get('enemy_stats')
    action = data.get('action')
    
    combat_system = CombatSystem(random.randint(1, 1000000))
    
    result = {
        "player_action": None,
        "enemy_action": None,
        "messages": [],
        "player_hp": player_stats['hp'],
        "enemy_hp": enemy_stats['hp'],
        "battle_end": False,
        "victory": False,
        "exp_gained": 0,
        "gold_gained": 0,
        "item_dropped": None
    }
    
    # Determina ordem de turno baseado em velocidade
    player_first = player_stats['speed'] >= enemy_stats['speed']
    
    # Ação do jogador
    if action['action_type'] == 'flee':
        flee_chance = 0.5 + (player_stats['speed'] - enemy_stats['speed']) * 0.05
        if random.random() < flee_chance:
            result['messages'].append("Você fugiu com sucesso!")
            result['battle_end'] = True
            return result
        else:
            result['messages'].append("Não conseguiu fugir!")
    
    elif action['action_type'] == 'item':
        item = ItemSystem.get_item(action['item_name'])
        if item:
            if item.effect == 'heal':
                heal_amount = min(item.value, player_stats['max_hp'] - player_stats['hp'])
                result['player_hp'] = player_stats['hp'] + heal_amount
                result['messages'].append(f"Usou {item.name}! Recuperou {heal_amount} HP!")
            elif item.effect == 'mp_restore':
                mp_amount = min(item.value, player_stats['max_mp'] - player_stats['mp'])
                result['messages'].append(f"Usou {item.name}! Recuperou {mp_amount} MP!")
    
    elif action['action_type'] == 'attack' or action['action_type'] == 'skill':
        # Skill do jogador
        player_skill = {'name': 'Attack', 'mp_cost': 0, 'power': 1.0, 'type': 'physical'}
        if action['action_type'] == 'skill' and 'skill_index' in action:
            # Implementar skills do jogador aqui
            pass
        
        # Calcula dano do jogador
        is_crit = combat_system.check_critical(player_stats['speed'], enemy_stats['speed'])
        damage = combat_system.calculate_damage(player_stats, enemy_stats, player_skill, is_crit)
        result['enemy_hp'] = max(0, enemy_stats['hp'] - damage)
        
        crit_text = " CRÍTICO!" if is_crit else ""
        result['messages'].append(f"Você atacou! {damage} de dano{crit_text}!")
        
        # Verifica vitória
        if result['enemy_hp'] <= 0:
            result['battle_end'] = True
            result['victory'] = True
            result['exp_gained'] = enemy_stats['exp_reward']
            result['gold_gained'] = enemy_stats['gold_reward']
            result['item_dropped'] = enemy_stats.get('item_drop')
            result['messages'].append(f"Vitória! Ganhou {result['exp_gained']} EXP e {result['gold_gained']} ouro!")
            return result
    
    # Ação do inimigo (se não morreu)
    if result['enemy_hp'] > 0:
        # Escolhe skill aleatória
        enemy_skill = random.choice(enemy_stats['skills'])
        
        # Calcula dano do inimigo
        is_crit = combat_system.check_critical(enemy_stats['speed'], player_stats['speed'])
        damage = combat_system.calculate_damage(enemy_stats, player_stats, enemy_skill, is_crit)
        result['player_hp'] = max(0, player_stats['hp'] - damage)
        
        crit_text = " CRÍTICO!" if is_crit else ""
        result['messages'].append(f"{enemy_stats['name']} usou {enemy_skill['name']}! {damage} de dano{crit_text}!")
        
        # Verifica derrota
        if result['player_hp'] <= 0:
            result['battle_end'] = True
            result['victory'] = False
            result['messages'].append("Você foi derrotado...")
    
    return result

@app.post("/level-up")
async def level_up_endpoint(data: dict):
    """Processa level up do jogador"""
    current_stats = PlayerStats(**data['player_stats'])
    exp_gained = data['exp_gained']
    
    new_stats, leveled_up = LevelSystem.add_exp(current_stats, exp_gained)
    
    return {
        "leveled_up": leveled_up,
        "player_stats": {
            "level": new_stats.level,
            "exp": new_stats.exp,
            "exp_to_next": new_stats.exp_to_next,
            "hp": new_stats.hp,
            "max_hp": new_stats.max_hp,
            "mp": new_stats.mp,
            "max_mp": new_stats.max_mp,
            "attack": new_stats.attack,
            "defense": new_stats.defense,
            "magic": new_stats.magic,
            "speed": new_stats.speed,
            "gold": new_stats.gold
        }
    }

@app.get("/starter-items")
async def get_starter_items():
    """Retorna itens iniciais"""
    items = ItemSystem.get_starter_items()
    return {"items": items}

@app.get("/item/{item_name}")
async def get_item_info(item_name: str):
    """Retorna informações de um item"""
    item = ItemSystem.get_item(item_name)
    if item:
        return {
            "name": item.name,
            "type": item.type,
            "effect": item.effect,
            "value": item.value,
            "description": item.description,
            "icon_color": item.icon_color
        }
    return {"error": "Item não encontrado"}

@app.post("/generate-chunk")
async def generate_chunk_endpoint(data: dict):
    """Gera chunk do mundo Minecraft"""
    chunk_x = data.get('chunk_x', 0)
    chunk_y = data.get('chunk_y', 0)
    seed = data.get('seed', 12345)
    
    try:
        world_gen = get_minecraft_world(seed)
        
        # Gera chunk
        chunk_image = world_gen.generate_chunk(chunk_x, chunk_y)
        
        # Converte para base64
        buffered = BytesIO()
        chunk_image.save(buffered, format='PNG')
        buffered.seek(0)
        image_base64 = base64.b64encode(buffered.read()).decode()
        
        # Gera mapa de colisão
        collision_map = world_gen.get_collision_map(chunk_x, chunk_y)
        
        # Informações do bioma
        biome = world_gen.get_biome(chunk_x, chunk_y)
        
        return {
            "success": True,
            "image": f"data:image/png;base64,{image_base64}",
            "collision_map": collision_map,
            "biome": biome,
            "chunk_x": chunk_x,
            "chunk_y": chunk_y
        }
    except Exception as e:
        print(f"Erro ao gerar chunk: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/check-collision")
async def check_collision_endpoint(data: dict):
    """Verifica colisão do jogador com o mapa"""
    player_rect = data.get('player_rect')
    collision_map = data.get('collision_map')
    
    try:
        collisions = CollisionDetector.check_collisions_with_map(player_rect, collision_map)
        
        return {
            "success": True,
            "collisions": collisions,
            "has_collision": len(collisions) > 0
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/world-info")
async def get_world_info(seed: int = 12345):
    """Retorna informações sobre o mundo"""
    world_gen = get_minecraft_world(seed)
    
    return {
        "seed": world_gen.seed,
        "chunk_size": world_gen.CHUNK_SIZE,
        "block_size": world_gen.BLOCK_SIZE,
        "blocks_per_chunk": world_gen.BLOCKS_PER_CHUNK,
        "biomes": list(world_gen.TERRAIN_HEIGHTS.keys())
    }

# Para rodar o servidor:
# 1. Navegue até a pasta 'backend' no terminal
# 2. Instale as dependências: pip install -r requirements.txt
# 3. Rode o servidor: uvicorn main:app --reload

