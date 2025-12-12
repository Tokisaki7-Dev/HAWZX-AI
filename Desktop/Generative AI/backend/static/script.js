const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

// Constantes de física
const GRAVITY = 980; // pixels/s² (9.8 m/s² * 100 para escala de jogo)
const MOVE_SPEED = 200; // pixels/s
const JUMP_STRENGTH = -400; // pixels/s (negativo porque Y cresce para baixo)
const GROUND_Y = 550; // Posição Y do chão

// Estado do Jogo
const gameState = {
    player: {
        x: 50,
        y: GROUND_Y,
        width: 50,
        height: 50,
        color: '#4A90E2',
        velocityX: 0,
        velocityY: 0,
        onGround: true,
        currentChunkX: 0,
        currentChunkY: 0
    },
    world: {
        backgroundImage: null,
        previousBackgroundImage: null, // Para transições suaves
        apiEndpoint: '',
        chunkSize: 800, // Tamanho do chunk em pixels
        seed: Math.floor(Math.random() * 1000000),
        chunks: new Map(), // Cache de chunks: key = "x,y", value = {image, biome}
        currentBiome: 'forest'
    },
    transition: {
        active: false,
        progress: 0,
        duration: 0.5, // 500ms de transição
        targetImage: null
    },
    loading: {
        active: false,
        message: ''
    },
    cache: {
        maxFrames: 10,
        frames: [],
        lastGeneratedTime: 0,
        minTimeBetweenGenerations: 5000 // 5 segundos entre gerações
    },
    keys: {
        left: false,
        right: false,
        up: false
    }
};

/**
 * Determina o bioma baseado na posição do chunk
 */
function getBiomeForChunk(chunkX, chunkY) {
    const hash = (chunkX * 73856093) ^ (chunkY * 19349663);
    const biomes = ['forest', 'desert', 'mountain', 'cave'];
    return biomes[Math.abs(hash) % biomes.length];
}

/**
 * Gera um prompt contextual baseado no bioma e posição
 */
function generatePromptForChunk(chunkX, chunkY, biome) {
    const prompts = {
        forest: "beautiful pixel art forest landscape, green grass, tall trees, rocks, blue sky, 2D platformer game style, side view",
        desert: "pixel art desert landscape, sand dunes, cacti, hot sun, 2D platformer game style, side view",
        mountain: "pixel art mountain landscape, rocky terrain, snow peaks, clouds, 2D platformer game style, side view",
        cave: "pixel art underground cave, stalactites, crystals, dark atmosphere, 2D platformer game style, side view"
    };
    return prompts[biome] || prompts.forest;
}

/**
 * Obtém ou gera um chunk
 */
async function getChunk(chunkX, chunkY) {
    const key = `${chunkX},${chunkY}`;
    
    // Verifica se já está em cache
    if (gameState.world.chunks.has(key)) {
        console.log(`Chunk ${key} carregado do cache`);
        return gameState.world.chunks.get(key);
    }
    
    // Gera novo chunk
    const biome = getBiomeForChunk(chunkX, chunkY);
    const prompt = generatePromptForChunk(chunkX, chunkY, biome);
    
    console.log(`Gerando novo chunk ${key} - Bioma: ${biome}`);
    
    const chunk = await generateChunkImage(prompt, biome);
    
    // Armazena no cache
    gameState.world.chunks.set(key, chunk);
    
    // Limita o tamanho do cache (mantém apenas os 9 chunks mais recentes)
    if (gameState.world.chunks.size > 9) {
        const firstKey = gameState.world.chunks.keys().next().value;
        gameState.world.chunks.delete(firstKey);
    }
    
    return chunk;
}

/**
 * Gera a imagem de um chunk via API
 */
async function generateChunkImage(prompt, biome) {
    // Ativa indicador de loading
    gameState.loading.active = true;
    gameState.loading.message = `Gerando ${biome}...`;
    
    try {
        const response = await fetch(`${gameState.world.apiEndpoint}/generate-frame`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ prompt })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        const result = await new Promise((resolve) => {
            const img = new Image();
            img.onload = () => {
                resolve({ image: img, biome });
            };
            img.onerror = () => {
                console.error('Erro ao carregar imagem do chunk');
                resolve({ image: null, biome });
            };
            img.src = data.image_url;
        });
        
        // Desativa loading
        gameState.loading.active = false;
        gameState.loading.message = '';
        
        return result;
    } catch (error) {
        console.error('Erro ao gerar chunk:', error);
        gameState.loading.active = false;
        gameState.loading.message = '';
        return { image: null, biome };
    }
}

/**
 * Chama o backend para gerar um novo frame do mundo.
 */
