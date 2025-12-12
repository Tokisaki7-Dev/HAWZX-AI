# 🎮 Sistema de Geração Procedural de Jogos JRPG - Noki AI

## 📋 Visão Geral

Sistema completo de geração procedural de jogos estilo JRPG (Chrono Trigger, Final Fantasy) com:
- ✅ NPCs com diálogos únicos
- ✅ Sistema de quests procedurais
- ✅ História gerada dinamicamente
- ✅ Controles específicos por jogo
- ✅ Mecânicas especiais por bioma
- ✅ Visual pixel art 16-bit autêntico

---

## 🌍 Geração de Mundos

Cada mundo gerado inclui:

### 📖 História Procedural
4 temas de história disponíveis:
- **Hero Journey**: Herói sem memória que deve restaurar a paz
- **Ancient Evil**: Mal ancestral selado que está despertando
- **Time Travel**: Viagem no tempo com consequências
- **Rebellion**: Liderança de resistência contra império

### 🎨 Biomas
Cada bioma tem características únicas:

#### 🌲 Floresta
- **Paleta**: Verdes, marrons, azuis
- **Mecânicas**: Clima dinâmico, animais domesticáveis, ciclo dia/noite
- **Controle Especial**: F - Plantar Sementes

#### 🏜️ Deserto
- **Paleta**: Amarelos, laranjas, marrons
- **Mecânicas**: Tempestades de areia, oásis recuperam HP, miragens
- **Controle Especial**: D - Usar Bússola

#### ⛰️ Montanha
- **Paleta**: Cinzas, brancos, azuis claros
- **Mecânicas**: Escalada vertical, avalanches, altitude afeta stamina
- **Controle Especial**: C - Escalar

#### 🕳️ Caverna
- **Paleta**: Cinzas escuros, roxos, amarelos (cristais)
- **Mecânicas**: Sistema de luz com tocha, cristais com buffs, ecos revelam segredos
- **Controle Especial**: L - Tocha (iluminar)

---

## 👥 Sistema de NPCs

### Tipos de NPCs
- **Guerreiro** (vermelho): NPCs de combate/guarda
- **Mago** (roxo): NPCs de magia/conhecimento
- **Mercador** (amarelo): NPCs de comércio
- **Ancião** (cinza): NPCs de sabedoria/história
- **Curandeiro** (verde): NPCs de cura/suporte

### Diálogos
Cada NPC tem 3 linhas de diálogo:
1. **Saudação**: Boas-vindas ao jogador
2. **Quest**: Oferta de missão
3. **Lore**: Informação sobre o mundo

### Posicionamento
NPCs são posicionados aleatoriamente no mapa e desenhados como sprites pixel art (8x8 pixels)

---

## 🎯 Sistema de Quests

4 tipos de quests procedurais:

### 1. Coleta
- **Objetivo**: Coletar 3-8 itens raros
- **Recompensa**: 50-200 moedas de ouro
- **Exemplo**: "Coleta de Cristais"

### 2. Escolta
- **Objetivo**: Proteger NPC até destino
- **Recompensa**: 100-300 moedas + item raro
- **Exemplo**: "Proteção de Viajante"

### 3. Combate
- **Objetivo**: Derrotar boss (Dragão/Espectro/Golem/Demônio)
- **Recompensa**: 200-500 EXP + equipamento lendário
- **Exemplo**: "Caça ao Dragão"

### 4. Exploração
- **Objetivo**: Explorar dungeon antiga
- **Recompensa**: Artefato mágico
- **Exemplo**: "Exploração Antiga"

Cada mundo gera 3 quests únicas.

---

## 🎮 Controles

### Controles Base (todos os jogos)
- **↑↓←→ / WASD**: Movimento (8 direções)
- **SPACE**: Interagir com NPCs / Avançar diálogo
- **E**: Abrir Menu de Quests
- **I**: Inventário
- **M**: Toggle Controles (mostrar/ocultar)

### Controles Especiais (por bioma)
Cada bioma adiciona 1 controle exclusivo relacionado às suas mecânicas.

---

