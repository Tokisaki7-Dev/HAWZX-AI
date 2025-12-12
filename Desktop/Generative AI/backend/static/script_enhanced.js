const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

// Estado do Jogo JRPG
const gameState = {
    player: {
        x: 256,
        y: 256,
        width: 16,
        height: 16,
        color: '#4A90E2',
        speed: 2,
        stats: {
            level: 1,
            exp: 0,
            exp_to_next: 100,
            hp: 100,
            max_hp: 100,
            mp: 50,
            max_mp: 50,
            attack: 10,
            defense: 5,
            magic: 8,
            speed: 7,
            gold: 100
        },
        inventory: []
    },
    world: {
        name: '',
        story: '',
        biome: 'forest',
        backgroundImage: null,
        npcs: [],
        quests: [],
        controls: {},
        special_mechanics: [],
        apiEndpoint: ''
    },
    combat: null,  // Será inicializado depois
    ui: {
        showDialogue: false,
        currentDialogue: [],
        dialogueIndex: 0,
        currentNPC: null,
        showMenu: false,
        showInventory: false,
        showControls: true,
        showStory: false,
        showStats: false,
        notifications: []
    },
    keys: {
        ArrowUp: false,
        ArrowDown: false,
        ArrowLeft: false,
        ArrowRight: false,
        w: false,
        a: false,
        s: false,
        d: false,
        Space: false,
        e: false,
        i: false,
        m: false,
        c: false
    },
    loading: false,
    encounterChance: 0.002,  // 0.2% por frame (~12% por segundo de movimento)
    stepsSinceEncounter: 0
};

// Sistema de Input
document.addEventListener('keydown', (e) => {
    if (e.key in gameState.keys) {
        gameState.keys[e.key] = true;
    }
    
    // Se está em combate, delega para o sistema de combate
    if (gameState.combat && gameState.combat.combatState.active) {
        gameState.combat.handleInput(e.key);
        return;
    }
    
    // Tela de história - fecha com SPACE
    if (gameState.ui.showStory && (e.key === ' ' || e.key === 'Space')) {
        e.preventDefault();
        gameState.ui.showStory = false;
        return;
    }
    
    // Comandos especiais
    if (e.key === ' ' || e.key === 'Space') {
        e.preventDefault();
        handleInteraction();
    } else if (e.key === 'e' || e.key === 'E') {
        toggleMenu();
    } else if (e.key === 'i' || e.key === 'I') {
        toggleInventory();
    } else if (e.key === 'm' || e.key === 'M') {
        toggleControls();
    } else if (e.key === 'c' || e.key === 'C') {
        toggleStats();
    }
});

document.addEventListener('keyup', (e) => {
    if (e.key in gameState.keys) {
        gameState.keys[e.key] = false;
    }
});

// Gera novo mundo
async function generateWorld() {
    gameState.loading = true;
    
    const prompts = [
        'mystical forest realm with ancient trees',
        'vast desert expanse with hidden oases',
        'towering mountain peaks covered in snow',
        'dark mysterious cave filled with crystals'
    ];
    
    const prompt = prompts[Math.floor(Math.random() * prompts.length)];
    
    try {
        const response = await fetch('/generate-frame', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt })
        });
        
        const data = await response.json();
        
        if (data.world) {
            // Atualiza mundo
            gameState.world.name = data.world.name;
            gameState.world.story = data.world.story;
            gameState.world.biome = data.world.biome;
            gameState.world.npcs = data.world.npcs || [];
            gameState.world.quests = data.world.quests || [];
            gameState.world.controls = data.world.controls || {};
            gameState.world.special_mechanics = data.world.special_mechanics || [];
            
            // Carrega imagem
            const img = new Image();
            img.onload = () => {
                gameState.world.backgroundImage = img;
                gameState.loading = false;
                showNotification(`Bem-vindo a ${gameState.world.name}!`);
                gameState.ui.showStory = true;
                
                // Inicializa sistema de combate
                gameState.combat = new CombatEngine(gameState);
                
                // Carrega inventário inicial
                loadStarterItems();
            };
            img.src = data.image_url;
            
            console.log('Mundo gerado:', gameState.world);
        }
    } catch (error) {
        console.error('Erro ao gerar mundo:', error);
        gameState.loading = false;
    }
}

