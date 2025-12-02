from transformers import pipeline
import requests # Importar requests

class AIService:
    def __init__(self, rag_service, game_service): # Added game_service
        self.rag_service = rag_service
        self.game_service = game_service # Stored game_service
        # Placeholder for actual model loading, consider efficient loading
        self.dialog_pipeline = pipeline("text-generation", model="microsoft/DialoGPT-medium")
        self.current_context = {"game": None, "player_health": None, "conversation_history": []}

        # Thinking Model Configuration
        self.thinking_model_name = None
        self.thinking_api_key = None
        self.thinking_endpoint = None
        
    def update_thinking_model_config(self, model_name: str = None, api_key: str = None, endpoint: str = None):
        if model_name:
            self.thinking_model_name = model_name
        if api_key:
            self.thinking_api_key = api_key
        if endpoint:
            self.thinking_endpoint = endpoint
        print(f"Thinking model config updated: Name={self.thinking_model_name}, Endpoint={self.thinking_endpoint}")


    def update_context(self, vision_data=None, voice_text=None):
        if vision_data:
            # Atualizar contexto com dados visuais
            self.current_context["game"] = vision_data.get("game")
            # Adicionar outros dados visuais conforme necessário
            # Ex: self.current_context["player_health"] = vision_data.get("health")

        if voice_text:
            self.current_context["conversation_history"].append({"speaker": "user", "text": voice_text})

    def process_query(self, query):
        # 1. Obter contexto relevante do RAG
        rag_context = self.rag_service.get_formatted_context(query)
        
        # 2. Combinar com o contexto interno da IA
        # Aumentar a complexidade do contexto conforme necessário para o modelo
        history_summary = " ".join([f"{item['speaker']}: {item['text']}" for item in self.current_context['conversation_history'][-2:]])
        full_context = f"Game: {self.current_context['game']}. History: {history_summary}. User: {query}. Relevant Info: {rag_context}"

        # --- Future integration with GameService ---
        # If 'query' is a game-specific command or question, AIService could delegate to GameService
        # Example:
        # if "what should I do" in query.lower() and self.current_context["game"]:
        #     game_strategy = self.game_service.get_current_game_ai()
        #     if game_strategy:
        #         # Assuming 'Game' object can be obtained from VisionService or passed directly
        #         dummy_game_state = Game() # Placeholder
        #         action = game_strategy.Act(dummy_game_state, self.game_service)
        #         # Process action into a natural language response
        #         # generated_text = f"Based on the game state, you should perform action: {action_to_text(action)}"
        #         # For now, just a placeholder.
        #         pass
        # --- End Future integration ---

        generated_text = ""
        # 3. Gerar resposta usando o thinking model ou fallback
        if self.thinking_endpoint and self.thinking_model_name:
            print(f"Using external thinking model: {self.thinking_model_name} at {self.thinking_endpoint}")
            headers = {"Content-Type": "application/json"}
            if self.thinking_api_key:
                headers["Authorization"] = f"Bearer {self.thinking_api_key}"
            
            try:
                # O formato da requisição e resposta depende da API do modelo externo
                payload = {"model": self.thinking_model_name, "prompt": full_context, "max_tokens": 50}
                response = requests.post(self.thinking_endpoint, headers=headers, json=payload, timeout=10)
                response.raise_for_status() # Lança exceção para erros HTTP
                
                # Assumindo que a resposta do modelo externo é um JSON com um campo 'text'
                external_model_output = response.json()
                generated_text = external_model_output.get("text", "").strip()
                if not generated_text:
                    print("External thinking model returned empty text. Falling back to local pipeline.")
                    generated_text = self.dialog_pipeline(full_context, max_new_tokens=50)[0]['generated_text']

            except requests.exceptions.RequestException as e:
                print(f"Error calling external thinking model: {e}. Falling back to local pipeline.")
                generated_text = self.dialog_pipeline(full_context, max_new_tokens=50)[0]['generated_text']
            except Exception as e:
                print(f"Unexpected error with external thinking model response: {e}. Falling back to local pipeline.")
                generated_text = self.dialog_pipeline(full_context, max_new_tokens=50)[0]['generated_text']
        else:
            print("No external thinking model configured. Using local pipeline.")
            try:
                generated_text = self.dialog_pipeline(full_context, max_new_tokens=50)[0]['generated_text']
            except Exception as e:
                print(f"Error generating AI response from local pipeline: {e}")
                generated_text = "Desculpe, tive um problema ao gerar a resposta."
        
        # Ensure generated_text is not empty
        if not generated_text:
            generated_text = "Não consegui gerar uma resposta neste momento."

        self.current_context["conversation_history"].append({"speaker": "ai", "text": generated_text})
        
        # 4. Determinar emoção (simplificado)
        emotion = "normal"
        if "help" in query.lower() or "problema" in query.lower():
            emotion = "alert"
        elif "feliz" in generated_text.lower() or "ótimo" in generated_text.lower():
            emotion = "happy"

        return {"text": generated_text, "emotion": emotion}