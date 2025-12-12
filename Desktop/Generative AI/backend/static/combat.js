// combat.js - Sistema de combate em turnos
class CombatEngine {
    constructor(gameState) {
        this.gameState = gameState;
        this.currentEnemy = null;
        this.combatState = {
            active: false,
            playerTurn: true,
            selectedAction: 'attack',
            selectedSkill: 0,
            selectedItem: null,
            messages: [],
            animating: false,
            victory: false,
            defeat: false
        };
    }
    
    async startBattle(biome, playerLevel) {
        // Gera inimigo
        const response = await fetch('/generate-enemy', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                biome: biome,
                player_level: playerLevel,
                seed: Math.floor(Math.random() * 1000000)
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            this.currentEnemy = data.enemy;
            this.combatState.active = true;
            this.combatState.playerTurn = true;
            this.combatState.messages = [`Um ${data.enemy.name} apareceu!`];
            this.combatState.victory = false;
            this.combatState.defeat = false;
            
            // Som de batalha (placeholder)
            this.playSound('battle_start');
        }
    }
    
    async executeAction(action) {
        if (this.combatState.animating) return;
        
        this.combatState.animating = true;
        
        const response = await fetch('/combat-action', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                player_stats: this.gameState.player.stats,
                enemy_stats: this.currentEnemy,
                action: action
            })
        });
        
        const result = await response.json();
        
        // Atualiza HP
        this.gameState.player.stats.hp = result.player_hp;
        this.currentEnemy.hp = result.enemy_hp;
        
        // Adiciona mensagens
        this.combatState.messages = result.messages;
        
        // Verifica fim de batalha
        if (result.battle_end) {
            if (result.victory) {
                this.combatState.victory = true;
                await this.handleVictory(result);
            } else {
                this.combatState.defeat = true;
                this.handleDefeat();
            }
        } else {
            // Próximo turno
            setTimeout(() => {
                this.combatState.animating = false;
                this.combatState.playerTurn = true;
            }, 1500);
        }
        
        this.playSound('attack');
    }
    
    async handleVictory(result) {
        // Adiciona EXP
        const levelUpResponse = await fetch('/level-up', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                player_stats: this.gameState.player.stats,
                exp_gained: result.exp_gained
            })
        });
        
        const levelData = await levelUpResponse.json();
        this.gameState.player.stats = levelData.player_stats;
        
        // Adiciona ouro
        this.gameState.player.stats.gold += result.gold_gained;
        
        // Adiciona item
        if (result.item_dropped) {
            this.gameState.player.inventory.push(result.item_dropped);
            this.combatState.messages.push(`Recebeu: ${result.item_dropped}!`);
        }
        
        if (levelData.leveled_up) {
            this.combatState.messages.push(`LEVEL UP! Agora é nível ${levelData.player_stats.level}!`);
            this.playSound('level_up');
        }
        
        setTimeout(() => {
            this.endBattle();
        }, 3000);
    }
    
    handleDefeat() {
        setTimeout(() => {
            // Respawn no início
            this.gameState.player.x = 256;
            this.gameState.player.y = 256;
            this.gameState.player.stats.hp = this.gameState.player.stats.max_hp;
            this.gameState.player.stats.gold = Math.floor(this.gameState.player.stats.gold * 0.5);
            this.endBattle();
        }, 3000);
    }
    
    endBattle() {
        this.combatState.active = false;
        this.currentEnemy = null;
        this.combatState.messages = [];
        this.combatState.animating = false;
        this.playSound('battle_end');
    }
    
    playSound(soundType) {
        // Placeholder para sistema de som
        console.log(`Som: ${soundType}`);
    }
    
    render(ctx) {
        if (!this.combatState.active) return;
        
        // Fundo de batalha
        ctx.fillStyle = 'rgba(0, 0, 0, 0.95)';
        ctx.fillRect(0, 0, 800, 600);
        
        // Desenha inimigo
        this.drawEnemy(ctx);
        
        // Desenha stats do jogador e inimigo
        this.drawBattleUI(ctx);
        
        // Desenha menu de ações
        if (this.combatState.playerTurn && !this.combatState.animating) {
            this.drawActionMenu(ctx);
        }
        
        // Desenha mensagens
        this.drawMessages(ctx);
        
        // Tela de vitória/derrota
        if (this.combatState.victory) {
            this.drawVictoryScreen(ctx);
        } else if (this.combatState.defeat) {
            this.drawDefeatScreen(ctx);
        }
    }
    
    drawEnemy(ctx) {
        const enemy = this.currentEnemy;
        const centerX = 600;
        const centerY = 200;
        const size = 80;
        
        // Corpo do inimigo (sprite simples)
        ctx.fillStyle = `rgb(${enemy.sprite_color[0]}, ${enemy.sprite_color[1]}, ${enemy.sprite_color[2]})`;
        ctx.fillRect(centerX - size/2, centerY - size/2, size, size);
        
        // Contorno
        ctx.strokeStyle = '#fff';
        ctx.lineWidth = 2;
        ctx.strokeRect(centerX - size/2, centerY - size/2, size, size);
        
        // Nome
        ctx.fillStyle = '#FFD700';
        ctx.font = 'bold 16px monospace';
        ctx.textAlign = 'center';
        ctx.fillText(enemy.name, centerX, centerY - size - 10);
        
        // Nível
        ctx.fillStyle = '#fff';
        ctx.font = '12px monospace';
        ctx.fillText(`Lv.${enemy.level}`, centerX, centerY - size - 25);
        
        // Barra de HP
        const barWidth = 120;
        const barHeight = 8;
        const barX = centerX - barWidth/2;
        const barY = centerY + size + 10;
        
        // Fundo da barra
        ctx.fillStyle = '#333';
        ctx.fillRect(barX, barY, barWidth, barHeight);
        
        // HP atual
        const hpPercent = enemy.hp / enemy.max_hp;
        ctx.fillStyle = hpPercent > 0.5 ? '#00ff00' : hpPercent > 0.25 ? '#ffff00' : '#ff0000';
        ctx.fillRect(barX, barY, barWidth * hpPercent, barHeight);
        
        // Texto HP
        ctx.fillStyle = '#fff';
        ctx.font = '10px monospace';
        ctx.fillText(`${enemy.hp}/${enemy.max_hp}`, centerX, barY + barHeight + 12);
    }
    
    drawBattleUI(ctx) {
        const stats = this.gameState.player.stats;
        
        // Caixa de stats do jogador
        ctx.fillStyle = 'rgba(0, 0, 0, 0.8)';
        ctx.fillRect(20, 400, 300, 120);
        ctx.strokeStyle = '#4A90E2';
        ctx.lineWidth = 2;
        ctx.strokeRect(20, 400, 300, 120);
        
        // Informações do jogador
        ctx.fillStyle = '#FFD700';
        ctx.font = 'bold 14px monospace';
        ctx.textAlign = 'left';
        ctx.fillText(`Lv.${stats.level} Herói`, 30, 420);
        
        // HP
        ctx.fillStyle = '#fff';
        ctx.font = '12px monospace';
        ctx.fillText('HP:', 30, 440);
        
        const hpBarWidth = 200;
        const hpBarHeight = 8;
        ctx.fillStyle = '#333';
        ctx.fillRect(70, 432, hpBarWidth, hpBarHeight);
        
        const hpPercent = stats.hp / stats.max_hp;
        ctx.fillStyle = hpPercent > 0.5 ? '#00ff00' : hpPercent > 0.25 ? '#ffff00' : '#ff0000';
        ctx.fillRect(70, 432, hpBarWidth * hpPercent, hpBarHeight);
        
        ctx.fillStyle = '#fff';
        ctx.fillText(`${stats.hp}/${stats.max_hp}`, 280, 440);
        
        // MP
        ctx.fillText('MP:', 30, 460);
        
        ctx.fillStyle = '#333';
        ctx.fillRect(70, 452, hpBarWidth, hpBarHeight);
        
        const mpPercent = stats.mp / stats.max_mp;
        ctx.fillStyle = '#0080ff';
        ctx.fillRect(70, 452, hpBarWidth * mpPercent, hpBarHeight);
        
        ctx.fillStyle = '#fff';
        ctx.fillText(`${stats.mp}/${stats.max_mp}`, 280, 460);
        
        // EXP
        ctx.fillText('EXP:', 30, 480);
        
        ctx.fillStyle = '#333';
        ctx.fillRect(70, 472, hpBarWidth, hpBarHeight);
        
        const expPercent = stats.exp / stats.exp_to_next;
        ctx.fillStyle = '#FFD700';
        ctx.fillRect(70, 472, hpBarWidth * expPercent, hpBarHeight);
        
        ctx.fillStyle = '#fff';
        ctx.fillText(`${stats.exp}/${stats.exp_to_next}`, 280, 480);
        
        // Gold
        ctx.fillStyle = '#FFD700';
        ctx.fillText(`💰 ${stats.gold} G`, 30, 505);
    }
    
    drawActionMenu(ctx) {
        // Menu de ações
        ctx.fillStyle = 'rgba(0, 0, 0, 0.9)';
        ctx.fillRect(400, 400, 380, 180);
        ctx.strokeStyle = '#FFD700';
        ctx.lineWidth = 3;
        ctx.strokeRect(400, 400, 380, 180);
        
        ctx.fillStyle = '#FFD700';
        ctx.font = 'bold 14px monospace';
        ctx.textAlign = 'left';
        ctx.fillText('AÇÕES', 420, 425);
        
        // Opções
        const actions = [
            { key: 'A', name: 'Atacar', action: 'attack' },
            { key: 'S', name: 'Skills', action: 'skill' },
            { key: 'I', name: 'Itens', action: 'item' },
            { key: 'F', name: 'Fugir', action: 'flee' }
        ];
        
        actions.forEach((action, i) => {
            const x = 420 + (i % 2) * 180;
            const y = 450 + Math.floor(i / 2) * 30;
            
            const isSelected = this.combatState.selectedAction === action.action;
            
            ctx.fillStyle = isSelected ? '#FFD700' : '#fff';
            ctx.font = isSelected ? 'bold 14px monospace' : '14px monospace';
            ctx.fillText(`[${action.key}] ${action.name}`, x, y);
        });
        
        // Instruções
        ctx.fillStyle = '#888';
        ctx.font = '12px monospace';
        ctx.fillText('Use as teclas para selecionar', 420, 560);
    }
    
    drawMessages(ctx) {
        if (this.combatState.messages.length === 0) return;
        
        // Caixa de mensagens
        ctx.fillStyle = 'rgba(0, 0, 0, 0.9)';
        ctx.fillRect(50, 50, 700, 100);
        ctx.strokeStyle = '#FFD700';
        ctx.lineWidth = 2;
        ctx.strokeRect(50, 50, 700, 100);
        
        // Mensagens
        ctx.fillStyle = '#fff';
        ctx.font = '14px monospace';
        ctx.textAlign = 'left';
        
        this.combatState.messages.forEach((msg, i) => {
            ctx.fillText(msg, 70, 80 + i * 22);
        });
    }
    
    drawVictoryScreen(ctx) {
        ctx.fillStyle = 'rgba(255, 215, 0, 0.3)';
        ctx.fillRect(0, 0, 800, 600);
        
        ctx.fillStyle = '#FFD700';
        ctx.font = 'bold 48px monospace';
        ctx.textAlign = 'center';
        ctx.fillText('VITÓRIA!', 400, 300);
    }
    
    drawDefeatScreen(ctx) {
        ctx.fillStyle = 'rgba(255, 0, 0, 0.3)';
        ctx.fillRect(0, 0, 800, 600);
        
        ctx.fillStyle = '#ff0000';
        ctx.font = 'bold 48px monospace';
        ctx.textAlign = 'center';
        ctx.fillText('DERROTADO...', 400, 300);
    }
    
    handleInput(key) {
        if (!this.combatState.active || this.combatState.animating) return;
        if (!this.combatState.playerTurn) return;
        if (this.combatState.victory || this.combatState.defeat) return;
        
        // Seleção de ação
        if (key === 'a' || key === 'A') {
            this.executeAction({ action_type: 'attack' });
        } else if (key === 'f' || key === 'F') {
            this.executeAction({ action_type: 'flee' });
        } else if (key === 'i' || key === 'I') {
            // Abrir menu de itens (implementar)
            console.log('Menu de itens');
        } else if (key === 's' || key === 'S') {
            // Abrir menu de skills (implementar)
            console.log('Menu de skills');
        }
    }
}

// Exporta para uso global
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CombatEngine;
}
