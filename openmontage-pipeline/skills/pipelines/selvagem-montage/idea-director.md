# Idea Director — Selvagem Montage

## Quando usar

Transformar o pedido do usuário no `brief` que todos os stages leem. Aqui o
brief não é um "tema": é uma BRIGA entre duas forças.

## Runtime

Trave `render_runtime = "remotion"` (o compose renderiza o corpo limpo pelo
mesmo caminho do documentary-montage e o destrói depois com ffmpeg).
Present both runtimes ao usuário — não escolha em silêncio (AGENT_GUIDE →
"Present Both Composition Runtimes"): diga que HyperFrames existe, mas que o
corpo limpo usa o caminho Remotion do documentary-montage. Registre uma
decisão `render_runtime_selection` em `decision_log`, com
`options_considered` = remotion e hyperframes, e hyperframes
`rejected_because: "corpo limpo reaproveita o CinematicRenderer do documentary-montage; o abuso é ffmpeg pós-render"`.

## Processo

### 1. Tese de colisão (UMA frase)

Formato: **"A contra B — e o que sobra é C."**

Bons exemplos:
- "Ordem de fábrica contra corpo suado no pogo — o que sobra é quem ainda se mexe."
- "Propaganda dos anos 50 contra porão de show — o que sobra é a mentira do conforto."
- "Hiena contra leão — o que sobra é que matilha vence rei."

Ruins:
- "Um clipe sobre liberdade" (sem antagonista)
- "Cenas da banda tocando" (é inventário, não tese)

Se o usuário não deu antagonista, PERGUNTE: "contra o que esse vídeo briga?"

### 2. Motivo visual

Um objeto, gesto ou forma que volta pelo menos 3 vezes e muda de sentido a
cada volta. Ex.: um punho fechando (ameaça → resistência → aplauso); uma porta
(fecha → arrombada → aberta pro vazio); o bracelete cravejado.

Registre: `metadata.motivo = { "nome": ..., "voltas": ["sentido 1", "sentido 2", "sentido 3"] }`.

### 3. Regra de ruptura

O que este vídeo SE RECUSA a fazer. Uma regra, escrita como proibição.
Ex.: "nunca mostrar o rosto do vocalista inteiro", "nenhum plano passa de 2s,
exceto um", "nenhum corte cai no beat no primeiro refrão".
Registre em `metadata.regra_ruptura`. O edit-director é cobrado por ela.

### 4. Duração e densidade

| Duração | Pares de colisão | Uso |
|---------|------------------|-----|
| 15–30s | 4–8 | reel, vinheta, teaser |
| 30–90s | 8–20 | abertura, trecho de clipe |
| 90–240s | 20–50 | videoclipe inteiro |

### 5. Fonte do material (OBRIGATÓRIO)

```json
"fonte_material": {
  "local_dir": "/caminho/pra/footage",   // ou null
  "proporcao": {"local": 0.7, "arquivo_aberto": 0.3},
  "eras_permitidas": ["1950-1970", "atual"]
}
```
Se o usuário tem footage próprio, essa é a base. Pergunte o caminho.

### 6. Música (OBRIGATÓRIO)

A música é a GRADE. Peça a faixa do usuário (caminho local). Registre
`metadata.music_plan = {"source": "user_file", "path": ..., "bpm": null}`.
Silêncio só com opt-out explícito do usuário.

### 7. Saída

Brief válido no schema, com em `metadata`: `tese_colisao`, `motivo`,
`regra_ruptura`, `fonte_material`, `music_plan`, `duration_seconds`,
`gramatica: "selvagem"`.

## Gate

Ao apresentar o brief, pergunte ao usuário:
1. A tese de colisão é a briga certa, ou tem uma briga mais funda embaixo?
2. Uma alternativa não óbvia (ex.: inverter A e B — e se o "vilão" for o
   protagonista?).

Checkpoint `awaiting_human` e ENCERRE o turno.
