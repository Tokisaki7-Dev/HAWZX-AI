import chromadb
from chromadb.utils import embedding_functions
from pydantic import BaseModel, Field
from typing import List, Dict, Any
import logging

# Configuração do Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Modelos de Dados (Pydantic) ---

class RagQueryRequest(BaseModel):
    query: str
    gameId: str
    top_k: int = 3

class Source(BaseModel):
    title: str
    url: str

class RagQueryResponse(BaseModel):
    sources: List[Source]
    snippets: List[str]
    answer: str = Field(..., description="Resposta sintetizada por um LLM (simulada por enquanto).")

# --- Serviço RAG ---

class RagService:
    def __init__(self, host: str = "localhost", port: int = 8001):
        logger.info(f"Conectando ao ChromaDB em http://{host}:{port}...")
        self.client = chromadb.HttpClient(host=host, port=port)
        # Usando um modelo de embedding leve que roda localmente na CPU
        self.embedding_function = embedding_functions.DefaultHuggingFaceEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        logger.info("Cliente ChromaDB e função de embedding inicializados.")

    def _add_dummy_data_if_needed(self, collection_name: str):
        """Adiciona dados de exemplo a uma coleção se ela estiver vazia."""
        collection = self.client.get_collection(name=collection_name, embedding_function=self.embedding_function)
        if collection.count() == 0:
            logger.info(f"Coleção '{collection_name}' está vazia. Adicionando dados de exemplo.")
            collection.add(
                documents=[
                    "Para derrotar o Grimm na fase 2, você deve pular sobre seus ataques de espinhos e usar o dash para desviar das bolas de fogo.",
                    "A melhor build para necromancer iniciante em Diablo IV foca em minions e explosão de cadáveres.",
                    "Em Stardew Valley, o peixe-gato pode ser encontrado no rio durante a primavera e outono, apenas em dias chuvosos."
                ],
                metadatas=[
                    {"title": "Guia Grimm Fase 2", "url": "local://docs/grimm-f2.md"},
                    {"title": "Build Necro D4", "url": "local://docs/d4-necro-build.md"},
                    {"title": "Pesca Stardew", "url": "local://docs/stardew-fishing.md"}
                ],
                ids=["doc1", "doc2", "doc3"]
            )

    def query(self, request: RagQueryRequest) -> RagQueryResponse:
        collection = self.client.get_or_create_collection(name=request.gameId, embedding_function=self.embedding_function)
        self._add_dummy_data_if_needed(request.gameId)

        results = collection.query(query_texts=[request.query], n_results=request.top_k)

        # Por enquanto, a resposta é simulada. No futuro, um LLM geraria isso.
        answer = f"Resposta simulada para a pergunta: '{request.query}'. A busca retornou {len(results.get('ids', [[]])[0])} resultados."
        
        sources = [Source(**meta) for meta in results.get('metadatas', [[]])[0]]
        snippets = results.get('documents', [[]])[0]

        return RagQueryResponse(sources=sources, snippets=snippets, answer=answer)

# Instância única do serviço
rag_service = RagService()