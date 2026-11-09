# Edit Director — Selvagem Montage

## Quando usar

Todo slot tem clipe. Agora você decide in/out, ordem, sync com a música e
ONDE a imagem apanha. Saída: `edit_decisions` com `metadata.abuso[]`.

Este skill é o espelho invertido de `documentary-montage/edit-director.md`.
Leia aquele pra entender o schema; as REGRAS daqui vencem as de lá.

## O que muda em relação ao documentary-montage

| Documentary diz | Selvagem diz |
|-----------------|--------------|
| proibido glitch, RGB split, flash | permitido — com motivo escrito e densidade controlada |
| freeze-frame parece erro | freeze é pontuação; use 1–2 vezes, nunca no final |
| dissolve para irmãos emocionais | dissolve proibido (exceto UM, se for piada) |
| não junte mesmo sujeito na mesma escala | junte DE PROPÓSITO quando for jump cut de agressão |
| corte sempre no downbeat | corte no beat é o padrão; QUEBRAR a grade é a ferramenta |
| silêncio uma vez no centro | silêncio seco, sem fade — corta o som como se puxasse o cabo |

## Processo

### 1. Grade da música

Rode `audio_energy` na faixa do usuário. Ache: ataque inicial, quedas de
energia, picos. Se souber o BPM, calcule a grade de beats; senão, use os
picos de energia como pontos de corte candidatos.

### 2. Monte os pares

Siga a ordem dos pares do scene_plan. O corte entre A e B é o mais
importante do vídeo; o corte entre um par e o próximo pode ser seco e rápido.

Cada `cut.reason` escrito como colisão:
`"slot_04 × slot_05 — parado contra pogo; o corpo parado é o que grita"`.

### 3. Quebra de grade (OBRIGATÓRIO)

Pelo menos UM corte cai fora do beat, de propósito — antecipado 2–4 frames
(corte nervoso) ou atrasado (corte bêbado). Registre:
`metadata.quebras_grade = [{"cut": "cut_09", "desvio_frames": -3, "motivo": "..."}]`.

### 4. Motivo

Cada volta do motivo com transformação concreta no cut: `speed` (0.25–0.5 na
última volta funciona), espelhar (`transform.flip`), escala (`transform.scale`
1.3–2.0), ou abuso (`negativo`, `reverso`) aplicado só nele.

### 5. Abuso (o passe destrutivo)

Declare em `metadata.abuso[]`, em segundos do TIMELINE FINAL. Só tipos que
`scripts/selvagem/abuso.py` suporta (`python3 scripts/selvagem/abuso.py --list`):

- janela (efeito por cima): `rgb_split`, `chroma_sangra`, `negativo`,
  `estouro`, `sujeira`, `fantasma`, `borrao_temporal`, `diferenca`
- estruturais (trocam os frames, não podem se sobrepor): `stutter`,
  `congela`, `reverso`

```json
{"tipo": "stutter", "inicio": 12.0, "fim": 12.5, "frames": 2,
 "motivo": "a guitarra engasga no ataque do refrão; a imagem engasga junto"}
```

Regras de densidade:
- no máximo 1 abuso a cada 4s em média, EXCETO num pico declarado em
  `metadata.pico = {"inicio": .., "fim": ..}` onde vale tudo;
- `negativo` e `estouro`: 2–6 frames. Mais que isso cansa;
- nunca abuso nos primeiros 2s — o espectador precisa ver a imagem antes de
  vê-la apanhar (exceção: se a `regra_ruptura` for justamente essa);
- todo abuso tem `motivo`. Sem motivo, apague.

Abuso que o script não faz (datamosh, slit-scan, displacement, recorte em
máscara) → `metadata.abuso_manual[]` com o mesmo formato; vira só marcador
no XML pra ser feito no AE.

### 6. Silêncio seco

`metadata.silence_window = {"start_seconds": .., "end_seconds": ..}` —
0.3–1.5s, sem fade. No compose, o áudio cai a zero instantâneo.

### 7. Campos fixos

- `renderer_family: "documentary-montage"` (o enum do schema não tem
  selvagem; o compose usa esse renderer só pro corpo limpo)
- `metadata.gramatica: "selvagem"`
- transições: `cut` em quase tudo; `fade_in` só no primeiro se a
  regra de ruptura deixar; nada de `dissolve` além de um.

## Quality gate

- `python3 scripts/selvagem/abuso.py --input <qualquer mp4 com a duração certa> --edit edit_decisions.json --output /dev/null --dry-run` não acusa erro (ou valide janelas à mão: dentro da duração, estruturais sem sobreposição)
- ≥ 1 quebra de grade, todo abuso com motivo, motivo transformado nas 3 voltas
- `regra_ruptura` do brief respeitada (cite como no `metadata.regra_ruptura_check`)
- soma dos cuts ±10% da duração do brief

## Gate

Apresente: a linha do tempo resumida (pares + onde estão os abusos), e
pergunte ao usuário onde ele sente que a montagem "relaxa" demais e onde ela
"grita" à toa. Ofereça uma alternativa radical (ex.: tirar TODOS os abusos e
deixar só a colisão de planos — às vezes o corte seco é mais violento).
Checkpoint e ENCERRE o turno.
