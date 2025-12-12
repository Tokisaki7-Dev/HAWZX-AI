// ===== MINECRAFT-STYLE INFINITE WORLD GAME =====
// Sistema de chunks infinitos com física avançada

const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

// === CONFIGURATION ===
const CONFIG = {
    CANVAS_WIDTH: 800,
    CANVAS_HEIGHT: 600,
    CHUNK_SIZE: 512,
    BLOCK_SIZE: 16,
    PLAYER_SIZE: 48,  // Increased from 32 to 48 for better visibility
    GRAVITY: 980,
    JUMP_STRENGTH: 400,
    MOVE_SPEED: 200,
    RUN_SPEED: 350,
    TERMINAL_VELOCITY: 500,
    WORLD_SEED: Math.floor(Math.random() * 1000000)
};

// === WORLD STATE ===
const world = {
    chunks: new Map(),
    currentBiome: 'plains',
    loadedChunks: 0,
    seed: CONFIG.WORLD_SEED
};

// === PLAYER STATE ===
const player = {
    x: CONFIG.CANVAS_WIDTH / 2,
    y: 150,  // Start at 150px instead of 100px to be closer to ground
    vx: 0,
    vy: 0,
    width: CONFIG.PLAYER_SIZE,
    height: CONFIG.PLAYER_SIZE,
    onGround: false,
    canDoubleJump: true,
    jumpBuffer: 0,
    coyoteTime: 0,
    hp: 100,
    maxHp: 100,
    level: 1,
    exp: 0
};

// === CAMERA ===
const camera = {
    x: 0,
    y: 0,
    targetX: 0,
    targetY: 0,
    smoothing: 0.1
};

// === INPUT ===
const keys = {};
window.addEventListener('keydown', (e) => {
    keys[e.key.toLowerCase()] = true;
    
    // Fix: Handle SPACE key properly
    if (e.key === ' ') {
        e.preventDefault();
        keys['space'] = true;
    }
});

window.addEventListener('keyup', (e) => {
    keys[e.key.toLowerCase()] = false;
    
    if (e.key === ' ') {
        keys['space'] = false;
    }
});

// === CHUNK SYSTEM ===
function getChunkKey(chunkX, chunkY) {
    return `${chunkX},${chunkY}`;
}

function getChunkCoords(worldX, worldY) {
    const chunkX = Math.floor(worldX / CONFIG.CHUNK_SIZE);
    const chunkY = Math.floor(worldY / CONFIG.CHUNK_SIZE);
    return { chunkX, chunkY };
}

