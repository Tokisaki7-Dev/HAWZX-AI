// O preload.js atua como uma ponte segura entre o processo principal (Node.js)
// e o processo de renderização (a página web).
const { contextBridge } = require('electron');

// Expõe um objeto 'api' para a janela do renderizador (index.html)
// de forma segura.
contextBridge.exposeInMainWorld('api', {
  // Função para buscar o estado do personagem no backend
  getCharacterState: async () => {
    try {
      // Faz a requisição para o endpoint do backend que criamos anteriormente
      const response = await fetch('http://localhost:8000/character/state');
      if (!response.ok) {
        throw new Error(`Erro na requisição: ${response.statusText}`);
      }
      return await response.json();
    } catch (error) {
      console.error("Falha ao buscar estado do personagem:", error);
      return null; // Retorna nulo em caso de erro para o renderer tratar
    }
  }
});

console.log('Preload script carregado com sucesso!');