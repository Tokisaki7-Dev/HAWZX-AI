import logging
from transformers import pipeline
from typing import Dict, Any

class AIEngine:
    """Serviço de IA para chat, geração, resumo, tradução e análise de sentimentos."""
    def __init__(self):
        self.models = {}
        self._load_models()

    def _load_models(self):
        """Carrega todos os modelos de IA definidos em uma configuração."""
        model_configs = {
            "chatbot": {"task": "conversational", "model": "microsoft/DialoGPT-medium", "description": "conversação (DialoGPT)"},
            "text_generator": {"task": "text-generation", "model": "gpt2", "description": "geração de texto (GPT-2)"},
            "summarizer": {"task": "summarization", "model": "facebook/bart-large-cnn", "description": "resumo (BART)"},
            "translator": {"task": "translation_en_to_pt", "model": "Helsinki-NLP/opus-mt-en-pt", "description": "tradução (Helsinki-NLP)"},
            "sentiment_analyzer": {"task": "sentiment-analysis", "model": "nlptown/bert-base-multilingual-uncased-sentiment", "description": "análise de sentimentos"}
        }

        for name, config in model_configs.items():
            try:
                logging.info(f"Carregando modelo de {config['description']}...")
                self.models[name] = pipeline(config["task"], model=config["model"])
                logging.info(f"Modelo de {config['description']} carregado com sucesso.")
            except Exception as e:
                self.models[name] = None
                logging.error(f"Falha ao carregar modelo de {config['description']}: {e}")

    @property
    def chatbot(self): return self.models.get("chatbot")
    @property
    def text_generator(self): return self.models.get("text_generator")
    @property
    def summarizer(self): return self.models.get("summarizer")
    @property
    def translator(self): return self.models.get("translator")
    @property
    def sentiment_analyzer(self): return self.models.get("sentiment_analyzer")

    def chat(self, text: str, persona: str) -> str:
        """Gera uma resposta de chat."""
        if not self.chatbot:
            logging.warning("Modelo de chat não carregado. Usando resposta simulada.")
            return f"Como {persona}, eu entendi que você disse: '{text}'. Minha resposta está sendo processada."

        try:
            # A persona pode ser usada para dar um contexto inicial ao chat, embora DialoGPT não a use nativamente.
            # Uma abordagem seria prefixar a primeira entrada, mas para simplicidade, mantemos a chamada direta.
            conversation = self.chatbot(text)
            return conversation.generated_responses[-1]
        except Exception as e:
            logging.error(f"Erro ao gerar resposta de chat: {e}")
            return "Desculpe, tive um problema ao processar sua pergunta."

    def generate_text(self, prompt: str, max_length: int = 50) -> str:
        """Gera um texto a partir de um prompt."""
        if not self.text_generator:
            logging.warning("Modelo de geração de texto não carregado.")
            return "Desculpe, o serviço de geração de texto não está disponível."
        try:
            generated = self.text_generator(prompt, max_length=max_length, num_return_sequences=1)
            return generated[0]['generated_text']
        except Exception as e:
            logging.error(f"Erro na geração de texto: {e}")
            return "Desculpe, não consegui gerar o texto."

    def summarize_text(self, text: str, min_length: int = 30, max_length: int = 130) -> str:
        """Gera um resumo de um texto."""
        if not self.summarizer:
            logging.warning("Modelo de resumo não carregado.")
            return "Desculpe, o serviço de resumo não está disponível."
        try:
            summary = self.summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
            return summary[0]['summary_text']
        except Exception as e:
            logging.error(f"Erro ao gerar resumo: {e}")
            return "Desculpe, não consegui resumir o texto."

    def translate_text(self, text: str) -> str:
        """Traduz um texto de inglês para português."""
        if not self.translator:
            logging.warning("Modelo de tradução não carregado.")
            return "Desculpe, o serviço de tradução não está disponível."
        try:
            translated = self.translator(text)
            return translated[0]['translation_text']
        except Exception as e:
            logging.error(f"Erro na tradução: {e}")
            return "Desculpe, não consegui traduzir o texto."

    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analisa o sentimento de um texto (de 1 a 5 estrelas)."""
        if not self.sentiment_analyzer:
            logging.warning("Modelo de análise de sentimentos não carregado.")
            return {"error": "Desculpe, o serviço de análise de sentimentos não está disponível."}
        try:
            # O pipeline retorna uma lista com um dicionário, pegamos o primeiro elemento.
            result = self.sentiment_analyzer(text)
            return result[0]
        except Exception as e:
            logging.error(f"Erro na análise de sentimentos: {e}")
            return {"error": "Desculpe, não consegui analisar o sentimento do texto."}

ai_engine = AIEngine()