// Carrega itens iniciais
async function loadStarterItems() {
    try {
        const response = await fetch('/starter-items');
        const data = await response.json();
        gameState.player.inventory = data.items || [];
    } catch (error) {
        console.error('Erro ao carregar itens:', error);
    }
}

// Detecta NPCs próximos
function getNearbyNPC() {
    const interactionDistance = 32;
    
    for (const npc of gameState.world.npcs) {
        const dx = gameState.player.x - npc.x;
        const dy = gameState.player.y - npc.y;
        const distance = Math.sqrt(dx * dx + dy * dy);
        
        if (distance < interactionDistance) {
            return npc;
        }
    }
    return null;
}

// Interação com NPCs
function handleInteraction() {
    // Fecha diálogo se estiver aberto
    if (gameState.ui.showDialogue) {
        gameState.ui.dialogueIndex++;
        
        if (gameState.ui.dialogueIndex >= gameState.ui.currentDialogue.length) {
            gameState.ui.showDialogue = false;
            gameState.ui.dialogueIndex = 0;
            gameState.ui.currentNPC = null;
        }
        return;
    }
    
    // Verifica NPC próximo
    const npc = getNearbyNPC();
    if (npc) {
        gameState.ui.showDialogue = true;
        gameState.ui.currentDialogue = npc.dialogue;
        gameState.ui.dialogueIndex = 0;
        gameState.ui.currentNPC = npc;
        console.log(`Falando com ${npc.name}`);
    }
}

// UI Toggles
function toggleMenu() {
    gameState.ui.showMenu = !gameState.ui.showMenu;
}

function toggleInventory() {
    gameState.ui.showInventory = !gameState.ui.showInventory;
}

function toggleControls() {
    gameState.ui.showControls = !gameState.ui.showControls;
}

function toggleStats() {
    gameState.ui.showStats = !gameState.ui.showStats;
}

// Verifica encontros aleatórios
function checkRandomEncounter() {
    if (gameState.combat && gameState.combat.combatState.active) return;
    if (gameState.ui.showDialogue || gameState.ui.showMenu || gameState.ui.showInventory) return;
    
    gameState.stepsSinceEncounter++;
    
    // Chance de encontro aumenta com passos
    const adjustedChance = gameState.encounterChance * (1 + gameState.stepsSinceEncounter / 1000);
    
    if (Math.random() < adjustedChance) {
        // Inicia batalha!
        gameState.stepsSinceEncounter = 0;
        gameState.combat.startBattle(gameState.world.biome, gameState.player.stats.level);
    }
}

// Notificações
function showNotification(message) {
    gameState.ui.notifications.push({
        message,
        time: Date.now()
    });
}

// Update
function update(deltaTime) {
    if (gameState.loading) return;
    if (gameState.combat && gameState.combat.combatState.active) return;  // Pausa durante combate
    
    // Movimento
    let dx = 0;
    let dy = 0;
    
    if (gameState.keys.ArrowLeft || gameState.keys.a) dx -= 1;
    if (gameState.keys.ArrowRight || gameState.keys.d) dx += 1;
    if (gameState.keys.ArrowUp || gameState.keys.w) dy -= 1;
    if (gameState.keys.ArrowDown || gameState.keys.s) dy += 1;
    
    // Normaliza diagonal
    if (dx !== 0 && dy !== 0) {
        dx *= 0.707;
        dy *= 0.707;
    }
    
    // Se está movendo, verifica encontros
    if (dx !== 0 || dy !== 0) {
        checkRandomEncounter();
    }
    
    gameState.player.x += dx * gameState.player.speed;
    gameState.player.y += dy * gameState.player.speed;
    
    // Limites
    gameState.player.x = Math.max(0, Math.min(512 - gameState.player.width, gameState.player.x));
    gameState.player.y = Math.max(0, Math.min(512 - gameState.player.height, gameState.player.y));
    
    // Remove notificações antigas
    gameState.ui.notifications = gameState.ui.notifications.filter(n => Date.now() - n.time < 3000);
}

