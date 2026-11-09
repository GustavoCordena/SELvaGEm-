# Executive Producer — Selvagem Montage

## Quando usar

O usuário quer uma montagem curta (15–180s) cujo sentido nasce do CHOQUE
entre imagens, não da ligação suave entre elas. Videoclipe punk/underground,
vinheta, teaser, reel, abertura de série, manifesto visual.

Gatilhos: "Selvagem", "montagem por colisão", "corte que bate", "edição punk",
"faz brigar", "anti-clipe", "quero que a montagem brigue consigo mesma",
"Eisenstein", "montagem de atrações", "videoclipe caótico mas intencional".

Se o usuário quer um explainer limpo, um trailer polido ou um tone-poem
contemplativo, use outro pipeline (documentary-montage, cinematic).

## Filosofia (leia antes de qualquer stage)

1. **Colisão, não conexão.** Plano A + plano B = C, uma terceira ideia que
   nenhum dos dois contém (Eisenstein). Se o corte só "flui", ele falhou.
2. **Caos com intenção.** Todo abuso visual (glitch, freeze, stutter,
   negativo) precisa de um motivo escrito. Efeito sem motivo é filtro de
   Instagram — e o Selvagem odeia filtro de Instagram.
3. **Motivo recorrente.** Um objeto, gesto ou forma volta 3+ vezes, e a
   cada volta muda de sentido. É a espinha que deixa o caos legível.
4. **A máquina monta o esqueleto, o humano destrói.** O produto final deste
   pipeline NÃO é o vídeo pronto. É: (a) um rascunho destruído pra sentir o
   ritmo, e (b) um XML de Premiere com a timeline e marcadores de cada abuso,
   pro editor executar à mão no Premiere/After Effects, onde o controle é fino.
5. **Material próprio primeiro.** Footage do usuário tem textura, rosto e
   história. Stock e arquivo aberto entram como contaminação, não como base.

## Overrides sobre o asset-director do documentary-montage

O stage `assets` reaproveita `pipelines/documentary-montage/asset-director`,
COM estas exceções (elas vencem o texto daquele skill):

- **Pasta local primeiro.** Se `brief.metadata.fonte_material.local_dir`
  existe, rode `scene_detect` nos vídeos dessa pasta, quebre em sub-clipes,
  use `frame_sampler`/`video_analyzer` pra descrever cada um e preencha os
  slots a partir daí. Assets locais: `source_tool: "local"`,
  `subtype: "own_footage"`, `path` relativo ao projeto (copie ou faça link
  simbólico pra dentro de `assets/`). Só vá pro `corpus_builder` /
  `direct_clip_search` pros slots que ficaram sem candidato.
- **Reuso é permitido para o motivo.** O mesmo clipe pode aparecer em vários
  slots do motivo — o edit vai transformá-lo a cada volta. Para os demais
  slots, a regra de não-reuso continua.
- **Sem geração por IA** salvo pedido explícito (igual ao documentary).
- **Proporção de fonte:** respeite `brief.metadata.fonte_material.proporcao`
  (ex.: 70% local / 30% arquivo). Registre o real em `metadata.fonte_real`.

## Stages

| Stage | Skill | Produz |
|-------|-------|--------|
| idea | `selvagem-montage/idea-director.md` | brief (tese de colisão, motivo, regra de ruptura) |
| scene_plan | `selvagem-montage/scene-director.md` | scene_plan em pares de colisão |
| assets | `documentary-montage/asset-director.md` + overrides acima | asset_manifest |
| edit | `selvagem-montage/edit-director.md` | edit_decisions + metadata.abuso |
| compose | `selvagem-montage/compose-director.md` | body.mp4, final_destruido.mp4, selvagem_premiere.xml |

## Ferramentas fora do registry (custom_scripts)

| Script | Papel |
|--------|-------|
| `scripts/selvagem/abuso.py` | Passe destrutivo em janelas de tempo: rgb_split, chroma_sangra, negativo, estouro, sujeira, fantasma, borrao_temporal, diferenca, stutter, congela, reverso. Preserva duração e sync. `--list` mostra tudo. |
| `scripts/selvagem/mapa.py` | Lê o material antes de tudo: BPM, beats, ataques, cortes de imagem, lista de planos. Obrigatório no edit. |
| `scripts/selvagem/remonta.py` | Remonta o vídeo a partir de fragmentos (`s`, `d`, `fx`) sobre o áudio inteiro. É o caminho do corpo quando o edit remonta. |
| `scripts/selvagem/premiere_xml.py` | Exporta edit_decisions como XML FCP7 (xmeml v4) pro Premiere, com marcadores de sequência pra cada abuso e silêncio. |

## Regras entre stages

- **Toda decisão criativa pergunta ao usuário o que ele acha** nos gates
  com aprovação humana. Não apresente só o artefato: pergunte o que ele vê,
  onde o corte não bateu, o que ele faria diferente.
- **Ofereça pelo menos uma direção não óbvia** em cada gate (ex.: inverter
  a ordem dos pares, trocar a música, matar o motivo no meio).
- **Fale português**, trate o usuário por "você".
- Abuso novo que não existe em `abuso.py` → NÃO invente no edit. Coloque em
  `metadata.abuso_manual[]` (vira só marcador no XML) e diga ao usuário.

## Lição do primeiro teste real

Filtro por cima de uma montagem pronta, escolhido só pelo som e contido por
uma regra fixa de densidade, ficou fraco: decoração, não colisão. Por isso o
pipeline agora exige: mapear o material (planos + ataques) antes de decidir,
escolher um modo de violência (contido / saturação / regra única) e remontar
antes de filtrar.

## Armadilhas

- Glitch em todo corte = papel de parede. A densidade de abuso é o que dá
  peso a ele. Pouco e no lugar certo.
- Confundir caos com aleatoriedade. Se você não consegue escrever o motivo
  de um corte em uma linha, o corte é arbitrário.
- Entregar o mp4 como se fosse o final. Não é. O XML é a entrega principal.
