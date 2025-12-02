import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class CharacterService:
    """
    Gerencia o estado, a persona e as animações do mascote da IA.
    """
    def __init__(self):
        """
        Inicializa o serviço do personagem.
        """
        self.current_persona = "Nika" # Persona padrão
        self.current_state = "idle" # Estado inicial
        
        # Mapeamento de estados para arquivos de animação (placeholder)
        self.animations = {
            "idle": "assets/character/Nika/idle.gif",
            "talking": "assets/character/Nika/talking.gif",
            "thinking": "assets/character/Nika/thinking.gif",
            "happy": "assets/character/Nika/happy.gif",
            "alert": "assets/character/Nika/alert.gif",
        }
        logging.info(f"Serviço de Personagem inicializado com a persona '{self.current_persona}'.")

    def set_state(self, state: str):
        """
        Define o estado do personagem. O overlay usará isso para mudar a animação.
        """
        if state in self.animations:
            self.current_state = state
            logging.info(f"Estado do personagem alterado para: {state}")
        else:
            logging.warning(f"Tentativa de definir um estado desconhecido: {state}. Mantendo '{self.current_state}'.")

    def get_current_state(self) -> dict:
        """Retorna o estado atual e o caminho da animação correspondente."""
        animation_path = self.animations.get(self.current_state, self.animations["idle"])
        return {"persona": self.current_persona, "state": self.current_state, "animation": animation_path}