async function loadChunk(chunkX, chunkY) {
    const key = getChunkKey(chunkX, chunkY);
    
    if (world.chunks.has(key)) {
        return world.chunks.get(key);
    }
    
    try {
        updateLoadingMessage(`Carregando chunk (${chunkX}, ${chunkY})...`);
        
        const response = await fetch('/generate-chunk', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                chunk_x: chunkX,
                chunk_y: chunkY,
                seed: world.seed
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Create image from base64
        const img = new Image();
        await new Promise((resolve, reject) => {
            img.onload = resolve;
            img.onerror = reject;
            img.src = `data:image/png;base64,${data.image}`;
        });
        
        const chunk = {
            x: chunkX,
            y: chunkY,
            image: img,
            collisionMap: data.collision_map,
            biome: data.biome,
            worldX: chunkX * CONFIG.CHUNK_SIZE,
            worldY: chunkY * CONFIG.CHUNK_SIZE
        };
        
        world.chunks.set(key, chunk);
        world.loadedChunks++;
        world.currentBiome = data.biome;
        
        updateChunkCounter();
        updateBiomeDisplay();
        
        return chunk;
    } catch (error) {
        console.error('Error loading chunk:', chunkX, chunkY, error);
        // Return a placeholder chunk to avoid breaking the game
        return createPlaceholderChunk(chunkX, chunkY);
    }
}

function createPlaceholderChunk(chunkX, chunkY) {
    // Create a simple colored chunk as fallback
    const canvas = document.createElement('canvas');
    canvas.width = CONFIG.CHUNK_SIZE;
    canvas.height = CONFIG.CHUNK_SIZE;
    const ctx = canvas.getContext('2d');
    
    // Fill with a grid pattern
    ctx.fillStyle = '#2a9d8f';
    ctx.fillRect(0, 0, CONFIG.CHUNK_SIZE, CONFIG.CHUNK_SIZE);
    
    const img = new Image();
    img.src = canvas.toDataURL();
    
    const chunk = {
        x: chunkX,
        y: chunkY,
        image: img,
        collisionMap: Array(32).fill(null).map(() => Array(32).fill(false)),
        biome: 'plains',
        worldX: chunkX * CONFIG.CHUNK_SIZE,
        worldY: chunkY * CONFIG.CHUNK_SIZE
    };
    
    world.chunks.set(getChunkKey(chunkX, chunkY), chunk);
    world.loadedChunks++;
    
    return chunk;
}

async function loadSurroundingChunks(centerChunkX, centerChunkY, radius = 2) {
    const promises = [];
    
    for (let dy = -radius; dy <= radius; dy++) {
        for (let dx = -radius; dx <= radius; dx++) {
            const chunkX = centerChunkX + dx;
            const chunkY = centerChunkY + dy;
            promises.push(loadChunk(chunkX, chunkY));
        }
    }
    
    await Promise.all(promises);
}

// === COLLISION DETECTION ===
function checkCollision(x, y, width, height) {
    const { chunkX, chunkY } = getChunkCoords(x + width/2, y + height);
    const chunk = world.chunks.get(getChunkKey(chunkX, chunkY));
    
    if (!chunk || !chunk.collisionMap) {
        return false;
    }
    
    // Convert world coordinates to chunk-local coordinates
    const localX = x - chunk.worldX;
    const localY = y - chunk.worldY;
    
    // Check corners and center
    const points = [
        { x: localX, y: localY },  // Top-left
        { x: localX + width, y: localY },  // Top-right
        { x: localX, y: localY + height },  // Bottom-left
        { x: localX + width, y: localY + height },  // Bottom-right
        { x: localX + width/2, y: localY + height }  // Bottom-center
    ];
    
    for (const point of points) {
        const blockX = Math.floor(point.x / CONFIG.BLOCK_SIZE);
        const blockY = Math.floor(point.y / CONFIG.BLOCK_SIZE);
        
        if (blockY >= 0 && blockY < chunk.collisionMap.length &&
            blockX >= 0 && blockX < chunk.collisionMap[0].length) {
            if (chunk.collisionMap[blockY][blockX]) {
                return true;
            }
        }
    }
    
    return false;
}

function checkGroundCollision() {
    return checkCollision(player.x, player.y + 2, player.width, player.height);
}

// === PHYSICS ===
function updatePhysics(deltaTime) {
    const dt = Math.min(deltaTime, 0.033); // Cap at 30 FPS for stability
    
    // Gravity
    if (!player.onGround) {
        player.vy += CONFIG.GRAVITY * dt;
        player.vy = Math.min(player.vy, CONFIG.TERMINAL_VELOCITY);
    }
    
    // Horizontal movement
    let targetVx = 0;
    const isRunning = keys['shift'];
    const maxSpeed = isRunning ? CONFIG.RUN_SPEED : CONFIG.MOVE_SPEED;
    const acceleration = player.onGround ? 1000 : 600; // 60% air control
    
    if (keys['a'] || keys['arrowleft']) {
        targetVx = -maxSpeed;
    }
    if (keys['d'] || keys['arrowright']) {
        targetVx = maxSpeed;
    }
    
    // Apply acceleration
    if (targetVx !== 0) {
        player.vx += (targetVx - player.vx) * acceleration * dt / 1000;
    } else {
        // Apply friction
        const friction = player.onGround ? 0.8 : 0.98;
        player.vx *= Math.pow(friction, dt * 60);
        if (Math.abs(player.vx) < 1) player.vx = 0;
    }
    
    // Jump
    if (player.jumpBuffer > 0) {
        player.jumpBuffer -= dt;
    }
    
    if (player.coyoteTime > 0 && !player.onGround) {
        player.coyoteTime -= dt;
    }
    
    if (keys['space'] || keys['w'] || keys['arrowup']) {
        if (!keys._jumpPressed) {
            keys._jumpPressed = true;
            player.jumpBuffer = 0.1;
            
            // Ground jump
            if (player.onGround || player.coyoteTime > 0) {
                player.vy = -CONFIG.JUMP_STRENGTH;
                player.canDoubleJump = true;
                player.coyoteTime = 0;
            }
            // Double jump
            else if (player.canDoubleJump) {
                player.vy = -CONFIG.JUMP_STRENGTH * 0.875;
                player.canDoubleJump = false;
            }
        }
    } else {
        keys._jumpPressed = false;
        
        // Variable jump height
        if (player.vy < 0) {
            player.vy *= 0.95;
        }
    }
    
    // Update position
    const nextX = player.x + player.vx * dt;
    const nextY = player.y + player.vy * dt;
    
    // Horizontal collision
    if (!checkCollision(nextX, player.y, player.width, player.height)) {
        player.x = nextX;
    } else {
        player.vx = 0;
    }
    
    // Vertical collision
    const wasOnGround = player.onGround;
    
    if (!checkCollision(player.x, nextY, player.width, player.height)) {
        player.y = nextY;
        player.onGround = false;
    } else {
        if (player.vy > 0) {
            // Landing
            player.onGround = true;
            player.canDoubleJump = true;
            player.coyoteTime = 0.1;
        }
        player.vy = 0;
    }
    
    // Check ground again for coyote time
    if (!player.onGround && wasOnGround) {
        player.coyoteTime = 0.1;
    }
    
    player.onGround = checkGroundCollision();
}

// === CAMERA ===
function updateCamera() {
    // Target camera on player
    camera.targetX = player.x - CONFIG.CANVAS_WIDTH / 2;
    camera.targetY = player.y - CONFIG.CANVAS_HEIGHT / 2;
    
    // Smooth camera movement
    camera.x += (camera.targetX - camera.x) * camera.smoothing;
    camera.y += (camera.targetY - camera.y) * camera.smoothing;
}

// === RENDERING ===
function render() {
    // Clear canvas
    ctx.fillStyle = '#87CEEB';
    ctx.fillRect(0, 0, CONFIG.CANVAS_WIDTH, CONFIG.CANVAS_HEIGHT);
    
    ctx.save();
    ctx.translate(-camera.x, -camera.y);
    
    // Render visible chunks
    const startChunkX = Math.floor(camera.x / CONFIG.CHUNK_SIZE) - 1;
    const startChunkY = Math.floor(camera.y / CONFIG.CHUNK_SIZE) - 1;
    const endChunkX = Math.ceil((camera.x + CONFIG.CANVAS_WIDTH) / CONFIG.CHUNK_SIZE) + 1;
    const endChunkY = Math.ceil((camera.y + CONFIG.CANVAS_HEIGHT) / CONFIG.CHUNK_SIZE) + 1;
    
    for (let cy = startChunkY; cy <= endChunkY; cy++) {
        for (let cx = startChunkX; cx <= endChunkX; cx++) {
            const chunk = world.chunks.get(getChunkKey(cx, cy));
            if (chunk && chunk.image) {
                ctx.drawImage(chunk.image, chunk.worldX, chunk.worldY);
            }
        }
    }
    
    // Render player with better visibility
    // Body
    ctx.fillStyle = '#4A90E2';  // Nice blue color
    ctx.fillRect(player.x, player.y, player.width, player.height);
    
    // Border/outline for better visibility
    ctx.strokeStyle = '#2C5F8D';
    ctx.lineWidth = 2;
    ctx.strokeRect(player.x, player.y, player.width, player.height);
    
    // Face - eyes
    ctx.fillStyle = '#FFFFFF';
    const eyeSize = 8;
    const eyeY = player.y + player.height * 0.3;
    ctx.fillRect(player.x + player.width * 0.25 - eyeSize/2, eyeY, eyeSize, eyeSize);
    ctx.fillRect(player.x + player.width * 0.75 - eyeSize/2, eyeY, eyeSize, eyeSize);
    
    // Pupils
    ctx.fillStyle = '#000000';
    const pupilSize = 4;
    ctx.fillRect(player.x + player.width * 0.25 - pupilSize/2, eyeY + 2, pupilSize, pupilSize);
    ctx.fillRect(player.x + player.width * 0.75 - pupilSize/2, eyeY + 2, pupilSize, pupilSize);
    
    // Mouth
    ctx.fillStyle = '#000000';
    const mouthY = player.y + player.height * 0.6;
    ctx.fillRect(player.x + player.width * 0.3, mouthY, player.width * 0.4, 3);
    
    // Ground indicator (feet glow when on ground)
    if (player.onGround) {
        ctx.fillStyle = 'rgba(0, 255, 0, 0.5)';
        ctx.fillRect(player.x, player.y + player.height - 4, player.width, 4);
    }
    
    ctx.restore();
    
    // HUD
    renderHUD();
}

function renderHUD() {
    // Health bar
    const barWidth = 200;
    const barHeight = 20;
    const barX = 20;
    const barY = 20;
    
    ctx.fillStyle = '#000';
    ctx.fillRect(barX - 2, barY - 2, barWidth + 4, barHeight + 4);
    
    ctx.fillStyle = '#ff0000';
    ctx.fillRect(barX, barY, barWidth, barHeight);
    
    ctx.fillStyle = '#00ff00';
    const healthWidth = (player.hp / player.maxHp) * barWidth;
    ctx.fillRect(barX, barY, healthWidth, barHeight);
    
    ctx.fillStyle = '#fff';
    ctx.font = 'bold 14px Arial';
    ctx.textAlign = 'center';
    ctx.fillText(`HP: ${player.hp}/${player.maxHp}`, barX + barWidth/2, barY + 15);
    
    // Level and position
    ctx.textAlign = 'left';
    ctx.fillText(`Nível: ${player.level}`, barX, barY + 40);
    ctx.fillText(`Posição: (${Math.floor(player.x)}, ${Math.floor(player.y)})`, barX, barY + 60);
    ctx.fillText(`Velocidade: ${Math.floor(Math.abs(player.vx))} px/s`, barX, barY + 80);
    
    // Debug info
    if (keys['f3']) {
        ctx.fillText(`Chunks carregados: ${world.loadedChunks}`, barX, barY + 100);
        ctx.fillText(`No chão: ${player.onGround}`, barX, barY + 120);
        ctx.fillText(`Pode pulo duplo: ${player.canDoubleJump}`, barX, barY + 140);
        ctx.fillText(`Coyote time: ${player.coyoteTime.toFixed(2)}s`, barX, barY + 160);
    }
}

// === UI UPDATES ===
function updateLoadingMessage(message) {
    const loadingMsg = document.getElementById('loading-message');
    if (loadingMsg) {
        loadingMsg.textContent = message;
    }
}

function updateLoadingProgress(percent) {
    const loadingBar = document.getElementById('loading-progress');
    if (loadingBar) {
        loadingBar.style.width = `${percent}%`;
    }
}

function updateChunkCounter() {
    const counter = document.getElementById('chunk-counter');
    if (counter) {
        counter.textContent = world.loadedChunks;
    }
}

function updateBiomeDisplay() {
    const biomeEl = document.getElementById('biome-display');
    if (biomeEl) {
        const biomeNames = {
            'plains': 'Planícies',
            'forest': 'Floresta',
            'mountains': 'Montanhas',
            'desert': 'Deserto',
            'ocean': 'Oceano',
            'hills': 'Colinas'
        };
        biomeEl.textContent = biomeNames[world.currentBiome] || world.currentBiome;
    }
}

function updateWorldSeed() {
    const seedEl = document.getElementById('world-seed');
    if (seedEl) {
        seedEl.textContent = world.seed;
    }
}

function hideLoadingScreen() {
    const loadingScreen = document.getElementById('loading-screen');
    if (loadingScreen) {
        loadingScreen.classList.add('hidden');
    }
}

// === GAME LOOP ===
let lastTime = 0;
let fpsFrames = 0;
let fpsTime = 0;

function gameLoop(currentTime) {
    const deltaTime = (currentTime - lastTime) / 1000;
    lastTime = currentTime;
    
    // FPS counter
    fpsFrames++;
    fpsTime += deltaTime;
    if (fpsTime >= 1) {
        const fpsCounter = document.getElementById('fps-counter');
        if (fpsCounter) {
            fpsCounter.textContent = fpsFrames;
        }
        fpsFrames = 0;
        fpsTime = 0;
    }
    
    // Update
    updatePhysics(deltaTime);
    updateCamera();
    
    // Load chunks dynamically
    const playerChunk = getChunkCoords(player.x, player.y);
    loadChunk(playerChunk.chunkX, playerChunk.chunkY);
    
    // Render
    render();
    
    requestAnimationFrame(gameLoop);
}

// === INITIALIZATION ===
async function init() {
    console.log('🎮 Noki AI - Minecraft-style Infinite World');
    console.log(`🌍 World Seed: ${world.seed}`);
    
    updateWorldSeed();
    updateLoadingMessage('Inicializando...');
    updateLoadingProgress(10);
    
    // Get world info (optional - continue if fails)
    try {
        const response = await fetch('/world-info');
        if (response.ok) {
            const worldInfo = await response.json();
            console.log('World configuration:', worldInfo);
        }
    } catch (error) {
        console.warn('Could not fetch world info:', error);
    }
    
    updateLoadingProgress(30);
    
    // Load initial chunks with error handling
    try {
        const playerChunk = getChunkCoords(player.x, player.y);
        updateLoadingMessage('Carregando chunks iniciais...');
        
        // Load chunks with timeout
        const loadPromise = loadSurroundingChunks(playerChunk.chunkX, playerChunk.chunkY, 1);
        const timeoutPromise = new Promise((resolve) => setTimeout(resolve, 5000));
        
        await Promise.race([loadPromise, timeoutPromise]);
        
            // Try to find ground and spawn player on it
            updateLoadingMessage('Encontrando terreno...');
            const spawnChunk = world.chunks.get(getChunkKey(playerChunk.chunkX, playerChunk.chunkY));
            if (spawnChunk && spawnChunk.collisionMap) {
                // Find ground at player's X position
                const localX = Math.floor((player.x - spawnChunk.worldX) / CONFIG.BLOCK_SIZE);
                if (localX >= 0 && localX < spawnChunk.collisionMap[0].length) {
                    // Find first solid block from top
                    for (let y = 0; y < spawnChunk.collisionMap.length; y++) {
                        if (spawnChunk.collisionMap[y][localX]) {
                            // Spawn player on top of this block
                            player.y = spawnChunk.worldY + (y * CONFIG.BLOCK_SIZE) - player.height;
                            console.log(`👤 Player spawned at ground level: Y=${player.y}`);
                            break;
                        }
                    }
                }
            }
        
        updateLoadingProgress(100);
        updateLoadingMessage('Mundo pronto!');
    } catch (error) {
        console.error('Error loading initial chunks:', error);
        updateLoadingMessage('Iniciando com chunks básicos...');
        
        // Create at least one chunk at player position
        const playerChunk = getChunkCoords(player.x, player.y);
        createPlaceholderChunk(playerChunk.chunkX, playerChunk.chunkY);
    }
    
    // Always start the game after timeout
    setTimeout(() => {
        hideLoadingScreen();
        
        // Start game loop
        lastTime = performance.now();
        requestAnimationFrame(gameLoop);
        
        console.log('✅ Game started!');
        console.log('Controls:');
        console.log('  WASD/Arrows - Move');
        console.log('  SPACE - Jump (press twice for double jump)');
        console.log('  SHIFT - Run');
        console.log('  F3 - Debug info');
    }, 1000);
}

// Start game when page loads
window.addEventListener('load', init);
