# Compose Director — Selvagem Montage

## Quando usar

O edit está aprovado. Você entrega TRÊS coisas, nesta ordem:

1. `renders/body.mp4` — o corpo LIMPO (cortes + música + silêncio seco, sem abuso)
2. `renders/final_destruido.mp4` — o corpo depois do passe de abuso
3. `renders/selvagem_premiere.xml` — o esqueleto pro Premiere, com marcadores

A entrega principal é o XML. O mp4 destruído é rascunho de ritmo.

## Runtime (RESTRIÇÃO DURA)

`render_runtime` travado como `remotion` no idea. O corpo limpo sai pelo
`video_compose` em Remotion; HyperFrames não é usado neste pipeline (sem
paridade com o CinematicRenderer do documentary-montage). Trocar em silêncio
pra hyperframes ou ffmpeg puro no corpo é violação — se o Remotion falhar,
pare e pergunte ao usuário. Passe o `proposal_packet` pro
`video_compose.execute()` pra a checagem `runtime_swap_detected` funcionar.
O passe de abuso (ffmpeg) roda DEPOIS e não conta como troca de runtime.

## 1. Corpo limpo

Siga `pipelines/documentary-montage/compose-director.md` seções 0–3 e 5–6
(hard requirement, canvas, concat plan via `video_compose`
`operation="render"`, grade por LUT, render spec, verificação), com estas
diferenças:

- **Pule o end-tag inteiro (seção 4b).** Selvagem não fecha com frase
  filosófica em serifa. Se o brief pedir cartela final, ela é um cut normal.
- **Grade:** prefira LUT de contraste alto / preto esmagado. Se o brief
  pedir "sujo", NÃO faça o grade uniforme suavizar diferença entre eras —
  a diferença é colisão de tempo, é conteúdo.
- **Silêncio seco:** em `edit_decisions.metadata.silence_window`, o volume
  da música vai a 0 SEM rampa. No ffmpeg:
  `volume=enable='between(t,S,E)':volume=0`.

## 2. Passe de abuso

```bash
python3 scripts/selvagem/abuso.py \
  --input projects/<nome>/renders/body.mp4 \
  --edit  projects/<nome>/edit_decisions.json \
  --output projects/<nome>/renders/final_destruido.mp4
```

- O script valida as janelas e falha alto se algo estiver fora do vídeo ou
  se dois abusos estruturais se sobrepuserem. Não "conserte" mexendo no
  script — volte ao edit e corrija a janela (send-back).
- Duração de saída tem que ser igual à de entrada (o script imprime as duas).

## 3. Inspeção (OBRIGATÓRIA)

Gere uma contact sheet com 1 frame do MEIO de cada janela de abuso e
OLHE pra ela (Read na imagem):

```bash
ffmpeg -i final_destruido.mp4 -vf "select='<eq(n,F1)+eq(n,F2)+...>',scale=320:-1,tile=6x1" \
  -frames:v 1 -fps_mode passthrough renders/contato_abuso.png
```

Pergunte de cada frame: o abuso está visível? Ele destrói a imagem certa?
Um `negativo` em plano escuro some; um `fantasma` em plano estático não faz
nada. Se não funcionou, registre em `render_report.warnings` e sugira trocar
o tipo — não esconda.

## 4. XML pro Premiere

```bash
python3 scripts/selvagem/premiere_xml.py \
  --edit projects/<nome>/edit_decisions.json \
  --manifest projects/<nome>/asset_manifest.json \
  --root projects/<nome> \
  --output projects/<nome>/renders/selvagem_premiere.xml \
  --fps <fps do canvas> --width <w> --height <h> --nome "<título>"
```

- Cada abuso (e cada `abuso_manual`) vira marcador de sequência com nome do
  tipo e comentário com o motivo. O usuário vai executar à mão.
- Cuts com `speed` ≠ 1 viram marcador "[SPEED ...]" no clip — o XML não
  aplica velocidade; avise o usuário.
- Os caminhos no XML são ABSOLUTOS do ambiente onde rodou. Se o projeto
  foi gerado em outra máquina, avise que o Premiere vai pedir "Localizar
  mídia" (aponte pra pasta `assets/`).

## 5. Render report

`render_report` com `metadata`:
```json
{
  "body_path": "renders/body.mp4",
  "final_path": "renders/final_destruido.mp4",
  "premiere_xml_path": "renders/selvagem_premiere.xml",
  "abusos_aplicados": 7,
  "abusos_manuais": 2,
  "duracao_body": 30.0, "duracao_final": 30.0,
  "contato_abuso": "renders/contato_abuso.png",
  "gramatica": "selvagem"
}
```

## Gate final

Mostre a contact sheet e pergunte ao usuário: qual abuso funcionou, qual
virou enfeite? Lembre que a timeline de verdade é o XML — sugira por qual
marcador ele deveria começar a destruir no Premiere.