## 🎨 Sistema Visual

### Técnica de Renderização
- **Tiles**: 16x16 pixels (maior que antes para melhor visualização)
- **Paletas**: SNES 16-bit autênticas (3-4 cores por elemento)
- **Noise**: Perlin noise multi-octave para variedade orgânica
- **NPCs**: Sprites 8x8 pixels com cores por tipo

### Camadas de Noise
```python
base_noise = pnoise2(x/8.0, y/8.0, octaves=4, persistence=0.5)
detail_noise = pnoise2(x/3.0, y/3.0, octaves=2, persistence=0.3)
combined = base_noise + detail_noise * 0.3
```

Isso cria terrenos mais complexos e naturais.

---

## 🖥️ Interface do Usuário

### Tela Inicial - História
Ao gerar novo mundo:
- Nome do mundo
- História completa (4 parágrafos)
- Mecânicas especiais
- **[SPACE]** para começar

### HUD - Controles
Caixa no canto superior esquerdo:
- Lista de todos os controles
- Toggle com **M**

### Diálogo com NPCs
Sistema de caixa de diálogo clássico JRPG:
- Borda dourada
- Fundo preto semi-transparente
- Nome do NPC em destaque
- **[SPACE]** para avançar

### Menu de Quests (E)
- Lista todas as quests disponíveis
- Título, descrição, objetivo e recompensa
- Design estilo menu SNES

### Inventário (I)
- Em desenvolvimento
- Estrutura pronta para implementação futura

### Notificações
- Aparecem no topo da tela
- Fade out em 3 segundos
- Cor dourada

---

## 🔧 Arquitetura Técnica

### Backend (FastAPI + Python)

#### `game_generator.py`
```python
class JRPGGenerator:
    - generate_name(): Nomes procedurais
    - generate_story(): Histórias baseadas em temas
    - generate_quest(): Quests variadas
    - generate_npcs(): 5 NPCs por mundo
    - generate_controls(): Controles base + especiais
    - generate_mechanics(): Mecânicas por bioma
    - generate_complete_world(): Mundo completo
```

#### `generate_enhanced_terrain()`
```python
def generate_enhanced_terrain(biome, seed, width=512, height=512):
    - Gera JRPGGenerator com seed
    - Cria GameWorld completo
    - Renderiza terreno com tiles 16x16
    - Desenha NPCs no mapa
    - Retorna (Image, GameWorld)
```

#### Endpoint `/generate-frame`
**Request**:
```json
{
    "prompt": "mystical forest realm"
}
```

**Response**:
```json
{
    "message": "Mundo JRPG 'Aerion - Forest Realm' gerado com sucesso!",
    "image_url": "data:image/png;base64,...",
    "world": {
        "name": "Aerion - Forest Realm",
        "story": "Um jovem herói desperta em Forest...",
        "biome": "forest",
        "npcs": [
            {
                "name": "Lunara",
                "x": 128,
                "y": 256,
                "dialogue": ["...", "...", "..."],
                "quest": {...}
            }
        ],
        "quests": [...],
        "controls": {...},
        "special_mechanics": [...]
    }
}
```

### Frontend (JavaScript)

#### `script_enhanced.js`

**GameState**:
```javascript
{
    player: { x, y, width, height, speed },
    world: { name, story, npcs, quests, controls, mechanics },
    ui: { showDialogue, showMenu, showInventory, showControls },
    keys: { ... }
}
```

**Funções Principais**:
- `generateWorld()`: Chama API e carrega mundo
- `getNearbyNPC()`: Detecta NPCs próximos (32px)
- `handleInteraction()`: Sistema de diálogo
- `update()`: Movimento WASD/Arrows
- `render()`: Renderiza tudo
- `drawDialogueBox()`: UI de diálogo
- `drawControls()`: HUD de controles
- `drawStory()`: Tela de história
- `drawMenu()`: Menu de quests

---

## 🚀 Como Usar

### 1. Gerar Novo Mundo
O jogo gera automaticamente ao carregar. Para regenerar:
```javascript
generateWorld();
```

