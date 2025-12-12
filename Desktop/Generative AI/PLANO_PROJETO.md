# 🎮 Plano de Projeto: Noki AI - Jogo de Vídeo Gerado por IA

## 📋 Visão Geral
Um jogo de vídeo completamente gerado por IA em tempo real, rodando a 20 FPS, sem motor de jogo tradicional. O mundo, física, gráficos e interações são todos gerados dinamicamente por modelos de inteligência artificial.

---

## 🎯 Objetivos Principais

1. **Renderização em Tempo Real**: Gerar frames do jogo usando IA generativa a 20 FPS constantes
2. **Mundo Procedural**: Criar ambientes exploráveis gerados dinamicamente
3. **Física Realista**: Simular gravidade, colisões e movimento sem engine tradicional
4. **Sistema de Inventário**: Gerenciar itens com sprites gerados por IA
5. **Interação Natural**: Pulo, movimento e coleta de objetos responsivos

---

## 🏗️ Arquitetura do Sistema

### 1. Camada de Geração de IA
```
┌─────────────────────────────────────┐
│   Modelos de IA                     │
│  - Stable Diffusion (frames)        │
│  - GPT-4 Vision (contexto)          │
│  - ControlNet (consistência)        │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│   Pipeline de Processamento         │
│  - Conditioning de frames           │
│  - Cache inteligente                │
│  - Predição de movimento            │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│   Motor de Jogo Simplificado        │
│  - Estado do mundo                  │
│  - Física simulada                  │
│  - Lógica de jogo                   │
└─────────────────────────────────────┘
```

### 2. Stack Tecnológico Proposto

**Frontend:**
- HTML5 Canvas / WebGL para renderização
- JavaScript/TypeScript para lógica
- WebSocket para comunicação em tempo real

**Backend:**
- Python + FastAPI para servidor
- PyTorch / TensorFlow para IA
- Redis para cache de frames
- PostgreSQL para persistência de estado

**IA:**
- Stable Diffusion XL (geração de frames)
- ControlNet (consistência temporal)
- CLIP (entendimento de contexto)
- GPT-4 Vision (análise de cena)

---

## 📐 Componentes Detalhados

### 🌍 1. Sistema de Geração de Mundo

**Características:**
- Geração procedural baseada em seeds
- Sistema de chunks (32x32 blocos)
- Biomas variados (floresta, deserto, montanha, caverna)
- Objetos interativos distribuídos naturalmente

**Implementação:**
```python
# Pseudo-código
class WorldGenerator:
    def generate_chunk(self, x, y, seed):
        # Gerar prompt baseado em posição
        prompt = self.create_terrain_prompt(x, y, biome)
        
        # Usar IA para gerar imagem do chunk
        chunk_image = stable_diffusion.generate(
            prompt=prompt,
            conditioning=adjacent_chunks,
            style_reference=game_style
        )
        
        # Extrair dados de colisão
        collision_map = self.analyze_terrain(chunk_image)
        
        return Chunk(image, collision_map)
```

**Prompts Exemplo:**
- "isometric pixel art forest terrain, green grass, tall trees, rocks, 32-bit game style"
- "underground cave system, stalactites, crystals, dark atmosphere, pixel art"

---

### ⚙️ 2. Motor de Física Simulado

**Componentes:**
- Gravidade: 9.8 m/s²
- Detecção de colisão por pixel
- Velocidade máxima de queda
- Fricção e atrito

**Sistema de Colisão:**
```javascript
class PhysicsEngine {
    update(player, deltaTime) {
        // Aplicar gravidade
        player.velocityY += this.gravity * deltaTime;
        
        // Prever próxima posição
        let nextX = player.x + player.velocityX * deltaTime;
        let nextY = player.y + player.velocityY * deltaTime;
        
        // Verificar colisões usando IA
        if (this.checkCollision(nextX, nextY)) {
            // Resolver colisão
            player.velocityY = 0;
            player.onGround = true;
        } else {
            player.x = nextX;
            player.y = nextY;
            player.onGround = false;
        }
    }
}
```

---

### 🎒 3. Sistema de Inventário

**Recursos:**
- Grid 10x4 (40 slots)
- Empilhamento de itens
- Categorias (armas, consumíveis, materiais, quest items)
- Sprites gerados por IA

