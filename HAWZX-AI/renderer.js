// Este script é executado no processo de renderização (na página index.html).
// Ele é responsável por interagir com a DOM e se comunicar com o backend
// através da API exposta pelo preload.js.

const characterImage = document.getElementById('character-animation');
let currentAnimationPath = '';

async function updateCharacter() {
    // Usa a função 'getCharacterState' que foi exposta no 'window.api' pelo preload.js
    const stateData = await window.api.getCharacterState();

    if (stateData && stateData.animation) {
        const newAnimationPath = stateData.animation;

        // Só atualiza a imagem se o caminho da animação mudou,
        // para evitar que o GIF reinicie a cada segundo.
        if (newAnimationPath !== currentAnimationPath) {
            console.log(`Mudando animação para: ${newAnimationPath}`);
            // O 'file://' é necessário para o Electron carregar arquivos locais.
            // Usamos um truque com timestamp para forçar o reload do GIF se o caminho for o mesmo
            // mas quisermos reiniciar a animação (útil no futuro).
            characterImage.src = `file:///${newAnimationPath.replace(/\\/g, '/')}`;
            currentAnimationPath = newAnimationPath;
        }
    } else {
        console.log("Não foi possível obter o estado do personagem ou animação não definida.");
    }
}

// Inicia o loop para atualizar o personagem a cada 1 segundo (1000 ms).
setInterval(updateCharacter, 1000);

// Chama a função uma vez no início para não esperar o primeiro segundo.
updateCharacter();