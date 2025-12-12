# physics_engine.py - Sistema de física avançado
import math
from typing import Tuple, List

class PhysicsEngine:
    """Motor de física completo para o jogo"""
    
    def __init__(self):
        # Constantes físicas
        self.GRAVITY = 980  # pixels/s² (9.8 m/s² * 100)
        self.TERMINAL_VELOCITY = 500  # Velocidade máxima de queda
        self.GROUND_FRICTION = 0.8  # Atrito no chão
        self.AIR_RESISTANCE = 0.98  # Resistência do ar
        
        # Pulo
        self.JUMP_STRENGTH = 400  # Força inicial do pulo
        self.DOUBLE_JUMP_STRENGTH = 350  # Força do pulo duplo
        self.COYOTE_TIME = 0.1  # Tempo após sair da plataforma que ainda pode pular (segundos)
        self.JUMP_BUFFER_TIME = 0.1  # Tempo de buffer para input de pulo
        
        # Movimento
        self.MAX_WALK_SPEED = 200  # Velocidade máxima de caminhada
        self.MAX_RUN_SPEED = 350  # Velocidade máxima de corrida
        self.WALK_ACCELERATION = 1000  # Aceleração ao andar
        self.AIR_CONTROL = 0.6  # Controle no ar (60% do controle normal)
    
    def apply_gravity(self, velocity_y: float, delta_time: float, on_ground: bool) -> float:
        """Aplica gravidade à velocidade vertical"""
        if not on_ground:
            # Aplica gravidade
            velocity_y += self.GRAVITY * delta_time
            
            # Limita à velocidade terminal
            velocity_y = min(velocity_y, self.TERMINAL_VELOCITY)
        else:
            # No chão, velocidade vertical zero
            velocity_y = 0
        
        return velocity_y
    
    def apply_movement(self, velocity_x: float, input_x: float, delta_time: float, 
                      on_ground: bool, is_running: bool) -> float:
        """Aplica movimento horizontal"""
        
        # Determina velocidade máxima
        max_speed = self.MAX_RUN_SPEED if is_running else self.MAX_WALK_SPEED
        
        # Determina aceleração (menor no ar)
        acceleration = self.WALK_ACCELERATION
        if not on_ground:
            acceleration *= self.AIR_CONTROL
        
        if input_x != 0:
            # Acelera na direção do input
            velocity_x += input_x * acceleration * delta_time
            
            # Limita velocidade máxima
            velocity_x = max(-max_speed, min(max_speed, velocity_x))
        else:
            # Desacelera com atrito
            if on_ground:
                velocity_x *= self.GROUND_FRICTION
            else:
                velocity_x *= self.AIR_RESISTANCE
            
            # Para completamente se muito devagar
            if abs(velocity_x) < 1:
                velocity_x = 0
        
        return velocity_x
    
    def apply_jump(self, velocity_y: float, can_jump: bool, is_double_jump: bool) -> Tuple[float, bool]:
        """Aplica força de pulo"""
        if can_jump:
            if is_double_jump:
                velocity_y = -self.DOUBLE_JUMP_STRENGTH
            else:
                velocity_y = -self.JUMP_STRENGTH
            return velocity_y, True
        return velocity_y, False
    
    def check_collision_block(self, player_rect: dict, block_rect: dict) -> dict:
        """Verifica colisão entre player e bloco, retorna informações de colisão"""
        
        # Expandir ligeiramente para precisão
        px1, py1 = player_rect['x'], player_rect['y']
        px2, py2 = px1 + player_rect['width'], py1 + player_rect['height']
        
        bx1, by1 = block_rect['x'], block_rect['y']
        bx2, by2 = bx1 + block_rect['width'], by1 + block_rect['height']
        
        # Verifica se há overlap
        overlaps_x = px2 > bx1 and px1 < bx2
        overlaps_y = py2 > by1 and py1 < by2
        
        if overlaps_x and overlaps_y:
            # Calcula profundidade da penetração em cada eixo
            overlap_left = px2 - bx1
            overlap_right = bx2 - px1
            overlap_top = py2 - by1
            overlap_bottom = by2 - py1
            
            # Menor penetração indica direção da colisão
            min_overlap_x = min(overlap_left, overlap_right)
            min_overlap_y = min(overlap_top, overlap_bottom)
            
            if min_overlap_x < min_overlap_y:
                # Colisão horizontal
                return {
                    'collided': True,
                    'side': 'left' if overlap_left < overlap_right else 'right',
                    'penetration_x': min_overlap_x if overlap_left < overlap_right else -min_overlap_x,
                    'penetration_y': 0
                }
            else:
                # Colisão vertical
                return {
                    'collided': True,
                    'side': 'top' if overlap_top < overlap_bottom else 'bottom',
                    'penetration_x': 0,
                    'penetration_y': min_overlap_y if overlap_top < overlap_bottom else -min_overlap_y
                }
        
        return {'collided': False}
    
    def resolve_collision(self, position: dict, velocity: dict, collision: dict) -> Tuple[dict, dict, bool]:
        """Resolve colisão, ajusta posição e velocidade"""
        
        on_ground = False
        
        if collision['collided']:
            side = collision['side']
            
            if side == 'bottom':
                # Colidiu com o chão
                position['y'] -= collision['penetration_y']
                velocity['y'] = 0
                on_ground = True
            
            elif side == 'top':
                # Colidiu com o teto
                position['y'] += collision['penetration_y']
                velocity['y'] = 0
            
            elif side == 'left':
                # Colidiu pela esquerda
                position['x'] -= collision['penetration_x']
                velocity['x'] = 0
            
            elif side == 'right':
                # Colidiu pela direita
                position['x'] += collision['penetration_x']
                velocity['x'] = 0
        
        return position, velocity, on_ground