// Render
function render() {
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Se está em combate, renderiza apenas o combate
    if (gameState.combat && gameState.combat.combatState.active) {
        gameState.combat.render(ctx);
        return;
    }
    
    // Background
    if (gameState.world.backgroundImage) {
        ctx.drawImage(gameState.world.backgroundImage, 0, 0);
    }
    
    // NPCs (já desenhados no mapa)
    
    // Player
    ctx.fillStyle = gameState.player.color;
    ctx.fillRect(
        gameState.player.x,
        gameState.player.y,
        gameState.player.width,
        gameState.player.height
    );
    
    // HUD - Stats permanente (canto superior direito)
    if (gameState.ui.showStats) {
        drawPlayerStats();
    }
    
    // Indicador de interação
    const nearbyNPC = getNearbyNPC();
    if (nearbyNPC && !gameState.ui.showDialogue) {
        ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
        ctx.font = '12px monospace';
        ctx.fillText('[SPACE] Falar', nearbyNPC.x - 20, nearbyNPC.y - 20);
    }
    
    // UI - Diálogo
    if (gameState.ui.showDialogue && gameState.ui.currentNPC) {
        drawDialogueBox();
    }
    
    // UI - Controles
    if (gameState.ui.showControls && !gameState.loading) {
        drawControls();
    }
    
    // UI - História
    if (gameState.ui.showStory) {
        drawStory();
    }
    
    // UI - Menu
    if (gameState.ui.showMenu) {
        drawMenu();
    }
    
    // UI - Inventário
    if (gameState.ui.showInventory) {
        drawInventory();
    }
    
    // Notificações
    drawNotifications();
    
    // Loading
    if (gameState.loading) {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = '#fff';
        ctx.font = '20px monospace';
        ctx.fillText('Gerando mundo...', 200, 300);
    }
}

function drawDialogueBox() {
    const npc = gameState.ui.currentNPC;
    const dialogue = gameState.ui.currentDialogue[gameState.ui.dialogueIndex];
    
    // Caixa
    ctx.fillStyle = 'rgba(0, 0, 0, 0.85)';
    ctx.fillRect(50, 400, 700, 150);
    ctx.strokeStyle = '#FFD700';
    ctx.lineWidth = 3;
    ctx.strokeRect(50, 400, 700, 150);
    
    // Nome do NPC
    ctx.fillStyle = '#FFD700';
    ctx.font = 'bold 16px monospace';
    ctx.fillText(npc.name, 70, 430);
    
    // Diálogo
    ctx.fillStyle = '#fff';
    ctx.font = '14px monospace';
    const lines = wrapText(dialogue, 650);
    lines.forEach((line, i) => {
        ctx.fillText(line, 70, 460 + i * 20);
    });
    
    // Indicador
    ctx.fillStyle = '#FFD700';
    ctx.font = '12px monospace';
    ctx.fillText('[SPACE] Continuar', 600, 535);
}

