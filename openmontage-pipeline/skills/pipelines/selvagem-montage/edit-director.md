# Edit Director — Selvagem Montage

## Quando usar

Todo slot tem clipe. Agora você decide in/out, ordem, sync com a música e
ONDE a imagem apanha. Saída: `edit_decisions` com `metadata.modo`,
`metadata.fragmentos[]` (se o modo pede remontagem) e `metadata.abuso[]`.

Este skill é o espelho invertido de `documentary-montage/edit-director.md`.
Leia aquele pra entender o schema; as REGRAS daqui vencem as de lá.

## Lição de origem (não repita)

O primeiro teste real deste pipeline ficou fraco por três motivos:
1. abusos escolhidos só pelo SOM caíram no plano errado;
2. filtro por cima de uma montagem pronta virou decoração, não colisão;
3. uma regra fixa de densidade ("1 abuso a cada 4s") deixou tudo tímido.
As seções 0, 1 e 5 abaixo existem por causa disso.

## O que muda em relação ao documentary-montage

| Documentary diz | Selvagem diz |
|-----------------|--------------|
| proibido glitch, RGB split, flash | permitido — com motivo escrito; a densidade é decidida pelo modo |
| freeze-frame parece erro | freeze é pontuação (ou a regra inteira, no modo regra única) |
| dissolve para irmãos emocionais | dissolve proibido (exceto UM, se for piada) |
| não junte mesmo sujeito na mesma escala | junte DE PROPÓSITO quando for jump cut de agressão |
| corte sempre no downbeat | corte no beat é o padrão; QUEBRAR a grade é a ferramenta |
| silêncio uma vez no centro | silêncio seco, sem fade — corta o som como se puxasse o cabo |

## Processo

### 0. Mapear o material (OBRIGATÓRIO, antes de decidir qualquer coisa)

```bash
python3 scripts/selvagem/mapa.py <video_ou_corpo.mp4> projects/<nome>/mapa.json
```
Dá BPM, grade de beats, ataques, cortes de imagem e a lista de planos. Depois
monte uma folha de contato com 1 frame do MEIO de cada plano, numerada, e
OLHE pra ela (Read na imagem). Classifique cada plano numa família (close de
rosto, aberto, detalhe, público, flash…) em `metadata.familias`.

Regra: **toda marcação de tempo (corte, abuso, fragmento) diz qual plano está
na tela naquele momento.** Abuso marcado só pelo ataque da música, sem
conferir a imagem, é proibido.

### 1. Escolha do modo (OBRIGATÓRIO)

Leia `brief.metadata.modo` (o idea-director propõe; se não houver, escolha e
justifique). Grave em `metadata.modo`.

| Modo | Como monta | Densidade de abuso |
|------|------------|--------------------|
| **contido** | pares de colisão em corte seco; poucos golpes em lugares exatos | baixa: o golpe precisa de silêncio em volta |
| **saturacao** | a destruição cresce até a imagem quase sumir; a degradação É a narrativa | alta e crescente: declare a curva em `metadata.curva` (ex.: 0–30% limpo, 30–70% 1 golpe por ataque, 70–100% golpe por meio-beat) |
| **regra_unica** | UMA violência repetida sem dó (ex.: tudo que é do "rei" congela no beat e gagueja) | não se conta golpe: conta-se se a regra foi aplicada SEMPRE. Exceção à regra = falha |

Ofereça ao usuário, no gate, o modo NÃO escolhido mais provocador.

### 2. Remontar antes de filtrar

Pergunta obrigatória: a ORDEM dos planos precisa mudar pra tese aparecer?
Quase sempre sim. Nesse caso o edit é uma lista de fragmentos que o compose
renderiza com `scripts/selvagem/remonta.py`:

```json
"fragmentos": [
  {"s": 6.1, "d": 0.93, "nota": "plano 6 (close Lemmy) — motivo, volta 1, limpo"},
  {"s": 16.2, "d": 0.46, "fx": ["rgb"], "nota": "plano 17 (palco aberto) × close anterior: escala"},
  {"s": 6.1, "d": 0.46, "fx": ["neg"], "nota": "plano 6 — motivo, volta 2, invertido"},
  {"s": 24.9, "d": 2.5, "fx": ["hold"], "nota": "plano 22 — FERIDA: congela tempo demais"}
]
```
- `s` = início na FONTE; `d` = duração (use múltiplos do beat do mapa);
- `fx` aceita: `neg`, `rgb`, `chroma`, `rev`, `hold`, `stut2`, `stut3`,
  `lag`, `noise`, `zoom`, `estouro`, `dif`;
