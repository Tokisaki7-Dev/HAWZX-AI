# minecraft_world.py - Sistema de geração de mundo infinito estilo Minecraft
import random
import noise
from PIL import Image, ImageDraw
from typing import Dict, Tuple, List
import math

class MinecraftWorldGenerator:
    """Gerador de mundo infinito com chunks procedurais estilo Minecraft"""
    
    CHUNK_SIZE = 512  # Pixels por chunk
    BLOCK_SIZE = 8    # Pixels por bloco (tiles menores para look JRPG)
    BLOCKS_PER_CHUNK = CHUNK_SIZE // BLOCK_SIZE  # 64 blocos por chunk
    
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
            'surface': [(139, 217, 114), (114, 191, 92)],  # Grama suave
            'underground': [(171, 140, 104), (152, 122, 92)],  # Terra clara
            'stone': [(150, 150, 160), (130, 130, 140)]  # Pedra suave
        },
        'forest': {
            'surface': [(98, 175, 114), (78, 150, 95)],
            'tree_trunk': [(120, 86, 60), (99, 68, 46)],
            'leaves': [(76, 148, 94), (62, 126, 79)],
            'underground': [(156, 125, 96)],
            'stone': [(140, 140, 150)]
        },
        'mountains': {
            'surface': [(170, 180, 190), (150, 160, 170)],  # Pedra suave
            'snow': [(245, 248, 250), (232, 236, 240)],  # Neve clara
            'underground': [(120, 120, 130)],
            'stone': [(90, 95, 105)]
        },
        'desert': {
            'surface': [(236, 209, 164), (228, 192, 139)],  # Areia suave
            'underground': [(214, 184, 146), (200, 170, 130)],
            'stone': [(156, 118, 78)]
        },
        'ocean': {
            'water': [(64, 149, 209), (52, 134, 194)],
            'sand': [(232, 205, 170)],
            'stone': [(140, 150, 160)]
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
            """Gera um chunk top-down estilo JRPG 16-bit"""

            cache_key = (chunk_x, chunk_y)
            if cache_key in self.chunks_cache:
                return self.chunks_cache[cache_key]

            tiles, collision_map = self.generate_tilemap(chunk_x, chunk_y)

            img = Image.new('RGB', (self.CHUNK_SIZE, self.CHUNK_SIZE))
            draw = ImageDraw.Draw(img)
            pixels = img.load()

            for y in range(self.BLOCKS_PER_CHUNK):
                for x in range(self.BLOCKS_PER_CHUNK):
                    tx = x * self.BLOCK_SIZE
                    ty = y * self.BLOCK_SIZE
                    tile = tiles[y][x]
                    self._draw_tile(pixels, tx, ty, tile)

            # Grid sutil para vibe de tileset
            self._draw_grid(draw)

            self.chunks_cache[cache_key] = img

            # Limita cache
            if len(self.chunks_cache) > 50:
                oldest_keys = list(self.chunks_cache.keys())[:len(self.chunks_cache) - 50]
                for key in oldest_keys:
                    del self.chunks_cache[key]

            return img

        def generate_tilemap(self, chunk_x: int, chunk_y: int):
            """Gera tiles top-down e mapa de colisão"""
            tile_count = self.BLOCKS_PER_CHUNK
            tiles: List[List[str]] = []
            collision: List[List[bool]] = []

            rng = random.Random(self.seed + chunk_x * 92821 + chunk_y * 49157)

            for y in range(tile_count):
                row = []
                crow = []
                for x in range(tile_count):
                    gx = chunk_x * tile_count + x
                    gy = chunk_y * tile_count + y

                    elev = noise.pnoise2(gx / 30.0, gy / 30.0, octaves=4, persistence=0.5, base=self.seed)
                    moist = noise.pnoise2(gx / 25.0, gy / 25.0, octaves=3, persistence=0.55, base=self.seed + 5000)

                    # Classifica tile
                    if elev < -0.35:
                        tile = 'deep_water'
                    elif elev < -0.15:
                        tile = 'water'
                    elif elev < 0.05:
                        tile = 'sand'
                    elif elev > 0.65:
                        tile = 'mountain'
                    elif elev > 0.45:
                        tile = 'hill'
                    else:
                        tile = 'grass'

                    # Umidade influencia floresta
                    if tile == 'grass' and moist > 0.25 and rng.random() < 0.35 + moist * 0.2:
                        tile = 'forest'

                    # Pequenos caminhos
                    if tile == 'grass' and rng.random() < 0.04:
                        tile = 'path'

                    # Rochas em colinas/areia
                    if tile in ['hill', 'sand'] and rng.random() < 0.05:
                        tile = 'rock'

                    solid_tiles = {'mountain', 'rock', 'forest', 'deep_water', 'water'}
                    row.append(tile)
                    crow.append(tile in solid_tiles)
                tiles.append(row)
                collision.append(crow)

            return tiles, collision
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

    def _draw_tile(self, pixels, x: int, y: int, tile: str):
        """Desenha tile 8px com aparência 16-bit"""
        palette = {
            'grass': [(123, 193, 102), (110, 176, 91), (138, 207, 118)],
            'forest': [(82, 143, 92), (68, 124, 78), (96, 161, 104)],
            'path': [(176, 150, 118), (162, 136, 105)],
            'sand': [(230, 205, 170), (216, 190, 154)],
            'rock': [(156, 150, 140), (134, 128, 118)],
            'hill': [(146, 169, 132), (126, 150, 117)],
            'mountain': [(128, 135, 142), (109, 116, 123)],
            'water': [(74, 140, 201), (62, 128, 189)],
            'deep_water': [(54, 110, 171), (42, 96, 157)]
        }

        colors = palette.get(tile, palette['grass'])
        base = random.choice(colors)

        for px in range(self.BLOCK_SIZE):
            for py in range(self.BLOCK_SIZE):
                rx = x + px
                ry = y + py
                if rx >= self.CHUNK_SIZE or ry >= self.CHUNK_SIZE:
                    continue

                # Dither pattern
                dither = ((px + py) % 2 == 0)
                variation = -6 if dither else 6
                gradient = 1.0 - (py / (self.BLOCK_SIZE * 4))
                r = int(max(0, min(255, base[0] * gradient + variation)))
                g = int(max(0, min(255, base[1] * gradient + variation)))
                b = int(max(0, min(255, base[2] * gradient + variation)))

                # Extra highlight for path and sand
                if tile in ['path', 'sand'] and dither:
                    r = min(255, r + 10)
                    g = min(255, g + 8)

                pixels[rx, ry] = (r, g, b)
    
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
        _, collision = self.generate_tilemap(chunk_x, chunk_y)
        return collision
    
    def get_chunk_at_position(self, world_x: int, world_y: int) -> Tuple[int, int]:
        """Converte posição do mundo para coordenadas de chunk"""
        chunk_x = math.floor(world_x / self.CHUNK_SIZE)
        chunk_y = math.floor(world_y / self.CHUNK_SIZE)
        return chunk_x, chunk_y
    
    def clear_cache(self):
        """Limpa cache de chunks"""
        self.chunks_cache.clear()
