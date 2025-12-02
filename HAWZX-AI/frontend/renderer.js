const websocket = new WebSocket("ws://localhost:8000/ws"); // Conectar ao backend FastAPI
const mascotAvatar = document.getElementById("mascot-avatar");
const chatMessages = document.getElementById("chat-messages");
const chatInput = document.getElementById("chat-input");

websocket.onopen = (event) => {
    console.log("WebSocket connected!");
    // Enviar dados iniciais, se necessário
    // Por exemplo, para iniciar a captura de tela no backend
    // websocket.send(JSON.stringify({ type: "start_screen_capture" }));
};

websocket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log("Message from backend:", data);

    // Atualizar mascote
    if (data.type === "ai_response" && data.emotion) {
        if (data.emotion === "talking") {
            mascotAvatar.src = "/static/talking.gif";
        } else if (data.emotion === "thinking") {
            mascotAvatar.src = "/static/thinking.gif";
        } else { // normal, happy, sad etc.
            mascotAvatar.src = "/static/idle.gif"; // Voltar ao idle por padrão
        }
    } else if (data.type === "vision_update") {
        // Pode-se adicionar lógica para mostrar um ícone de "vendo" ou "analisando"
        // mascotAvatar.src = "/static/thinking.gif"; // Exemplo
        console.log("Vision update received:", data);
        // Implementar lógica para atualizar o widget de status do jogo, se houver
    }


    // Adicionar mensagem ao chat
    if (data.type === "ai_response" && data.text) {
        const messageElement = document.createElement("p");
        messageElement.textContent = `HAWZX: ${data.text}`;
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight; // Scroll to bottom
    }
    // Outras atualizações do overlay...
};

websocket.onclose = (event) => {
    console.log("WebSocket closed.");
};

websocket.onerror = (error) => {
    console.error("WebSocket error:", error);
};

// Enviar mensagem do chat para o backend
chatInput.addEventListener("keypress", (event) => {
    if (event.key === "Enter" && chatInput.value.trim() !== "") {
        const message = { type: "chat_message", text: chatInput.value.trim() };
        websocket.send(JSON.stringify(message));
        
        const userMessageElement = document.createElement("p");
        userMessageElement.textContent = `Você: ${chatInput.value.trim()}`;
        chatMessages.appendChild(userMessageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        chatInput.value = "";
    }
});