class CollisionDetector:
    """Sistema de detecção de colisão por análise de imagem"""
    
    BLOCK_SIZE = 16  # Tamanho do bloco em pixels
    
    @staticmethod
    def get_block_at_position(x: int, y: int, chunk_size: int = 512) -> Tuple[int, int]:
        """Converte posição em pixels para coordenadas de bloco"""
        block_x = int(x // CollisionDetector.BLOCK_SIZE)
        block_y = int(y // CollisionDetector.BLOCK_SIZE)
        return block_x, block_y
    
    @staticmethod
    def get_surrounding_blocks(player_rect: dict) -> List[Tuple[int, int]]:
        """Retorna lista de blocos ao redor do jogador que precisam ser verificados"""
        blocks = []
        
        # Cantos do retângulo do jogador
        corners = [
            (player_rect['x'], player_rect['y']),  # Top-left
            (player_rect['x'] + player_rect['width'], player_rect['y']),  # Top-right
            (player_rect['x'], player_rect['y'] + player_rect['height']),  # Bottom-left
            (player_rect['x'] + player_rect['width'], player_rect['y'] + player_rect['height'])  # Bottom-right
        ]
        
        # Adiciona blocos únicos
        seen = set()
        for cx, cy in corners:
            block = CollisionDetector.get_block_at_position(cx, cy)
            if block not in seen:
                blocks.append(block)
                seen.add(block)
        
        # Adiciona blocos intermediários (para jogadores grandes)
        mid_points = [
            (player_rect['x'] + player_rect['width'] // 2, player_rect['y']),  # Top-mid
            (player_rect['x'] + player_rect['width'] // 2, player_rect['y'] + player_rect['height']),  # Bottom-mid
            (player_rect['x'], player_rect['y'] + player_rect['height'] // 2),  # Left-mid
            (player_rect['x'] + player_rect['width'], player_rect['y'] + player_rect['height'] // 2)  # Right-mid
        ]
        
        for mx, my in mid_points:
            block = CollisionDetector.get_block_at_position(mx, my)
            if block not in seen:
                blocks.append(block)
                seen.add(block)
        
        return blocks
    
    @staticmethod
    def check_collisions_with_map(player_rect: dict, collision_map: List[List[bool]]) -> List[dict]:
        """Verifica colisões com o mapa de colisão"""
        
        # Pega blocos ao redor
        blocks_to_check = CollisionDetector.get_surrounding_blocks(player_rect)
        
        collisions = []
        physics = PhysicsEngine()
        
        for block_x, block_y in blocks_to_check:
            # Verifica limites do mapa
            if 0 <= block_y < len(collision_map) and 0 <= block_x < len(collision_map[0]):
                # Verifica se bloco é sólido
                if collision_map[block_y][block_x]:
                    # Cria retângulo do bloco
                    block_rect = {
                        'x': block_x * CollisionDetector.BLOCK_SIZE,
                        'y': block_y * CollisionDetector.BLOCK_SIZE,
                        'width': CollisionDetector.BLOCK_SIZE,
                        'height': CollisionDetector.BLOCK_SIZE
                    }
                    
                    # Verifica colisão
                    collision = physics.check_collision_block(player_rect, block_rect)
                    if collision['collided']:
                        collisions.append(collision)
        
        return collisions
    
    @staticmethod
    def analyze_pixel_collision(image, player_x: int, player_y: int, 
                                player_width: int, player_height: int) -> bool:
        """
        Análise de colisão por cor de pixel (alternativa ao mapa de blocos)
        Retorna True se colidiu com algo sólido
        """
        pixels = image.load()
        width, height = image.size
        
        # Define cores que são consideradas sólidas (não céu)
        SKY_COLORS = [
            (135, 206, 235),  # Azul claro
            (100, 149, 237),  # Azul médio
            (0, 0, 0)  # Preto (fundo)
        ]
        
        # Verifica pixels nos cantos e centro do jogador
        points_to_check = [
            (player_x, player_y + player_height),  # Bottom-left
            (player_x + player_width, player_y + player_height),  # Bottom-right
            (player_x + player_width // 2, player_y + player_height),  # Bottom-center
            (player_x, player_y + player_height // 2),  # Mid-left
            (player_x + player_width, player_y + player_height // 2)  # Mid-right
        ]
        
        for px, py in points_to_check:
            # Verifica limites
            if 0 <= px < width and 0 <= py < height:
                pixel_color = pixels[px, py]
                
                # Se não é cor de céu, é sólido
                if pixel_color not in SKY_COLORS:
                    return True
        
        return False
