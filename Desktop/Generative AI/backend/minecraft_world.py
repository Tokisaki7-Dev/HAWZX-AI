# minecraft_world.py - Sistema de geração de mundo infinito estilo Minecraft
import random
import noise
from PIL import Image, ImageDraw
from typing import Dict, Tuple, List
import math

class MinecraftWorldGenerator:
    """Gerador de mundo infinito com chunks procedurais estilo Minecraft"""
    
    CHUNK_SIZE = 512  # Pixels por chunk
    BLOCK_SIZE = 16   # Pixels por bloco
    BLOCKS_PER_CHUNK = CHUNK_SIZE // BLOCK_SIZE  # 32 blocos por chunk
    
    # Alturas de terreno por bioma
    TERRAIN_HEIGHTS = {
        'plains': (0.3, 0.5),      # Planície: altura média-baixa
        'forest': (0.4, 0.6),       # Floresta: altura média
        'mountains': (0.6, 0.9),    # Montanhas: altura alta
        'desert': (0.35, 0.45),     # Deserto: altura baixa
        'ocean': (0.0, 0.2),        # Oceano: muito baixo
        'hills': (0.5, 0.7)         # Colinas: altura média-alta
    }
    
    # Blocos por bioma
    BLOCK_TYPES = {
        'plains': {
            'surface': [(124, 252, 0), (34, 139, 34)],  # Grama
            'underground': [(139, 90, 43), (101, 67, 33)],  # Terra
            'stone': [(128, 128, 128), (105, 105, 105)]  # Pedra
        },
        'forest': {
            'surface': [(34, 139, 34), (0, 100, 0)],
            'tree_trunk': [(101, 67, 33), (139, 90, 43)],
            'leaves': [(0, 128, 0), (34, 139, 34)],
            'underground': [(139, 90, 43)],
            'stone': [(128, 128, 128)]
        },
        'mountains': {
            'surface': [(169, 169, 169), (128, 128, 128)],  # Pedra
            'snow': [(255, 250, 250), (240, 240, 240)],  # Neve
            'underground': [(105, 105, 105)],
            'stone': [(64, 64, 64)]
        },
        'desert': {
            'surface': [(237, 201, 175), (244, 164, 96)],  # Areia
            'underground': [(210, 180, 140), (222, 184, 135)],
            'stone': [(139, 90, 43)]
        },
        'ocean': {
            'water': [(0, 105, 148), (25, 118, 210)],
            'sand': [(237, 201, 175)],
            'stone': [(128, 128, 128)]
        }
    }
    
    def __init__(self, seed: int):
        self.seed = seed
        self.chunks_cache: Dict[Tuple[int, int], Image.Image] = {}
        random.seed(seed)
    
    def get_biome(self, chunk_x: int, chunk_y: int) -> str:
        """Determina bioma usando Perlin noise para transições suaves"""
        # Escala menor para biomas grandes
        biome_noise = noise.pnoise2(
            chunk_x / 8.0,
            chunk_y / 8.0,
            octaves=4,
            persistence=0.5,
            base=self.seed
        )
        
        # Temperatura (eixo X)
        temp_noise = noise.pnoise2(
            chunk_x / 6.0,
            chunk_y / 6.0,
            octaves=3,
            base=self.seed + 1000
        )
        
        # Umidade (eixo Y)
        humidity_noise = noise.pnoise2(
            chunk_x / 5.0,
            chunk_y / 5.0,
            octaves=3,
            base=self.seed + 2000
        )
        
        # Oceano (áreas muito baixas)
        if biome_noise < -0.4:
            return 'ocean'
        
        # Montanhas (áreas muito altas)
        if biome_noise > 0.5:
            return 'mountains'
        
        # Deserto (quente e seco)
        if temp_noise > 0.3 and humidity_noise < -0.2:
            return 'desert'
        
        # Floresta (úmido)
        if humidity_noise > 0.2:
            return 'forest'
        
        # Colinas (intermediário alto)
        if biome_noise > 0.2:
            return 'hills'
        
        # Planície (padrão)
        return 'plains'
    
    def generate_heightmap(self, chunk_x: int, chunk_y: int, biome: str) -> List[int]:
        """Gera mapa de altura para o chunk"""
        heightmap = []
        base_height = self.TERRAIN_HEIGHTS[biome]
        
        for x in range(self.BLOCKS_PER_CHUNK):
            # Posição global do bloco
            global_x = chunk_x * self.BLOCKS_PER_CHUNK + x
            
            # Multi-octave Perlin noise para terreno natural
            height = noise.pnoise2(
                global_x / 20.0,
                chunk_y / 20.0,
                octaves=6,
                persistence=0.5,
                lacunarity=2.0,
                base=self.seed
            )
            
            # Normaliza para faixa do bioma
            normalized = (height + 1) / 2  # -1~1 para 0~1
            final_height = base_height[0] + normalized * (base_height[1] - base_height[0])
            
            # Converte para blocos (0 = topo, 32 = fundo)
            block_height = int(final_height * self.BLOCKS_PER_CHUNK)
            heightmap.append(block_height)
        
        return heightmap
    
    def generate_chunk(self, chunk_x: int, chunk_y: int) -> Image.Image:
        """Gera um chunk completo estilo Minecraft"""
        
        # Verifica cache
        cache_key = (chunk_x, chunk_y)
        if cache_key in self.chunks_cache:
            return self.chunks_cache[cache_key]
        
        # Determina bioma
        biome = self.get_biome(chunk_x, chunk_y)
        
        # Gera heightmap
        heightmap = self.generate_heightmap(chunk_x, chunk_y, biome)
        
        # Cria imagem
        img = Image.new('RGB', (self.CHUNK_SIZE, self.CHUNK_SIZE))
        draw = ImageDraw.Draw(img)
        pixels = img.load()
        
        # Desenha blocos
        for x in range(self.BLOCKS_PER_CHUNK):
            surface_y = heightmap[x]
            
            for y in range(self.BLOCKS_PER_CHUNK):
                block_x = x * self.BLOCK_SIZE
                block_y = y * self.BLOCK_SIZE
                
                # Determina tipo de bloco
                if biome == 'ocean':
                    if y < 10:  # Nível do mar
                        color = random.choice(self.BLOCK_TYPES[biome]['water'])
                    elif y < surface_y:
                        color = random.choice(self.BLOCK_TYPES[biome]['sand'])
                    else:
                        color = random.choice(self.BLOCK_TYPES[biome]['stone'])
                
                elif y < surface_y:
                    # Céu/ar - consistent sky color
                    color = (135, 206, 235)
                
                elif y == surface_y:
                    # Superfície
                    if biome == 'mountains' and surface_y < 8:
                        color = random.choice(self.BLOCK_TYPES[biome]['snow'])
                    else:
                        color = random.choice(self.BLOCK_TYPES[biome]['surface'])
                
                elif y < surface_y + 3:
                    # Subsuperfície
                    color = random.choice(self.BLOCK_TYPES[biome]['underground'])
                
                else:
                    # Pedra profunda
                    color = random.choice(self.BLOCK_TYPES[biome]['stone'])
                
                # Desenha bloco com variação
                self._draw_block(pixels, block_x, block_y, color)
        
        # Adiciona estruturas (árvores, rochas, etc.)
        self._add_structures(img, draw, biome, heightmap)
        
        # Grid de blocos (opcional)
        self._draw_grid(draw)
        
        # Armazena no cache
        self.chunks_cache[cache_key] = img
        
        # Limita cache (mantém apenas 9 chunks: atual + 8 adjacentes)
        if len(self.chunks_cache) > 50:
            # Remove chunks mais antigos
            oldest_keys = list(self.chunks_cache.keys())[:len(self.chunks_cache) - 50]
            for key in oldest_keys:
                del self.chunks_cache[key]
        
        return img
    
    def _draw_block(self, pixels, x: int, y: int, color: Tuple[int, int, int]):
        """Desenha um bloco com textura melhorada tipo Minecraft"""
        base_r, base_g, base_b = color
        
        for px in range(self.BLOCK_SIZE):
            for py in range(self.BLOCK_SIZE):
                if x + px >= 512 or y + py >= 512:
                    continue
                
                # Add subtle gradient for 3D effect
                # Lighter at top-left, darker at bottom-right
                gradient_factor = 1.0 - (px + py) / (self.BLOCK_SIZE * 2) * 0.15
                
                # Add very subtle noise (reduced from ±10 to ±3)
                noise_variation = random.randint(-3, 3)
                
                # Apply both effects
                r = int(max(0, min(255, base_r * gradient_factor + noise_variation)))
                g = int(max(0, min(255, base_g * gradient_factor + noise_variation)))
                b = int(max(0, min(255, base_b * gradient_factor + noise_variation)))
                
                pixels[x + px, y + py] = (r, g, b)
    
    def _add_structures(self, img: Image.Image, draw: ImageDraw.Draw, 
                       biome: str, heightmap: List[int]):
        """Adiciona estruturas procedurais (árvores, cactos, etc.)"""
        
        if biome == 'forest':
            # Árvores
            for _ in range(random.randint(3, 7)):
                x = random.randint(2, self.BLOCKS_PER_CHUNK - 3)
                surface_y = heightmap[x]
                
                if surface_y < self.BLOCKS_PER_CHUNK - 5:
                    self._draw_tree(draw, x, surface_y)
        
        elif biome == 'desert':
            # Cactos
            for _ in range(random.randint(1, 4)):
                x = random.randint(1, self.BLOCKS_PER_CHUNK - 2)
                surface_y = heightmap[x]
                
                if surface_y < self.BLOCKS_PER_CHUNK - 3:
                    self._draw_cactus(draw, x, surface_y)
        
        elif biome == 'mountains':
            # Pedregulhos
            for _ in range(random.randint(2, 5)):
                x = random.randint(1, self.BLOCKS_PER_CHUNK - 2)
                surface_y = heightmap[x]
                
                if surface_y < self.BLOCKS_PER_CHUNK - 2:
                    self._draw_boulder(draw, x, surface_y)
    
    def _draw_tree(self, draw: ImageDraw.Draw, block_x: int, block_y: int):
        """Desenha árvore estilo Minecraft"""
        x = block_x * self.BLOCK_SIZE + self.BLOCK_SIZE // 2
        y = block_y * self.BLOCK_SIZE
        
        # Tronco (2-4 blocos de altura)
        trunk_height = random.randint(2, 4) * self.BLOCK_SIZE
        trunk_color = (101, 67, 33)
        draw.rectangle(
            [x - 4, y - trunk_height, x + 4, y],
            fill=trunk_color
        )
        
        # Folhagem (círculo de folhas)
        leaves_color = (34, 139, 34)
        leaves_radius = self.BLOCK_SIZE * 1.5
        draw.ellipse(
            [x - leaves_radius, y - trunk_height - leaves_radius,
             x + leaves_radius, y - trunk_height + leaves_radius],
            fill=leaves_color
        )
    
    def _draw_cactus(self, draw: ImageDraw.Draw, block_x: int, block_y: int):
        """Desenha cacto"""
        x = block_x * self.BLOCK_SIZE + self.BLOCK_SIZE // 2
        y = block_y * self.BLOCK_SIZE
        
        height = random.randint(1, 3) * self.BLOCK_SIZE
        draw.rectangle(
            [x - 6, y - height, x + 6, y],
            fill=(0, 128, 0),
            outline=(0, 100, 0)
        )
    
    def _draw_boulder(self, draw: ImageDraw.Draw, block_x: int, block_y: int):
        """Desenha pedregulho"""
        x = block_x * self.BLOCK_SIZE + self.BLOCK_SIZE // 2
        y = block_y * self.BLOCK_SIZE
        
        size = self.BLOCK_SIZE
        draw.ellipse(
            [x - size//2, y - size, x + size//2, y],
            fill=(128, 128, 128),
            outline=(105, 105, 105)
        )
    
    def _draw_grid(self, draw: ImageDraw.Draw):
        """Desenha grid de blocos (bordas sutis nos blocos sólidos)"""
        # Light grid to show block boundaries
        for x in range(0, self.CHUNK_SIZE, self.BLOCK_SIZE):
            for y in range(0, self.CHUNK_SIZE, self.BLOCK_SIZE):
                # Draw subtle border around each block
                draw.rectangle(
                    [x, y, x + self.BLOCK_SIZE - 1, y + self.BLOCK_SIZE - 1],
                    outline=(0, 0, 0, 40),
                    width=1
                )
    
    def get_collision_map(self, chunk_x: int, chunk_y: int) -> List[List[bool]]:
        """Retorna mapa de colisão para o chunk (True = sólido, False = ar)"""
        biome = self.get_biome(chunk_x, chunk_y)
        heightmap = self.generate_heightmap(chunk_x, chunk_y, biome)
        
        collision_map = []
        for y in range(self.BLOCKS_PER_CHUNK):
            row = []
            for x in range(self.BLOCKS_PER_CHUNK):
                # Sólido se Y >= altura da superfície
                is_solid = y >= heightmap[x]
                row.append(is_solid)
            collision_map.append(row)
        
        return collision_map
    
    def get_chunk_at_position(self, world_x: int, world_y: int) -> Tuple[int, int]:
        """Converte posição do mundo para coordenadas de chunk"""
        chunk_x = math.floor(world_x / self.CHUNK_SIZE)
        chunk_y = math.floor(world_y / self.CHUNK_SIZE)
        return chunk_x, chunk_y
    
    def clear_cache(self):
        """Limpa cache de chunks"""
        self.chunks_cache.clear()