- o áudio da fonte (ou o da música do brief) corre inteiro por baixo;
- toda `nota` cita o número do plano do mapa.

Só pule a remontagem se o corte do usuário já for a colisão certa — e diga
isso no gate. Aí o trabalho é o passe de abuso (seção 6) sobre o corte dele.

### 3. Monte os pares

Siga a ordem dos pares do scene_plan. O corte entre A e B é o mais
importante do vídeo; o corte entre um par e o próximo pode ser seco e rápido.

Cada `cut.reason` (ou `nota` de fragmento) escrito como colisão:
`"plano 4 × plano 17 — parado contra pogo; o corpo parado é o que grita"`.

### 4. Quebra de grade (OBRIGATÓRIO)

Pelo menos UM corte cai fora do beat, de propósito — antecipado 2–4 frames
(corte nervoso) ou atrasado (corte bêbado). Registre:
`metadata.quebras_grade = [{"cut": "cut_09", "desvio_frames": -3, "motivo": "..."}]`.

### 5. Motivo

Cada volta do motivo com transformação concreta: `speed`, espelhar, escala
(`zoom`), ou um fx (`neg`, `rev`, `stut2`) aplicado só nele. A primeira volta
é a mais limpa e a mais longa; a última, a mais destruída.

### 6. Abuso por cima (o passe destrutivo)

Declare em `metadata.abuso[]`, em segundos do TIMELINE FINAL. Só tipos que
`scripts/selvagem/abuso.py` suporta (`python3 scripts/selvagem/abuso.py --list`):

- janela (efeito por cima): `rgb_split`, `chroma_sangra`, `negativo`,
  `estouro`, `sujeira`, `fantasma`, `borrao_temporal`, `diferenca`
- estruturais (trocam os frames, não podem se sobrepor): `stutter`,
  `congela`, `reverso`

```json
{"tipo": "stutter", "inicio": 12.0, "fim": 12.5, "frames": 2,
 "plano": 13, "motivo": "a guitarra engasga no ataque; o plano 13 é o grito, a imagem engasga junto"}
```

Regras (valem em qualquer modo):
- todo abuso tem `plano` (do mapa) e `motivo`. Sem os dois, apague;
- confira se o efeito FUNCIONA no plano: `negativo` em plano escuro some,
  `fantasma` em plano parado não faz nada, `sujeira` leve em 720p não aparece;
- `negativo` e `estouro`: 2–6 frames, salvo no modo saturação;
- a densidade vem do MODO (seção 1), não de um número fixo.

Abuso que o script não faz (datamosh, slit-scan, displacement, recorte em
máscara) → `metadata.abuso_manual[]` com o mesmo formato; vira só marcador
no XML pra ser feito no AE. Não escreva caminho de menu nem nome de efeito do
Premiere/AE aqui: descreva o gesto; a execução fica com `premiere-master` /
`ae-operador`.

### 7. Silêncio seco

`metadata.silence_window = {"start_seconds": .., "end_seconds": ..}` —
0.3–1.5s, sem fade. No compose, o áudio cai a zero instantâneo.

### 8. Campos fixos

- `renderer_family: "documentary-montage"` (o enum do schema não tem
  selvagem; o compose usa esse renderer só pro corpo limpo quando não há
  remontagem)
- `metadata.gramatica: "selvagem"`
- transições: `cut` em quase tudo; nada de `dissolve` além de um.

## Quality gate

- `mapa.json` existe e a folha de planos foi OLHADA
- `metadata.modo` declarado e respeitado (regra única sem exceções; saturação com curva)
- todo abuso e todo fragmento citam o plano do mapa e têm motivo
- `abuso.py --dry-run` não acusa erro (janelas dentro da duração, estruturais sem sobreposição)
- ≥ 1 quebra de grade, motivo transformado nas 3 voltas
- `regra_ruptura` do brief respeitada (`metadata.regra_ruptura_check`)
- soma dos cuts/fragmentos ±10% da duração do brief

## Gate

Apresente: o modo, a linha do tempo resumida (pares + fragmentos + abusos,
com número do plano), e pergunte ao usuário onde a montagem "relaxa" demais e
onde ela "grita" à toa. Ofereça o modo não escolhido mais provocador.
Checkpoint e ENCERRE o turno.
