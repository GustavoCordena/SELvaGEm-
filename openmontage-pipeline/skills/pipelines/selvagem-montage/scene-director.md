# Scene Director — Selvagem Montage

## Quando usar

O brief existe. Agora você desenha os SLOTS — mas não em fila. Em PARES que
se chocam. A unidade de pensamento deste pipeline é o par A|B, não o plano.

## Pré-requisitos

| Recurso | Uso |
|---------|-----|
| `state.artifacts["idea"]["brief"]` | tese, motivo, regra de ruptura, fonte |
| `schemas/artifacts/scene_plan.schema.json` | validação |
| `scene_detect`, `frame_sampler`, `video_analyzer` | se há `local_dir`: veja o que EXISTE antes de pedir o que não existe |

## Processo

### 0. Se há footage local, olhe antes de escrever

Rode `scene_detect` na pasta, amostre 1 frame por cena com `frame_sampler`,
e faça um inventário curto (o que é, escala, movimento, cor dominante).
Desenhe os pares a partir do que existe. Pedir "close de punho fechado" quando
o footage tem 40 planos abertos de palco é desenhar no vazio.

### 1. Tipos de colisão (use pelo menos 4 diferentes)

| Tipo | A | B |
|------|---|---|
| escala | plano aberto extremo | detalhe extremo |
| ritmo | plano parado, quase morto | movimento violento |
| cor | dessaturado/frio | saturado/quente |
| direção | movimento → | movimento ← |
| sentido | imagem "positiva" | mesma forma em contexto podre |
| tempo | arquivo velho | footage de agora |
| forma | círculo | círculo (match cut de forma com sentido oposto) |

### 2. Os pares

Cada slot tem as chaves normais do schema (descrição, queries, hold alvo) MAIS:

```json
"metadata": {
  "pares": [
    {"par": 1, "a": "slot_01", "b": "slot_02", "tipo_colisao": "escala",
     "terceira_ideia": "o detalhe é maior que a multidão"}
  ],
  "motivo_slots": [
    {"slot": "slot_03", "volta": 1, "sentido": "ameaça"},
    {"slot": "slot_11", "volta": 2, "sentido": "resistência"},
    {"slot": "slot_19", "volta": 3, "sentido": "celebração", "transformacao": "invertido + câmera lenta"}
  ],
  "feridas": ["slot_14"]
}
```

- `terceira_ideia`: o que o choque diz que nenhum plano diz sozinho. Se você
  não consegue escrever, o par não existe.
- **Ferida**: pelo menos 1 slot que fica TEMPO DEMAIS (3–6s num vídeo de
  cortes de 0.3s). É o respiro desconfortável. Desenhe-o perto do clímax.

### 3. Queries (pra slots sem material local)

2–3 queries curtas, concretas, em inglês (os provedores de stock são em
inglês): substantivo + adjetivo + textura. "sweaty crowd moshpit dark",
"1950s factory assembly line", "hyena pack night". Nunca "chaos" ou
"rebellion" — abstração não acha clipe.

### 4. Holds

Base de hold por duração total: 15–30s → 0.4s; 30–90s → 0.6s; 90s+ → 0.8s.
Feridas: 3–6s. Motivo: hold da primeira volta é o MAIOR das três.

## Quality gate

- ≥ 4 tipos de colisão diferentes
- motivo em ≥ 3 slots com sentidos diferentes
- ≥ 1 ferida
- soma dos holds ±15% de `brief.duration_seconds`
- `regra_ruptura` do brief não violada pelo desenho

## Gate

Mostre os pares como lista "A × B → terceira ideia". Pergunte ao usuário
qual par é o mais fraco e por quê, e ofereça uma reordenação inesperada
(ex.: começar pelo último par). Checkpoint e ENCERRE o turno.
