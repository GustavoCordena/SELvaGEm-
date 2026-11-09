# selvagem-montage — pipeline de colisão pro OpenMontage

O OpenMontage vem com um pipeline de montagem documental que **proíbe**
glitch, RGB split, freeze-frame e transição chamativa ("lê como linguagem de
rede social"). Este pacote é o fork invertido: a mesma máquina, com a
gramática do Selvagem — colisão em vez de conexão, abuso visual com motivo
escrito, motivo recorrente que muda de sentido, e entrega em **XML pro
Premiere** em vez de vídeo "pronto".

## O que tem aqui

```
pipeline_defs/selvagem-montage.yaml          # o pipeline (5 stages, valida no schema do repo)
skills/pipelines/selvagem-montage/
  executive-producer.md                      # filosofia + overrides (footage local primeiro)
  idea-director.md                           # tese "A contra B → C", motivo, regra de ruptura
  scene-director.md                          # slots em PARES de colisão, slot "ferida"
  edit-director.md                           # quebra de grade, abuso com densidade controlada
  compose-director.md                        # corpo limpo → abuso → contact sheet → XML
scripts/selvagem/
  abuso.py                                   # passe destrutivo ffmpeg (11 tipos)
  premiere_xml.py                            # edit_decisions → XML FCP7 pro Premiere
skills/INDEX.md                              # (versão com a entrada do pipeline)
```

## Instalar

1. Clone e configure o OpenMontage normalmente:
   ```
   git clone https://github.com/calesthio/OpenMontage.git
   cd OpenMontage
   make setup
   ```
2. Copie o conteúdo deste zip **por cima** da pasta `OpenMontage` (as pastas
   batem). Só `skills/INDEX.md` é sobrescrito; o resto é arquivo novo.
3. Teste que o pipeline carrega:
   ```
   python -c "from lib.pipeline_loader import load_pipeline; print(load_pipeline('selvagem-montage')['name'])"
   ```

## Usar

Abra a pasta no Claude Code e peça, por exemplo:

> Usa o pipeline selvagem-montage. 30 segundos pro reel do Selvagem.
> Footage meu em D:\SELVAGEM\brutos, música em D:\SELVAGEM\musica\morde.wav.
> A briga é hiena contra leão.

O agente vai parar em cada gate (brief, pares de colisão, assets, edit) pra
você aprovar. No fim você recebe:

- `renders/body.mp4` — corte limpo, pra sentir a colisão sem efeito
- `renders/final_destruido.mp4` — com os abusos aplicados
- `renders/selvagem_premiere.xml` — **a entrega de verdade**: Arquivo >
  Importar no Premiere. Cada abuso vira um marcador na sequência com o
  motivo no comentário. Você executa à mão (ou no AE), onde o controle é seu.

## Os abusos (`python scripts/selvagem/abuso.py --list`)

| Tipo | O que faz |
|------|-----------|
| `rgb_split` | separa canais R/B — imagem rachada |
| `chroma_sangra` | croma vazando, VHS gasto |
| `negativo` | inverte — use em 2–6 frames |
| `estouro` | estoura luminância |
| `sujeira` | ruído pesado animado |
| `fantasma` | rastro dos pixels claros |
| `borrao_temporal` | funde N frames, movimento vira mancha |
| `diferenca` | só o que se move aparece |
| `stutter` | gagueira: repete N frames em loop na janela |
| `congela` | freeze proposital |
| `reverso` | janela de trás pra frente |

Tudo preserva duração e sync de áudio. Dá pra usar o script sozinho, fora do
pipeline, em qualquer vídeo seu:

```
python scripts/selvagem/abuso.py --input clipe.mp4 --abusos abusos.json --output clipe_destruido.mp4
```
com `abusos.json` = `[{"tipo":"stutter","inicio":2.0,"fim":2.5,"frames":2}, ...]`

## Limites honestos

- O XML não aplica velocidade (cuts com `speed` viram marcador) e só leva o
  vídeo dos clipes + a música; o áudio próprio dos clipes não vai.
- Os caminhos no XML são do computador onde o pipeline rodou. Se rodar em
  outra máquina, o Premiere pede "Localizar mídia".
- `premiere_xml.py` gera XML válido no formato FCP7 que o Premiere importa,
  mas não foi aberto num Premiere real durante o desenvolvimento — teste com
  um projeto curto primeiro.
- Datamosh, slit-scan, displacement: não estão no script. O edit coloca em
  `abuso_manual` e eles viram só marcador pra fazer no AE.
- Licença do OpenMontage é AGPLv3 — vale pra esses arquivos também se você
  distribuir.