### 2. Explorar
Use **WASD** ou **Setas** para mover o quadrado azul (player).

### 3. Interagir com NPCs
- Aproxime-se de um NPC (círculo colorido)
- Aparece **[SPACE] Falar**
- Pressione **SPACE** para iniciar diálogo
- **SPACE** novamente para avançar

### 4. Ver Quests
Pressione **E** para abrir menu com todas as quests disponíveis.

### 5. Toggle Controles
Pressione **M** para mostrar/ocultar lista de controles.

---

## 📊 Performance

### Geração de Mundo
- **Tempo**: ~200-300ms (anteriormente 30s com API externa)
- **Custo**: $0 (procedural, sem API)
- **Consistência**: Mesmo seed = mesmo mundo
- **NPCs**: 5 por mundo
- **Quests**: 3 por mundo

### Visual
- **Resolução**: 512x512 pixels
- **FPS**: 60 (game loop otimizado)
- **Memória**: ~2MB por mundo gerado

---

## 🎲 Sistema de Seeds

Cada prompt gera um seed único:
```python
seed = hash(prompt) % 1000000
random.seed(seed)
```

Isso garante:
- ✅ Mesmo prompt = mesmo mundo
- ✅ Prompts diferentes = mundos únicos
- ✅ Reprodutibilidade total

---

## 🔮 Recursos Futuros

### Em Desenvolvimento
- [ ] Sistema de inventário funcional
- [ ] Sistema de combate em turnos
- [ ] Salvamento de progresso
- [ ] Mais tipos de NPCs
- [ ] Dungeons procedurais
- [ ] Sistema de equipamentos
- [ ] Múltiplos personagens jogáveis
- [ ] Música procedural por bioma

### Planejado
- [ ] Multiplayer local
- [ ] Geração de cidades
- [ ] Sistema de crafting
- [ ] Pets/companheiros
- [ ] Boss battles dinâmicos
- [ ] Eventos aleatórios

---

## 🎯 Diferenças do Sistema Anterior

| Aspecto | Antes | Agora |
|---------|-------|-------|
| **Geração** | Stability AI API (30s) | Procedural (~300ms) |
| **Custo** | $0.05 por imagem | $0 (grátis) |
| **NPCs** | ❌ Não existiam | ✅ 5 por mundo com diálogos |
| **Quests** | ❌ Não existiam | ✅ 3 por mundo |
| **História** | ❌ Não existia | ✅ Gerada proceduralmente |
| **Controles** | Fixos | Dinâmicos por bioma |
| **Mecânicas** | Básicas | Específicas por bioma |
| **Perspectiva** | Side-scrolling | Top-down JRPG |
| **Tiles** | 8x8 pixels | 16x16 pixels |
| **Interação** | ❌ Nenhuma | ✅ NPCs, diálogos, UI |

---

## 📝 Notas de Desenvolvimento

### Geração de Nomes
Usa combinação de prefixos e sufixos:
```python
NAME_PREFIXES = ['Aer', 'Lun', 'Sol', 'Nox', 'Zeph', 'Cael', 'Thal', 'Eld']
NAME_SUFFIXES = ['ion', 'ara', 'or', 'is', 'yn', 'eth', 'os', 'ia']
# Resultado: Aerion, Lunara, Soleth, Noxis, etc.
```

### Wrapping de Texto
Função `wrapText()` quebra texto longo em múltiplas linhas respeitando largura máxima.

### Sistema de Notificações
Queue de notificações com auto-remoção após 3 segundos e fade out.

---

## 🐛 Debug

Para debug, console mostra:
```javascript
console.log('Mundo gerado:', gameState.world);
console.log(`Falando com ${npc.name}`);
```

---

## 🌐 Deploy

URL: **https://noki-ai.fly.dev**

Plataforma: Fly.io (IAD - Virginia)

---

## 📄 Licença

Projeto educacional - Noki AI

---

**Desenvolvido com**: FastAPI, Python, JavaScript, PIL/Pillow, Perlin Noise

**Inspiração**: Chrono Trigger, Final Fantasy, Secret of Mana, Earthbound
