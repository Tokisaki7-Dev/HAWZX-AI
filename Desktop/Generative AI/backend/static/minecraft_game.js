// ===== MINECRAFT-STYLE INFINITE WORLD GAME =====
// Sistema de chunks infinitos com física avançada

const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

// === CONFIGURATION ===
const CONFIG = {
    CANVAS_WIDTH: 800,
    CANVAS_HEIGHT: 600,
    CHUNK_SIZE: 512,
    BLOCK_SIZE: 8, // Smaller tiles for JRPG-style detail
    PLAYER_SIZE: 24,  // JRPG chibi size
    MOVE_SPEED: 140,
    RUN_SPEED: 220,
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
    y: CONFIG.CANVAS_HEIGHT / 2,
    vx: 0,
    vy: 0,
    width: CONFIG.PLAYER_SIZE,
    height: CONFIG.PLAYER_SIZE,
    facing: 'down',
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
        
        // Create image from base64 (backend already returns data URL prefix)
        const img = new Image();
        const imageSrc = data.image.startsWith('data:image')
            ? data.image
            : `data:image/png;base64,${data.image}`;
        await new Promise((resolve, reject) => {
            img.onload = resolve;
            img.onerror = reject;
            img.src = imageSrc;
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
    
    // Draw a simple grass ground at bottom
    const tileCount = CONFIG.CHUNK_SIZE / CONFIG.BLOCK_SIZE;
    const groundRows = Math.max(4, Math.floor(tileCount * 0.15));
    ctx.fillStyle = '#3da35d';
    ctx.fillRect(0, CONFIG.CHUNK_SIZE - groundRows * CONFIG.BLOCK_SIZE, CONFIG.CHUNK_SIZE, groundRows * CONFIG.BLOCK_SIZE);
    
    const img = new Image();
    img.src = canvas.toDataURL();
    
    // Build collision map with solid ground rows
    const rows = tileCount;
    const cols = tileCount;
    const collisionMap = Array.from({ length: rows }, (_, y) =>
        Array.from({ length: cols }, () => y >= rows - groundRows)
    );

    const chunk = {
        x: chunkX,
        y: chunkY,
        image: img,
        collisionMap,
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
    // Sample corners and center across chunks
    const samples = [
        { sx: x, sy: y },
        { sx: x + width, sy: y },
        { sx: x, sy: y + height },
        { sx: x + width, sy: y + height },
        { sx: x + width / 2, sy: y + height / 2 }
    ];

    for (const p of samples) {
        const { chunkX, chunkY } = getChunkCoords(p.sx, p.sy);
        const chunk = world.chunks.get(getChunkKey(chunkX, chunkY));
        if (!chunk || !chunk.collisionMap) continue;

        const localX = p.sx - chunk.worldX;
        const localY = p.sy - chunk.worldY;
        const blockX = Math.floor(localX / CONFIG.BLOCK_SIZE);
        const blockY = Math.floor(localY / CONFIG.BLOCK_SIZE);

        if (blockY >= 0 && blockY < chunk.collisionMap.length &&
            blockX >= 0 && blockX < chunk.collisionMap[0].length) {
            if (chunk.collisionMap[blockY][blockX]) {
                return true;
            }
        }
    }
    return false;
}

// === PHYSICS ===
function updatePhysics(deltaTime) {
    const dt = Math.min(deltaTime, 0.033);
    const isRunning = keys['shift'];
    const speed = isRunning ? CONFIG.RUN_SPEED : CONFIG.MOVE_SPEED;

    let dx = 0;
    let dy = 0;
    if (keys['a'] || keys['arrowleft']) { dx -= 1; player.facing = 'left'; }
    if (keys['d'] || keys['arrowright']) { dx += 1; player.facing = 'right'; }
    if (keys['w'] || keys['arrowup']) { dy -= 1; player.facing = 'up'; }
    if (keys['s'] || keys['arrowdown']) { dy += 1; player.facing = 'down'; }

    // Normalize diagonal speed
    if (dx !== 0 || dy !== 0) {
        const len = Math.hypot(dx, dy);
        dx /= len; dy /= len;
    }

    const nextX = player.x + dx * speed * dt;
    const nextY = player.y + dy * speed * dt;

    // Move with collision resolution per axis
    if (!checkCollision(nextX, player.y, player.width, player.height)) {
        player.x = nextX;
    }
    if (!checkCollision(player.x, nextY, player.width, player.height)) {
        player.y = nextY;
    }
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
    
    // Top-down JRPG chibi sprite
    const px = player.x;
    const py = player.y;
    const w = player.width;
    const h = player.height;

    // Body
    ctx.fillStyle = '#3d7ddf';
    ctx.fillRect(px, py + h * 0.25, w, h * 0.6);

    // Head
    ctx.fillStyle = '#f5d7b2';
    ctx.fillRect(px + w * 0.15, py, w * 0.7, h * 0.35);

    // Hair fringe
    ctx.fillStyle = '#2b4c9b';
    ctx.fillRect(px + w * 0.1, py, w * 0.8, h * 0.12);

    // Eyes based on facing
    const eyeY = py + h * 0.18;
    const eyeSize = 3;
    ctx.fillStyle = '#1a1a1a';
    if (player.facing === 'left') {
        ctx.fillRect(px + w * 0.25, eyeY, eyeSize, eyeSize);
    } else if (player.facing === 'right') {
        ctx.fillRect(px + w * 0.65, eyeY, eyeSize, eyeSize);
    } else { // up/down
        ctx.fillRect(px + w * 0.35, eyeY, eyeSize, eyeSize);
        ctx.fillRect(px + w * 0.55, eyeY, eyeSize, eyeSize);
    }

    // Belt
    ctx.fillStyle = '#222';
    ctx.fillRect(px, py + h * 0.55, w, 2);

    // Boots
    ctx.fillStyle = '#1f2b46';
    ctx.fillRect(px + 2, py + h * 0.8, w - 4, h * 0.15);
    
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
        ctx.fillText(`Direção: ${player.facing}`, barX, barY + 120);
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
                // Find a walkable tile near chunk center
                const size = spawnChunk.collisionMap.length;
                const startX = Math.floor(size / 2);
                const startY = Math.floor(size / 2);
                let placed = false;

                const maxRadius = size;
                for (let r = 0; r < maxRadius && !placed; r++) {
                    for (let dy = -r; dy <= r && !placed; dy++) {
                        for (let dx = -r; dx <= r && !placed; dx++) {
                            const tx = startX + dx;
                            const ty = startY + dy;
                            if (tx < 0 || ty < 0 || tx >= size || ty >= size) continue;
                            if (!spawnChunk.collisionMap[ty][tx]) {
                                player.x = spawnChunk.worldX + tx * CONFIG.BLOCK_SIZE + (CONFIG.BLOCK_SIZE - player.width) / 2;
                                player.y = spawnChunk.worldY + ty * CONFIG.BLOCK_SIZE + (CONFIG.BLOCK_SIZE - player.height) / 2;
                                placed = true;
                            }
                        }
                    }
                }

                if (!placed) {
                    // Absolute fallback: place at chunk center
                    player.x = spawnChunk.worldX + (CONFIG.CHUNK_SIZE - player.width) / 2;
                    player.y = spawnChunk.worldY + (CONFIG.CHUNK_SIZE - player.height) / 2;
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
