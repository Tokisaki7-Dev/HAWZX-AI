import pyttsx3
import speech_recognition as sr # Para STT (Speech-to-Text)
import threading # Para lidar com a fala em um thread separado

class VoiceService:
    def __init__(self):
        print("Initializing VoiceService...")
        self.engine = pyttsx3.init()
        # Configurar as propriedades da voz (ex: voz feminina, masculina, velocidade)
        # self.engine.setProperty('voice', 'brazil') # Exemplo, dependendo das vozes instaladas
        self.engine.setProperty('rate', 150) # Velocidade padrão
        self.emotion_presets = {
            "normal": {"rate": 150, "volume": 1.0},
            "alert": {"rate": 170, "volume": 1.2},
            "happy": {"rate": 160, "volume": 1.1},
            "sad": {"rate": 130, "volume": 0.9},
        }
        self.recognizer = sr.Recognizer()
        print("VoiceService initialized.")

    def _speak_thread(self, text, emotion):
        """Método auxiliar para rodar a fala em um thread separado."""
        preset = self.emotion_presets.get(emotion, self.emotion_presets["normal"])
        self.engine.setProperty('rate', preset["rate"])
        self.engine.setProperty('volume', preset["volume"])
        
        # O ajuste de tom (pitch) não é padrão no pyttsx3, pode exigir customização
        # através da seleção de voz ou bibliotecas adicionais como 'pydub' para manipulação de áudio.
        
        self.engine.say(text)
        self.engine.runAndWait()

    def speak(self, text, emotion="normal"):
        """Converte texto em fala com base na emoção."""
        print(f"HAWZX AI speaking ({emotion}): {text}")
        # Inicia a fala em um novo thread para não bloquear a execução principal
        speak_thread = threading.Thread(target=self._speak_thread, args=(text, emotion))
        speak_thread.start()

    def recognize_speech(self, source=None):
        """
        Captura áudio do microfone e o converte em texto.
        Usa o Google Web Speech API como fallback se o Whisper local não for implementado.
        """
        if source is None:
            with sr.Microphone() as source:
                print("Listening for speech...")
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source)
        else:
            audio = self.recognizer.listen(source) # Para usar com fontes de áudio específicas

        try:
            print("Recognizing speech...")
            # Tentativa de usar o Google Web Speech API como um exemplo simples
            # Para Whisper local, você precisaria de uma configuração mais complexa
            # Ex: text = self.recognizer.recognize_whisper(audio, model="base")
            text = self.recognizer.recognize_google(audio, language="pt-BR")
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
            return ""
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
            return ""
        except Exception as e:
            print(f"An unexpected error occurred during speech recognition: {e}")
            return ""

