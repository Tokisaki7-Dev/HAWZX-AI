import pytest
from src.ai.service import AIService

@pytest.fixture
def ai_service():
    """
    Fixture do pytest para criar uma instância do AIService para os testes.
    """
    return AIService()

def test_ai_service_initialization(ai_service):
    """
    Testa se o AIService é inicializado sem erros.
    """
    assert ai_service is not None

def test_generate_response_returns_correct_format(ai_service):
    """
    Testa se o método generate_response retorna um dicionário com as chaves esperadas.
    """
    context = {"user_command": "me dê uma dica"}
    response = ai_service.generate_response(context)
    
    assert isinstance(response, dict)
    assert "response_text" in response
    assert "emotion" in response