async function generateInitialFrame() {
    console.log("Carregando chunk inicial do mundo...");
    
    // Gera o chunk inicial (0, 0)
    const initialChunk = await getChunk(0, 0);
    
    if (initialChunk.image) {
        gameState.world.backgroundImage = initialChunk.image;
        gameState.world.currentBiome = initialChunk.biome;
        console.log(`Chunk inicial carregado - Bioma: ${initialChunk.biome}`);
    }
    
    // Pré-carrega chunks adjacentes em background
    setTimeout(() => {
        preloadAdjacentChunks(0, 0);
    }, 1000);
}

/**
 * Pré-carrega chunks adjacentes para transições suaves
 */
async function preloadAdjacentChunks(chunkX, chunkY) {
    const adjacentChunks = [
        [chunkX - 1, chunkY],
        [chunkX + 1, chunkY],
        [chunkX, chunkY - 1],
        [chunkX, chunkY + 1]
    ];
    
    for (const [x, y] of adjacentChunks) {
        await getChunk(x, y);
    }
    
    console.log('Chunks adjacentes pré-carregados');
}

/**
 * Configura os controles do teclado
 */
function setupControls() {
    document.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowLeft' || e.key === 'a' || e.key === 'A') {
            gameState.keys.left = true;
        }
        if (e.key === 'ArrowRight' || e.key === 'd' || e.key === 'D') {
            gameState.keys.right = true;
        }
        if (e.key === 'ArrowUp' || e.key === 'w' || e.key === 'W' || e.key === ' ') {
            gameState.keys.up = true;
        }
    });

    document.addEventListener('keyup', (e) => {
        if (e.key === 'ArrowLeft' || e.key === 'a' || e.key === 'A') {
            gameState.keys.left = false;
        }
        if (e.key === 'ArrowRight' || e.key === 'd' || e.key === 'D') {
            gameState.keys.right = false;
        }
        if (e.key === 'ArrowUp' || e.key === 'w' || e.key === 'W' || e.key === ' ') {
            gameState.keys.up = false;
        }
    });
}

/**
 * Atualiza a lógica do jogo (física e movimento)
 */
function update(deltaTime) {
    const { player, keys } = gameState;
    
    // Atualiza transição se ativa
    if (gameState.transition.active) {
        gameState.transition.progress += deltaTime / gameState.transition.duration;
        
        if (gameState.transition.progress >= 1) {
            // Transição completa
            gameState.transition.active = false;
            gameState.transition.progress = 1;
            gameState.world.backgroundImage = gameState.transition.targetImage;
            gameState.world.previousBackgroundImage = null;
            gameState.transition.targetImage = null;
        }
    }

    // Movimento horizontal
    if (keys.left) {
        player.velocityX = -MOVE_SPEED;
    } else if (keys.right) {
        player.velocityX = MOVE_SPEED;
    } else {
        player.velocityX = 0;
    }

    // Pulo
    if (keys.up && player.onGround) {
        player.velocityY = JUMP_STRENGTH;
        player.onGround = false;
    }

    // Aplica gravidade
    if (!player.onGround) {
        player.velocityY += GRAVITY * deltaTime;
    }

    // Atualiza posição
    player.x += player.velocityX * deltaTime;
    player.y += player.velocityY * deltaTime;

    // Colisão com as bordas horizontais
    if (player.x < 0) {
        player.x = 0;
    }
    if (player.x + player.width > canvas.width) {
        player.x = canvas.width - player.width;
    }

    // Colisão com o chão
    if (player.y + player.height >= GROUND_Y) {
        player.y = GROUND_Y - player.height;
        player.velocityY = 0;
        player.onGround = true;
    }
    
    // Detecta mudança de chunk
    const newChunkX = Math.floor(player.x / gameState.world.chunkSize);
    const newChunkY = Math.floor(player.y / gameState.world.chunkSize);
    
    if (newChunkX !== player.currentChunkX || newChunkY !== player.currentChunkY) {
        player.currentChunkX = newChunkX;
        player.currentChunkY = newChunkY;
        loadChunk(newChunkX, newChunkY);
    }
}

/**
 * Carrega um novo chunk quando o jogador se move
 */
async function loadChunk(chunkX, chunkY) {
    console.log(`Mudando para chunk (${chunkX}, ${chunkY})`);
    
    const chunk = await getChunk(chunkX, chunkY);
    
    if (chunk.image) {
        // Inicia transição suave
        startTransition(chunk.image, chunk.biome);
        
        // Pré-carrega chunks adjacentes
        preloadAdjacentChunks(chunkX, chunkY);
    }
}