function drawControls() {
    // Glassmorphism
    ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
    ctx.fillRect(10, 10, 270, 220);
    
    const gradient = ctx.createLinearGradient(10, 10, 280, 230);
    gradient.addColorStop(0, 'rgba(102, 126, 234, 0.6)');
    gradient.addColorStop(1, 'rgba(118, 75, 162, 0.6)');
    ctx.strokeStyle = gradient;
    ctx.lineWidth = 3;
    ctx.strokeRect(10, 10, 270, 220);
    
    ctx.fillStyle = '#f093fb';
    ctx.font = 'bold 16px monospace';
    ctx.fillText('⌨️ CONTROLES', 20, 35);
    
    ctx.fillStyle = '#fff';
    ctx.font = '13px monospace';
    let y = 60;
    for (const [key, action] of Object.entries(gameState.world.controls)) {
        // Key badge
        ctx.fillStyle = 'rgba(240, 147, 251, 0.3)';
        ctx.fillRect(20, y - 12, 40, 18);
        ctx.strokeStyle = '#f093fb';
        ctx.lineWidth = 1;
        ctx.strokeRect(20, y - 12, 40, 18);
        
        ctx.fillStyle = '#FFD700';
        ctx.font = 'bold 11px monospace';
        ctx.fillText(key, 25, y);
        
        ctx.fillStyle = '#fff';
        ctx.font = '12px monospace';
        ctx.fillText(action, 70, y);
        y += 24;
    }
    
    ctx.fillStyle = 'rgba(255, 255, 255, 0.5)';
    ctx.font = '11px monospace';
    ctx.fillText('[M] Toggle Controles', 20, 215);
}

function drawStory() {
    // Overlay escuro com gradiente
    const gradient = ctx.createLinearGradient(0, 0, 0, 600);
    gradient.addColorStop(0, 'rgba(102, 126, 234, 0.95)');
    gradient.addColorStop(1, 'rgba(118, 75, 162, 0.95)');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, 800, 600);
    
    // Caixa principal com glassmorphism
    ctx.fillStyle = 'rgba(255, 255, 255, 0.1)';
    ctx.fillRect(80, 80, 640, 440);
    
    // Borda gradiente
    const borderGradient = ctx.createLinearGradient(80, 80, 720, 520);
    borderGradient.addColorStop(0, '#f093fb');
    borderGradient.addColorStop(1, '#4facfe');
    ctx.strokeStyle = borderGradient;
    ctx.lineWidth = 4;
    ctx.strokeRect(80, 80, 640, 440);
    
    // Título com gradiente
    ctx.font = 'bold 28px monospace';
    ctx.textAlign = 'center';
    const titleGradient = ctx.createLinearGradient(0, 110, 800, 110);
    titleGradient.addColorStop(0, '#f093fb');
    titleGradient.addColorStop(0.5, '#FFD700');
    titleGradient.addColorStop(1, '#4facfe');
    ctx.fillStyle = titleGradient;
    ctx.fillText(gameState.world.name, 400, 120);
    
    // Linha decorativa
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(120, 140);
    ctx.lineTo(680, 140);
    ctx.stroke();
    
    // História
    ctx.fillStyle = '#fff';
    ctx.font = '14px monospace';
    ctx.textAlign = 'left';
    const lines = wrapText(gameState.world.story, 580);
    lines.forEach((line, i) => {
        ctx.fillText(line, 110, 170 + i * 22);
    });
    
    // Mecânicas Especiais
    ctx.font = 'bold 16px monospace';
    const mechGradient = ctx.createLinearGradient(0, 320, 400, 320);
    mechGradient.addColorStop(0, '#4facfe');
    mechGradient.addColorStop(1, '#f093fb');
    ctx.fillStyle = mechGradient;
    ctx.fillText('✨ Mecânicas Especiais', 110, 320);
    
    ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
    ctx.font = '12px monospace';
    gameState.world.special_mechanics.forEach((mech, i) => {
        const mechLines = wrapText(`• ${mech}`, 560);
        mechLines.forEach((line, j) => {
            ctx.fillText(line, 110, 345 + (i * 32) + (j * 16));
        });
    });
    
    // Botão animado
    const time = Date.now() / 1000;
    const pulse = Math.sin(time * 3) * 0.1 + 1;
    
    ctx.save();
    ctx.translate(400, 480);
    ctx.scale(pulse, pulse);
    
    ctx.fillStyle = 'rgba(240, 147, 251, 0.3)';
    ctx.fillRect(-180, -20, 360, 40);
    
    ctx.strokeStyle = '#f093fb';
    ctx.lineWidth = 3;
    ctx.strokeRect(-180, -20, 360, 40);
    
    ctx.font = 'bold 16px monospace';
    ctx.textAlign = 'center';
    ctx.fillStyle = '#FFD700';
    ctx.fillText('⚡ Pressione SPACE para Começar ⚡', 0, 5);
    
    ctx.restore();
    ctx.textAlign = 'left';
}