**Geração de Itens:**
```python
class ItemGenerator:
    def create_item(self, item_type, rarity):
        # Gerar sprite do item
        sprite = stable_diffusion.generate(
            prompt=f"{rarity} {item_type}, game icon, 64x64 pixels, detailed, transparent background",
            size="64x64",
            guidance_scale=7.5
        )
        
        # Gerar atributos
        attributes = gpt4.generate_attributes(item_type, rarity)
        
        return Item(sprite, attributes)
```

---

### 🖼️ 4. Pipeline de Renderização

**Estratégia Multi-Frame:**

1. **Frame Atual** (t): Exibido ao jogador
2. **Frame Cache** (t-1, t-2): Referências para consistência
3. **Frame Preditivo** (t+1): Pré-gerado em background

**Processo de Geração:**
```python
async def generate_frame(game_state):
    # 1. Construir prompt contextual
    prompt = f"""
    Third-person view of pixel art game character at position ({game_state.player.x}, {game_state.player.y}),
    facing {game_state.player.direction},
    {game_state.animation_state},
    environment: {game_state.current_biome},
    lighting: {game_state.time_of_day},
    reference previous frame for consistency
    """
    
    # 2. Gerar frame com condicionamento
    frame = await stable_diffusion.img2img(
        prompt=prompt,
        init_image=previous_frame,  # Consistência temporal
        strength=0.3,  # 70% similar ao anterior
        controlnet_conditioning=depth_map
    )
    
    # 3. Aplicar pós-processamento
    frame = apply_color_correction(frame)
    frame = add_ui_overlay(frame, game_state)
    
    return frame
```

**Otimização de Performance:**
- Cache LRU de 50 frames
- Compressão de frames antigos
- Geração assíncrona
- Redução de qualidade dinâmica

---

### 🕹️ 5. Controles e Interações

**Mapeamento de Entrada:**
```javascript
const controls = {
    movement: {
        left: 'A' || 'ArrowLeft',
        right: 'D' || 'ArrowRight',
        up: 'W' || 'ArrowUp',
        down: 'S' || 'ArrowDown'
    },
    actions: {
        jump: 'Space',
        interact: 'E',
        inventory: 'I',
        attack: 'LeftClick'
    }
};
```

**Sistema de Pulo:**
- Força inicial: 8 m/s
- Pulo duplo disponível
- Pulo variável (quanto mais tempo pressionado, mais alto)
- Coyote time (100ms após sair da plataforma)

---

### 🎨 6. Consistência Visual

**Técnicas para Coerência entre Frames:**

1. **Temporal Conditioning**: Usar frame anterior como referência
2. **Depth Maps**: Manter estrutura espacial consistente
3. **Color Palette Lock**: Paleta de cores fixa para estilo
4. **Feature Matching**: Garantir que objetos persistam

**Exemplo de Implementação:**
```python
class VisualConsistency:
    def __init__(self):
        self.style_reference = load_style_images()
        self.color_palette = extract_palette(self.style_reference)
    
    def ensure_consistency(self, new_frame, previous_frames):
        # Análise de features
        features_old = clip.encode_image(previous_frames[-1])
        features_new = clip.encode_image(new_frame)
        
        # Se divergência > threshold, reajustar
        if cosine_distance(features_old, features_new) > 0.3:
            new_frame = self.blend_frames(
                new_frame, 
                previous_frames[-1], 
                weight=0.7
            )
        
        # Aplicar paleta de cores
        new_frame = self.apply_palette(new_frame, self.color_palette)
        
        return new_frame
```

---

## 🚀 Fases de Desenvolvimento

### **Fase 1: Protótipo Básico (Semanas 1-3)**
- [x] Configurar ambiente de desenvolvimento
- [x] Integrar API do Stable Diffusion
- [x] Gerar single frame estático
- [x] Implementar controles básicos (esquerda/direita)
- [x] Sistema de física simples (gravidade + chão)

**Entregável:** Demo com personagem movendo-se em cenário fixo ✅ **CONCLUÍDO**

---

### **Fase 2: Geração Dinâmica (Semanas 4-6)**
- [x] Sistema de geração de mundo por chunks
- [x] Cache de frames inteligente
- [ ] Transições suaves entre frames
- [ ] Detecção de colisão por análise de imagem
- [ ] Pulo funcional