/**
 * Inicia uma transição suave entre chunks
 */
function startTransition(newImage, newBiome) {
    if (!gameState.world.backgroundImage) {
        // Se não há imagem anterior, aplica diretamente
        gameState.world.backgroundImage = newImage;
        gameState.world.currentBiome = newBiome;
        return;
    }
    
    // Salva imagem anterior e inicia transição
    gameState.world.previousBackgroundImage = gameState.world.backgroundImage;
    gameState.transition.active = true;
    gameState.transition.progress = 0;
    gameState.transition.targetImage = newImage;
    gameState.world.currentBiome = newBiome;
}

/**
 * Desenha todos os elementos do jogo
 */
function draw() {
    // Limpa o canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Desenha o fundo com transição suave
    if (gameState.transition.active && gameState.world.previousBackgroundImage) {
        // Desenha imagem antiga
        ctx.globalAlpha = 1 - gameState.transition.progress;
        ctx.drawImage(gameState.world.previousBackgroundImage, 0, 0, canvas.width, canvas.height);
        
        // Desenha imagem nova com fade-in
        ctx.globalAlpha = gameState.transition.progress;
        ctx.drawImage(gameState.transition.targetImage, 0, 0, canvas.width, canvas.height);
        
        // Restaura opacidade
        ctx.globalAlpha = 1;
    } else if (gameState.world.backgroundImage) {
        ctx.drawImage(gameState.world.backgroundImage, 0, 0, canvas.width, canvas.height);
    } else {
        // Gradiente de céu
        const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
        gradient.addColorStop(0, '#87CEEB');
        gradient.addColorStop(1, '#E0F6FF');
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // Chão
        ctx.fillStyle = '#8B7355';
        ctx.fillRect(0, GROUND_Y, canvas.width, canvas.height - GROUND_Y);
        
        // Texto de carregamento
        ctx.fillStyle = 'white';
        ctx.textAlign = 'center';
        ctx.font = '20px Arial';
        ctx.fillText("Carregando cenário gerado por IA...", canvas.width / 2, 30);
    }

    // Desenha o jogador
    const { player } = gameState;
    ctx.fillStyle = player.color;
    ctx.fillRect(player.x, player.y, player.width, player.height);
    
    // Borda do jogador
    ctx.strokeStyle = '#2E5C8A';
    ctx.lineWidth = 2;
    ctx.strokeRect(player.x, player.y, player.width, player.height);

    // Indicador de loading
    if (gameState.loading.active) {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.6)';
        ctx.fillRect(canvas.width / 2 - 150, canvas.height / 2 - 40, 300, 80);
        
        ctx.fillStyle = 'white';
        ctx.textAlign = 'center';
        ctx.font = '18px Arial';
        ctx.fillText(gameState.loading.message, canvas.width / 2, canvas.height / 2);
        
        // Spinner animado
        const spinnerRadius = 15;
        const spinnerX = canvas.width / 2;
        const spinnerY = canvas.height / 2 + 25;
        const angle = (Date.now() / 100) % (2 * Math.PI);
        
        ctx.strokeStyle = 'white';
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.arc(spinnerX, spinnerY, spinnerRadius, angle, angle + Math.PI * 1.5);
        ctx.stroke();
    }

    // Instruções e debug info
    ctx.fillStyle = 'black';
    ctx.textAlign = 'left';
    ctx.font = '14px Arial';
    ctx.fillText("Controles: ← → (Mover) | ↑ / Espaço (Pular)", 10, canvas.height - 30);
    
    // Informações de debug
    ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
    ctx.fillRect(10, 10, 250, 80);
    ctx.fillStyle = 'white';
    ctx.font = '12px monospace';
    ctx.fillText(`Chunk: (${player.currentChunkX}, ${player.currentChunkY})`, 20, 30);
    ctx.fillText(`Bioma: ${gameState.world.currentBiome}`, 20, 50);
    ctx.fillText(`Chunks em cache: ${gameState.world.chunks.size}`, 20, 70);
    ctx.fillText(`Seed: ${gameState.world.seed}`, 20, 90);
}

let lastTime = 0;
function gameLoop(timestamp) {
    const deltaTime = (timestamp - lastTime) / 1000;
    lastTime = timestamp;

    update(deltaTime);
    draw();

    requestAnimationFrame(gameLoop);
}

// --- INICIALIZAÇÃO ---
async function main() {
    console.log("Iniciando o jogo...");
    setupControls(); // Configura os controles do teclado
    await generateInitialFrame(); // Gera o primeiro frame do mundo
    requestAnimationFrame(gameLoop); // Inicia o loop do jogo
}

main();