function drawMenu() {
    ctx.fillStyle = 'rgba(0, 0, 0, 0.85)';
    ctx.fillRect(150, 150, 500, 300);
    ctx.strokeStyle = '#FFD700';
    ctx.lineWidth = 3;
    ctx.strokeRect(150, 150, 500, 300);
    
    ctx.fillStyle = '#FFD700';
    ctx.font = 'bold 18px monospace';
    ctx.fillText('MENU DE QUESTS', 200, 180);
    
    ctx.fillStyle = '#fff';
    ctx.font = '13px monospace';
    
    gameState.world.quests.forEach((quest, i) => {
        const y = 210 + i * 80;
        
        ctx.fillStyle = '#4A90E2';
        ctx.fillText(`Quest ${i + 1}: ${quest.title}`, 170, y);
        
        ctx.fillStyle = '#fff';
        ctx.fillText(quest.description, 170, y + 20);
        ctx.fillText(`Objetivo: ${quest.objective}`, 170, y + 40);
        
        ctx.fillStyle = '#FFD700';
        ctx.fillText(`Recompensa: ${quest.reward}`, 170, y + 60);
    });
    
    ctx.fillStyle = '#888';
    ctx.font = '12px monospace';
    ctx.fillText('[E] Fechar Menu', 300, 430);
}

function drawInventory() {
    ctx.fillStyle = 'rgba(0, 0, 0, 0.85)';
    ctx.fillRect(200, 150, 400, 300);
    ctx.strokeStyle = '#4A90E2';
    ctx.lineWidth = 3;
    ctx.strokeRect(200, 150, 400, 300);
    
    ctx.fillStyle = '#FFD700';
    ctx.font = 'bold 16px monospace';
    ctx.fillText('INVENTÁRIO', 250, 180);
    
    ctx.fillStyle = '#fff';
    ctx.font = '13px monospace';
    
    if (gameState.player.inventory.length === 0) {
        ctx.fillText('Inventário vazio', 250, 220);
    } else {
        gameState.player.inventory.forEach((item, i) => {
            const y = 210 + i * 25;
            ctx.fillText(`${i + 1}. ${item}`, 220, y);
        });
    }
    
    ctx.fillStyle = '#888';
    ctx.font = '12px monospace';
    ctx.fillText('[I] Fechar Inventário', 250, 420);
}