**Entregável:** Mundo explorável gerado proceduralmente ⌛ **EM ANDAMENTO**

---

### **Fase 3: Mecânicas de Jogo (Semanas 7-9)**
- [ ] Sistema de inventário completo
- [ ] Geração de itens com IA
- [ ] Interação com objetos
- [ ] Sistema de coleta
- [ ] UI responsiva

**Entregável:** Jogo jogável com progressão básica

---

### **Fase 4: Otimização e Polimento (Semanas 10-12)**
- [ ] Otimizar para 20 FPS constantes
- [ ] Melhorar consistência visual
- [ ] Sistema de save/load
- [ ] Efeitos sonoros (gerados por IA)
- [ ] Menu principal e configurações
- [ ] Testes extensivos

**Entregável:** Produto final polido e otimizado

---

## 📊 Métricas de Sucesso

| Métrica | Objetivo | Como Medir |
|---------|----------|------------|
| **FPS** | 20 FPS constantes | Monitor de performance |
| **Latência de Geração** | < 50ms por frame | Timestamps de pipeline |
| **Consistência Visual** | > 85% similaridade frame-a-frame | SSIM/CLIP score |
| **Taxa de Colisão** | 0 falsos positivos | Testes automatizados |
| **Tempo de Carregamento** | < 3s para novo chunk | Logs de performance |

---

## 💰 Estimativa de Custos (API de IA)

**Baseado em uso de Stable Diffusion API:**
- Custo por frame: ~$0.002
- Frames por segundo: 20
- Custo por minuto de jogo: ~$2.40
- **Otimização crítica necessária!**

**Estratégias de Redução:**
1. Cache agressivo de frames
2. Reusar frames com pequenas modificações
3. Gerar apenas elementos que mudaram
4. Usar modelos locais (RunDiffusion, Automatic1111)
5. Reduzir resolução (upscale apenas quando necessário)

---

## 🛠️ Ferramentas e Recursos

### **IA e ML:**
- [Stable Diffusion WebUI](https://github.com/AUTOMATIC1111/stable-diffusion-webui)
- [ComfyUI](https://github.com/comfyanonymous/ComfyUI)
- [ControlNet](https://github.com/lllyasviel/ControlNet)
- [CLIP Interrogator](https://github.com/pharmapsychotic/clip-interrogator)

### **Desenvolvimento:**
- VS Code com extensões Python/JS
- Git para versionamento
- Docker para containerização
- Postman para testes de API

### **Monitoramento:**
- Prometheus + Grafana para métricas
- Sentry para error tracking
- Wandb para experimentos de ML

---

## ⚠️ Desafios e Mitigações

| Desafio | Risco | Mitigação |
|---------|-------|-----------|
| **Latência de IA** | Alto | Cache preditivo, geração assíncrona |
| **Custo de API** | Alto | Modelos locais, otimização agressiva |
| **Inconsistência Visual** | Médio | Temporal conditioning, reference frames |
| **Física Imprecisa** | Médio | Sistema híbrido (regras + IA) |
| **Performance** | Alto | Redução de qualidade dinâmica, LOD |

---

## 🎓 Aprendizados e Inovações

Este projeto explora fronteiras de:
- **Game Design Generativo**: Jogo que se cria enquanto é jogado
- **Real-time AI Graphics**: Gráficos gerados on-the-fly
- **Emergent Gameplay**: Mecânicas que surgem da IA
- **Infinite Content**: Conteúdo verdadeiramente infinito

---

## 📚 Próximos Passos

1. ✅ **Criar plano detalhado** (Concluído)
2. ⏳ **Setup do ambiente de desenvolvimento**
3. ⏳ **Primeiro protótipo de geração de frame**
4. ⏳ **Implementação do loop de jogo**
5. ⏳ **Integração de física**

---

## 📞 Recursos Adicionais

- [Paper: Genie - Interactive AI Worlds](https://arxiv.org/abs/2402.15391)
- [GameNGen: Neural Game Engine](https://gamengen.github.io/)
- [Oasis: First Playable AI-Generated Game](https://oasis-model.github.io/)
- [Stable Diffusion Documentation](https://stability.ai/stable-diffusion)

---

**Data de Criação:** Dezembro 2025  
**Versão do Plano:** 1.0  
**Status:** Em Planejamento 🚧