function drawPlayerStats() {
    const stats = gameState.player.stats;
    
    // Glassmorphism background
    ctx.fillStyle = 'rgba(0, 0, 0, 0.75)';
    ctx.fillRect(540, 10, 250, 160);
    
    const gradient = ctx.createLinearGradient(540, 10, 790, 170);
    gradient.addColorStop(0, 'rgba(240, 147, 251, 0.6)');
    gradient.addColorStop(1, 'rgba(79, 172, 254, 0.6)');
    ctx.strokeStyle = gradient;
    ctx.lineWidth = 3;
    ctx.strokeRect(540, 10, 250, 160);
    
    // Título
    const titleGradient = ctx.createLinearGradient(550, 30, 650, 30);
    titleGradient.addColorStop(0, '#f093fb');
    titleGradient.addColorStop(1, '#FFD700');
    ctx.fillStyle = titleGradient;
    ctx.font = 'bold 16px monospace';
    ctx.textAlign = 'left';
    ctx.fillText(`⚔️ Lv.${stats.level} Herói`, 550, 35);
    
    // Stats com barras
    ctx.fillStyle = '#fff';
    ctx.font = '12px monospace';
    
    // HP Bar
    ctx.fillText('HP', 550, 58);
    drawStatBar(590, 48, 180, 12, stats.hp, stats.max_hp, '#00ff00', '#ff0000');
    ctx.fillText(`${stats.hp}/${stats.max_hp}`, 680, 58);
    
    // MP Bar
    ctx.fillText('MP', 550, 78);
    drawStatBar(590, 68, 180, 12, stats.mp, stats.max_mp, '#0080ff', '#004080');
    ctx.fillText(`${stats.mp}/${stats.max_mp}`, 680, 78);
    
    // Stats
    ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
    ctx.font = '11px monospace';
    ctx.fillText(`⚔️ ATK: ${stats.attack}`, 550, 98);
    ctx.fillText(`🛡️ DEF: ${stats.defense}`, 550, 113);
    ctx.fillText(`✨ MAG: ${stats.magic}`, 660, 98);
    ctx.fillText(`⚡ SPD: ${stats.speed}`, 660, 113);
    
    // EXP Bar
    ctx.fillStyle = '#FFD700';
    ctx.font = 'bold 11px monospace';
    ctx.fillText('EXP', 550, 133);
    drawStatBar(590, 123, 180, 10, stats.exp, stats.exp_to_next, '#FFD700', '#886600');
    ctx.fillText(`${stats.exp}/${stats.exp_to_next}`, 660, 133);
    
    // Gold
    ctx.fillStyle = '#FFD700';
    ctx.font = 'bold 13px monospace';
    ctx.fillText(`💰 ${stats.gold} G`, 550, 153);
    
    ctx.fillStyle = 'rgba(255, 255, 255, 0.4)';
    ctx.font = '10px monospace';
    ctx.fillText('[C] Toggle', 710, 165);
}

function drawStatBar(x, y, width, height, current, max, colorFull, colorLow) {
    // Fundo
    ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
    ctx.fillRect(x, y, width, height);
    
    // Barra
    const percent = Math.max(0, Math.min(1, current / max));
    const barWidth = width * percent;
    
    const barGradient = ctx.createLinearGradient(x, y, x + barWidth, y);
    barGradient.addColorStop(0, colorFull);
    barGradient.addColorStop(1, colorLow);
    ctx.fillStyle = barGradient;
    ctx.fillRect(x, y, barWidth, height);
    
    // Borda
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)';
    ctx.lineWidth = 1;
    ctx.strokeRect(x, y, width, height);
}

function drawNotifications() {
    gameState.ui.notifications.forEach((notif, i) => {
        const alpha = Math.max(0, 1 - (Date.now() - notif.time) / 3000);
        ctx.fillStyle = `rgba(255, 215, 0, ${alpha})`;
        ctx.font = 'bold 14px monospace';
        ctx.fillText(notif.message, 300, 50 + i * 25);
    });
}

function wrapText(text, maxWidth) {
    const words = text.split(' ');
    const lines = [];
    let currentLine = '';
    
    ctx.font = '13px monospace';
    
    for (const word of words) {
        const testLine = currentLine + (currentLine ? ' ' : '') + word;
        const metrics = ctx.measureText(testLine);
        
        if (metrics.width > maxWidth && currentLine) {
            lines.push(currentLine);
            currentLine = word;
        } else {
            currentLine = testLine;
        }
    }
    
    if (currentLine) {
        lines.push(currentLine);
    }
    
    return lines;
}

// Game Loop
let lastTime = 0;
function gameLoop(currentTime) {
    const deltaTime = (currentTime - lastTime) / 1000;
    lastTime = currentTime;
    
    update(deltaTime);
    render();
    
    requestAnimationFrame(gameLoop);
}

// Inicia o jogo
generateWorld();
requestAnimationFrame(gameLoop);
